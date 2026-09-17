from pydantic import BaseModel

from agents.shared.llm import llm


class TestOutput(BaseModel):
    answer: str
    confidence: float


structured_llm = llm.with_structured_output(TestOutput)

result = structured_llm.invoke(
    "Say that Gemini is working and give confidence 0.99."
)

print(result)
print(type(result))