"""
Evidence-first Fact Checker report generation.

This module converts the structured fact-checking state into a
human-readable Markdown report.

No LLM call is made here.

The report is deterministic and derived exclusively from:
    - extracted claims
    - retrieved evidence
    - verification results
"""

from agents.fact_check_agent.agent_state import (
    AgentState,
    EvidenceSource,
    VerificationResult,
)


# ============================================================
# HELPERS
# ============================================================

def _percentage(value: float) -> int:
    """Convert a 0-1 confidence/relevance value into a percentage."""

    return round(max(0.0, min(1.0, value)) * 100)


def _source_role(
    source_url: str,
    verification: VerificationResult,
    evidence_index: int,
) -> str:
    """
    Determine whether a retrieved source was marked as supporting,
    conflicting, or neutral by the verification stage.
    """

    if source_url in verification.supporting_sources:
        return "Supporting"

    if source_url in verification.conflicting_sources:
        return "Conflicting"

    # Evidence that was retrieved but not explicitly classified by the
    # verification model remains neutral.
    return "Retrieved"


def _append_evidence(
    lines: list[str],
    sources: list[EvidenceSource],
    verification: VerificationResult,
) -> None:
    """Append structured evidence details to the report."""

    if not sources:
        lines.extend(
            [
                "No web evidence was retrieved for this claim.",
                "",
            ]
        )
        return

    for index, source in enumerate(sources, start=1):
        role = _source_role(
            source.url,
            verification,
            index,
        )

        relevance = (
            _percentage(source.score)
            if source.score is not None
            else None
        )

        credibility = (
            _percentage(source.credibility)
            if source.credibility is not None
            else None
        )

        lines.extend(
            [
                f"#### Evidence {index}: {source.title or 'Untitled source'}",
                "",
                f"**Role:** {role}",
                "",
            ]
        )

        if source.url:
            lines.extend(
                [
                    f"**Source:** {source.url}",
                    "",
                ]
            )

        if relevance is not None:
            lines.extend(
                [
                    f"**Retrieval relevance:** {relevance}%",
                    "",
                ]
            )

        if credibility is not None:
            lines.extend(
                [
                    f"**Source credibility heuristic:** {credibility}%",
                    "",
                ]
            )

        if source.query_used:
            lines.extend(
                [
                    f"**Search query:** {source.query_used}",
                    "",
                ]
            )

        if source.content:
            lines.extend(
                [
                    "**Evidence excerpt:**",
                    "",
                    f"> {source.content}",
                    "",
                ]
            )


# ============================================================
# REPORT GENERATOR
# ============================================================

