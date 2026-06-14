"""
02 - MCP Client with Claude

Connects to the MCP server in 01_simple_mcp_server.py over stdio,
discovers its tools, converts them to the Anthropic API's tool shape,
and runs the same agentic loop from Module 03 - except tool execution
is a call to the MCP server instead of a local Python function.
"""

import asyncio
import json
import os

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 5

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "01_simple_mcp_server.py")


async def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    server_params = StdioServerParameters(command="python", args=[SERVER_SCRIPT])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. Discover tools from the MCP server and convert to the
            #    Anthropic API's tool shape.
            mcp_tools = await session.list_tools()
            anthropic_tools = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema,
                }
                for t in mcp_tools.tools
            ]
            print("Discovered MCP tools:", [t["name"] for t in anthropic_tools])

            messages = [
                {
                    "role": "user",
                    "content": (
                        "A customer is on the annual plan and wants to know our "
                        "refund policy, and also wants to know the status of "
                        "order ORD-5678."
                    ),
                }
            ]

            # 2. Same agentic loop as Module 03, but tool execution goes via MCP.
            for iteration in range(1, MAX_ITERATIONS + 1):
                print(f"\n=== Iteration {iteration} ===")

                response = client.messages.create(
                    model=MODEL,
                    max_tokens=1024,
                    tools=anthropic_tools,
                    messages=messages,
                )

                messages.append({"role": "assistant", "content": response.content})

                for block in response.content:
                    if block.type == "text" and block.text.strip():
                        print(f"[text] {block.text.strip()}")
                    elif block.type == "tool_use":
                        print(f"[tool_use] {block.name}({json.dumps(block.input)})")

                if response.stop_reason != "tool_use":
                    print("\n--- Final answer ---")
                    for block in response.content:
                        if block.type == "text":
                            print(block.text)
                    break

                # Execute every requested tool call via the MCP server.
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = await session.call_tool(block.name, block.input)
                        result_text = "\n".join(
                            item.text for item in result.content if item.type == "text"
                        )
                        print(f"[tool_result] {result_text}")
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result_text,
                                "is_error": result.isError,
                            }
                        )

                messages.append({"role": "user", "content": tool_results})
            else:
                print(f"\nStopped after reaching MAX_ITERATIONS={MAX_ITERATIONS}.")


if __name__ == "__main__":
    asyncio.run(main())
