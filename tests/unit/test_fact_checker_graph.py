from unittest.mock import patch

from agents.fact_check_agent.agent_state import (
    EvidenceSource,
    VerificationResult,
)
from agents.fact_check_agent.main import build_fact_checker_graph


def test_fact_checker_graph_runs_end_to_end():
    """Verify the complete fact-checking graph pipeline."""

    mock_claims = [
        {
            "id": 1,
            "claim": "The Earth revolves around the Sun.",
            "type": "factual",
            "normalized_claim": "The Earth revolves around the Sun.",
        },
        {
            "id": 2,
            "claim": "India became independent in 1947.",
            "type": "temporal",
            "normalized_claim": "India became independent in 1947.",
        },
    ]

    mock_evidence = [
        {
            "title": "NASA",
            "content": "Earth orbits the Sun.",
            "url": "https://www.nasa.gov/example",
            "score": 0.95,
            "credibility": 1.0,
        }
    ]

    mock_verifications = {
        1: VerificationResult(
            verdict="True",
            confidence=0.96,
            reason="The retrieved evidence supports the claim.",
            supporting_sources=[
                "https://www.nasa.gov/example"
            ],
            conflicting_sources=[],
            uncertainty_reason=None,
        ),
        2: VerificationResult(
            verdict="True",
            confidence=0.94,
            reason="The retrieved evidence supports the claim.",
            supporting_sources=[
                "https://www.nasa.gov/example"
            ],
            conflicting_sources=[],
            uncertainty_reason=None,
        ),
    }

    with (
        patch(
            "agents.fact_check_agent.main.extract_claims",
            return_value={"claims": mock_claims},
        ),
        patch(
            "agents.fact_check_agent.main.collect_evidence",
            return_value={
                "evidence": {
                    1: [
                        EvidenceSource(
                            title=mock_evidence[0]["title"],
                            content=mock_evidence[0]["content"],
                            url=mock_evidence[0]["url"],
                            score=mock_evidence[0]["score"],
                            query_used=(
                                "The Earth revolves around the Sun."
                            ),
                            credibility=mock_evidence[0][
                                "credibility"
                            ],
                        )
                    ],
                    2: [
                        EvidenceSource(
                            title=mock_evidence[0]["title"],
                            content=(
                                "India became independent in 1947."
                            ),
                            url=mock_evidence[0]["url"],
                            score=mock_evidence[0]["score"],
                            query_used=(
                                "India became independent in 1947."
                            ),
                            credibility=mock_evidence[0][
                                "credibility"
                            ],
                        )
                    ],
                }
            },
        ),
        patch(
            "agents.fact_check_agent.main.verify_evidence",
            return_value={
                "verifications": mock_verifications,
            },
        ),
    ):
        graph = build_fact_checker_graph()

        result = graph.invoke(
            {
                "input_text": (
                    "The Earth revolves around the Sun. "
                    "India became independent in 1947."
                )
            }
        )

    assert len(result["claims"]) == 2

    assert 1 in result["evidence"]
    assert 2 in result["evidence"]

    assert 1 in result["verifications"]
    assert 2 in result["verifications"]

    assert (
        result["verifications"][1].verdict
        == "True"
    )

    assert (
        result["verifications"][2].verdict
        == "True"
    )

    assert result["final_report"]

    assert "NeuroShield Fact Verification Report" in (
        result["final_report"]
    )


def test_fact_checker_graph_preserves_unverifiable_result():
    """
    Verify that an unavailable verification stage propagates
    Unverifiable rather than inventing a factual verdict.
    """

    mock_claims = [
        {
            "id": 1,
            "claim": "Some unknown claim.",
            "type": "factual",
            "normalized_claim": "Some unknown claim.",
        }
    ]

    unavailable_result = VerificationResult(
        verdict="Unverifiable",
        confidence=0.0,
        reason=(
            "The verification service was unavailable."
        ),
        supporting_sources=[],
        conflicting_sources=[],
        uncertainty_reason=(
            "Verification could not be completed."
        ),
    )

    with (
        patch(
            "agents.fact_check_agent.main.extract_claims",
            return_value={"claims": mock_claims},
        ),
        patch(
            "agents.fact_check_agent.main.collect_evidence",
            return_value={
                "evidence": {
                    1: []
                }
            },
        ),
        patch(
            "agents.fact_check_agent.main.verify_evidence",
            return_value={
                "verifications": {
                    1: unavailable_result
                }
            },
        ),
    ):
        graph = build_fact_checker_graph()

        result = graph.invoke(
            {
                "input_text": "Some unknown claim."
            }
        )

    verification = result["verifications"][1]

    assert isinstance(
        verification,
        VerificationResult,
    )

    assert verification.verdict == "Unverifiable"
    assert verification.confidence == 0.0

    assert "Unverifiable" in result["final_report"]
    assert "Verification could not be completed." in (
        result["final_report"]
    )


def test_fact_checker_graph_handles_empty_claims():
    """Verify the graph produces a valid report with no claims."""

    with (
        patch(
            "agents.fact_check_agent.main.extract_claims",
            return_value={"claims": []},
        ),
        patch(
            "agents.fact_check_agent.main.collect_evidence",
            return_value={
                "evidence": {}
            },
        ),
        patch(
            "agents.fact_check_agent.main.verify_evidence",
            return_value={
                "verifications": {}
            },
        ),
    ):
        graph = build_fact_checker_graph()

        result = graph.invoke(
            {
                "input_text": "Hello, how are you?"
            }
        )

    assert result["claims"] == []
    assert result["evidence"] == {}
    assert result["verifications"] == {}

    assert result["final_report"]

    assert (
        "No verifiable claims were detected."
        in result["final_report"]
    )