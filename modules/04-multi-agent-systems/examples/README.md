# Module 04 — Examples

Runnable scripts demonstrating multi-agent orchestration patterns from the module README.

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
| [`01_supervisor_worker.py`](01_supervisor_worker.py) | A supervisor agent that delegates two sub-tasks to specialized "worker" calls and synthesizes their outputs into a final answer |
| [`02_pipeline_of_agents.py`](02_pipeline_of_agents.py) | A sequential pipeline — research agent → writer agent → reviewer agent — where each stage's output becomes the next stage's input |

Run any script directly:

```bash
python 01_supervisor_worker.py
```
