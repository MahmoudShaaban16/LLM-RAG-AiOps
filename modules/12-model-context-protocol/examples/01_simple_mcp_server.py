"""
01 - Simple MCP Server

A minimal MCP server built with FastMCP, exposing two tools that mirror
the mock tools from Module 03's agentic loop example. Run this file
directly to start the server over stdio - it's launched as a subprocess
by 02_mcp_client_with_claude.py.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")

# Hardcoded "databases" for the demo - a real server would query a
# database, vector store (Module 02/05), or internal API.
ORDERS = {
    "ORD-1234": "shipped",
    "ORD-5678": "processing",
    "ORD-9012": "delivered",
}

KNOWLEDGE_BASE = {
    "refund policy": (
        "Customers can request a full refund within 30 days of purchase. "
        "Refunds are processed within 5-7 business days."
    ),
    "annual plan price": (
        "The annual plan costs $1,200/year, billed upfront, which is "
        "equivalent to a 20% discount versus the monthly plan."
    ),
    "monthly plan price": "The monthly plan costs $125/month.",
}


@mcp.tool()
def get_order_status(order_id: str) -> str:
    """Look up the current status of a customer order by order ID."""
    return ORDERS.get(order_id, "not_found")


@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """Search the internal knowledge base for information about company
    policies, products, or pricing."""
    query_lower = query.lower()
    for key, value in KNOWLEDGE_BASE.items():
        if key in query_lower or query_lower in key:
            return value
    return f"No knowledge base entry found for '{query}'."


if __name__ == "__main__":
    mcp.run()
