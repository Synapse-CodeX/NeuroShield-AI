import re
from collections.abc import Iterable

from agents.fact_check_agent.agent_state import (
    AgentState,
    Claim,
    ClaimExtractionOutput,
)
from agents.shared.llm import llm


# ---------------------------------------------------------------------------
# Gemini extraction
# ---------------------------------------------------------------------------

def _extract_with_gemini(text: str) -> list[Claim]:
    """Extract atomic, independently verifiable claims using Gemini."""

    structured_llm = llm.with_structured_output(ClaimExtractionOutput)

    prompt = f"""
You are the claim extraction component of an evidence-first fact-checking
system.

Extract ONLY factual claims from the text below.

A good claim must:
- be independently verifiable using external sources
- express one atomic proposition
- preserve the meaning of the original statement
- be understandable without surrounding context
- avoid opinions, questions, instructions, predictions, or vague statements

Classify each claim as exactly one of:
- factual: ordinary factual statement
- numerical: contains a measurable quantity, statistic, percentage, amount,
  ranking, count, or numerical measurement
- entity: primarily makes a claim about a named person, organization, place,
  product, object, or other identifiable entity
- temporal: primarily concerns a date, year, historical event, duration,
  chronology, or time-related fact

For each claim:
- assign a unique integer id starting at 1
- preserve the original claim meaning
- provide a concise normalized_claim suitable for web search

Do not invent facts.
Do not combine unrelated statements.
Do not return commentary outside the structured output.

TEXT:
{text}
""".strip()

    result = structured_llm.invoke(prompt)

    claims = getattr(result, "claims", None)

    if not claims:
        return []

    return _normalize_claims(claims)


# ---------------------------------------------------------------------------
# Deterministic fallback
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> list[str]:
    """
    Split text into reasonably meaningful sentences.

    This intentionally remains lightweight and dependency-free because it is
    used when the LLM is unavailable.
    """

    normalized = re.sub(r"\s+", " ", text.strip())

    if not normalized:
        return []

    # Protect common abbreviations from naive sentence splitting.
    protected = normalized

    abbreviations = {
        "Mr.": "Mr<prd>",
        "Mrs.": "Mrs<prd>",
        "Ms.": "Ms<prd>",
        "Dr.": "Dr<prd>",
        "Prof.": "Prof<prd>",
        "e.g.": "e<prd>g<prd>",
        "i.e.": "i<prd>e<prd>",
        "etc.": "etc<prd>",
    }

    for original, replacement in abbreviations.items():
        protected = protected.replace(original, replacement)

    sentences = re.split(r"(?<=[.!?])\s+", protected)

    restored = [
        sentence.replace("<prd>", ".").strip()
        for sentence in sentences
        if sentence.strip()
    ]

    return restored


def _looks_like_claim(sentence: str) -> bool:
    """Filter out obvious non-claims from fallback extraction."""

    text = sentence.strip()

    if len(text) < 12:
        return False

    lowered = text.lower()

    # Questions are not claims.
    if text.endswith("?"):
        return False

    # Common non-factual sentence patterns.
    non_claim_patterns = (
        r"^(please|let's|let us|should we|can we|could we)\b",
        r"^(i think|i believe|in my opinion)\b",
        r"^(maybe|perhaps|hopefully)\b",
        r"^(click|visit|try|use|download|install)\b",
    )

    if any(re.search(pattern, lowered) for pattern in non_claim_patterns):
        return False

    # Pure headings should not become claims.
    if len(text.split()) <= 5 and not re.search(r"\d", text):
        if text.upper() == text:
            return False

    # A sentence should contain at least some alphabetic content.
    if not re.search(r"[A-Za-z]", text):
        return False

    return True


