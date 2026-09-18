from unittest.mock import patch

from agents.fact_check_agent.agent_state import (
    AgentState,
    Claim,
    EvidenceSource,
)
from agents.fact_check_agent.search_and_verify import (
    get_credibility,
    is_bad,
    search,
    collect_evidence,
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


def test_is_bad_rejects_known_social_domains():
    assert is_bad("https://reddit.com/r/test")
    assert is_bad("https://www.reddit.com/r/test")
    assert is_bad("https://quora.com/question/example")
    assert is_bad("https://www.facebook.com/example")


def test_is_bad_accepts_normal_domain():
    assert not is_bad("https://www.nasa.gov/example")


def test_is_bad_handles_subdomains():
    assert is_bad("https://subdomain.reddit.com/example")


def test_credibility_known_high_quality_domain():
    assert get_credibility("https://www.reuters.com/article") == 1.0
    assert get_credibility("https://www.nasa.gov/news") == 1.0
    assert get_credibility("https://www.who.int/news") == 1.0


def test_credibility_edu_domain():
    assert get_credibility("https://example.edu/research") == 0.90


def test_credibility_gov_domain():
    assert get_credibility("https://example.gov/report") == 0.95


def test_credibility_https_generic_domain():
    assert get_credibility("https://example.com/article") == 0.60


def test_credibility_http_generic_domain():
    assert get_credibility("http://example.com/article") == 0.40


def test_credibility_invalid_url():
    assert get_credibility("") == 0.0


def test_search_filters_bad_domains():
    tavily_response = {
        "results": [
            {
                "title": "Bad Social Source",
                "content": "This should be removed.",
                "url": "https://reddit.com/example",
                "score": 0.99,
            },
            {
                "title": "Good Source",
                "content": "Useful factual evidence.",
                "url": "https://example.com/article",
                "score": 0.80,
            },
        ]
    }

    with patch(
        "agents.fact_check_agent.search_and_verify.search_client.search",
        return_value=tavily_response,
    ):
        results = search("test query")

    assert len(results) == 1
    assert results[0]["title"] == "Good Source"
    assert results[0]["url"] == "https://example.com/article"


def test_search_removes_results_without_url():
    tavily_response = {
        "results": [
            {
                "title": "Missing URL",
                "content": "Some content.",
                "url": "",
                "score": 0.90,
            },
            {
                "title": "Valid Source",
                "content": "Useful evidence.",
                "url": "https://example.com",
                "score": 0.80,
            },
        ]
    }

    with patch(
        "agents.fact_check_agent.search_and_verify.search_client.search",
        return_value=tavily_response,
    ):
        results = search("test query")

    assert len(results) == 1
    assert results[0]["title"] == "Valid Source"


def test_search_removes_results_without_content():
    tavily_response = {
        "results": [
            {
                "title": "Empty Source",
                "content": "",
                "url": "https://example.com",
                "score": 0.90,
            },
            {
                "title": "Valid Source",
                "content": "Useful evidence.",
                "url": "https://example.org",
                "score": 0.80,
            },
        ]
    }

    with patch(
        "agents.fact_check_agent.search_and_verify.search_client.search",
        return_value=tavily_response,
    ):
        results = search("test query")

    assert len(results) == 1
    assert results[0]["title"] == "Valid Source"


def test_search_limits_evidence_per_claim():
    tavily_response = {
        "results": [
            {
                "title": f"Source {index}",
                "content": f"Evidence {index}",
                "url": f"https://example{index}.com",
                "score": 0.90 - (index * 0.01),
            }
            for index in range(10)
        ]
    }

    with patch(
        "agents.fact_check_agent.search_and_verify.search_client.search",
        return_value=tavily_response,
    ):
        results = search("test query")

    assert len(results) == 3


def test_search_truncates_long_content():
    long_content = "A" * 5000

    tavily_response = {
        "results": [
            {
                "title": "Long Source",
                "content": long_content,
                "url": "https://example.com",
                "score": 0.90,
            }
        ]
    }

    with patch(
        "agents.fact_check_agent.search_and_verify.search_client.search",
        return_value=tavily_response,
    ):
        results = search("test query")

    assert len(results) == 1
    assert len(results[0]["content"]) == 700


def test_search_returns_empty_list_on_tavily_failure():
    with patch(
        "agents.fact_check_agent.search_and_verify.search_client.search",
        side_effect=Exception("Tavily unavailable"),
    ):
        results = search("test query")

    assert results == []


def test_search_combines_relevance_and_credibility():
    tavily_response = {
        "results": [
            {
                "title": "Generic Highly Relevant",
                "content": "Evidence.",
                "url": "https://example.com",
                "score": 0.95,
            },
            {
                "title": "Trusted Source",
                "content": "Evidence.",
                "url": "https://www.nasa.gov",
                "score": 0.80,
            },
        ]
    }

    with patch(
        "agents.fact_check_agent.search_and_verify.search_client.search",
        return_value=tavily_response,
    ):
        results = search("test query")

    assert len(results) == 2

    assert (
        results[0]["credibility"]
        >= results[1]["credibility"]
        or results[0]["score"]
        >= results[1]["score"]
    )


def test_collect_evidence_maps_results_to_claim_ids():
    claim = make_claim()

    state = AgentState(
        input_text=claim.claim,
        claims=[claim],
    )

    mocked_results = [
        {
            "title": "NASA",
            "content": "The Earth orbits the Sun.",
            "url": "https://www.nasa.gov/example",
            "score": 0.95,
            "credibility": 1.0,
        }
    ]

    with patch(
        "agents.fact_check_agent.search_and_verify.search",
        return_value=mocked_results,
    ):
        result = collect_evidence(state)

    assert 1 in result["evidence"]
    assert len(result["evidence"][1]) == 1

    evidence = result["evidence"][1][0]

    assert isinstance(evidence, EvidenceSource)
    assert evidence.title == "NASA"
    assert evidence.url == "https://www.nasa.gov/example"
    assert evidence.score == 0.95
    assert evidence.credibility == 1.0
    assert evidence.query_used == claim.claim


def test_collect_evidence_handles_no_search_results():
    claim = make_claim()

    state = AgentState(
        input_text=claim.claim,
        claims=[claim],
    )

    with patch(
        "agents.fact_check_agent.search_and_verify.search",
        return_value=[],
    ):
        result = collect_evidence(state)

    assert result["evidence"] == {
        1: []
    }


def test_collect_evidence_processes_multiple_claims():
    claims = [
        make_claim(
            1,
            "The Earth revolves around the Sun.",
        ),
        make_claim(
            2,
            "India became independent in 1947.",
        ),
    ]

    state = AgentState(
        input_text="Two claims",
        claims=claims,
    )

    def fake_search(query):
        return [
            {
                "title": f"Evidence for {query}",
                "content": "Relevant evidence.",
                "url": "https://example.com",
                "score": 0.90,
                "credibility": 0.60,
            }
        ]

    with patch(
        "agents.fact_check_agent.search_and_verify.search",
        side_effect=fake_search,
    ):
        result = collect_evidence(state)

    assert set(result["evidence"].keys()) == {1, 2}
    assert len(result["evidence"][1]) == 1
    assert len(result["evidence"][2]) == 1