import asyncio
import uuid
from backend.server import scanner_chat, ChatRequest, _sessions

_sessions["test-id"] = {
    "type": "scanner",
    "result": {"overall_score": 90, "verdict": "SAFE"}
}

async def test():
    req = ChatRequest(question="Is it safe?", session_id="test-id")
    try:
        res = await scanner_chat(req)
        print("RES:", res)
    except Exception as e:
        print("EXCEPTION:", type(e), str(e))

asyncio.run(test())
