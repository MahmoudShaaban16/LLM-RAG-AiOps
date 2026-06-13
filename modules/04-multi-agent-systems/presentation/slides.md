---
marp: true
title: Multi-Agent Systems
paginate: true
---

# Multi-Agent Systems
### Module 04

Coordinating multiple LLM calls toward one task

---

## Agenda

1. When a single agent isn't enough
2. Orchestration patterns
3. Agent-to-agent communication & shared state
4. Cost and latency implications
5. Debugging multi-agent systems
6. Common failure modes

---

## 1. When a Single Agent Isn't Enough

- Task needs different "expertise" per step (research vs. write vs. review)
- Tool/instruction set too large for one agent
- Independent subtasks could run in **parallel**
- Want separation of concerns for review / human checkpoints

> Still just `client.messages.create` — more calls, more specialized prompts

---

## 2. Orchestration Patterns

**Supervisor / Worker**
- Supervisor delegates subtasks to specialized workers, synthesizes results
- Workers can run in parallel or sequentially

**Pipeline**
- Fixed sequence: research → write → review
- Simple, inspectable, but rigid

**Peer-to-peer**
- Agents talk directly, often in a loop (e.g., drafter ↔ critic)
- Most flexible, hardest to bound

---

## 2. Orchestration Patterns (diagram)

```
                ┌──────────────┐
 task ────────► │  Supervisor  │
                └──────┬───────┘
         ┌─────────────┼─────────────┐
         ▼              ▼             ▼
    Worker A        Worker B      Worker C
         │              │             │
         └──────────────┼─────────────┘
                         ▼
                  Supervisor (synthesize) ──► final answer
```

---

## 3. Agent-to-Agent Communication

- Agents are stateless — "communication" = your code passing outputs as inputs
- "Shared state" = a dict/DB row/file your orchestrator manages
- Define explicit handoff payloads (use structured outputs / tool schemas)

```python
research = call_research_agent(topic)
draft    = call_writer_agent(research)
final    = call_reviewer_agent(draft)
```

---

## 4. Cost & Latency Implications

| Pattern | API calls | Latency shape |
|---|---|---|
| Pipeline, K stages | K | Sum of K calls |
| Supervisor + M workers (parallel) | M + 2 | ≈ max(workers) + 2 |
| Supervisor + M workers (sequential) | M + 2 | Sum of all M + 2 |

**Headline:** "one request" to a user can be 3-10+ billed API calls.

---

## 5. Debugging Multi-Agent Systems

- **Error attribution**: which stage caused the bad output?
- **Compounding non-determinism**: each stage independently varies
- **Partial failures**: what if one worker fails?

**Mitigations:**
- Log full input/output per stage
- Each agent = independently testable function
- Explicit fallback behavior for missing results

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| Output ignores earlier stages | Explicit structured handoffs |
| Costs higher than expected | Pass only what's needed, not full context |
| One slow worker blocks everything | Per-call timeouts + fallback synthesis |
| Hard to trace bad output | Per-stage logging |
| Peer-to-peer loop never ends | Cap turns, require explicit "done" signal |

---

## Hands-on

- `examples/01_supervisor_worker.py` — supervisor delegates to 2 workers
- `examples/02_pipeline_of_agents.py` — research → write → review pipeline
- `exercises/` — practice problems + solutions

---

# Questions?

Next module: **Vector Databases & Embeddings** →
