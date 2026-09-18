from agents.fact_check_agent.extraction_claim import (
    _classify_claim,
    _extract_with_fallback,
    _looks_like_claim,
    _normalize_claims,
    _split_sentences,
)
from agents.fact_check_agent.agent_state import Claim


def test_split_sentences():
    text = (
        "The Earth revolves around the Sun. "
        "India became independent in 1947. "
        "Water boils at 100°C."
    )

    sentences = _split_sentences(text)

    assert len(sentences) == 3
    assert sentences[0] == "The Earth revolves around the Sun."
    assert sentences[1] == "India became independent in 1947."
    assert sentences[2] == "Water boils at 100°C."


def test_split_sentences_handles_abbreviations():
    text = "Dr. Smith published a study. It was widely cited."

    sentences = _split_sentences(text)

    assert len(sentences) == 2
    assert sentences[0] == "Dr. Smith published a study."
    assert sentences[1] == "It was widely cited."


def test_looks_like_claim_accepts_factual_statement():
    assert _looks_like_claim(
        "The Earth revolves around the Sun."
    )


def test_looks_like_claim_rejects_question():
    assert not _looks_like_claim(
        "Is the Earth larger than the Moon?"
    )


def test_looks_like_claim_rejects_instruction():
    assert not _looks_like_claim(
        "Please visit the website."
    )


def test_classify_numerical_claim():
    assert (
        _classify_claim(
            "The Earth revolves around the Sun once every 365.25 days."
        )
        == "numerical"
    )


def test_classify_temporal_claim():
    assert (
        _classify_claim(
            "India became independent in 1947."
        )
        == "temporal"
    )


def test_classify_entity_claim():
    assert (
        _classify_claim(
            "The Eiffel Tower is located in Paris."
        )
        == "entity"
    )


def test_classify_factual_claim():
    assert (
        _classify_claim(
            "Water is composed of hydrogen and oxygen."
        )
        == "factual"
    )


def test_fallback_extracts_multiple_claims():
    text = (
        "The Earth revolves around the Sun once every 365.25 days. "
        "India became independent in 1947. "
        "Water boils at 100°C at sea level."
    )

    claims = _extract_with_fallback(text)

    assert len(claims) == 3

    assert claims[0].id == 1
    assert claims[1].id == 2
    assert claims[2].id == 3


def test_fallback_assigns_unique_ids():
    text = (
        "The Earth revolves around the Sun. "
        "India became independent in 1947."
    )

    claims = _extract_with_fallback(text)

    assert [claim.id for claim in claims] == [1, 2]


def test_fallback_deduplicates_identical_claims():
    text = (
        "The Earth revolves around the Sun. "
        "The Earth revolves around the Sun."
    )

    claims = _extract_with_fallback(text)

    assert len(claims) == 1
    assert claims[0].id == 1


def test_fallback_preserves_claim_text():
    text = "India became independent in 1947."

    claims = _extract_with_fallback(text)

    assert claims[0].claim == text
    assert claims[0].normalized_claim == text


def test_empty_text_returns_no_claims():
    assert _extract_with_fallback("") == []


def test_whitespace_only_text_returns_no_claims():
    assert _extract_with_fallback("   ") == []


def test_normalize_claims_removes_duplicates_and_reindexes():
    claims = [
        Claim(
            id=7,
            claim="The Earth revolves around the Sun.",
            type="factual",
            normalized_claim="Earth revolves around Sun",
        ),
        Claim(
            id=99,
            claim="The Earth revolves around the Sun.",
            type="factual",
            normalized_claim="Earth revolves around Sun",
        ),
        Claim(
            id=42,
            claim="India became independent in 1947.",
            type="temporal",
            normalized_claim="India independence 1947",
        ),
    ]

    normalized = _normalize_claims(claims)

    assert len(normalized) == 2
    assert [claim.id for claim in normalized] == [1, 2]
    assert normalized[0].claim == "The Earth revolves around the Sun."
    assert normalized[1].claim == "India became independent in 1947."