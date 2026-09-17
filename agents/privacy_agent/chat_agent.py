from typing import Any, Iterable

from agents.shared.llm import llm


def ask_privacy_question(question: str, analysis_result: dict, chat_history=None) -> str:
    vector_store = analysis_result.get("vector_store", None)

    if vector_store is None:
        return "Vector store not available."

    # 🔍 Retrieve relevant chunks
    docs = vector_store.similarity_search(question, k=3)
    context = "\n".join([doc.page_content for doc in docs])

    structured_data = analysis_result.get("structured_data", {})
    risks = analysis_result.get("risks", [])

    # 🧠 Strong prompt
    prompt = f"""
You are a privacy policy assistant.

Answer the question using ONLY the information below.

Context:
{context}

Structured Data:
{structured_data}

Risks:
{risks}

Question:
{question}

Rules:
- Be clear and direct
- Do NOT hallucinate
- If not mentioned, say: "Not mentioned in policy"
"""

    response = llm.invoke(prompt)
    return response.content
