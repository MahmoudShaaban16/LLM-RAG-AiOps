# Module 04 — Multi-Agent Systems

> Status: 🚧 Planned — structure below shows what this module will contain.

## What you'll learn

- When a single agent isn't enough: specialization, parallelism, separation of concerns
- Orchestration patterns: supervisor/worker, pipeline, peer-to-peer
- Agent-to-agent communication and shared state/memory
- Cost and latency implications of multi-agent systems (multiple LLM calls per task)
- Debugging and observability challenges unique to multi-agent systems

🧑‍💼 **PM view:** Multi-agent systems multiply both capability *and* cost/latency/complexity. Treat "let's add another agent" as an architectural decision with a cost, not a free upgrade.

🧭 **Tech lead view:** Most production "multi-agent" systems are actually a single orchestrator agent calling specialized sub-agents as tools — understand this pattern before reaching for more complex topologies.

## Planned contents

```
modules/04-multi-agent-systems/
├── README.md
├── presentation/slides.md
├── examples/
│   ├── 01_supervisor_worker.py
│   └── 02_pipeline_of_agents.py
└── exercises/
```

Builds on [Module 03 — AI Agents](../03-ai-agents/README.md).
