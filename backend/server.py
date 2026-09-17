"""
NeuroShield — FastAPI Backend

Thin REST API layer over the NeuroShield LangGraph agents.

Agents:
    - Privacy Intelligence
    - Fact Intelligence
    - Website Intelligence
"""

import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# ENVIRONMENT
# ============================================================

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

load_dotenv(
    os.path.join(ROOT_DIR, ".env")
)


# ============================================================
# AGENT IMPORTS
# ============================================================

from agents.privacy_agent.graph import (
    build_graph as build_privacy_graph,
)

from agents.privacy_agent.chat_agent import (
    ask_privacy_question,
)

from agents.fact_check_agent.main import (
    fact_checker_graph,
)

from agents.website_scan_agent.graph import (
    build_graph as build_scan_graph,
)

from agents.website_scan_agent.chat_agent import (
    ask_website_safety_question,
)

from agents.shared.utils import (
    get_risk_level,
)


# ============================================================
# BUILD LONG-LIVED GRAPHS
# ============================================================

privacy_graph = build_privacy_graph()

scan_graph = build_scan_graph()


# ============================================================
# SESSION STORE
# ============================================================

_sessions: dict[str, dict] = {}


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="NeuroShield API",
    description=(
        "AI-powered web trust and fact verification API."
    ),
    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class PrivacyRequest(BaseModel):
    raw_text: str


class ChatRequest(BaseModel):
    question: str
    session_id: str


class FactCheckRequest(BaseModel):
    input_text: str


class ScanRequest(BaseModel):
    url: str


# ============================================================
# PRIVACY INTELLIGENCE
# ============================================================

@app.post("/api/privacy/analyze")
async def privacy_analyze(
    req: PrivacyRequest,
):
    """
    Analyze a privacy policy.
    """

    if not req.raw_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text is required",
        )

    try:

        result = privacy_graph.invoke(
            {
                "raw_text": req.raw_text
            }
        )

        session_id = str(
            uuid.uuid4()
        )

        _sessions[session_id] = {
            "type": "privacy",
            "result": result,
        }

        score = result.get(
            "score",
            0,
        )

        return {
            "session_id": session_id,
            "score": score,
            "risk_level": get_risk_level(
                score
            ),
            "structured_data": result.get(
                "structured_data",
                {},
            ),
            "risks": result.get(
                "risks",
                [],
            ),
            "findings": result.get(
                "findings",
                [],
            ),
            "evidence": result.get(
                "evidence",
                [],
            ),
            "recommendations": result.get(
                "recommendations",
                [],
            ),
            "summary": result.get(
                "summary",
                "",
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Privacy analysis failed: {exc}",
        ) from exc


@app.post("/api/privacy/chat")
async def privacy_chat(
    req: ChatRequest,
):
    """
    Ask a question about a previously analyzed privacy policy.
    """

    session = _sessions.get(
        req.session_id
    )

    if (
        not session
        or session["type"] != "privacy"
    ):
        raise HTTPException(
            status_code=404,
            detail="Privacy analysis session not found",
        )

    try:

        answer = ask_privacy_question(
            question=req.question,
            analysis_result=session["result"],
        )

        return {
            "answer": answer
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Privacy chat failed: {exc}",
        ) from exc


# ============================================================
# FACT INTELLIGENCE
# ============================================================

@app.post("/api/factcheck/analyze")
async def factcheck_analyze(
    req: FactCheckRequest,
):
    """
    Extract, retrieve, verify, and report on factual claims.
    """

    if not req.input_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text is required",
        )

    try:

        result = fact_checker_graph.invoke(
            {
                "input_text": req.input_text
            }
        )

        # ----------------------------------------------------
        # CLAIMS
        # ----------------------------------------------------

        claims_list = []

        for claim in result.get(
            "claims",
            [],
        ):

            claims_list.append(
                {
                    "id": claim.id,
                    "claim": claim.claim,
                    "type": claim.type,
                    "normalized_claim": (
                        claim.normalized_claim
                    ),
                }
            )

        # ----------------------------------------------------
        # EVIDENCE
        # ----------------------------------------------------

        evidence_map = {}

        for claim_id, sources in (
            result.get(
                "evidence",
                {},
            ).items()
        ):

            evidence_map[str(claim_id)] = []

            for source in sources:

                evidence_map[
                    str(claim_id)
                ].append(
                    {
                        "title": source.title,
                        "content": source.content,
                        "url": source.url,
                        "score": source.score,
                        "query_used": (
                            source.query_used
                        ),
                        "credibility": (
                            source.credibility
                        ),
                    }
                )

        # ----------------------------------------------------
        # VERIFICATIONS
        # ----------------------------------------------------

        verifications_map = {}

        for claim_id, verification in (
            result.get(
                "verifications",
                {},
            ).items()
        ):

            verifications_map[
                str(claim_id)
            ] = {
                "verdict": (
                    verification.verdict
                ),
                "confidence": (
                    verification.confidence
                ),
                "reason": (
                    verification.reason
                ),
                "supporting_sources": (
                    verification.supporting_sources
                ),
                "conflicting_sources": (
                    verification.conflicting_sources
                ),
                "uncertainty_reason": (
                    verification.uncertainty_reason
                ),
            }

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {
            "claims": claims_list,
            "evidence": evidence_map,
            "verifications": verifications_map,
            "final_report": result.get(
                "final_report",
                "",
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Fact checking failed: {exc}",
        ) from exc


# ============================================================
# WEBSITE INTELLIGENCE
# ============================================================

@app.post("/api/scanner/scan")
async def scanner_scan(
    req: ScanRequest,
):
    """
    Analyze a website for safety and trust signals.
    """

    if not req.url.strip():
        raise HTTPException(
            status_code=400,
            detail="URL is required",
        )

    try:

        result = scan_graph.invoke(
            {
                "url": req.url
            }
        )

        session_id = str(
            uuid.uuid4()
        )

        _sessions[session_id] = {
            "type": "scanner",
            "result": result,
        }

        return {
            "session_id": session_id,
            "overall_score": result.get(
                "overall_score",
                0,
            ),
            "verdict": result.get(
                "verdict",
                "CAUTION",
            ),
            "scores": result.get(
                "scores",
                {},
            ),
            "recommendations": result.get(
                "recommendations",
                [],
            ),
            "url_analysis": result.get(
                "url_analysis",
                {},
            ),
            "domain_age_analysis": result.get(
                "domain_age_analysis",
                {},
            ),
            "scam_report_analysis": result.get(
                "scam_report_analysis",
                {},
            ),
            "ssl_analysis": result.get(
                "ssl_analysis",
                {},
            ),
            "content_analysis": result.get(
                "content_analysis",
                {},
            ),
            "reputation_analysis": result.get(
                "reputation_analysis",
                {},
            ),
            "summary": result.get(
                "summary",
                "",
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Website scan failed: {exc}",
        ) from exc


@app.post("/api/scanner/chat")
async def scanner_chat(
    req: ChatRequest,
):
    """
    Ask a question about a previously scanned website.
    """

    session = _sessions.get(
        req.session_id
    )

    if (
        not session
        or session["type"] != "scanner"
    ):
        raise HTTPException(
            status_code=404,
            detail="Scanner session not found",
        )

    try:

        answer = ask_website_safety_question(
            question=req.question,
            analysis_result=session["result"],
        )

        return {
            "answer": answer
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Scanner chat failed: {exc}",
        ) from exc


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
async def health():
    """
    Basic API health check.
    """

    return {
        "status": "ok",
        "service": "NeuroShield API",
        "version": "2.0.0",
    }


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
