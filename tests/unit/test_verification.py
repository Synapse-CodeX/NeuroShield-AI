from unittest.mock import patch

from agents.fact_check_agent.agent_state import (
    AgentState,
    Claim,
    EvidenceSource,
)
from agents.fact_check_agent.search_and_verify import (
    _build_unavailable_verifications,
    _is_rate_limit_error,
    verify_evidence,
)


def make_claim(
    claim_id: int = 1,
    text: str = "The Earth revolves around the Sun.",
) -> Claim:
    return Claim(
        id=claim_id,
        claim=text,
        type="factual",
        normalized_claim=text,
    )


def make_state(
    claims: list[Claim],
    evidence: dict[int, list[EvidenceSource]] | None = None,
) -> AgentState:
    return AgentState(
        input_text="Test input",
        claims=claims,
        evidence=evidence or {},
    )


def test_rate_limit_error_detection():
    assert _is_rate_limit_error(
        Exception("429 RESOURCE_EXHAUSTED")
    )

    assert _is_rate_limit_error(
        Exception("Quota exceeded for metric")
    )

    assert _is_rate_limit_error(
        Exception("Rate limit exceeded")
    )


def test_non_rate_limit_error_detection():
    assert not _is_rate_limit_error(
        Exception("Connection timeout")
    )

    assert not _is_rate_limit_error(
        Exception("Invalid request")
    )


def test_unavailable_verification_result():
    claims = [
        make_claim(1),
        make_claim(
            2,
            "Water boils at 100 degrees Celsius at sea level.",
        ),
    ]

    results = _build_unavailable_verifications(
        claims,
        "Gemini quota exhausted.",
    )

    assert len(results) == 2

    assert results[1].verdict == "Unverifiable"
    assert results[1].confidence == 0.0
    assert results[1].supporting_sources == []
    assert results[1].conflicting_sources == []
    assert (
        results[1].uncertainty_reason
        == "Gemini quota exhausted."
    )


def test_unavailable_verification_does_not_create_factual_verdict():
    claims = [make_claim()]

    results = _build_unavailable_verifications(
        claims,
        "Verification service unavailable.",
    )

    assert results[1].verdict not in {
        "True",
        "False",
        "Partially True",
    }

    assert results[1].verdict == "Unverifiable"


def test_verify_empty_claims():
    state = make_state([])

    result = verify_evidence(state)

    assert result == {
        "verifications": {}
    }


def test_verify_handles_gemini_rate_limit():
    claim = make_claim()

    state = make_state(
        [claim],
        {
            1: [
                EvidenceSource(
                    title="Example Source",
                    content="Example evidence.",
                    url="https://example.com",
                    score=0.9,
                    query_used=claim.claim,
                    credibility=0.6,
                )
            ]
        },
    )

    with patch(
        "agents.fact_check_agent.search_and_verify.llm"
    ) as mocked_llm:
        mocked_llm.with_structured_output.side_effect = (
            Exception(
                "429 RESOURCE_EXHAUSTED: quota exceeded"
            )
        )

        result = verify_evidence(state)

    verification = result["verifications"][1]

    assert verification.verdict == "Unverifiable"
    assert verification.confidence == 0.0

    assert (
        "quota"
        in verification.uncertainty_reason.lower()
    )

    assert verification.supporting_sources == []
    assert verification.conflicting_sources == []


def test_verify_handles_generic_model_error():
    claim = make_claim()

    state = make_state([claim])

    with patch(
        "agents.fact_check_agent.search_and_verify.llm"
    ) as mocked_llm:
        mocked_llm.with_structured_output.side_effect = (
            Exception("Temporary model failure")
        )

        result = verify_evidence(state)

    verification = result["verifications"][1]

    assert verification.verdict == "Unverifiable"
    assert verification.confidence == 0.0

    assert (
        "verification service"
        in verification.uncertainty_reason.lower()
    )


def test_verify_guarantees_result_for_missing_model_output():
    claim_one = make_claim(
        1,
        "The Earth revolves around the Sun.",
    )

    claim_two = make_claim(
        2,
        "India became independent in 1947.",
    )

    state = make_state(
        [claim_one, claim_two]
    )

    class FakeResponse:
        results = []

    with patch(
        "agents.fact_check_agent.search_and_verify.llm"
    ) as mocked_llm:
        mocked_structured_llm = mocked_llm.with_structured_output.return_value
        mocked_structured_llm.invoke.return_value = FakeResponse()

        result = verify_evidence(state)

    verifications = result["verifications"]

    assert len(verifications) == 2
    assert verifications[1].verdict == "Unverifiable"
    assert verifications[2].verdict == "Unverifiable"


def test_verify_does_not_expose_raw_exception():
    claim = make_claim()

    state = make_state([claim])

    raw_error = (
        "Internal API secret: abc123 "
        "RESOURCE_EXHAUSTED"
    )

    with patch(
        "agents.fact_check_agent.search_and_verify.llm"
    ) as mocked_llm:
        mocked_llm.with_structured_output.side_effect = (
            Exception(raw_error)
        )

        result = verify_evidence(state)

    verification = result["verifications"][1]

    # The user-facing explanation should not simply dump the raw
    # provider exception.
    assert verification.uncertainty_reason != raw_error

    assert (
        "quota"
        in verification.uncertainty_reason.lower()
    )