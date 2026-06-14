---
marp: true
title: Model Context Protocol (MCP)
paginate: true
---

# Model Context Protocol (MCP)
### Module 12

A standard protocol for tools, resources, and prompts

---

## Agenda

1. What is MCP, and why does it exist?
2. MCP architecture: hosts, clients, servers
3. MCP tools vs. inline tool definitions (Module 03)
4. Building an MCP server
5. Connecting Claude to an MCP server
6. Security considerations
7. Common failure modes

---

## 1. What is MCP, and Why Does it Exist?

Module 03: tools defined **inline** — JSON schema + Python function, in your app

Gets awkward when:
- Same tools need to be used by **multiple** apps/agents
- You want tools built by **someone else** without copying their code
- Tools need to be added/updated **independently** of the app

**MCP** = standardized way for a "host" to discover and call tools/resources/prompts exposed by a separate **MCP server**

---

## MCP in One Picture

```
Without MCP:  your agent code  --(hardcoded tool functions)-->  each integration

With MCP:     your agent code  --(MCP protocol)-->  MCP server  --> the actual integration
                    (host/client)                    (anyone can build/run this)
```

> Like USB-C for device connectors, or LSP for editor/language integrations

🧑‍💼 **PM view:** MCP matters when tools need to be **shared, reused, or operated independently**. For a single agent with a handful of owned tools, inline tools (Module 03) remain simpler.

---

## 2. MCP Architecture

| Role | What it is | Example |
|---|---|---|
| **Host** | The application the user interacts with | Your agent app, Claude Desktop/Code |
| **Client** | The part of the host that speaks MCP | `ClientSession` (embedded in host) |
| **Server** | A process exposing tools/resources/prompts | "GitHub" MCP server, "company DB" server |

A host can connect to **multiple** servers, aggregating all their tools.

**Transports:**
- **stdio** — client launches server as a subprocess (local, simple)
- **HTTP/SSE** — server runs as a network service (shared/hosted)

---

## 3. MCP Tools vs. Inline Tools

Both produce the same thing the Anthropic API needs:
`{"name", "description", "input_schema"}` + a way to execute a named tool

| | Inline tools (Module 03) | MCP server tools |
|---|---|---|
| Where defined | Your application code | Separate MCP server process |
| Who can reuse | Only this codebase | Any MCP-compatible host |
| Update cycle | Redeploy your app | Update/restart server independently |
| New tool | Edit your code | Add to server — clients see it automatically |
| Operational surface | One service | Two services (host + server) |

🧭 **Tech lead view:** Not "MCP vs. tool use" — MCP **is** tool use, behind a protocol boundary.

---

## 4. Building an MCP Server

`FastMCP` makes a minimal server straightforward:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")

@mcp.tool()
def get_order_status(order_id: str) -> str:
    """Look up the current status of a customer order by order ID."""
    mock_orders = {"ORD-1234": "shipped", "ORD-5678": "processing"}
    return mock_orders.get(order_id, "not_found")

if __name__ == "__main__":
    mcp.run()
```

`@mcp.tool()` derives the schema from the signature/type hints, description from the docstring

---

## 5. Connecting Claude to an MCP Server

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(command="python", args=["01_simple_mcp_server.py"])

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # 1. Discover tools from the MCP server
        mcp_tools = await session.list_tools()
        anthropic_tools = [
            {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
            for t in mcp_tools.tools
        ]

        # 2. Same agentic loop as Module 03, but tool execution
        #    goes via session.call_tool(block.name, block.input)
```

🧭 Everything from Module 03 (`stop_reason`, `tool_result`, `MAX_ITERATIONS`) is unchanged

---

## 6. Security Considerations

MCP servers are **tool providers your agent grants capabilities to** — Module 09's trust questions apply, plus:

- **Tool-access allow-lists** apply to MCP tools too — validate `tool_use.name` before calling `session.call_tool`
- **Tool descriptions are untrusted input** if the server isn't yours — a malicious server could write descriptions designed to manipulate the model
- **Resource/data exposure** — prefer servers configured with the **minimum** tool set the task needs

🧭 "We added an MCP server" = adding a third-party dependency that can act on your behalf

---

## 7. Common Failure Modes

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Client can't connect | Wrong command/args, server crashed | Run server standalone first |
| Tool call fails silently | Name/schema mismatch, server exception | Log results/errors explicitly |
| New tool not available | Tool list fetched once at startup | Re-fetch `list_tools()` per session |
| Agent calls a tool it shouldn't | No allow-list on MCP tools | Apply Module 09's guardrail |
| Broke in prod | stdio → HTTP/SSE without network handling | Apply Module 07's retry/fallback thinking |

---

## Hands-on

- `examples/01_simple_mcp_server.py` — minimal MCP server with two tools
- `examples/02_mcp_client_with_claude.py` — Claude client connecting via stdio
- `exercises/` — practice problems + solutions

---

# Questions?

Next module: **Capstone Project** →