def generate_report(state: AgentState) -> dict:
    """
    Generate the final deterministic evidence-first report.

    The report contains:
        - aggregate verdict counts
        - claim-level verdicts
        - confidence
        - explanations
        - supporting evidence
        - conflicting evidence
        - retrieved evidence
        - uncertainty information
        - methodology
    """

    print("\n[Agent 4] Generating final report...")

    total_claims = len(state.claims)

    counts = {
        "True": 0,
        "False": 0,
        "Partially True": 0,
        "Unverifiable": 0,
    }

    # --------------------------------------------------------
    # COUNT VERDICTS
    # --------------------------------------------------------

    for verification in state.verifications.values():
        verdict = verification.verdict

        if verdict in counts:
            counts[verdict] += 1

    # --------------------------------------------------------
    # OVERALL STATUS
    # --------------------------------------------------------

    if total_claims == 0:

        overall_status = "No verifiable claims were detected."

    elif counts["False"] > 0:

        overall_status = (
            f"{counts['False']} claim(s) were contradicted "
            "by the retrieved evidence."
        )

    elif counts["Partially True"] > 0:

        overall_status = (
            f"{counts['Partially True']} claim(s) contained "
            "materially mixed or qualified information."
        )

    elif counts["Unverifiable"] == total_claims:

        overall_status = (
            "The available evidence was insufficient to establish "
            "the truth of the analyzed claims."
        )

    else:

        overall_status = (
            "The retrieved evidence supports the analyzed claims."
        )

    # --------------------------------------------------------
    # REPORT HEADER
    # --------------------------------------------------------

    lines = [
        "# NeuroShield Fact Verification Report",
        "",
        "## Verification Summary",
        "",
        f"**Claims analyzed:** {total_claims}",
        "",
        f"**True:** {counts['True']}",
        "",
        f"**False:** {counts['False']}",
        "",
        f"**Partially True:** {counts['Partially True']}",
        "",
        f"**Unverifiable:** {counts['Unverifiable']}",
        "",
        f"**Overall assessment:** {overall_status}",
        "",
        "---",
        "",
    ]

    # --------------------------------------------------------
    # CLAIM DETAILS
    # --------------------------------------------------------

    for claim in state.claims:

        verification = state.verifications.get(
            claim.id
        )

        lines.extend(
            [
                f"## Claim {claim.id}",
                "",
                f"**Claim:** {claim.claim}",
                "",
                f"**Type:** {claim.type}",
                "",
            ]
        )

        if verification is None:

            lines.extend(
                [
                    "**Verdict:** Unverifiable",
                    "",
                    "**Confidence:** 0%",
                    "",
                    (
                        "**Reason:** "
                        "No verification result was available for "
                        "this claim."
                    ),
                    "",
                    "---",
                    "",
                ]
            )

            continue

        confidence_percentage = _percentage(
            verification.confidence
        )

        lines.extend(
            [
                f"**Verdict:** {verification.verdict}",
                "",
                f"**Confidence:** {confidence_percentage}%",
                "",
                f"**Reason:** {verification.reason}",
                "",
            ]
        )

        # ----------------------------------------------------
        # SUPPORTING SOURCES
        # ----------------------------------------------------

        if verification.supporting_sources:

            lines.extend(
                [
                    "### Supporting Evidence",
                    "",
                ]
            )

            supporting_urls = set(
                verification.supporting_sources
            )

            supporting_evidence = [
                source
                for source in state.evidence.get(
                    claim.id,
                    [],
                )
                if source.url in supporting_urls
            ]

            if supporting_evidence:
                _append_evidence(
                    lines,
                    supporting_evidence,
                    verification,
                )
            else:
                for url in verification.supporting_sources:
                    lines.extend(
                        [
                            f"- {url}",
                            "",
                        ]
                    )

        # ----------------------------------------------------
        # CONFLICTING SOURCES
        # ----------------------------------------------------

        if verification.conflicting_sources:

            lines.extend(
                [
                    "### Conflicting Evidence",
                    "",
                ]
            )

            conflicting_urls = set(
                verification.conflicting_sources
            )

            conflicting_evidence = [
                source
                for source in state.evidence.get(
                    claim.id,
                    [],
                )
                if source.url in conflicting_urls
            ]

            if conflicting_evidence:
                _append_evidence(
                    lines,
                    conflicting_evidence,
                    verification,
                )
            else:
                for url in verification.conflicting_sources:
                    lines.extend(
                        [
                            f"- {url}",
                            "",
                        ]
                    )

        # ----------------------------------------------------
        # UNCERTAINTY
        # ----------------------------------------------------

        if verification.uncertainty_reason:

            lines.extend(
                [
                    "### Uncertainty",
                    "",
                    verification.uncertainty_reason,
                    "",
                ]
            )

        # ----------------------------------------------------
        # ALL RETRIEVED EVIDENCE
        # ----------------------------------------------------

        sources = state.evidence.get(
            claim.id,
            [],
        )

        if sources:

            supporting_urls = set(
                verification.supporting_sources
            )

            conflicting_urls = set(
                verification.conflicting_sources
            )

            neutral_sources = [
                source
                for source in sources
                if (
                    source.url not in supporting_urls
                    and source.url not in conflicting_urls
                )
            ]

            if neutral_sources:

                lines.extend(
                    [
                        "### Additional Retrieved Evidence",
                        "",
                    ]
                )

                _append_evidence(
                    lines,
                    neutral_sources,
                    verification,
                )

        else:

            lines.extend(
                [
                    "### Evidence Availability",
                    "",
                    (
                        "No web evidence was retrieved for this claim."
                    ),
                    "",
                ]
            )

        lines.extend(
            [
                "---",
                "",
            ]
        )

    # --------------------------------------------------------
    # FOOTER / METHODOLOGY
    # --------------------------------------------------------

    lines.extend(
        [
            "## Method",
            "",
            (
                "Claims were extracted into atomic, independently "
                "verifiable statements. Web evidence was retrieved "
                "using Tavily and filtered using retrieval relevance "
                "and deterministic source-credibility heuristics."
            ),
            "",
            (
                "Claims were then evaluated against the retrieved "
                "evidence using the verification model. NeuroShield "
                "does not treat the number of sources as proof of truth."
            ),
            "",
            (
                "When evidence is insufficient or verification is "
                "unavailable, the system returns Unverifiable rather "
                "than fabricating a factual verdict."
            ),
        ]
    )

    final_report = "\n".join(lines)

    print("Evidence-first report generated.")

    return {
        "final_report": final_report,
    }