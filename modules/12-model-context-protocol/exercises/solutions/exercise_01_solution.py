"""
Solution: Exercise 1 - Add a new tool to the MCP server and confirm
auto-discovery.
"""

import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "mcp_server.py")


async def main() -> None:
    server_params = StdioServerParameters(command="python", args=[SERVER_SCRIPT])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = await session.list_tools()
            tool_names = [t.name for t in mcp_tools.tools]
            print("Discovered tools:", tool_names)
            assert "get_shipping_estimate" in tool_names

            known = await session.call_tool("get_shipping_estimate", {"country": "US"})
            print("US ->", known.content[0].text)

            unknown = await session.call_tool("get_shipping_estimate", {"country": "ZZ"})
            print("ZZ ->", unknown.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
