from langgraph.graph import END, StateGraph

from agents.privacy_agent.nodes import (
    chunk_node,
    embed_store_node,
    extract_node,
    merge_node,
    risk_node,
    score_node,
    summary_node,
)
from agents.privacy_agent.state import GraphState


def build_graph():
    """Build and compile the privacy-policy analysis graph."""

    workflow = StateGraph(GraphState)

    workflow.add_node("chunk", chunk_node)
    workflow.add_node("embed", embed_store_node)
    workflow.add_node("extract", extract_node)
    workflow.add_node("merge", merge_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("score", score_node)
    workflow.add_node("summary", summary_node)

    workflow.set_entry_point("chunk")

    workflow.add_edge("chunk", "embed")
    workflow.add_edge("embed", "extract")
    workflow.add_edge("extract", "merge")
    workflow.add_edge("merge", "risk")
    workflow.add_edge("risk", "score")
    workflow.add_edge("score", "summary")
    workflow.add_edge("summary", END)

    return workflow.compile()