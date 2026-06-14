# Module 12 — Examples

Runnable scripts demonstrating an MCP server and a Claude client that connects to it.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## Scripts

| Script | Demonstrates |
|---|---|
| [`01_simple_mcp_server.py`](01_simple_mcp_server.py) | A minimal `FastMCP` server exposing `get_order_status` and `search_knowledge_base` tools over stdio |
| [`02_mcp_client_with_claude.py`](02_mcp_client_with_claude.py) | Launches the server as a subprocess, discovers its tools, converts them to the Anthropic API's tool shape, and runs the Module 03 agentic loop with tool execution via `session.call_tool` |

Run the client directly - it launches the server itself:

```bash
python 02_mcp_client_with_claude.py
```

You can also run the server standalone to confirm it starts without errors (it will wait for stdio input):

```bash
python 01_simple_mcp_server.py
```
