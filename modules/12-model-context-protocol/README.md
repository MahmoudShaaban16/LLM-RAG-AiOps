# Module 12 — Model Context Protocol (MCP)

> **Goal:** Understand what MCP is, how it relates to the tool-use patterns from Module 03, when to build/use an MCP server instead of inline tool definitions, and how to connect an MCP server to Claude.

## Contents

- [1. What is MCP, and why does it exist?](#1-what-is-mcp-and-why-does-it-exist)
- [2. MCP architecture: hosts, clients, servers](#2-mcp-architecture-hosts-clients-servers)
- [3. MCP tools vs. inline tool definitions (Module 03)](#3-mcp-tools-vs-inline-tool-definitions-module-03)
- [4. Building an MCP server](#4-building-an-mcp-server)
- [5. Connecting Claude to an MCP server](#5-connecting-claude-to-an-mcp-server)
- [6. Security considerations](#6-security-considerations)
- [7. Common failure modes](#7-common-failure-modes)
- [Hands-on](#hands-on)

---

## 1. What is MCP, and why does it exist?

In Module 03, every tool was defined **inline**: a JSON schema plus a Python function, both living in your application code. That works well for a handful of tools you own. It gets awkward when:

- The **same tools** (e.g., "search our internal wiki", "query our database") need to be used by *multiple* applications or agents
- You want to use tools built by **someone else** (another team, a vendor, an open-source project) without copying their implementation into your codebase
- Tools need to be added/updated **independently** of the application that uses them

**MCP (Model Context Protocol)** is an open protocol — a standardized way for an application (the "host", e.g. an agent you build, or Claude Code/Claude Desktop) to discover and call tools, read resources, and use prompts exposed by a separate **MCP server**, over a well-defined interface (JSON-RPC over stdio, HTTP, or SSE).

```
Without MCP:  your agent code  --(hardcoded tool functions)-->  each integration

With MCP:     your agent code  --(MCP protocol)-->  MCP server  --> the actual integration
                    (host/client)                    (anyone can build/run this)
```

> Think of MCP as roughly analogous to what USB-C did for device connectors, or what LSP (Language Server Protocol) did for editor/language integrations — a shared interface so integrations can be built once and used by many hosts.

🧑‍💼 **PM view:** MCP matters when tool integrations need to be **shared, reused, or operated independently** from the application using them — e.g., a "company knowledge base" MCP server that multiple internal agents/tools connect to, maintained by the team that owns that data. For a single agent with a handful of tools you own end-to-end, Module 03's inline tools remain simpler and are not "wrong."

🧑‍💻 **Engineer view:** MCP is a protocol, not a specific product — the official Python/TypeScript SDKs (`mcp` package) give you `FastMCP` for building servers quickly, and a client (`ClientSession`) for connecting to them. The shapes of MCP **tools** (name, description, JSON Schema input) map directly onto the Anthropic API's tool-use shape from Module 03.

🧭 **Tech lead view:** Adopting MCP is an architectural decision about **where integrations live and who owns them** — not a capability change to the model itself. The agentic loop (Module 03) is identical; MCP just changes *where the tool implementations live* and *how your code discovers them*.

---

## 2. MCP architecture: hosts, clients, servers

| Role | What it is | Example |
|---|---|---|
| **Host** | The application the user interacts with | Your agent app, Claude Desktop, Claude Code |
| **Client** | The part of the host that speaks the MCP protocol | The `mcp` SDK's `ClientSession`, embedded in the host |
| **Server** | A process exposing tools/resources/prompts via MCP | A "GitHub" MCP server, a "company database" MCP server |

A host can connect to **multiple** MCP servers at once, aggregating all their tools into a single list it can offer to the model — this is exactly the situation in *this* session: the assistant you're talking to connects to a GitHub MCP server alongside other tools.

**Transports:**

- **stdio** — the client launches the server as a subprocess and communicates over stdin/stdout. Simple, local-only, no networking — good for development and locally-run servers.
- **HTTP / SSE** — the server runs as a network service the client connects to remotely. Needed for shared/hosted servers, but brings normal network-service concerns (auth, availability — Module 07).

🧑‍💻 **Engineer view:** For local development and learning, stdio is the simplest transport — [`examples/01_simple_mcp_server.py`](examples/01_simple_mcp_server.py) and [`examples/02_mcp_client_with_claude.py`](examples/02_mcp_client_with_claude.py) use it.

---

## 3. MCP tools vs. inline tool definitions (Module 03)

Both ultimately produce the same thing the Anthropic API needs: a list of `{"name", "description", "input_schema"}` tool definitions, and a way to execute a named tool with arguments.

| | Inline tools (Module 03) | MCP server tools |
|---|---|---|
| Where defined | In your application code | In a separate MCP server process |
| Who can reuse them | Only this codebase | Any MCP-compatible host |
| Update cycle | Redeploy your app | Update/restart the MCP server independently |
| Adding a new tool | Edit your code | Add to the server — clients see it automatically |
| Operational surface | One service | Two services (host + server) |

🧭 **Tech lead view:** The decision isn't "MCP vs. tool use" — MCP *is* tool use, with the implementation moved behind a protocol boundary. Choose MCP when the **reuse/ownership** benefits outweigh the **extra operational surface** of running and securing another service. Module 03's bounded-agent guidance still applies on top: a narrow, well-scoped set of tools, whether inline or via MCP.

---

## 4. Building an MCP server

The `mcp` Python SDK's `FastMCP` makes a minimal server straightforward — decorate a function with `@mcp.tool()` and its signature/docstring become the tool's schema and description:

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

See [`examples/01_simple_mcp_server.py`](examples/01_simple_mcp_server.py) for a complete version with two tools.

🧑‍💻 **Engineer view:** This should look familiar — it's the same `check_order_status`-style mock tool from Module 03/10, just exposed via `@mcp.tool()` instead of a hand-written JSON schema. The MCP SDK derives the schema from the function signature and type hints, and the description from the docstring.

---

## 5. Connecting Claude to an MCP server

A host connects to an MCP server, asks it for its tool list, converts that list into the Anthropic API's `tools` shape, and runs the **same agentic loop from Module 03** — except tool execution is a call to the MCP server instead of a local Python function:

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

        # 2. Same agentic loop as Module 03, but tool execution goes via MCP:
        # response = client.messages.create(model=MODEL, tools=anthropic_tools, messages=messages)
        # ... for each tool_use block:
        # result = await session.call_tool(block.name, block.input)
```

See [`examples/02_mcp_client_with_claude.py`](examples/02_mcp_client_with_claude.py) for the full working loop.

🧭 **Tech lead view:** Steps 1-2 are the whole story. Everything from Module 03 (the loop, `stop_reason` handling, `tool_result` messages, `MAX_ITERATIONS`) is unchanged — MCP only replaces *where the tool list comes from* and *how a tool call is executed*. If your team already has a solid agentic loop, adding MCP is additive, not a rewrite.

> **Note on the Anthropic API's MCP connector:** Anthropic also offers a server-side MCP connector (a beta feature of the Messages API) that lets the API call **remote** MCP servers directly, without your code running the loop shown above. The client-side pattern shown here works with any MCP server (local or remote) and makes the loop explicit for learning purposes — check the current Anthropic API docs for the server-side connector's exact parameters if you want Anthropic's infrastructure to manage the MCP connection.

---

## 6. Security considerations

MCP servers are **tool providers your agent grants capabilities to** — the same trust questions from Module 09 apply, with an extra wrinkle: an MCP server may be operated by **someone else**.

- **Tool-access allow-lists** (Module 09) apply to MCP tools too — validate `tool_use.name` against an allow-list before calling `session.call_tool`, especially for a server you don't operate.
- **Tool descriptions are untrusted input** if the server isn't yours — a malicious MCP server could write tool descriptions designed to manipulate the model (a form of prompt injection via tool metadata, not just tool *output*).
- **Resource/data exposure** — an MCP server might expose more tools/data than a given agent should use; prefer connecting to servers (or configuring them) with the **minimum** tool set the task needs.

🧭 **Tech lead view:** "We added an MCP server" is an integration decision with the same review bar as adding any third-party dependency that can take actions on your behalf — who operates it, what can it do, and what's your allow-list/approval story (Module 09) if it's compromised or misbehaves?

---

## 7. Common failure modes

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Client can't connect to server | Wrong command/args in `StdioServerParameters`, server crashed on startup | Run the server standalone first to check for errors |
| Tool call from Claude fails silently | MCP tool name/schema mismatch, or server-side exception | Log `session.call_tool` results/errors explicitly; return structured errors (Module 03) |
| New server tool not available to the model | Tool list fetched once at startup, server added a tool after | Re-fetch `list_tools()` per session, or restart the client |
| Agent calls a tool it shouldn't | No allow-list on MCP tools, especially from a third-party server | Apply Module 09's tool-access guardrail to MCP tool names |
| "It worked locally, broke in prod" | Switched from stdio (local subprocess) to HTTP/SSE (network service) without handling network failure modes | Apply Module 07's retry/fallback thinking to the MCP connection too |

---

## Hands-on

Continue to:
- 📊 [Presentation slides](presentation/slides.md) — a workshop-ready deck covering this module
- 💻 [Code examples](examples/) — a minimal MCP server and a Claude client that connects to it
- ✏️ [Exercises](exercises/) — practice problems with starter code and solutions
