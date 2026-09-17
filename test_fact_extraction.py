from agents.fact_check_agent.agent_state import AgentState
from agents.fact_check_agent.extraction_claim import extract_claims


state = AgentState(
    input_text=(
        "The Earth revolves around the Sun once every 365.25 days. "
        "The Great Wall of China is visible from space with the naked eye. "
        "Mount Everest is 8,848 meters tall."
    )
)

result = extract_claims(state)

print("\n" + "=" * 60)
print("CLAIM EXTRACTION TEST")
print("=" * 60)

claims = result["claims"]

print(f"\nTotal claims: {len(claims)}")

for claim in claims:
    print(f"\nClaim {claim.id}")
    print(f"  Text:       {claim.claim}")
    print(f"  Type:       {claim.type}")
    print(f"  Normalized: {claim.normalized_claim}")

print("\n" + "=" * 60)