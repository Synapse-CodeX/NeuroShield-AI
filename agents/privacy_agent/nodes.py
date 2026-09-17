from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agents.privacy_agent.state import (
    ChunkExtraction,
    GraphState,
    PrivacyExtraction,
    PrivacyReport,
)
from agents.shared.embeddings import embedding_model
from agents.shared.evidence import Evidence, Finding
from agents.shared.llm import llm
from agents.shared.risk_engine import RiskEngine, RiskSignal


# ---------------------------------------------------------------------------
# SHARED COMPONENTS
# ---------------------------------------------------------------------------

structured_llm = llm.with_structured_output(
    PrivacyExtraction
)

risk_engine = RiskEngine()


# ---------------------------------------------------------------------------
# RETRIEVAL CONFIGURATION
# ---------------------------------------------------------------------------

RETRIEVAL_QUERIES = {
    "data_collected": (
        "What personal information, sensitive information, "
        "device information, identifiers, location information, "
        "or usage information does the company collect?"
    ),
    "data_usage": (
        "How does the company use personal information? "
        "Look for service delivery, personalization, analytics, "
        "advertising, marketing, product improvement, and other purposes."
    ),
    "third_party_sharing": (
        "Who does the company share personal information with? "
        "Look for service providers, advertising partners, analytics "
        "providers, affiliates, business partners, and authorities."
    ),
    "tracking_methods": (
        "What cookies, pixels, SDKs, analytics systems, advertising "
        "identifiers, or tracking technologies are used?"
    ),
    "retention_policy": (
        "How long does the company retain personal information? "
        "Look for explicit durations, deletion rules, retention periods, "
        "indefinite retention, and conditions for retaining data."
    ),
}


EVIDENCE_KEYWORDS = {
    "third_party_sharing": [
        "share",
        "third party",
        "service provider",
        "partner",
        "affiliate",
    ],
    "location": [
        "location",
        "geolocation",
    ],
    "advertising": [
        "advertising",
        "advertisement",
        "targeted",
        "marketing",
    ],
    "retention": [
        "retain",
        "retention",
        "indefinitely",
        "indefinite",
        "permanent",
        "forever",
        "delete",
    ],
    "tracking": [
        "cookie",
        "cookies",
        "pixel",
        "pixels",
        "sdk",
        "tracking",
        "analytics",
    ],
    "sensitive_data": [
        "health",
        "medical",
        "biometric",
        "genetic",
        "financial",
        "religious",
        "racial",
        "sexual",
    ],
}


# ---------------------------------------------------------------------------
# TEXT UTILITIES
# ---------------------------------------------------------------------------

def _normalize_text(text: str) -> str:
    """Normalize whitespace without changing semantic content."""

    return " ".join(
        text.replace("\n", " ").split()
    ).strip()


def _extract_relevant_excerpt(
    text: str,
    keywords: list[str],
    max_length: int = 500,
) -> str:
    """
    Extract a compact evidence excerpt directly from source text.

    No LLM rewriting occurs here. This guarantees that evidence shown
    to the user comes directly from the supplied privacy policy.
    """

    normalized = _normalize_text(text)

    if not normalized:
        return ""

    # Basic sentence segmentation.
    sentences = [
        sentence.strip()
        for sentence in normalized.replace(
            "! ",
            "!\n",
        ).replace(
            "? ",
            "?\n",
        ).replace(
            ". ",
            ".\n",
        ).splitlines()
        if sentence.strip()
    ]

    matching_sentences = []

    for sentence in sentences:

        lower_sentence = sentence.lower()

        if any(
            keyword.lower() in lower_sentence
            for keyword in keywords
        ):
            matching_sentences.append(
                sentence
            )

    if matching_sentences:

        excerpt = " ".join(
            matching_sentences[:2]
        )

    else:

        excerpt = " ".join(
            sentences[:2]
        )

    if len(excerpt) <= max_length:
        return excerpt

    truncated = excerpt[:max_length]

    if " " in truncated:
        truncated = truncated.rsplit(
            " ",
            1,
        )[0]

    return f"{truncated}..."


def _normalize_llm_content(content) -> str:
    """
    Normalize Gemini/LangChain content into plain text.

    Retained as a utility for compatibility with Gemini content blocks.
    """

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):

        text_parts: list[str] = []

        for item in content:

            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):

                text = item.get("text")

                if text:
                    text_parts.append(
                        str(text)
                    )

        return "\n".join(
            text_parts
        ).strip()

    if isinstance(content, dict):

        text = content.get("text")

        if text:
            return str(text).strip()

    return str(content).strip()


# ---------------------------------------------------------------------------
# CHUNKING
# ---------------------------------------------------------------------------

def chunk_node(state: GraphState) -> dict:
    """Split the privacy policy into overlapping chunks."""

    raw_text = (
        state.raw_text or ""
    ).strip()

    if not raw_text:
        return {
            "chunks": []
        }

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=[
            "\n\n",
            "\n",
            ". ",
            ", ",
            " ",
        ],
    )

    chunks = splitter.split_text(
        raw_text
    )

    return {
        "chunks": chunks
    }


# ---------------------------------------------------------------------------
# LOCAL FAISS INDEX
# ---------------------------------------------------------------------------

def embed_store_node(state: GraphState) -> dict:
    """
    Create a local FAISS vector index.

    Embeddings are generated locally using Hugging Face.
    """

    if not state.chunks:
        return {
            "vector_store": None
        }

    vector_store = FAISS.from_texts(
        state.chunks,
        embedding_model,
        metadatas=[
            {
                "chunk_index": str(index)
            }
            for index in range(
                len(state.chunks)
            )
        ],
    )

    return {
        "vector_store": vector_store
    }


# ---------------------------------------------------------------------------
# MULTI-QUERY RETRIEVAL
# ---------------------------------------------------------------------------

def _retrieve_context(
    state: GraphState,
    per_query: int = 2,
) -> list[tuple[int, str]]:
    """
    Perform local semantic retrieval for all privacy categories.

    The results are merged and deduplicated before being sent to Gemini.
    This gives us category-aware RAG while requiring only ONE LLM call.
    """

    if not state.chunks:
        return []

    if state.vector_store is None:
        return [
            (
                index,
                chunk,
            )
            for index, chunk in enumerate(
                state.chunks
            )
        ]

    retrieved: dict[
        int,
        str,
    ] = {}

    for query in RETRIEVAL_QUERIES.values():

        try:

            documents = (
                state.vector_store.similarity_search(
                    query,
                    k=min(
                        per_query,
                        len(state.chunks),
                    ),
                )
            )

        except Exception as exc:

            print(
                "[Privacy Retrieval] "
                f"Query failed: "
                f"{type(exc).__name__}: {exc}"
            )

            continue

        for document in documents:

            metadata = (
                document.metadata or {}
            )

            chunk_index = metadata.get(
                "chunk_index"
            )

            if chunk_index is None:

                try:

                    chunk_index = (
                        state.chunks.index(
                            document.page_content
                        )
                    )

                except ValueError:
                    continue

            try:

                chunk_index = int(
                    chunk_index
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            retrieved[
                chunk_index
            ] = document.page_content

    # Preserve original document order.
    return [
        (
            index,
            retrieved[index],
        )
        for index in sorted(
            retrieved
        )
    ]


# ---------------------------------------------------------------------------
# SINGLE GEMINI EXTRACTION
# ---------------------------------------------------------------------------

def extract_node(state: GraphState) -> dict:
    """
    Perform one structured Gemini extraction over the semantically
    retrieved policy context.

    This deliberately uses a single LLM request to remain compatible
    with restrictive free-tier quotas.
    """

    if not state.chunks:
        return {
            "extracted_results": [],
            "chunk_extractions": [],
        }

    contexts = _retrieve_context(
        state,
        per_query=2,
    )

    if not contexts:
        contexts = [
            (
                index,
                chunk,
            )
            for index, chunk in enumerate(
                state.chunks[:10]
            )
        ]

    context_text = "\n\n".join(
        (
            f"[POLICY CHUNK {index + 1}]\n"
            f"{text}"
        )
        for index, text in contexts
    )

    prompt = f"""
You are an expert privacy-policy analysis engine.

Analyze ONLY the supplied privacy-policy excerpts.

Extract all explicitly supported information into the
PrivacyExtraction schema.

You must analyze:

1. Data collection
2. Data usage
3. Third-party sharing
4. Tracking technologies
5. Data retention

STRICT GROUNDING RULES:

- Use only information explicitly present in the supplied text.
- Never hallucinate.
- Never infer a company practice that is not stated.
- Never invent third parties.
- Never invent retention periods.
- Never invent tracking technologies.
- Preserve important details.
- If a category is not supported by the text, return an empty value.
- Treat the policy text as the sole source of truth.

PRIVACY POLICY EXCERPTS:

{context_text}
"""

    try:

        extraction = structured_llm.invoke(
            prompt
        )

    except Exception as exc:

        print(
            "[Privacy Extraction] "
            f"Gemini request failed: "
            f"{type(exc).__name__}: {exc}"
        )

        # Graceful degradation.
        extraction = PrivacyExtraction()

    chunk_extractions = [
        ChunkExtraction(
            chunk_index=index,
            category="document_analysis",
            extraction=extraction,
            source_text=text,
        )
        for index, text in contexts
    ]

    extracted_results = [
        {
            "chunk_index": result.chunk_index,
            "category": result.category,
            "data_collected": (
                result.extraction.data_collected
            ),
            "data_usage": (
                result.extraction.data_usage
            ),
            "third_party_sharing": (
                result.extraction.third_party_sharing
            ),
            "tracking_methods": (
                result.extraction.tracking_methods
            ),
            "retention_policy": (
                result.extraction.retention_policy
            ),
            "source_text": result.source_text,
        }
        for result in chunk_extractions
    ]

    return {
        "chunk_extractions": chunk_extractions,
        "extracted_results": extracted_results,
    }


# ---------------------------------------------------------------------------
# MERGE
# ---------------------------------------------------------------------------

def merge_node(state: GraphState) -> dict:
    """
    Merge the single document-level extraction into the graph state.
    """

    if not state.chunk_extractions:

        return {
            "structured_data": {
                "data_collected": [],
                "data_usage": [],
                "third_party_sharing": [],
                "tracking_methods": [],
                "retention_policy": "",
            }
        }

    extraction = (
        state.chunk_extractions[0].extraction
    )

    structured_data = {
        "data_collected": sorted(
            set(
                item.strip()
                for item in extraction.data_collected
                if item.strip()
            )
        ),
        "data_usage": sorted(
            set(
                item.strip()
                for item in extraction.data_usage
                if item.strip()
            )
        ),
        "third_party_sharing": sorted(
            set(
                item.strip()
                for item in extraction.third_party_sharing
                if item.strip()
            )
        ),
        "tracking_methods": sorted(
            set(
                item.strip()
                for item in extraction.tracking_methods
                if item.strip()
            )
        ),
        "retention_policy": (
            extraction.retention_policy.strip()
        ),
    }

    return {
        "structured_data": structured_data
    }


# ---------------------------------------------------------------------------
# EVIDENCE
# ---------------------------------------------------------------------------

def _find_matching_chunks(
    state: GraphState,
    category: str,
) -> list[Evidence]:
    """
    Find evidence directly in the original policy chunks.

    Evidence is deterministic and never generated by Gemini.
    """

    keywords = EVIDENCE_KEYWORDS.get(
        category,
        [],
    )

    if not keywords:
        return []

    evidence: list[Evidence] = []

    for index, text in enumerate(
        state.chunks
    ):

        normalized = text.lower()

        if not any(
            keyword.lower() in normalized
            for keyword in keywords
        ):
            continue

        excerpt = _extract_relevant_excerpt(
            text,
            keywords,
        )

        evidence.append(
            Evidence(
                source_type="privacy_policy",
                title=(
                    f"Privacy Policy — "
                    f"Chunk {index + 1}"
                ),
                excerpt=excerpt,
                relevance_score=0.90,
                credibility_score=1.0,
                metadata={
                    "chunk_index": str(index),
                    "category": category,
                    "evidence_method": (
                        "deterministic_source_extraction"
                    ),
                },
            )
        )

    return evidence


# ---------------------------------------------------------------------------
# RISK ANALYSIS
# ---------------------------------------------------------------------------

def risk_node(state: GraphState) -> dict:
    """Convert structured privacy information into explainable findings."""

    structured = (
        state.structured_data
    )

    signals: list[
        RiskSignal
    ] = []

    findings: list[
        Finding
    ] = []

    all_evidence: list[
        Evidence
    ] = []

    recommendations: list[
        str
    ] = []

    # -----------------------------------------------------------------------
    # THIRD-PARTY SHARING
    # -----------------------------------------------------------------------

    if structured.get(
        "third_party_sharing"
    ):

        evidence = (
            _find_matching_chunks(
                state,
                "third_party_sharing",
            )
        )

        signal = RiskSignal(
            name="third_party_sharing",
            category="Data Sharing",
            severity="high",
            penalty=20.0,
            description=(
                "The policy explicitly describes sharing personal "
                "information with third parties."
            ),
            recommendation=(
                "Review which third parties receive data and whether "
                "you can opt out of non-essential sharing."
            ),
        )

        signals.append(
            signal
        )

        findings.append(
            Finding(
                category=signal.category,
                title="Third-party data sharing",
                description=signal.description,
                severity=signal.severity,
                confidence=0.90,
                evidence=evidence,
                recommendation=signal.recommendation,
            )
        )

        all_evidence.extend(
            evidence
        )

        recommendations.append(
            signal.recommendation
        )

    # -----------------------------------------------------------------------
    # LOCATION
    # -----------------------------------------------------------------------

    location_present = any(
        (
            "location" in item.lower()
            or "geolocation" in item.lower()
        )
        for item in structured.get(
            "data_collected",
            [],
        )
    )

    if location_present:

        evidence = (
            _find_matching_chunks(
                state,
                "location",
            )
        )

        signal = RiskSignal(
            name="location_collection",
            category="Sensitive Data",
            severity="high",
            penalty=15.0,
            description=(
                "The policy indicates that location or geolocation "
                "information may be collected."
            ),
            recommendation=(
                "Check whether location collection is necessary and "
                "disable location permissions when they are not required."
            ),
        )

        signals.append(
            signal
        )

        findings.append(
            Finding(
                category=signal.category,
                title="Location data collection",
                description=signal.description,
                severity=signal.severity,
                confidence=0.92,
                evidence=evidence,
                recommendation=signal.recommendation,
            )
        )

        all_evidence.extend(
            evidence
        )

        recommendations.append(
            signal.recommendation
        )

    # -----------------------------------------------------------------------
    # ADVERTISING
    # -----------------------------------------------------------------------

    advertising_present = any(
        any(
            keyword in item.lower()
            for keyword in (
                "advertis",
                "marketing",
                "targeted",
                "personalized ads",
            )
        )
        for item in structured.get(
            "data_usage",
            [],
        )
    )

    if advertising_present:

        evidence = (
            _find_matching_chunks(
                state,
                "advertising",
            )
        )

        signal = RiskSignal(
            name="advertising",
            category="Advertising",
            severity="medium",
            penalty=15.0,
            description=(
                "The policy indicates that collected information may "
                "be used for advertising or targeted marketing."
            ),
            recommendation=(
                "Review advertising and marketing opt-out controls."
            ),
        )

        signals.append(
            signal
        )

        findings.append(
            Finding(
                category=signal.category,
                title="Advertising or targeted marketing",
                description=signal.description,
                severity=signal.severity,
                confidence=0.88,
                evidence=evidence,
                recommendation=signal.recommendation,
            )
        )

        all_evidence.extend(
            evidence
        )

        recommendations.append(
            signal.recommendation
        )

    # -----------------------------------------------------------------------
    # INDEFINITE RETENTION
    # -----------------------------------------------------------------------

    retention = structured.get(
        "retention_policy",
        "",
    ).lower()

    indefinite_retention = any(
        keyword in retention
        for keyword in (
            "indefinite",
            "indefinitely",
            "permanent",
            "forever",
        )
    )

    if indefinite_retention:

        evidence = (
            _find_matching_chunks(
                state,
                "retention",
            )
        )

        signal = RiskSignal(
            name="indefinite_retention",
            category="Data Retention",
            severity="high",
            penalty=25.0,
            description=(
                "The policy contains language indicating that some "
                "information may be retained indefinitely or permanently."
            ),
            recommendation=(
                "Look for deletion controls or request deletion of "
                "stored personal information where applicable."
            ),
        )

        signals.append(
            signal
        )

        findings.append(
            Finding(
                category=signal.category,
                title="Indefinite data retention",
                description=signal.description,
                severity=signal.severity,
                confidence=0.94,
                evidence=evidence,
                recommendation=signal.recommendation,
            )
        )

        all_evidence.extend(
            evidence
        )

        recommendations.append(
            signal.recommendation
        )

    # -----------------------------------------------------------------------
    # TRACKING
    # -----------------------------------------------------------------------

    if structured.get(
        "tracking_methods"
    ):

        evidence = (
            _find_matching_chunks(
                state,
                "tracking",
            )
        )

        signal = RiskSignal(
            name="tracking",
            category="Tracking",
            severity="medium",
            penalty=10.0,
            description=(
                "The policy explicitly describes tracking or "
                "analytics technologies."
            ),
            recommendation=(
                "Review cookie and tracking preferences and disable "
                "non-essential tracking where possible."
            ),
        )

        signals.append(
            signal
        )

        findings.append(
            Finding(
                category=signal.category,
                title="Tracking technologies",
                description=signal.description,
                severity=signal.severity,
                confidence=0.91,
                evidence=evidence,
                recommendation=signal.recommendation,
            )
        )

        all_evidence.extend(
            evidence
        )

        recommendations.append(
            signal.recommendation
        )

    # -----------------------------------------------------------------------
    # DEDUPLICATE EVIDENCE
    # -----------------------------------------------------------------------

    unique_evidence: dict[
        tuple[str, int],
        Evidence,
    ] = {}

    for evidence in all_evidence:

        key = (
            evidence.metadata.get(
                "category",
                "",
            ),
            int(
                evidence.metadata.get(
                    "chunk_index",
                    "-1",
                )
            ),
        )

        unique_evidence[key] = evidence

    risk_signals = [
        {
            "name": signal.name,
            "category": signal.category,
            "severity": signal.severity,
            "penalty": signal.penalty,
            "description": signal.description,
            "recommendation": (
                signal.recommendation
            ),
        }
        for signal in signals
    ]

    return {
        "risks": [
            signal.name
            for signal in signals
        ],
        "risk_signals": risk_signals,
        "findings": findings,
        "evidence": list(
            unique_evidence.values()
        ),
        "recommendations": list(
            dict.fromkeys(
                recommendations
            )
        ),
    }


# ---------------------------------------------------------------------------
# SCORE
# ---------------------------------------------------------------------------

def score_node(state: GraphState) -> dict:
    """Calculate the deterministic privacy risk score."""

    signals = [
        RiskSignal(
            name=item["name"],
            category=item["category"],
            severity=item["severity"],
            penalty=float(
                item["penalty"]
            ),
            description=item["description"],
            recommendation=item[
                "recommendation"
            ],
        )
        for item in state.risk_signals
    ]

    score = risk_engine.calculate_score(
        signals
    )

    verdict = risk_engine.verdict(
        score
    )

    if not state.chunks:

        confidence = 0.0

    elif not state.findings:

        confidence = 0.70

    else:

        confidence = min(
            0.98,
            0.75
            + 0.04 * len(
                state.findings
            ),
        )

    return {
        "score": score,
        "verdict": verdict,
        "confidence": confidence,
    }


# ---------------------------------------------------------------------------
# DETERMINISTIC SUMMARY
# ---------------------------------------------------------------------------

def summary_node(state: GraphState) -> dict:
    """
    Build a concise summary without another LLM request.

    This intentionally avoids consuming Gemini quota for presentation
    text. The summary is derived exclusively from already validated
    findings.
    """

    if not state.chunks:

        summary = (
            "No privacy-policy text was available for analysis."
        )

        report = PrivacyReport(
            verdict="Unknown",
            score=0.0,
            confidence=0.0,
            structured_data=PrivacyExtraction(),
            risks=[],
            findings=[],
            evidence=[],
            recommendations=[
                "Provide a valid privacy policy for analysis."
            ],
            summary=summary,
        )

        return {
            "summary": summary,
            "report": report,
        }

    lines = [
        (
            f"**Verdict:** "
            f"{state.verdict or 'Unknown'}"
        ),
        (
            f"**Score:** "
            f"{state.score or 0:.1f}/100 "
            f"(Confidence: "
            f"{state.confidence:.2f})"
        ),
        "",
        "**Key Findings:**",
    ]

    if not state.findings:

        lines.append(
            "* No major privacy risk signals were detected."
        )

    else:

        for finding in state.findings:

            lines.append(
                (
                    f"* **{finding.title}:** "
                    f"{finding.description}"
                )
            )

    summary = "\n".join(
        lines
    )

    report = PrivacyReport(
        verdict=state.verdict or "Unknown",
        score=state.score or 0.0,
        confidence=state.confidence,
        structured_data=PrivacyExtraction(
            **state.structured_data
        ),
        risks=state.risks,
        findings=state.findings,
        evidence=state.evidence,
        recommendations=state.recommendations,
        summary=summary,
    )

    return {
        "summary": summary,
        "report": report,
    }