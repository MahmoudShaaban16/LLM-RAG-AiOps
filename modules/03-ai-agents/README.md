# Module 03 — AI Agents

> **Goal:** Understand what turns a single LLM call into an "agent" — tool use plus a loop — and learn to design tools, choose planning patterns, and decide when an agent is (and isn't) the right architecture.

## Contents

- [1. From a single call to an agent](#1-from-a-single-call-to-an-agent)
- [2. The agentic loop](#2-the-agentic-loop)
- [3. Designing tools](#3-designing-tools)
- [4. Planning patterns: ReAct and plan-and-execute](#4-planning-patterns-react-and-plan-and-execute)
- [5. Should I build an agent?](#5-should-i-build-an-agent)
- [6. Common failure modes](#6-common-failure-modes)
- [Hands-on](#hands-on)

---

## 1. From a single call to an agent

In Module 01, every example was a **single round trip**: send a prompt, get a response, done. The model could only act on what it already knew from training plus whatever text you put in the prompt.

An **agent** is a system where the model can:

1. **Use tools** — call functions you define (look up data, run code, query an API, write a file) to extend what it can do beyond generating text.
2. **Loop** — see the result of a tool call, decide what to do next (call another tool, or give a final answer), and repeat until the task is done.

```
Single LLM call:   prompt → model → response                         (done)

Agent:             prompt → model → tool call → your code runs the tool
                      ↑                              │
                      └──────── result fed back ─────┘
                   ... repeats until model stops calling tools ...
```

Nothing about the *model* changes — it's the same Messages API, the same `client.messages.create`. What changes is that **your code runs a loop**, executing whatever tools the model asks for and feeding results back in as new messages.

🧑‍💼 **PM view:** An agent is not a different product — it's the same model, given access to actions (tools) and allowed to take more than one step per request. The value comes from the model being able to gather information or take actions it didn't have at prompt time, rather than you having to anticipate everything up front.

🧑‍💻 **Engineer view:** "Tool use" in the Anthropic API means: you pass a `tools` list (each with a `name`, `description`, and JSON Schema `input_schema`) in `client.messages.create`. If the model decides a tool is useful, it returns a `tool_use` content block instead of (or alongside) text. You execute that tool in your own code, then send the result back as a `tool_result` content block in the next message.

🧭 **Tech lead view:** The "loop" is just application code — a `while` loop that keeps calling the API until `stop_reason != "tool_use"`. There's no hidden magic or separate "agent service" required to get started; the SDK's tool-running helpers are conveniences over this same pattern.

---

## 2. The agentic loop

The core loop, step by step:

1. **You** send the conversation so far, plus the list of available `tools`.
2. **The model** responds. Its `stop_reason` tells you what happened:
   - `"end_turn"` — the model gave a final text answer. Loop ends.
   - `"tool_use"` — the model wants to call one or more tools.
3. If `tool_use`, **your code** executes the requested tool(s) with the arguments the model provided (`block.input`), and builds `tool_result` content blocks with the output.
4. **You** append the model's tool-call message *and* your tool-result message to the conversation, and go back to step 1.

```python
messages = [{"role": "user", "content": "What's 23 * 47, and is the result prime?"}]

while True:
    response = client.messages.create(
        model=MODEL, max_tokens=1024, tools=TOOLS, messages=messages
    )
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason != "tool_use":
        break  # model gave a final answer

    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = run_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(result),
            })
    messages.append({"role": "user", "content": tool_results})
```

Each iteration is a full API call — that's the key cost/latency implication: **an N-step agent task makes N API calls**, each re-sending the growing conversation history.

🧑‍💼 **PM view:** Because the number of loop iterations isn't fixed, both cost and latency for an "agent task" are *ranges*, not constants. Two requests that look identical to a user can take 1 step or 10, depending on what the model decides it needs to do.

🧑‍💻 **Engineer view:** Always cap the loop with a `max_iterations` (or similar) guard. A model that keeps calling tools without converging will otherwise loop indefinitely, burning tokens. See [`examples/02_agentic_loop.py`](examples/02_agentic_loop.py) and [exercise 3](exercises/).

🧭 **Tech lead view:** The full message history (including every tool call and result) is re-sent on every iteration — this is what makes context-window management (Module 01, Section 3) and cost monitoring especially important for agents. Long-running agents need a strategy for summarizing or pruning history.

---

## 3. Designing tools

A tool is defined with three things, and the model relies entirely on them to decide *whether* and *how* to call it — it never sees your implementation:

```python
{
    "name": "get_weather",
    "description": "Get the current weather for a given city. Returns temperature in Celsius and a short condition description.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. 'Tokyo'"},
            "units": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "Temperature units"},
        },
        "required": ["city"],
    },
}
```

Guidelines that make tools reliable in practice:

- **Name like a function, not a sentence.** `get_weather`, `search_knowledge_base`, `create_ticket` — verbs that describe an action.
- **Describe *when* to use it, not just what it does.** "Use this when the user asks about current weather conditions" helps the model pick the right tool among several.
- **Keep schemas tight.** Use `enum` for fixed choices, mark required fields, and avoid deeply nested optional structures the model has to guess at.
- **Return useful errors, not just failures.** If a tool fails, return a `tool_result` describing *why* (e.g., `"error: city not found"`) so the model can recover — retry, ask the user, or try a different approach — rather than crashing the loop.
- **One tool, one responsibility.** A `search_knowledge_base` tool and a `send_email` tool are easy for the model to choose between; a single `do_anything` tool is not.

🧑‍💼 **PM view:** Tool descriptions are product copy aimed at the model. Vague descriptions cause the model to pick the wrong tool, call it with bad arguments, or not use it at all — this shows up as "the agent didn't do what I asked," and the fix is usually rewriting the tool description, not the user-facing prompt.

🧑‍💻 **Engineer view:** Treat `input_schema` like an API contract — validate the model's input on your side too (types, ranges, enums). The model is usually accurate but not infallible, especially with complex schemas.

🧭 **Tech lead view:** Tool design is the highest-leverage place to invest in agent reliability. Before reaching for bigger models or longer prompts, audit: are tool names unambiguous? Do descriptions disambiguate overlapping tools? Are error messages actionable? This consistently moves the needle more than prompt tuning.

---

## 4. Planning patterns: ReAct and plan-and-execute

Two common patterns for how an agent approaches a multi-step task:

### ReAct (Reason + Act)

The model interleaves **reasoning** ("I need to find X, so I'll call tool Y") with **acting** (calling the tool), one step at a time, adjusting its plan based on each result. This is exactly the loop in Section 2 — it's the default behavior when you give a model tools and let it iterate.

- **Strength:** adapts as it learns new information (a tool result might change what it does next).
- **Weakness:** can be inefficient — the model re-reasons from scratch each step, and may take a winding path.

### Plan-and-execute

The model first produces an explicit **plan** (a list of steps), and then either:
- executes each step in sequence (optionally re-planning if a step fails or reveals new information), or
- hands steps off to sub-agents (Module 04).

- **Strength:** more predictable, easier to show progress to a user ("step 2 of 5"), easier to parallelize independent steps.
- **Weakness:** the upfront plan may be wrong if early steps reveal the task is different than expected — needs a re-planning mechanism.

🧑‍💼 **PM view:** ReAct is "figure it out as you go" — good for open-ended tasks where you can't predict the steps. Plan-and-execute is "show your homework first" — good when you want visibility/approval of the plan before the agent acts (useful for higher-stakes actions).

🧭 **Tech lead view:** Most production agents use ReAct for the inner loop (Section 2) but can be nudged toward plan-and-execute behavior via the system prompt ("first, list the steps you'll take; then execute them one at a time"). True plan-and-execute architectures usually emerge once you split planning and execution across multiple agent calls — see Module 04.

---

## 5. Should I build an agent?

Agents add real cost: more API calls, higher latency, harder testing (non-deterministic step counts), and new failure modes (infinite loops, wrong tool calls, runaway costs). Before reaching for an agent, weigh four factors:

| Criterion | Question | Favors an agent when... |
|---|---|---|
| **Complexity** | Can the task be done in one (or a fixed few) LLM call(s)? | The steps needed *depend on intermediate results* and can't be predetermined |
| **Value** | Is the task valuable enough to justify variable cost/latency? | The task is high-value enough that "it might take 1 or 10 steps" is acceptable |
| **Viability** | Do reliable tools exist for the actions the agent needs? | You can give the model well-scoped, well-tested tools — not vague or risky ones |
| **Cost of error** | What happens if the agent does the wrong thing? | Errors are cheap/reversible, or there's a human checkpoint before high-stakes actions |

If a fixed sequence of steps (a traditional script, or a single well-crafted prompt with structured output) gets the job done — use that. It's cheaper, faster, and far easier to test.

🧑‍💼 **PM view:** "Add an agent" is not a feature, it's an architecture decision with ongoing cost and reliability implications. Ask: what does this agent do that a deterministic workflow + one or two LLM calls couldn't?

🧭 **Tech lead view:** A useful middle ground is a **bounded agent**: a small, fixed set of tools, a low `max_iterations`, and a narrow task. This captures most of the adaptability benefit of agents while keeping cost and failure modes manageable — start here before building open-ended agents.

---

## 6. Common failure modes

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Agent loops forever (or hits max iterations every time) | Tool results don't give the model enough to determine it's "done"; ambiguous task | Add a clear termination condition to the system prompt; cap `max_iterations` and handle the cap gracefully |
| Model calls the wrong tool | Overlapping/vague tool descriptions | Make descriptions mutually exclusive; add "use this when..." / "do not use this for..." guidance |
| Model calls a tool with invalid arguments | Schema too loose, or task underspecified | Tighten `input_schema` (enums, required fields); validate and return a descriptive error so the model can retry |
| One failed tool call derails the whole task | No error-handling path — tool result is a raw exception/traceback | Catch errors in your tool runner and return a structured `"error: ..."` result the model can reason about |
| Costs spike unexpectedly | Long agent runs re-send growing history every step | Set `max_iterations`; monitor `usage` per step; consider summarizing history for long runs |
| Agent takes a "weird" path to the right answer | ReAct re-reasons from scratch each step | Consider plan-and-execute for tasks where the path matters (e.g., for auditability) |

---

## Hands-on

Continue to:
- 📊 [Presentation slides](presentation/slides.md) — a workshop-ready deck covering this module
- 💻 [Code examples](examples/) — a single tool call, then a full manual agentic loop with multiple tools
- ✏️ [Exercises](exercises/) — practice problems with starter code and solutions

Next module: [Module 04 — Multi-Agent Systems](../04-multi-agent-systems/README.md), which builds on this loop to coordinate multiple agents.
