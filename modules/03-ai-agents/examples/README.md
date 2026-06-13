# Module 03 — Examples

Runnable scripts demonstrating tool use and the agentic loop from the module README.

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
| [`01_simple_tool_use.py`](01_simple_tool_use.py) | A single tool definition, `tool_choice`, and one full round trip: model calls a tool, you return the result, model responds |
| [`02_agentic_loop.py`](02_agentic_loop.py) | A manual agentic loop with two tools (`calculate` and `search_knowledge_base`) that runs until the model stops calling tools, printing each step |

Run any script directly:

```bash
python 01_simple_tool_use.py
```
