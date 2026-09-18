import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tavily import TavilyClient

from agents.fact_check_agent.agent_state import (
    AgentState,
    EvidenceSource,
    VerificationResult,
)
from agents.shared.llm import llm


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY is not configured.")

search_client = TavilyClient(api_key=TAVILY_API_KEY)


# ============================================================
# SEARCH CONFIGURATION
# ============================================================

MAX_SEARCH_RESULTS = 5
MAX_EVIDENCE_PER_CLAIM = 3
MAX_CONTENT_LENGTH = 700

BAD_DOMAINS = {
    "facebook.com",
    "reddit.com",
    "quora.com",
    "youtube.com",
    "brainly.com",
    "pinterest.com",
    "instagram.com",
}

TRUSTED_DOMAIN_SCORES = {
    "reuters.com": 1.00,
    "who.int": 1.00,
    "nasa.gov": 1.00,
    "gov": 0.95,
    "edu": 0.90,
    "nature.com": 0.95,
    "science.org": 0.95,
    "bbc.com": 0.90,
    "britannica.com": 0.90,
    "nationalgeographic.com": 0.90,
    "wikipedia.org": 0.80,
}


# ============================================================
# STRUCTURED VERIFICATION OUTPUT
# ============================================================

class ClaimVerification(BaseModel):
    """Verification result returned by Gemini for one claim."""

    claim_id: int = Field(..., ge=1)

    verdict: str = Field(
        ...,
        description=(
            "One of: True, False, Partially True, Unverifiable"
        ),
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )

    reason: str = Field(
        ...,
        description="Evidence-based explanation.",
    )

    supporting_evidence_ids: list[int] = Field(
        default_factory=list,
        description=(
            "1-based indexes of evidence items supporting the claim."
        ),
    )

    conflicting_evidence_ids: list[int] = Field(
        default_factory=list,
        description=(
            "1-based indexes of evidence items contradicting the claim."
        ),
    )

    uncertainty_reason: str | None = None


class BatchVerificationOutput(BaseModel):
    """Verification results for all claims in one Gemini call."""

    results: list[ClaimVerification] = Field(
        default_factory=list,
    )


# ============================================================
# DOMAIN HELPERS
# ============================================================

def _hostname(url: str) -> str:
    """Extract a normalized hostname from a URL."""

    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""


def is_bad(url: str) -> bool:
    """Reject known low-value social/content-farm domains."""

    hostname = _hostname(url).lower()

    return any(
        hostname == domain
        or hostname.endswith(f".{domain}")
        for domain in BAD_DOMAINS
    )


def get_credibility(url: str) -> float:
    """
    Estimate source credibility using deterministic domain heuristics.

    This is a heuristic signal, not a claim that a source is objectively
    correct.
    """

    hostname = _hostname(url).lower()

    if not hostname:
        return 0.0

    for domain, score in TRUSTED_DOMAIN_SCORES.items():
        if (
            hostname == domain
            or hostname.endswith(f".{domain}")
            or (
                hostname.endswith(f".{domain.split('.')[-1]}")
                and domain in {"gov", "edu"}
            )
        ):
            return score

    if url.lower().startswith("https://"):
        return 0.60

    return 0.40


# ============================================================
# SEARCH
# ============================================================

def search(query: str) -> list[dict]:
    """
    Retrieve web evidence from Tavily.

    No LLM call is performed here.
    """

    try:
        response = search_client.search(
            query=query,
            max_results=MAX_SEARCH_RESULTS,
            search_depth="advanced",
            include_answer=False,
            include_raw_content=False,
        )

        results = response.get("results", [])

        cleaned_results: list[dict] = []

        for result in results:
            url = str(result.get("url", "") or "").strip()

            if not url:
                continue

            if is_bad(url):
                continue

            content = str(result.get("content", "") or "").strip()

            if not content:
                continue

            tavily_score = float(
                result.get("score", 0.0) or 0.0
            )

            credibility = get_credibility(url)

            cleaned_results.append(
                {
                    "title": (
                        str(result.get("title", "") or "Untitled source")
                        .strip()
                    ),
                    "content": content[:MAX_CONTENT_LENGTH],
                    "url": url,
                    "score": tavily_score,
                    "credibility": credibility,
                }
            )

        # Combine retrieval relevance with source credibility.
        for item in cleaned_results:
            item["combined_score"] = (
                0.65 * item["score"]
                + 0.35 * item["credibility"]
            )

        cleaned_results.sort(
            key=lambda item: item["combined_score"],
            reverse=True,
        )

        return cleaned_results[:MAX_EVIDENCE_PER_CLAIM]

    except Exception as exc:
        print(f"[Tavily Search Error] {exc}")
        return []


