from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ============================================================
# CLAIM
# ============================================================

class Claim(BaseModel):
    """A single atomic, independently verifiable claim."""

    id: int = Field(
        ...,
        ge=1,
        description="Unique sequential identifier for the claim.",
    )

    claim: str = Field(
        ...,
        min_length=1,
        description="Atomic factual claim.",
    )

    type: Literal[
        "factual",
        "numerical",
        "entity",
        "temporal",
    ] = Field(
        ...,
        description="Category of the claim.",
    )

    normalized_claim: Optional[str] = Field(
        default=None,
        description=(
            "Cleaned version of the claim optimized for web search."
        ),
    )


# ============================================================
# CLAIM EXTRACTION OUTPUT
# ============================================================

class ClaimExtractionOutput(BaseModel):
    """Structured output produced by the claim extraction stage."""

    claims: List[Claim] = Field(
        default_factory=list,
        description="Atomic claims extracted from the input.",
    )


# ============================================================
# EVIDENCE SOURCE
# ============================================================

class EvidenceSource(BaseModel):
    """A web source retrieved as evidence for a claim."""

    title: str = Field(
        default="",
        description="Title of the evidence source.",
    )

    content: str = Field(
        default="",
        description="Relevant content retrieved from the source.",
    )

    url: str = Field(
        default="",
        description="URL of the evidence source.",
    )

    score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Tavily relevance score.",
    )

    query_used: Optional[str] = Field(
        default=None,
        description="Search query used to retrieve this source.",
    )

    credibility: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Estimated source credibility score.",
    )


# ============================================================
# VERIFICATION RESULT
# ============================================================

class VerificationResult(BaseModel):
    """Structured verification result for one claim."""

    verdict: Literal[
        "True",
        "False",
        "Partially True",
        "Unverifiable",
    ] = Field(
        ...,
        description="Verification verdict.",
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the verification result.",
    )

    reason: str = Field(
        ...,
        description="Evidence-based explanation of the verdict.",
    )

    supporting_sources: List[str] = Field(
        default_factory=list,
        description="URLs supporting the claim.",
    )

    conflicting_sources: List[str] = Field(
        default_factory=list,
        description="URLs contradicting the claim.",
    )

    uncertainty_reason: Optional[str] = Field(
        default=None,
        description="Explanation of remaining uncertainty.",
    )


# ============================================================
# MAIN AGENT STATE
# ============================================================

class AgentState(BaseModel):
    """State flowing through the fact-checking LangGraph."""

    input_text: str = Field(
        ...,
        description="Original user-provided text.",
    )

    claims: List[Claim] = Field(
        default_factory=list,
        description="Atomic claims extracted from the input.",
    )

    evidence: Dict[int, List[EvidenceSource]] = Field(
        default_factory=dict,
        description=(
            "Mapping from claim ID to retrieved evidence sources."
        ),
    )

    verifications: Dict[int, VerificationResult] = Field(
        default_factory=dict,
        description=(
            "Mapping from claim ID to verification result."
        ),
    )

    final_report: str = Field(
        default="",
        description=(
            "Final human-readable fact-checking report."
        ),
    )