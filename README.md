# LLM & AI Engineering Hub

A practical, hands-on curriculum for understanding and building with Large Language Models (LLMs) — written for **project managers**, **software engineers**, and **tech leaders** who need to go from "what is this?" to "how do we build/ship/operate this?"

This repo blends two styles inspired by the community:

- **Explanations & presentations** — clear, audience-aware breakdowns of concepts (inspired by [ai-engineering-hub](https://github.com/patchy631/ai-engineering-hub))
- **Runnable code samples & exercises** — practical, minimal, working examples (inspired by [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps))

## How the Repo Is Organized

Each module lives under `modules/` and follows the same four-part structure:

```
modules/NN-topic-name/
├── README.md           # Explanation: concepts, audience-tiered breakdowns, diagrams
├── presentation/        # Slide deck (Markdown/Marp) for team talks or workshops
├── examples/             # Runnable Python code samples
└── exercises/            # Practice problems + starter code + solutions
```

### Audience tiers

Throughout the explanations, look for these callouts:

- 🧑‍💼 **PM view** — what this means for scope, cost, timelines, and risk
- 🧑‍💻 **Engineer view** — how it works and how to implement it
- 🧭 **Tech lead view** — architectural tradeoffs, when to use it, when not to

## Modules

| # | Module | Status | Summary |
|---|--------|--------|---------|
| 01 | [LLM Fundamentals & Prompting](modules/01-llm-fundamentals-and-prompting/README.md) | ✅ Complete | How LLMs work, tokens & context windows, prompt engineering basics |
| 02 | [RAG Systems](modules/02-rag-systems/README.md) | 🚧 Planned | Retrieval-augmented generation, chunking, embeddings pipelines |
| 03 | [AI Agents](modules/03-ai-agents/README.md) | 🚧 Planned | Tool use, agentic loops, planning & execution |
| 04 | [Multi-Agent Systems](modules/04-multi-agent-systems/README.md) | 🚧 Planned | Orchestration patterns, agent-to-agent communication |
| 05 | [Vector Databases & Embeddings](modules/05-vector-databases-embeddings/README.md) | 🚧 Planned | Embedding models, vector stores, similarity search |
| 06 | [LLM Evaluation & Testing](modules/06-llm-evaluation-and-testing/README.md) | 🚧 Planned | Benchmarks, LLM-as-judge, regression testing for prompts |
| 07 | [LLMOps & AIOps](modules/07-llmops-and-aiops/README.md) | 🚧 Planned | Deployment, monitoring, cost management, observability |
| 08 | [Fine-Tuning](modules/08-fine-tuning/README.md) | 🚧 Planned | When to fine-tune vs. prompt, data prep, evaluation |
| 09 | [Security & Responsible AI](modules/09-security-and-responsible-ai/README.md) | 🚧 Planned | Prompt injection, data privacy, guardrails, governance |
| 10 | [Production Capstone](modules/10-production-capstone/README.md) | 🚧 Planned | End-to-end project combining RAG + agents + evaluation + ops |

## Getting Started

Each module's `examples/` folder includes its own `requirements.txt` and a `README.md` with setup instructions. As a baseline:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r modules/01-llm-fundamentals-and-prompting/examples/requirements.txt
```

You'll need an [Anthropic API key](https://console.anthropic.com/) set as `ANTHROPIC_API_KEY` to run the examples.

## Suggested Learning Paths

- **Project Manager**: Read each module's README, focusing on the 🧑‍💼 PM view sections and the "Why it matters" / "Cost & risk" sections. Skim the presentations for talking points.
- **Software Engineer**: Read the README, run the `examples/`, then complete the `exercises/`.
- **Tech Lead**: Read the README in full, review architectural tradeoffs (🧭), and use the presentation deck to brief your team.

## Contributing

New modules should follow the same four-part structure (`README.md`, `presentation/`, `examples/`, `exercises/`). See [modules/01-llm-fundamentals-and-prompting](modules/01-llm-fundamentals-and-prompting/) as the reference template.
