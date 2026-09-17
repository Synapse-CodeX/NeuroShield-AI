"""
NeuroShield Fact Checker LangGraph.

Pipeline:

    User Input
        ↓
    Claim Extraction
        ↓
    Evidence Retrieval
        ↓
    Batch Verification
        ↓
    Final Report
"""

from langgraph.graph import END, StateGraph

from agents.fact_check_agent.agent_state import AgentState
from agents.fact_check_agent.extraction_claim import extract_claims
from agents.fact_check_agent.search_and_verify import (
    collect_evidence,
    verify_evidence,
)
from agents.fact_check_agent.report_gen import generate_report


# ============================================================
# GRAPH NODES
# ============================================================

def build_fact_checker_graph():
    """
    Build and compile the NeuroShield fact-checking graph.

    The graph deliberately contains small, explicit stages so that
    each stage can be tested and replaced independently.
    """

    builder = StateGraph(AgentState)

    # --------------------------------------------------------
    # 1. Claim extraction
    # --------------------------------------------------------

    builder.add_node(
        "extract_claims",
        extract_claims,
    )

    # --------------------------------------------------------
    # 2. Web evidence retrieval
    # --------------------------------------------------------

    builder.add_node(
        "collect_evidence",
        collect_evidence,
    )

    # --------------------------------------------------------
    # 3. Evidence-based verification
    # --------------------------------------------------------

    builder.add_node(
        "verify_evidence",
        verify_evidence,
    )

    # --------------------------------------------------------
    # 4. Deterministic report generation
    # --------------------------------------------------------

    builder.add_node(
        "generate_report",
        generate_report,
    )

    # --------------------------------------------------------
    # GRAPH FLOW
    # --------------------------------------------------------

    builder.set_entry_point(
        "extract_claims"
    )

    builder.add_edge(
        "extract_claims",
        "collect_evidence",
    )

    builder.add_edge(
        "collect_evidence",
        "verify_evidence",
    )

    builder.add_edge(
        "verify_evidence",
        "generate_report",
    )

    builder.add_edge(
        "generate_report",
        END,
    )

    return builder.compile()


# ============================================================
# COMPILED GRAPH
# ============================================================

fact_checker_graph = build_fact_checker_graph()


# ============================================================
# COMPATIBILITY ALIAS
# ============================================================

# Existing backend code may refer to `graph`.
# Keep this alias so the integration remains simple.

graph = fact_checker_graph


# ============================================================
# LOCAL DEBUG TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("NEUROSHIELD FACT CHECKER")
    print("=" * 70)

    initial_state = AgentState(
        input_text=(
            "The Earth is the third planet from the Sun and "
            "completes one rotation every 24 hours. "
            "It takes exactly 365 days to orbit the Sun. "
            "Water covers about 71% of Earth's surface. "
            "The Great Wall of China is visible from space "
            "with the naked eye. "
            "Humans can survive without oxygen for several "
            "hours without harm. "
            "Mount Everest is the tallest mountain above sea "
            "level, standing at 8,848 meters. "
            "The Moon has stronger gravity than Earth. "
            "Lightning never strikes the same place twice. "
            "Plants produce oxygen through photosynthesis."
        )
    )

    try:

        result = fact_checker_graph.invoke(
            initial_state
        )

        print(
            "\n✅ Fact Checker execution completed."
        )

        # ----------------------------------------------------
        # CLAIMS
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print("CLAIMS")
        print("-" * 70)

        for claim in result["claims"]:

            print(
                f"\n[{claim.id}] {claim.claim}"
            )

            print(
                f"    Type: {claim.type}"
            )

            print(
                f"    Search query: "
                f"{claim.normalized_claim}"
            )

        # ----------------------------------------------------
        # EVIDENCE
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print("EVIDENCE")
        print("-" * 70)

        for claim_id, sources in (
            result["evidence"].items()
        ):

            print(
                f"\nClaim {claim_id}: "
                f"{len(sources)} sources"
            )

            for source in sources:

                print(
                    f"  • {source.title}"
                )

                print(
                    f"    URL: {source.url}"
                )

                print(
                    f"    Relevance: "
                    f"{source.score}"
                )

                print(
                    f"    Credibility: "
                    f"{source.credibility}"
                )

        # ----------------------------------------------------
        # VERIFICATIONS
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print("VERIFICATIONS")
        print("-" * 70)

        for claim_id, verification in (
            result["verifications"].items()
        ):

            print(
                f"\nClaim {claim_id}"
            )

            print(
                f"  Verdict: "
                f"{verification.verdict}"
            )

            print(
                f"  Confidence: "
                f"{verification.confidence:.0%}"
            )

            print(
                f"  Reason: "
                f"{verification.reason}"
            )

            if verification.supporting_sources:

                print(
                    "  Supporting sources:"
                )

                for url in (
                    verification.supporting_sources
                ):
                    print(
                        f"    - {url}"
                    )

            if verification.conflicting_sources:

                print(
                    "  Conflicting sources:"
                )

                for url in (
                    verification.conflicting_sources
                ):
                    print(
                        f"    - {url}"
                    )

        # ----------------------------------------------------
        # FINAL REPORT
        # ----------------------------------------------------

        print("\n" + "=" * 70)
        print("FINAL REPORT")
        print("=" * 70)

        print(
            result["final_report"]
        )

        print(
            "\n" + "=" * 70
        )
        print(
            "FACT CHECKER COMPLETE"
        )
        print(
            "=" * 70
        )

    except Exception as exc:

        print(
            "\n❌ FACT CHECKER ERROR"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )