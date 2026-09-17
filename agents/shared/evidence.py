from typing import Literal

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Evidence supporting an AI-generated finding."""

    source_type: Literal[
        "privacy_policy",
        "web",
        "website",
        "ssl",
        "url",
        "domain",
        "search",
    ]

    title: str = ""
    url: str = ""

    excerpt: str = Field(
        default="",
        description="Short evidence excerpt supporting the finding.",
    )

    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    credibility_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )


class Finding(BaseModel):
    """A user-facing security or privacy finding."""

    category: str
    title: str
    description: str

    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
        "info",
    ]

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    evidence: list[Evidence] = Field(
        default_factory=list,
    )

    recommendation: str = ""


class AnalysisReport(BaseModel):
    """Unified analysis result shared across NeuroShield."""

    verdict: str
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

    findings: list[Finding] = Field(
        default_factory=list,
    )

    recommendations: list[str] = Field(
        default_factory=list,
    )

    evidence: list[Evidence] = Field(
        default_factory=list,
    )

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )