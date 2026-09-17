from langgraph.graph import StateGraph, END
from agents.website_scan_agent.state import WebsiteScanState
from agents.website_scan_agent.nodes import (
    url_analysis_node,
    domain_age_node,
    scam_report_node,
    ssl_analysis_node,
    content_analysis_node,
    reputation_node,
    scoring_node,
    verdict_node,
)


def build_graph():
    """
    Build the Website Scan Agent LangGraph pipeline.

    Flow:
        url_analysis → [domain_age, scam_report, ssl, content, reputation] → scoring → verdict
    """
    workflow = StateGraph(WebsiteScanState)

    # ── Register nodes ──
    workflow.add_node("url_analysis", url_analysis_node)
    workflow.add_node("domain_age", domain_age_node)
    workflow.add_node("scam_report", scam_report_node)
    workflow.add_node("ssl_analysis", ssl_analysis_node)
    workflow.add_node("content_analysis", content_analysis_node)
    workflow.add_node("reputation", reputation_node)
    workflow.add_node("scoring", scoring_node)
    workflow.add_node("verdict", verdict_node)

    # ── Entry point: always start with URL structure analysis ──
    workflow.set_entry_point("url_analysis")

    # ── After URL analysis, fan out to independent checks ──
    workflow.add_edge("url_analysis", "domain_age")
    workflow.add_edge("url_analysis", "scam_report")
    workflow.add_edge("url_analysis", "ssl_analysis")
    workflow.add_edge("url_analysis", "content_analysis")
    workflow.add_edge("url_analysis", "reputation")

    # ── All checks converge into scoring ──
    workflow.add_edge("domain_age", "scoring")
    workflow.add_edge("scam_report", "scoring")
    workflow.add_edge("ssl_analysis", "scoring")
    workflow.add_edge("content_analysis", "scoring")
    workflow.add_edge("reputation", "scoring")

    # ── Scoring → Verdict → END ──
    workflow.add_edge("scoring", "verdict")
    workflow.add_edge("verdict", END)

    return workflow.compile()
