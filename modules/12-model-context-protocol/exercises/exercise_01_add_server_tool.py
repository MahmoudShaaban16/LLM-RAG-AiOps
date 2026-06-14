"""
Exercise 1: Add a new tool to the MCP server and confirm auto-discovery

TODO:
  1. In `mcp_server.py` (a local copy of
     examples/01_simple_mcp_server.py), add a new tool called
     `get_shipping_estimate` that takes a `country` string and returns a
     hardcoded shipping estimate (see SHIPPING_ESTIMATES below for the data
     it should use).
  2. Run this script. It launches the server over stdio and calls
     `session.list_tools()` - confirm `get_shipping_estimate` appears in
     the list without any changes to this client file.
  3. Call the new tool directly with `session.call_tool(...)` for a known
     and an unknown country and print both results.

This script does NOT call Claude - it only exercises the MCP
client/server connection, so no ANTHROPIC_API_KEY is needed.
"""

import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add this dict to mcp_server.py and use it in get_shipping_estimate.
SHIPPING_ESTIMATES = {
    "US": "3-5 business days",
    "CA": "5-7 business days",
    "UK": "7-10 business days",
}

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "mcp_server.py")


async def main() -> None:
    server_params = StdioServerParameters(command="python", args=[SERVER_SCRIPT])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # TODO: list tools and print their names - confirm
            # get_shipping_estimate is there once you add it to the server.

            # TODO: call get_shipping_estimate for "US" and for "ZZ"
            # (an unknown country) and print both results.
            pass


if __name__ == "__main__":
    asyncio.run(main())
