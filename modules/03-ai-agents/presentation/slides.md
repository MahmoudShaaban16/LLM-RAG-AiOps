---
marp: true
title: AI Agents
paginate: true
---

# AI Agents
### Module 03

Tool use, the agentic loop, and when to use one

---

## Agenda

1. From a single call to an agent
2. The agentic loop
3. Designing tools
4. Planning patterns: ReAct vs. plan-and-execute
5. Should I build an agent?
6. Common failure modes

---

## 1. From a Single Call to an Agent

- Module 01: prompt → model → response (done)
- Agent: model can call **tools**, see results, and **loop**
- Same API (`client.messages.create`) — your code runs the loop

> Nothing magic — it's a `while` loop around the Messages API

---

## 2. The Agentic Loop

```
prompt → model → tool call → your code runs the tool
   ↑                              │
   └──────── result fed back ─────┘
... repeats until stop_reason != "tool_use" ...
```

- `stop_reason == "tool_use"` → execute tool(s), append `tool_result`, loop
- `stop_reason == "end_turn"` → final answer, done

**Cost/latency:** N steps = N API calls, each re-sending growing history

---

## 3. Designing Tools

```python
{
    "name": "get_weather",
    "description": "Get current weather for a city...",
    "input_schema": { "type": "object", "properties": {...}, "required": [...] }
}
```

- Name like a function (verb + object)
- Describe **when** to use it, not just what it does
- Tight schemas: enums, required fields
- Return actionable errors, not crashes

**Tool design > prompt tweaks** for agent reliability

---

## 4. Planning Patterns

**ReAct (Reason + Act)**
- Interleave reasoning and tool calls, one step at a time
- Adaptive, but can wander

**Plan-and-execute**
- Model lists steps up front, then executes (re-planning if needed)
- Predictable, auditable, parallelizable

---

## 5. Should I Build an Agent?

| Criterion | Favors an agent when... |
|---|---|
| **Complexity** | Steps depend on intermediate results |
| **Value** | High enough to justify variable cost/latency |
| **Viability** | Reliable, well-scoped tools exist |
| **Cost of error** | Errors are cheap/reversible, or human-checked |

Start with a **bounded agent**: few tools, low `max_iterations`, narrow task

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| Infinite loop | Clear termination condition + `max_iterations` |
| Wrong tool called | Sharper, mutually exclusive descriptions |
| Invalid tool arguments | Tighter schema + validation |
| One failure derails task | Structured error results |
| Cost spikes | Cap iterations, monitor `usage` |

---

## Hands-on

- `examples/01_simple_tool_use.py` — one tool, one round trip
- `examples/02_agentic_loop.py` — manual multi-step loop, 2+ tools
- `exercises/` — practice problems + solutions

---

# Questions?

Next module: **Multi-Agent Systems** →
