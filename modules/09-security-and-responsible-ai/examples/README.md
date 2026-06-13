# Module 09 — Examples

Runnable scripts demonstrating the concepts from the module README.

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
| [`01_prompt_injection_demo.py`](01_prompt_injection_demo.py) | A prompt injection scenario via an untrusted "document," and a mitigation using delimiters + explicit system-prompt instructions |
| [`02_tool_access_guardrails.py`](02_tool_access_guardrails.py) | An agent loop where a guardrail function enforces a tool allow-list and a human-approval requirement for destructive tools, before any tool executes |

Run any script directly:

```bash
python 01_prompt_injection_demo.py
python 02_tool_access_guardrails.py
```

## A note on this content

These examples are **defensive and educational**: they illustrate the risk
of prompt injection and unrestricted tool access, and demonstrate
mitigations (delimiting untrusted content, allow-lists, human-in-the-loop
approval). They are not intended to demonstrate how to bypass model
safeguards, and the "attacks" shown are simple, illustrative examples.
