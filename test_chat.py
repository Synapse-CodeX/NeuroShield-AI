import sys
import os

# mock the LLM
class MockLLM:
    def invoke(self, prompt):
        class Resp:
            content = "mock answer"
        return Resp()

sys.modules["agents.shared.llm"] = type("mock", (), {"llm": MockLLM()})()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend", ".."))
from agents.website_scan_agent.chat_agent import ask_website_safety_question

result = {
    "scores": {},
    "verdict": "SAFE",
    "recommendations": [],
    "url_analysis": {},
    "ssl_analysis": {},
    "content_analysis": {},
    "reputation_analysis": {},
    "domain_age_analysis": {},
    "scam_report_analysis": {},
    "overall_score": 100
}

try:
    ans = ask_website_safety_question("Is it safe?", result)
    print("Success:", ans)
except Exception as e:
    import traceback
    traceback.print_exc()

