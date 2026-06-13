# Module 03 — AI Agents

> Status: 🚧 Planned — structure below shows what this module will contain.

## What you'll learn

- What makes an "agent" different from a single LLM call: tool use + a loop
- The agentic loop: model decides → calls a tool → observes result → repeats until done
- Designing tools (function definitions) the model can call reliably
- Planning patterns: ReAct, plan-and-execute
- When an agent is the right tool — and when a simpler workflow is better (see Module 01's "Should I Build an Agent?" criteria)

🧑‍💼 **PM view:** Agents trade predictability for flexibility. They're powerful for open-ended tasks but harder to test and estimate cost/latency for, since the number of steps isn't fixed in advance.

🧭 **Tech lead view:** Agent reliability depends heavily on tool design — clear names, descriptions, and schemas reduce incorrect tool calls more than prompt tweaks do.

## Planned contents

```
modules/03-ai-agents/
├── README.md
├── presentation/slides.md
├── examples/
│   ├── 01_simple_tool_use.py        # Single tool call
│   ├── 02_agentic_loop.py           # Manual agent loop with multiple tools
│   └── 03_tool_runner.py            # Using the SDK's tool runner
└── exercises/
```