# ============================================================
# EVIDENCE COLLECTION
# ============================================================

def collect_evidence(state: AgentState) -> dict:
    """
    Retrieve web evidence for every extracted claim.

    This stage performs retrieval only and never consumes Gemini quota.
    """

    print("\n[Agent 2] Retrieving web evidence...")

    evidence_map: dict[int, list[EvidenceSource]] = {}

    for claim in state.claims:
        query = claim.normalized_claim or claim.claim

        print(
            f"[Claim {claim.id}] Searching: {query}"
        )

        results = search(query)

        evidence_items: list[EvidenceSource] = []

        for result in results:
            evidence_items.append(
                EvidenceSource(
                    title=result["title"],
                    content=result["content"],
                    url=result["url"],
                    score=result["score"],
                    query_used=query,
                    credibility=result["credibility"],
                )
            )

        evidence_map[claim.id] = evidence_items

        print(
            f"[Claim {claim.id}] "
            f"Retrieved {len(evidence_items)} sources"
        )

    return {
        "evidence": evidence_map,
    }


# ============================================================
# VERIFICATION HELPERS
# ============================================================

def _is_rate_limit_error(exc: Exception) -> bool:
    """Detect common Gemini/API quota exhaustion errors."""

    message = str(exc).lower()

    return any(
        marker in message
        for marker in (
            "429",
            "resource_exhausted",
            "quota exceeded",
            "rate limit",
            "too many requests",
        )
    )


def _build_unavailable_verifications(
    claims,
    reason: str,
) -> dict[int, VerificationResult]:
    """
    Create explicit verification-unavailable results.

    These are NOT factual verdicts. They communicate that the verification
    service could not complete the reasoning step.
    """

    return {
        claim.id: VerificationResult(
            verdict="Unverifiable",
            confidence=0.0,
            reason=(
                "The available web evidence was retrieved, but "
                "AI verification could not be completed."
            ),
            supporting_sources=[],
            conflicting_sources=[],
            uncertainty_reason=reason,
        )
        for claim in claims
    }


def _deduplicate_urls(urls: list[str]) -> list[str]:
    """Preserve source order while removing duplicate URLs."""

    return list(dict.fromkeys(url for url in urls if url))


# ============================================================
# BATCH VERIFICATION
# ============================================================

