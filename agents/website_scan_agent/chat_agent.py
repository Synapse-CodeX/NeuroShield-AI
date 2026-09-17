from agents.shared.llm import llm


def ask_website_safety_question(
    question: str,
    analysis_result: dict,
    chat_history: list | None = None,
) -> str:
    """
    Answer follow-up questions about a website scan result using LLM.

    Works like the privacy agent's ``ask_privacy_question`` but operates on
    the website scan analysis output instead of a vector store.
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
- If not available in the data, say: "This information is not available in the scan results"
"""

    response = llm.invoke(prompt)
    return response.content
