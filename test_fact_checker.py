from agents.fact_check_agent.agent_state import AgentState
from agents.fact_check_agent.extraction_claim import extract_claims
from agents.fact_check_agent.search_and_verify import (
    collect_evidence,
    verify_evidence,
    generate_final_report,
)


# ============================================================
# TEST INPUT
# ============================================================

state = AgentState(
    input_text=(
        "The Earth revolves around the Sun once every 365.25 days. "
        "The Great Wall of China is visible from space with the naked eye. "
        "Mount Everest is 8,848 meters tall."
    )
)


# ============================================================
# STEP 1 — CLAIM EXTRACTION
# ============================================================

print("\n" + "=" * 70)
print("STEP 1 — CLAIM EXTRACTION")
print("=" * 70)

extraction_result = extract_claims(state)

state = state.model_copy(
    update=extraction_result
)

print(
    f"\nExtracted {len(state.claims)} claims."
)

for claim in state.claims:
    print(
        f"\n[{claim.id}] {claim.claim}"
    )
    print(
        f"    Type: {claim.type}"
    )
    print(
        f"    Search: {claim.normalized_claim}"
    )


# ============================================================
# STEP 2 — TAVILY EVIDENCE RETRIEVAL
# ============================================================

print("\n" + "=" * 70)
print("STEP 2 — TAVILY EVIDENCE RETRIEVAL")
print("=" * 70)

evidence_result = collect_evidence(state)

state = state.model_copy(
    update=evidence_result
)

for claim in state.claims:

    sources = state.evidence.get(
        claim.id,
        []
    )

    print(
        f"\nClaim {claim.id}: "
        f"{len(sources)} sources"
    )

    for index, source in enumerate(
        sources,
        start=1,
    ):
        print(
            f"  [{index}] {source.title}"
        )
        print(
            f"      URL: {source.url}"
        )
        print(
            f"      Relevance: {source.score}"
        )
        print(
            f"      Credibility: {source.credibility}"
        )


# ============================================================
# STEP 3 — BATCH GEMINI VERIFICATION
# ============================================================

print("\n" + "=" * 70)
print("STEP 3 — GEMINI VERIFICATION")
print("=" * 70)

verification_result = verify_evidence(state)

state = state.model_copy(
    update=verification_result
)

for claim in state.claims:

    result = state.verifications.get(
        claim.id
    )

    print(
        f"\nClaim {claim.id}: {claim.claim}"
    )

    if result:
        print(
            f"  Verdict: {result.verdict}"
        )
        print(
            f"  Confidence: "
            f"{result.confidence:.0%}"
        )
        print(
            f"  Reason: {result.reason}"
        )

        if result.supporting_sources:
            print(
                "  Supporting sources:"
            )

            for url in result.supporting_sources:
                print(
                    f"    - {url}"
                )

        if result.conflicting_sources:
            print(
                "  Conflicting sources:"
            )

            for url in result.conflicting_sources:
                print(
                    f"    - {url}"
                )


# ============================================================
# STEP 4 — FINAL REPORT
# ============================================================

print("\n" + "=" * 70)
print("STEP 4 — FINAL REPORT")
print("=" * 70)

report_result = generate_final_report(state)

print(
    "\n" + report_result["final_report"]
)

print("\n" + "=" * 70)
print("FACT CHECKER TEST COMPLETE")
print("=" * 70)