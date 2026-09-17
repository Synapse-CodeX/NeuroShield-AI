from typing import Any

from pydantic import BaseModel, Field

from agents.shared.evidence import Evidence, Finding


class PrivacyExtraction(BaseModel):
    """Structured privacy information extracted from policy text."""

    data_collected: list[str] = Field(
        default_factory=list,
        description=(
            "Types of personal, device, usage, location, or sensitive "
            "information explicitly collected."
        ),
    )

    data_usage: list[str] = Field(
        default_factory=list,
        description=(
            "Explicit purposes for which collected information is used."
        ),
    )

    third_party_sharing: list[str] = Field(
        default_factory=list,
        description=(
            "Third parties, recipient categories, or organizations "
            "with which information is explicitly shared."
        ),
    )

    tracking_methods: list[str] = Field(
        default_factory=list,
        description=(
            "Explicitly mentioned cookies, pixels, SDKs, analytics, "
            "advertising identifiers, or tracking technologies."
        ),
    )

    retention_policy: str = Field(
        default="",
        description=(
            "Explicit statement describing how long personal information "
            "is retained and under what conditions."
        ),
    )


class ChunkExtraction(BaseModel):
    """Extraction result associated with a source policy chunk."""

    chunk_index: int = Field(
        ge=0,
        description="Index of the source policy chunk.",
    )

    category: str = Field(
        default="document_analysis",
        description=(
            "Analysis context associated with this extraction."
        ),
    )

    extraction: PrivacyExtraction = Field(
        default_factory=PrivacyExtraction,
    )

    source_text: str = Field(
        default="",
        description=(
            "Original policy text used as evidence."
        ),
    )


class PrivacyReport(BaseModel):
    """Final explainable privacy-analysis report."""

    verdict: str = "Unknown"

    score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
    )

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    structured_data: PrivacyExtraction = Field(
        default_factory=PrivacyExtraction,
    )

    risks: list[str] = Field(
        default_factory=list,
    )

    findings: list[Finding] = Field(
        default_factory=list,
    )

    evidence: list[Evidence] = Field(
        default_factory=list,
    )

    recommendations: list[str] = Field(
        default_factory=list,
    )

    summary: str = ""


class GraphState(BaseModel):
    """State carried through the privacy LangGraph pipeline."""

    raw_text: str | None = None

    chunks: list[str] = Field(
        default_factory=list,
    )

    vector_store: Any = None

    extracted_results: list[dict[str, Any]] = Field(
        default_factory=list,
    )

    chunk_extractions: list[ChunkExtraction] = Field(
        default_factory=list,
    )

    structured_data: dict[str, Any] = Field(
        default_factory=dict,
    )

    risks: list[str] = Field(
        default_factory=list,
    )

    risk_signals: list[dict[str, Any]] = Field(
        default_factory=list,
    )

    score: float | None = None

    verdict: str | None = None

    confidence: float = 0.0

    evidence: list[Evidence] = Field(
        default_factory=list,
    )

    findings: list[Finding] = Field(
        default_factory=list,
    )

    recommendations: list[str] = Field(
        default_factory=list,
    )

    summary: str | None = None

    report: PrivacyReport | None = None