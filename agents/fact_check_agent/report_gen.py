"""
Fact Checker report generation.

This module converts the structured fact-checking state into a
human-readable report.

No LLM call is made here.
"""

from agents.fact_check_agent.agent_state import AgentState


# ============================================================
# REPORT GENERATOR
# ============================================================

def generate_report(state: AgentState) -> dict:
    """
    Generate the final deterministic fact-checking report.

    The report is derived exclusively from the claims, evidence,
    and verification results already present in the graph state.
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

        overall_status = "No claims detected."

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
            "The available evidence was insufficient to "
            "verify the claims."
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
        "## Summary",
        "",
        f"**Claims analyzed:** {total_claims}",
        "",
        f"**True:** {counts['True']}",
        f"**False:** {counts['False']}",
        f"**Partially True:** {counts['Partially True']}",
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

        if verification is None:

            lines.extend(
                [
                    f"## Claim {claim.id}",
                    "",
                    f"**Claim:** {claim.claim}",
                    "",
                    "**Verdict:** Unverifiable",
                    "",
                    "**Confidence:** 0%",
                    "",
                    (
                        "**Reason:** "
                        "No verification result was available."
                    ),
                    "",
                    "---",
                    "",
                ]
            )

            continue

        confidence_percentage = round(
            verification.confidence * 100
        )

        lines.extend(
            [
                f"## Claim {claim.id}",
                "",
                f"**Claim:** {claim.claim}",
                "",
                f"**Type:** {claim.type}",
                "",
                f"**Verdict:** {verification.verdict}",
                "",
                (
                    f"**Confidence:** "
                    f"{confidence_percentage}%"
                ),
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
                    "### Supporting Sources",
                    "",
                ]
            )

            for url in (
                verification.supporting_sources
            ):

                lines.append(
                    f"- {url}"
                )

            lines.append("")

        # ----------------------------------------------------
        # CONFLICTING SOURCES
        # ----------------------------------------------------

        if verification.conflicting_sources:

            lines.extend(
                [
                    "### Conflicting Sources",
                    "",
                ]
            )

            for url in (
                verification.conflicting_sources
            ):

                lines.append(
                    f"- {url}"
                )

            lines.append("")

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
        # RETRIEVED EVIDENCE
        # ----------------------------------------------------

        sources = state.evidence.get(
            claim.id,
            []
        )

        if sources:

            lines.extend(
                [
                    "### Retrieved Evidence",
                    "",
                ]
            )

            for index, source in enumerate(
                sources,
                start=1,
            ):

                lines.extend(
                    [
                        (
                            f"**Evidence {index}: "
                            f"{source.title}**"
                        ),
                        "",
                        (
                            f"{source.content}"
                        ),
                        "",
                        f"Source: {source.url}",
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
    # FOOTER
    # --------------------------------------------------------

    lines.extend(
        [
            "## Method",
            "",
            (
                "Claims were extracted into atomic, independently "
                "verifiable statements. Web evidence was then "
                "retrieved using Tavily and the claims were "
                "verified against the retrieved evidence."
            ),
            "",
            (
                "Verification results are evidence-grounded and "
                "may remain Unverifiable when the retrieved "
                "sources do not provide sufficient information."
            ),
        ]
    )

    final_report = "\n".join(lines)

    print("Report generated.")

    return {
        "final_report": final_report
    }