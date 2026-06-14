"""
Solution: Exercise 1 server - adds get_shipping_estimate.
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

SHIPPING_ESTIMATES = {
    "US": "3-5 business days",
    "CA": "5-7 business days",
    "UK": "7-10 business days",
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


@mcp.tool()
def get_shipping_estimate(country: str) -> str:
    """Get the estimated shipping time for a destination country code
    (e.g. 'US', 'CA', 'UK')."""
    return SHIPPING_ESTIMATES.get(country.upper(), "unknown")


if __name__ == "__main__":
    mcp.run()
