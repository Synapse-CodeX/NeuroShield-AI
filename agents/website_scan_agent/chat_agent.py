from agents.shared.llm import llm


def _format_score_breakdown(scores: dict) -> str:
    """Create a readable score breakdown from the scan results."""
    if not scores:
        return "No score breakdown is available."

    lines = []

    for name, value in scores.items():
        if isinstance(value, (int, float)):
            label = name.replace("_", " ").title()
            lines.append(f"- {label}: {value}/100")

    return "\n".join(lines) if lines else "No score breakdown is available."


def _fallback_answer(
    question: str,
    analysis_result: dict,
) -> str:
    """
    Generate an evidence-grounded response without using an LLM.

    This is used when Gemini is unavailable, rate-limited, or otherwise fails.
    The fallback only uses information already present in the scan result.
    """
    question_lower = question.lower()

    scores = analysis_result.get("scores", {})
    verdict = analysis_result.get("verdict", "Unknown")
    recommendations = analysis_result.get("recommendations", [])
    overall_score = analysis_result.get("overall_score", 0)

    url_analysis = analysis_result.get("url_analysis", {})
    ssl_analysis = analysis_result.get("ssl_analysis", {})
    content_analysis = analysis_result.get("content_analysis", {})
    reputation_analysis = analysis_result.get("reputation_analysis", {})
    domain_age_analysis = analysis_result.get("domain_age_analysis", {})
    scam_report_analysis = analysis_result.get("scam_report_analysis", {})

    # ---------------------------------------------------------
    # Overall score / verdict questions
    # ---------------------------------------------------------
    if any(
        keyword in question_lower
        for keyword in (
            "score",
            "verdict",
            "rating",
            "safe",
            "risk",
            "why",
        )
    ):
        score_breakdown = _format_score_breakdown(scores)

        answer = (
            f"The scan gave this website an overall score of "
            f"{overall_score}/100 with a verdict of **{verdict}**.\n\n"
            f"Score breakdown:\n"
            f"{score_breakdown}"
        )

        if recommendations:
            answer += "\n\nRecommendations from the scan:\n"
            answer += "\n".join(
                f"- {recommendation}" for recommendation in recommendations
            )

        return answer

    # ---------------------------------------------------------
    # SSL questions
    # ---------------------------------------------------------
    if any(
        keyword in question_lower
        for keyword in (
            "ssl",
            "certificate",
            "https",
            "tls",
        )
    ):
        if not ssl_analysis:
            return "This information is not available in the scan results."

        score = scores.get("ssl", scores.get("ssl_score"))

        answer = "The scan's SSL/TLS assessment is:\n\n"
        answer += f"{ssl_analysis}"

        if isinstance(score, (int, float)):
            answer += f"\n\nSSL score: **{score}/100**."

        return answer

    # ---------------------------------------------------------
    # URL questions
    # ---------------------------------------------------------
    if any(
        keyword in question_lower
        for keyword in (
            "url",
            "link",
            "domain",
            "address",
        )
    ):
        if not url_analysis:
            return "This information is not available in the scan results."

        score = scores.get("url", scores.get("url_score"))

        answer = "The scan's URL/domain structure assessment is:\n\n"
        answer += f"{url_analysis}"

        if isinstance(score, (int, float)):
            answer += f"\n\nURL structure score: **{score}/100**."

        return answer

    # ---------------------------------------------------------
    # Content questions
    # ---------------------------------------------------------
    if any(
        keyword in question_lower
        for keyword in (
            "content",
            "page",
            "website text",
            "quality",
        )
    ):
        if not content_analysis:
            return "This information is not available in the scan results."

        score = scores.get("content", scores.get("content_score"))

        answer = "The scan's content-quality assessment is:\n\n"
        answer += f"{content_analysis}"

        if isinstance(score, (int, float)):
            answer += f"\n\nContent quality score: **{score}/100**."

        return answer

    # ---------------------------------------------------------
    # Reputation questions
    # ---------------------------------------------------------
    if any(
        keyword in question_lower
        for keyword in (
            "reputation",
            "trust",
            "trusted",
            "credibility",
        )
    ):
        if not reputation_analysis:
            return "This information is not available in the scan results."

        score = scores.get("reputation", scores.get("reputation_score"))

        answer = "The scan's reputation assessment is:\n\n"
        answer += f"{reputation_analysis}"

        if isinstance(score, (int, float)):
            answer += f"\n\nReputation score: **{score}/100**."

        return answer

    # ---------------------------------------------------------
    # Domain age questions
    # ---------------------------------------------------------
    if any(
        keyword in question_lower
        for keyword in (
            "age",
            "old",
            "created",
            "registration",
            "registered",
        )
    ):
        if not domain_age_analysis:
            return "This information is not available in the scan results."

        score = scores.get("domain_age", scores.get("domain_age_score"))

        answer = "The scan's domain-age assessment is:\n\n"
        answer += f"{domain_age_analysis}"

        if isinstance(score, (int, float)):
            answer += f"\n\nDomain age score: **{score}/100**."

        return answer

    # ---------------------------------------------------------
    # Scam report questions
    # ---------------------------------------------------------
    if any(
        keyword in question_lower
        for keyword in (
            "scam",
            "report",
            "complaint",
            "fraud",
        )
    ):
        if not scam_report_analysis:
            return "This information is not available in the scan results."

        score = scores.get(
            "scam_reports",
            scores.get("scam_report_score"),
        )

        answer = "The scan's scam-report assessment is:\n\n"
        answer += f"{scam_report_analysis}"

        if isinstance(score, (int, float)):
            answer += f"\n\nScam-report score: **{score}/100**."

        return answer

    # ---------------------------------------------------------
    # Recommendation questions
    # ---------------------------------------------------------
    if any(
        keyword in question_lower
        for keyword in (
            "recommend",
            "recommendation",
            "should i",
            "what should",
            "what do",
            "action",
        )
    ):
        if not recommendations:
            return "This information is not available in the scan results."

        return (
            "Based on the scan results, the recommended actions are:\n\n"
            + "\n".join(
                f"- {recommendation}"
                for recommendation in recommendations
            )
        )

    # ---------------------------------------------------------
    # Generic fallback
    # ---------------------------------------------------------
    return (
        "I can answer this using the stored scan results, but the AI "
        "reasoning service is currently unavailable.\n\n"
        f"Overall score: **{overall_score}/100**\n"
        f"Verdict: **{verdict}**\n\n"
        f"Available score breakdown:\n"
        f"{_format_score_breakdown(scores)}\n\n"
        "This information is limited to the data produced by the website "
        "scan."
    )


