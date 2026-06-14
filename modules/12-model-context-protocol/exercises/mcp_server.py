"""
Starter MCP server for Exercise 1.

A copy of examples/01_simple_mcp_server.py. Add the
`get_shipping_estimate` tool here as described in
exercise_01_add_server_tool.py.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")

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

# TODO (Exercise 1): add a SHIPPING_ESTIMATES dict and a
# get_shipping_estimate tool here.


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