def _classify_claim(text: str) -> str:
    """Assign a lightweight claim type for fallback extraction."""

    lowered = text.lower()

    temporal_patterns = (
        r"\b(?:19|20)\d{2}\b",
        r"\b(?:19|20)\d{2}s\b",
        r"\b(?:january|february|march|april|may|june|july|august|"
        r"september|october|november|december)\b",
        r"\b(?:before|after|during|since|until|between)\b",
        r"\b(?:yesterday|today|tomorrow|last year|next year)\b",
        r"\b(?:century|decade|historical|ancient|modern)\b",
        r"\b(?:became|founded|established|occurred|happened)\b"
        r".*\b(?:in|on|during|after|before)\b",
    )

    if any(re.search(pattern, lowered) for pattern in temporal_patterns):
        return "temporal"

    # Numerical claims.
    numerical_patterns = (
        r"\b\d+(?:\.\d+)?\s*%",
        r"\b\d+(?:\.\d+)?\s*(?:kg|km|m|cm|mm|mph|km/h|°c|°f|gb|mb|tb)\b",
        r"\b\d[\d,]*(?:\.\d+)?\b",
        r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten)"
        r"\s+(?:times|percent|people|users|items|countries|years)\b",
    )

    if any(re.search(pattern, lowered) for pattern in numerical_patterns):
        return "numerical"

    # Entity-oriented claims.
    entity_pattern = (
        r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\b"
    )

    if re.search(entity_pattern, text):
        return "entity"

    return "factual"


def _normalize_text(text: str) -> str:
    """Normalize whitespace without changing the semantic content."""

    return re.sub(r"\s+", " ", text).strip()


def _normalize_claims(claims: Iterable[Claim]) -> list[Claim]:
    """
    Clean, deduplicate, and re-index claims.

    The original claim text is preserved while normalized_claim is generated
    when the model did not provide one.
    """

    normalized_claims: list[Claim] = []
    seen: set[str] = set()

    for claim in claims:
        claim_text = _normalize_text(claim.claim)

        if not claim_text:
            continue

        key = claim_text.casefold()

        if key in seen:
            continue

        seen.add(key)

        normalized_search_claim = (
            _normalize_text(claim.normalized_claim)
            if claim.normalized_claim
            else claim_text
        )

        normalized_claims.append(
            Claim(
                id=len(normalized_claims) + 1,
                claim=claim_text,
                type=claim.type,
                normalized_claim=normalized_search_claim,
            )
        )

    return normalized_claims


def _extract_with_fallback(text: str) -> list[Claim]:
    """
    Deterministically extract candidate claims when Gemini is unavailable.

    This is intentionally conservative. It does not attempt to determine
    whether a claim is true or false; it only identifies statements that can
    subsequently be searched and verified.
    """

    candidates: list[Claim] = []

    for sentence in _split_sentences(text):
        if not _looks_like_claim(sentence):
            continue

        claim_text = _normalize_text(sentence)

        candidates.append(
            Claim(
                id=len(candidates) + 1,
                claim=claim_text,
                type=_classify_claim(claim_text),
                normalized_claim=claim_text,
            )
        )

    return _normalize_claims(candidates)


# ---------------------------------------------------------------------------
# LangGraph node
# ---------------------------------------------------------------------------

def extract_claims(state: AgentState) -> dict:
    """
    LangGraph node for claim extraction.

    Primary path:
        Gemini structured extraction.

    Reliability path:
        deterministic extraction when Gemini fails for any reason.

    Importantly, an LLM/API failure is never represented as "no claims".
    The fallback attempts to recover candidate claims so downstream evidence
    collection can continue.
    """

    print("[Agent 1] Extracting claims...")

    text = _normalize_text(state.input_text)

    if not text:
        print("[Claim Extraction] Empty input.")
        return {"claims": []}

    try:
        claims = _extract_with_gemini(text)

        print(
            f"[Claim Extraction] Gemini extracted {len(claims)} claim(s)."
        )

        return {"claims": claims}

    except Exception as exc:
        print(
            "[Claim Extraction] Gemini unavailable. "
            f"Using deterministic fallback. Error: {exc}"
        )

        claims = _extract_with_fallback(text)

        print(
            f"[Claim Extraction] Fallback extracted {len(claims)} claim(s)."
        )

        return {"claims": claims}