# Module 04 — Multi-Agent Systems

> **Goal:** Understand when a single agent isn't enough, the common patterns for coordinating multiple LLM calls toward one task, and the cost/latency/debugging tradeoffs that come with each.

## Contents

- [1. When a single agent isn't enough](#1-when-a-single-agent-isnt-enough)
- [2. Orchestration patterns](#2-orchestration-patterns)
- [3. Agent-to-agent communication and shared state](#3-agent-to-agent-communication-and-shared-state)
- [4. Cost and latency implications](#4-cost-and-latency-implications)
- [5. Debugging multi-agent systems](#5-debugging-multi-agent-systems)
- [6. Common failure modes](#6-common-failure-modes)
- [Hands-on](#hands-on)

---

## 1. When a single agent isn't enough

Module 03 covered the agentic loop: one model, a set of tools, looping until done. That pattern scales surprisingly far — but it starts to strain in a few situations:

- **The task needs genuinely different "expertise."** A single system prompt that tries to be a researcher, a writer, *and* a fact-checker tends to do all three averagely. Separate prompts, each focused on one job, tend to do better at each job.
- **The tool/instruction set gets too large.** A single agent with 30 tools and a system prompt covering 5 unrelated workflows starts picking the wrong tool more often (Module 03, Section 3) — splitting into focused agents with fewer tools each reduces this.
- **Steps are independent and could run in parallel.** A single agentic loop is inherently sequential (one API call at a time). If two subtasks don't depend on each other, running them as separate agent calls lets you parallelize.
- **You want separation of concerns for review/control.** E.g., a "drafting" agent and a separate "review" agent whose only job is to critique the draft — easier to reason about and to insert a human checkpoint between them.

A **multi-agent system** is just multiple LLM calls — each with its own system prompt, tools, and (often) conversation history — coordinated by your application code to accomplish one overall task.

🧑‍💼 **PM view:** "Multi-agent" sounds like a big architectural leap, but it's an incremental one: you're still making `client.messages.create` calls, just more of them, with more specialized prompts, and your code passes results between them. The leap is in *coordination logic* and *cost*, not in new model capabilities.

🧑‍💻 **Engineer view:** Nothing here requires a new SDK or framework. A "supervisor" is a Python function that calls the Messages API, optionally calls it again for each "worker," and combines the results — see [`examples/01_supervisor_worker.py`](examples/01_supervisor_worker.py).

🧭 **Tech lead view:** Most production "multi-agent" systems are a single orchestrator making sequential or parallel calls to specialized prompts — not autonomous agents independently negotiating with each other. Understand and build this pattern first before reaching for more complex topologies (peer-to-peer negotiation, dynamic agent creation, etc.), which add complexity that's rarely justified.

---

## 2. Orchestration patterns

### Supervisor / worker

A **supervisor** agent receives the task, breaks it into subtasks, delegates each to a **worker** (a separate call with a specialized system prompt), and synthesizes the worker outputs into a final response.

```
                    ┌──────────────┐
   task ──────────► │  Supervisor  │
                    └──────┬───────┘
              ┌────────────┼────────────┐
              ▼            ▼             ▼
        ┌──────────┐ ┌──────────┐  ┌──────────┐
        │ Worker A │ │ Worker B │  │ Worker C │
        └────┬─────┘ └────┬─────┘  └────┬─────┘
             │            │             │
             └────────────┼─────────────┘
                           ▼
                    ┌──────────────┐
                    │  Supervisor  │ ── synthesizes ──► final answer
                    │ (final pass) │
                    └──────────────┘
```

Workers can run **in parallel** if their subtasks are independent (e.g., two unrelated research questions), or **sequentially** if one worker's output feeds another's input.

### Pipeline

A fixed sequence of agents, each transforming the output of the previous one — like a Unix pipe. E.g., **research → write → review**, where each stage is a separate call with a narrow job.

```
input ──► [Research agent] ──► [Writer agent] ──► [Reviewer agent] ──► output
```

Pipelines are simple to reason about and debug (each stage's input/output is inspectable), but rigid — there's no branching or re-planning unless you add it explicitly.

### Peer-to-peer

Agents communicate with each other directly (rather than only through a central supervisor), potentially in a loop — e.g., a "drafter" and "critic" that go back and forth until the critic is satisfied. More flexible, but much harder to bound (when does the conversation end?) and debug.

🧑‍💼 **PM view:**
- **Pipeline** — best when the steps are well-known and always happen in the same order (most "content generation" workflows).
- **Supervisor/worker** — best when the *number and nature* of subtasks varies by request (e.g., "research these N competitors" where N varies).
- **Peer-to-peer** — highest flexibility, highest risk of unpredictable cost/time; reserve for cases where the back-and-forth itself is the value (e.g., iterative critique).

🧑‍💻 **Engineer view:** All three patterns are built from the same primitive: a function that takes input, calls `client.messages.create` with a specific system prompt, and returns output. The "pattern" is just how your code wires these functions together (sequentially, fanned out then merged, or in a loop). See [`examples/01_supervisor_worker.py`](examples/01_supervisor_worker.py) and [`examples/02_pipeline_of_agents.py`](examples/02_pipeline_of_agents.py).

🧭 **Tech lead view:** Start with a **pipeline** if your workflow has a fixed shape — it's the easiest to test (each stage is a pure function you can unit test with fixed inputs) and the easiest to add a human-in-the-loop checkpoint to (pause between stages). Move to supervisor/worker when the *set of subtasks* needs to be decided at runtime. Avoid peer-to-peer loops unless you have a hard, enforced termination condition (max turns, explicit "I'm satisfied" signal) — they are the multi-agent equivalent of Module 03's "infinite loop" failure mode, with cost multiplied by the number of agents.

---

## 3. Agent-to-agent communication and shared state

Agents don't share memory — every call is stateless. "Communication" between agents is just **your code passing strings (or structured data) from one call's output into another call's input**:

```python
research_output = call_research_agent(topic)          # agent 1's output...
draft = call_writer_agent(research_output)            # ...is agent 2's input
final = call_reviewer_agent(draft)                    # ...whose output is agent 3's input
```

Two practical implications:

- **Define the "interface" between agents deliberately.** If the writer agent expects research findings as a bulleted list but the research agent returns prose, the writer has to figure out the structure itself — wasting capability and adding variance. Consider using the structured-output pattern from Module 01 (a tool schema) to get clean, parseable handoffs between agents.
- **"Shared state" is just data your orchestrator holds and passes along** — a dict, a database row, a file. There's no special "shared memory" mechanism; if Worker B needs something Worker A produced, your code is responsible for getting it there.

🧑‍💼 **PM view:** The "interface" between agents is a product decision as much as a technical one — what information must flow from the research step to the writing step? Under-specifying this is a common source of "the final output ignored the research" bugs.

🧑‍💻 **Engineer view:** Treat each agent's output schema like an API contract between services. If a downstream agent needs structured fields (not just prose), use a tool-call schema (Module 01, `04_structured_output.py`) to force the upstream agent to produce them.

🧭 **Tech lead view:** As the number of agents grows, so does the temptation to pass "everything" between them (full conversation histories, all intermediate results) "just in case." Resist this — it multiplies token usage at every stage. Define minimal, explicit handoff payloads per stage.

---

## 4. Cost and latency implications

Every additional agent call is **another full Messages API call** — with its own input tokens (system prompt + its input), output tokens, and latency.

| Pattern | API calls for one task | Latency shape |
|---|---|---|
| Single agent (Module 03), N tool-loop steps | N | Sequential — total latency ≈ sum of N calls |
| Pipeline, K stages | K | Sequential — total latency ≈ sum of K calls |
| Supervisor/worker, M workers run in parallel | 1 (supervisor plan) + M (workers, parallel) + 1 (synthesis) = M + 2 | ≈ max(worker latencies) + 2 sequential calls — much better than sequential if M is large |
| Supervisor/worker, M workers run sequentially | M + 2 | Sequential — total latency ≈ sum of all M + 2 calls |

The headline number to communicate: **a multi-agent task that "feels like one request" to a user might be 3-10+ API calls under the hood**, each separately billed.

🧑‍💼 **PM view:** Multi-agent systems can *reduce* latency (via parallelism) compared to one agent doing everything sequentially — but they virtually always *increase total token cost*, because system prompts and context are duplicated across calls, and synthesis/review steps add their own calls. Budget and communicate both numbers, not just one.

🧑‍💻 **Engineer view:** Run independent worker calls concurrently (e.g., `asyncio.gather` with an async client, or a thread pool) — this is where multi-agent systems can actually be *faster* than a single long agentic loop, not just more expensive.

🧭 **Tech lead view:** Track cost and latency **per stage**, not just per request — when a multi-agent pipeline gets slow or expensive, you need to know which stage (and which model tier) is responsible. This is also where model-tier mixing pays off most: e.g., a cheap model for a "triage" or "research" worker, a stronger model only for final synthesis or review.

---

## 5. Debugging multi-agent systems

Debugging gets harder as you add agents, for a few concrete reasons:

- **Error attribution.** If the final output is wrong, which stage caused it — research found the wrong facts, or the writer misrepresented correct research, or the reviewer missed an error? You need visibility into *each stage's* input and output, not just the final result.
- **Non-determinism compounds.** Each agent call is independently non-deterministic; a 3-stage pipeline has more combined "paths" through the system than a single call.
- **Partial failures.** What happens if Worker B fails (API error, timeout, refused to answer) but Workers A and C succeeded? Does the supervisor proceed without B's input, retry, or fail the whole task?

Practical mitigations:

- **Log every stage's full input and output** (system prompt, messages, response) — not just the final answer. This is the single highest-value debugging investment for multi-agent systems.
- **Make each stage independently testable.** Because each agent is "just a function" (input → `client.messages.create` → output), you can unit-test each one with fixed inputs, independent of the others.
- **Design explicit fallback behavior for partial failures** — e.g., the supervisor's synthesis step should handle "Worker B's result is missing" gracefully, the same way Module 03 covered handling a failing tool.

🧑‍💼 **PM view:** "The agent gave a wrong answer" is rarely actionable for a multi-agent system — ask "which stage" and "what did that stage receive as input." Per-stage logging turns vague bug reports into specific, fixable ones.

🧭 **Tech lead view:** Apply the same engineering discipline as any distributed system: structured logging/tracing per stage, clear timeout and retry policies per call, and dashboards on per-stage latency/cost/error-rate. A multi-agent pipeline is an internal microservice architecture where each "service" happens to be an LLM call.

---

## 6. Common failure modes

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Final output ignores earlier stages' work | Handoff payload between agents is missing/unclear, or buried in a huge context | Define explicit, structured handoff payloads (Section 3); use tool schemas for structured handoffs |
| Costs much higher than expected | Each stage re-includes large shared context (e.g., full documents) in its own prompt | Pass only what each stage needs; summarize large context before handoff |
| One slow/failed worker blocks the whole task | No timeout or fallback for individual worker calls | Add per-call timeouts; design supervisor synthesis to handle missing worker results |
| Hard to tell which stage caused a bad output | No per-stage logging, only final output is inspected | Log full input/output per stage (Section 5) |
| Peer-to-peer "conversation" between agents never terminates | No explicit termination condition | Cap total turns; require an explicit "done" signal from one agent (structured output) |
| Supervisor's plan doesn't match what workers can actually do | Worker capabilities/prompts not reflected in supervisor's instructions | Keep supervisor's view of "what each worker can do" in sync with worker system prompts — treat as an API contract |

---

## Hands-on

Continue to:
- 📊 [Presentation slides](presentation/slides.md) — a workshop-ready deck covering this module
- 💻 [Code examples](examples/) — a supervisor/worker example and a sequential pipeline of specialized agents
- ✏️ [Exercises](exercises/) — practice problems with starter code and solutions

This module builds directly on [Module 03 — AI Agents](../03-ai-agents/README.md) — the agentic loop from Module 03 can itself be one "worker" or one "stage" in the patterns covered here.
