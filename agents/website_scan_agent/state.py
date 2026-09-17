from typing import Any, List, Optional
from pydantic import BaseModel, Field


class WebsiteScanState(BaseModel):
    """State that flows through the website scan LangGraph pipeline."""

    # ── Input ──
    url: str = ""

    # ── Intermediate analysis results (per-node) ──
    url_analysis: dict[str, Any] = Field(default_factory=dict)
    domain_age_analysis: dict[str, Any] = Field(default_factory=dict)
    ssl_analysis: dict[str, Any] = Field(default_factory=dict)
    content_analysis: dict[str, Any] = Field(default_factory=dict)
    reputation_analysis: dict[str, Any] = Field(default_factory=dict)
    scam_report_analysis: dict[str, Any] = Field(default_factory=dict)

    # ── Aggregated outputs ──
    scores: dict[str, int] = Field(default_factory=dict)
    overall_score: int = 0
    verdict: str = ""
    recommendations: List[str] = Field(default_factory=list)
    summary: str = ""


# ── Structured output models for LLM-backed nodes ──

class ContentQualityExtraction(BaseModel):
    """Structured extraction from fetched page content."""

    has_meaningful_content: bool = Field(
        default=False,
        description="Whether the page has real, substantive content (not just filler/lorem ipsum)"
    )
    language_quality: str = Field(
        default="unknown",
        description="Quality of the language: 'good', 'poor', 'suspicious', or 'unknown'"
    )
    has_contact_info: bool = Field(
        default=False,
        description="Whether the page provides legitimate contact information"
    )
    has_legal_pages: bool = Field(
        default=False,
        description="Whether the site references privacy policy, terms, etc."
    )
    red_flags: List[str] = Field(
        default_factory=list,
        description="List of suspicious content indicators (e.g., urgency tactics, fake testimonials)"
    )
    legitimacy_indicators: List[str] = Field(
        default_factory=list,
        description="List of positive trust signals found in the content"
    )


class ReputationExtraction(BaseModel):
    """Structured extraction from LLM reputation knowledge."""

    is_known_brand: bool = Field(
        default=False,
        description="Whether the domain belongs to a well-known, legitimate brand"
    )
    known_scam: bool = Field(
        default=False,
        description="Whether the domain is associated with known scams"
    )
    category: str = Field(
        default="unknown",
        description="Category of the website: 'legitimate', 'suspicious', 'malicious', or 'unknown'"
    )
    notes: List[str] = Field(
        default_factory=list,
        description="Any notable observations about the domain's reputation"
    )
