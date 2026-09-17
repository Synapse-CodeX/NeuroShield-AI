from agents.shared.llm import llm
from agents.fact_check_agent.agent_state import (
    AgentState,
    Claim,
    ClaimExtractionOutput,
)


# ============================================================
# CLAIM EXTRACTION
# ============================================================

def extract_claims(state: AgentState) -> dict:
    """
    Extract atomic, independently verifiable claims from user text.

    Uses exactly one structured Gemini call.
    """

    print("\n[Agent 1] Extracting claims...")

    prompt = f"""
You are the Claim Extraction Agent of an evidence-first fact-checking
system.

Your task is to extract atomic claims from the user's input.

IMPORTANT:
Extract claims only. Do NOT verify them.
Do NOT decide whether they are true or false.
Do NOT use your own world knowledge to remove claims.

RULES:

1. Extract ALL statements that can reasonably be fact-checked.
2. Include claims that may be false, misleading, unusual, or absurd.
3. Ignore pure opinions, preferences, emotions, and vague statements.
4. Break complex sentences into separate atomic claims.
5. Each claim must contain ONE independently verifiable fact.
6. Do not merge multiple facts into one claim.
7. Avoid duplicate claims.
8. Preserve the meaning of the original statement.
9. Do not add information that was not present in the input.
10. For numerical claims, preserve the number and unit.
11. For temporal claims, preserve dates or time periods.
12. For entity claims, preserve the relevant person, organization,
    location, product, or other entity.
13. normalized_claim should be a concise version suitable for web search.
14. If the original claim is already suitable for search, normalized_claim
    may closely match it.

Claim types:

- factual:
  A general factual statement.

- numerical:
  A statement involving quantities, percentages, measurements,
  counts, rates, or numerical comparisons.

- temporal:
  A statement involving dates, years, historical periods, or timing.

- entity:
  A statement whose verification substantially depends on identifying
  a particular person, organization, place, product, or other entity.

Examples of atomic claims:

- The Earth revolves around the Sun once every 365.25 days.
- The average human body contains about 5 liters of blood.
- Lightning never strikes the same place twice.
- Octopuses have three hearts.
- A bolt of lightning can reach temperatures hotter than the surface
  of the Sun.
- The Great Wall of China is visible from space with the naked eye.
- Electric vehicle adoption has increased globally in the past decade.
- Artificial intelligence can generate human-like text from prompts.
- Drinking water helps regulate body temperature.
- Mount Everest is the tallest mountain above sea level on Earth.

USER INPUT:

{state.input_text}

Return only the structured claim extraction result.
"""

    try:
        structured_llm = llm.with_structured_output(
            ClaimExtractionOutput
        )

        response: ClaimExtractionOutput = structured_llm.invoke(prompt)

        claims: list[Claim] = []

        for index, extracted_claim in enumerate(
            response.claims,
            start=1,
        ):
            normalized = (
                extracted_claim.normalized_claim
                or extracted_claim.claim
            )

            claims.append(
                Claim(
                    id=index,
                    claim=extracted_claim.claim.strip(),
                    type=extracted_claim.type,
                    normalized_claim=normalized.strip(),
                )
            )

        print(f"Extracted {len(claims)} claims")

        return {"claims": claims}

    except Exception as exc:
        print(f"[Claim Extraction Error] {exc}")

        return {
            "claims": [],
        }