def verify_evidence(state: AgentState) -> dict:
    """
    Verify all claims using the retrieved evidence.

    Exactly one structured Gemini request is made for the complete batch.

    If Gemini is unavailable, every claim receives an explicit
    Unverifiable result rather than a fabricated factual verdict.
    """

    print(
        "\n[Agent 3] Verifying claims using evidence..."
    )

    if not state.claims:
        return {
            "verifications": {}
        }

    evidence_context_parts: list[str] = []

    for claim in state.claims:
        evidence_context_parts.append(
            f"\n===== CLAIM {claim.id} =====\n"
            f"Claim: {claim.claim}\n"
        )

        sources = state.evidence.get(
            claim.id,
            [],
        )

        if not sources:
            evidence_context_parts.append(
                "No web evidence was retrieved.\n"
            )
            continue

        for index, source in enumerate(
            sources,
            start=1,
        ):
            evidence_context_parts.append(
                f"""
Evidence {index}
Title: {source.title}
URL: {source.url}
Tavily relevance: {source.score}
Source credibility heuristic: {source.credibility}
Content:
{source.content}
"""
            )

    evidence_context = "\n".join(
        evidence_context_parts
    )

    prompt = f"""
You are the verification engine of an evidence-first fact-checking
system.

Verify every claim using ONLY the supplied web evidence.

Do NOT rely on your own background knowledge when the supplied evidence
does not establish the answer.

VERDICT RULES:

True:
The evidence supports the claim without a material contradiction.

False:
Reliable evidence directly contradicts the claim.

Partially True:
The evidence supports part of the claim but contradicts or qualifies
another material part.

Unverifiable:
The supplied evidence is insufficient to establish whether the claim
is true or false.

IMPORTANT:

1. Evaluate each claim independently.
2. Do not transfer evidence between unrelated claims.
3. Do not treat the number of sources as proof of truth.
4. Prefer evidence that directly addresses the claim.
5. Distinguish contradiction from absence of evidence.
6. If evidence conflicts, use Partially True or Unverifiable when
   appropriate.
7. Confidence must reflect evidence strength and directness.
8. Never invent sources, URLs, quotations, or evidence.
9. supporting_evidence_ids and conflicting_evidence_ids are 1-based
   indexes of evidence items listed under the corresponding claim.
10. Keep reasons concise but specific.
11. If evidence is insufficient, explain what is missing.
12. Return exactly one result for every claim.
13. A claim can only be marked True or False when the supplied evidence
   provides sufficient support for that verdict.

SUPPLIED CLAIMS AND EVIDENCE:

{evidence_context}
"""

    try:
        structured_llm = llm.with_structured_output(
            BatchVerificationOutput
        )

        response: BatchVerificationOutput = (
            structured_llm.invoke(prompt)
        )

        verification_map: dict[int, VerificationResult] = {}

        allowed_verdicts = {
            "True",
            "False",
            "Partially True",
            "Unverifiable",
        }

        for result in response.results:
            claim_evidence = state.evidence.get(
                result.claim_id,
                [],
            )

            supporting_sources: list[str] = []

            for evidence_id in result.supporting_evidence_ids:
                index = evidence_id - 1

                if 0 <= index < len(claim_evidence):
                    url = claim_evidence[index].url

                    if url:
                        supporting_sources.append(url)

            conflicting_sources: list[str] = []

            for evidence_id in result.conflicting_evidence_ids:
                index = evidence_id - 1

                if 0 <= index < len(claim_evidence):
                    url = claim_evidence[index].url

                    if url:
                        conflicting_sources.append(url)

            verdict = result.verdict.strip()

            if verdict not in allowed_verdicts:
                verdict = "Unverifiable"

            verification_map[result.claim_id] = VerificationResult(
                verdict=verdict,
                confidence=result.confidence,
                reason=result.reason.strip(),
                supporting_sources=_deduplicate_urls(
                    supporting_sources
                ),
                conflicting_sources=_deduplicate_urls(
                    conflicting_sources
                ),
                uncertainty_reason=(
                    result.uncertainty_reason.strip()
                    if result.uncertainty_reason
                    else None
                ),
            )

        # Never allow incomplete structured output to silently remove claims.
        for claim in state.claims:
            if claim.id in verification_map:
                continue

            verification_map[claim.id] = VerificationResult(
                verdict="Unverifiable",
                confidence=0.0,
                reason=(
                    "The verification model did not return a complete "
                    "result for this claim."
                ),
                supporting_sources=[],
                conflicting_sources=[],
                uncertainty_reason=(
                    "Incomplete verification response."
                ),
            )

        print(
            f"[Agent 3] Verified {len(verification_map)} claims."
        )

        return {
            "verifications": verification_map,
        }

    except Exception as exc:
        if _is_rate_limit_error(exc):
            reason = (
                "Gemini verification is temporarily unavailable because "
                "the configured API quota or rate limit has been reached. "
                "Retrieved web evidence remains available, but no factual "
                "verdict is asserted."
            )

            print(
                "[Verification Warning] Gemini quota/rate limit reached. "
                "Returning explicit Unverifiable results."
            )
        else:
            reason = (
                "The verification service encountered an unexpected "
                "error. Retrieved web evidence remains available, but "
                "no factual verdict is asserted."
            )

            print(
                f"[Verification Error] {exc}"
            )

        return {
            "verifications": _build_unavailable_verifications(
                state.claims,
                reason,
            )
        }