def ask_website_safety_question(
    question: str,
    analysis_result: dict,
    chat_history: list | None = None,
) -> str:
    """
    Answer follow-up questions about a website scan result.

    Gemini is used for normal conversational reasoning. If Gemini is
    unavailable or rate-limited, a deterministic fallback answers the
    question using only the stored scan results.
    """
    scores = analysis_result.get("scores", {})
    verdict = analysis_result.get("verdict", "")
    recommendations = analysis_result.get("recommendations", [])
    url_analysis = analysis_result.get("url_analysis", {})
    ssl_analysis = analysis_result.get("ssl_analysis", {})
    content_analysis = analysis_result.get("content_analysis", {})
    reputation_analysis = analysis_result.get("reputation_analysis", {})
    domain_age_analysis = analysis_result.get("domain_age_analysis", {})
    scam_report_analysis = analysis_result.get("scam_report_analysis", {})
    overall_score = analysis_result.get("overall_score", 0)

    prompt = f"""You are a cybersecurity assistant helping users understand website safety reports.

Answer the question using ONLY the analysis data below.

URL Analysis:
{url_analysis}

Domain Age:
{domain_age_analysis}

Scam Reports:
{scam_report_analysis}

SSL Certificate:
{ssl_analysis}

Content Analysis:
{content_analysis}

Reputation:
{reputation_analysis}

Scores:
{scores}

Overall Score: {overall_score}/100
Verdict: {verdict}
Recommendations: {recommendations}

Question:
{question}

Rules:
- Be clear and direct
- Use simple, non-technical language
- Do NOT hallucinate or invent information
- Base every factual statement on the supplied scan data
- If not available in the data, say:
  "This information is not available in the scan results"
"""

    # Include recent conversation context when available.
    if chat_history:
        recent_history = chat_history[-6:]

        history_text = "\n".join(
            f"{message.get('role', 'user').title()}: "
            f"{message.get('content', '')}"
            for message in recent_history
            if isinstance(message, dict)
        )

        prompt += f"""

Recent conversation:
{history_text}
"""

    try:
        response = llm.invoke(prompt)

        content = response.content

        if isinstance(content, str) and content.strip():
            return content.strip()

        # Some LangChain model responses can contain structured content.
        if isinstance(content, list):
            text_parts = []

            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict) and item.get("text"):
                    text_parts.append(str(item["text"]))

            combined = "\n".join(text_parts).strip()

            if combined:
                return combined

        raise ValueError("Gemini returned an empty response.")

    except Exception:  # noqa: BLE001
        # Gemini failures must never make the scanner chat endpoint fail.
        # Fall back to deterministic answers grounded entirely in the scan.
        return _fallback_answer(
            question=question,
            analysis_result=analysis_result,
        )