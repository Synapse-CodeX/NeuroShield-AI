from langchain_core.tools import tool

from agents.shared.llm import llm


@tool
def test_search(query: str) -> str:
    """Search for information about a query."""
    return f"Search result for: {query}"


llm_with_tools = llm.bind_tools([test_search])

response = llm_with_tools.invoke(
    "Find information about the capital of France. "
    "Use the test_search tool."
)

print("CONTENT:")
print(response.content)

print("\nTOOL CALLS:")
print(response.tool_calls)