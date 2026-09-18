from agents.shared.llm import llm


def _format_risks(risks: list) -> str:
    """Format detected privacy risks for a user-facing response."""
    if not risks:
        return "No privacy risks were detected in the analysis."

    lines = []

    for risk in risks:
        if isinstance(risk, dict):
            title = risk.get("title") or risk.get("name") or "Privacy risk"
            severity = risk.get("severity", "")
            description = risk.get("description", "")

            line = f"- {title}"

            if severity:
                line += f" ({severity})"

            if description:
                line += f": {description}"

            lines.append(line)

        else:
            lines.append(f"- {risk}")

    return "\n".join(lines)


def _format_structured_data(structured_data: dict) -> str:
    """Format extracted privacy-policy information."""
    if not structured_data:
        return "No structured policy information is available."

    lines = []

    for key, value in structured_data.items():
        label = str(key).replace("_", " ").title()

        if isinstance(value, list):
            value_text = ", ".join(
                str(item) for item in value if str(item).strip()
        )
        if not value_text:
            continue
        else:
            value_text = str(value).strip()

        if value_text:
            lines.append(f"- {label}: {value_text}")

        return "\n".join(lines)


def _fallback_answer(
    question: str,
    analysis_result: dict,
) -> str:
    """
    Provide a deterministic, evidence-grounded privacy answer when Gemini
    is unavailable.

    The fallback never invents an interpretation. It uses only:
    - retrieved policy chunks
    - structured extraction
    - detected privacy risks
    - analysis metadata
    """
    vector_store = analysis_result.get("vector_store")

    structured_data = analysis_result.get("structured_data", {})
    risks = analysis_result.get("risks", [])

    # Retrieve policy passages relevant to the user's question.
    docs = []

    if vector_store is not None:
        try:
            docs = vector_store.similarity_search(question, k=3)
        except Exception:  # noqa: BLE001
            docs = []

    if not docs:
        return (
            "The AI reasoning service is currently unavailable, and no "
            "relevant policy evidence could be retrieved for this question."
        )

    answer_parts = [
        (
            "The AI reasoning service is temporarily unavailable, so I'm "
            "showing the relevant information directly from the analyzed "
            "privacy policy."
        ),
        "",
        "Relevant policy evidence:",
    ]

    for index, doc in enumerate(docs, start=1):
        content = getattr(doc, "page_content", "")

        if not content:
            continue

        answer_parts.extend(
            [
                "",
                f"**Policy excerpt {index}:**",
                content.strip(),
            ]
        )

    # Add relevant detected risks because these are already part of the
    # deterministic privacy analysis.
    if risks:
        answer_parts.extend(
            [
                "",
                "Detected privacy risks:",
                _format_risks(risks),
            ]
        )

    # Add structured extraction when available.
    if structured_data:
        answer_parts.extend(
            [
                "",
                "Extracted policy information:",
                _format_structured_data(structured_data),
            ]
        )

    answer_parts.extend(
        [
            "",
            (
                "This response is based only on the stored privacy-policy "
                "analysis and retrieved policy excerpts."
            ),
        ]
    )

    return "\n".join(answer_parts)


def ask_privacy_question(
    question: str,
    analysis_result: dict,
    chat_history=None,
) -> str:
    """
    Answer follow-up questions about a privacy-policy analysis.

    Gemini provides the normal conversational answer. If Gemini is
    unavailable or rate-limited, the function falls back to relevant
    policy evidence and deterministic analysis results.
    """
    vector_store = analysis_result.get("vector_store")

    if vector_store is None:
        return "Vector store not available."

    try:
        # Retrieve relevant chunks from the analyzed policy.
        docs = vector_store.similarity_search(question, k=3)
    except Exception:  # noqa: BLE001
        docs = []

    context = "\n".join(
        doc.page_content
        for doc in docs
        if getattr(doc, "page_content", "")
    )

    structured_data = analysis_result.get("structured_data", {})
    risks = analysis_result.get("risks", [])

    prompt = f"""
You are a privacy policy assistant.

Answer the question using ONLY the information below.

Relevant Policy Context:
{context}

Structured Data:
{structured_data}

Detected Privacy Risks:
{risks}

Question:
{question}

Rules:
- Be clear and direct
- Use simple language
- Do NOT hallucinate
- Do NOT make claims that are not supported by the supplied policy data
- If the requested information is not present, say:
  "Not mentioned in policy"
"""

    if chat_history:
        recent_history = chat_history[-6:]

        history_lines = []

        for message in recent_history:
            if not isinstance(message, dict):
                continue

            role = message.get("role", "user").title()
            content = message.get("content", "")

            if content:
                history_lines.append(f"{role}: {content}")

        if history_lines:
            prompt += (
                "\n\nRecent conversation:\n"
                + "\n".join(history_lines)
            )

    try:
        response = llm.invoke(prompt)

        content = response.content

        if isinstance(content, str) and content.strip():
            return content.strip()

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
        # Gemini failures must never turn an otherwise valid privacy
        # analysis into a broken chat experience.
        return _fallback_answer(
            question=question,
            analysis_result=analysis_result,
        )