---
marp: true
title: AI Use Cases & Project Management for PMs
paginate: true
---

# AI Use Cases & Project Management for PMs
### Module 13

Spotting, scoring, scoping, and shipping AI features

---

## Agenda

1. A framework for spotting AI use cases
2. Use-case catalog: patterns and where they fit
3. Scoring and prioritizing
4. Writing the one-pager / business case
5. Working with engineering: scoping
6. Defining success metrics and evals
7. Rollout, risk, and governance
8. Common PM pitfalls

---

## 1. Spotting AI Use Cases

**Good signals**
- Language in, language out (reading, drafting, classifying, extracting)
- High volume, repetitive
- Existing examples/data (past tickets, transcripts, documents)
- Tolerant of an error rate, with a human/system safety net

**Red flags**
- Needs near-100% accuracy with no review step
- Needs information the model can't access or retrieve
- It's really a data/process problem, not a language problem

> Before scoping: what happens when the model is wrong, and who reviews it?

---

## 2. Use-Case Catalog

| Use case | Pattern | Modules |
|---|---|---|
| Drafting, summarizing, classifying | Single prompt, structured output | 01 |
| Internal knowledge search | RAG | 02, 05 |
| Support assistant with actions | Agent with tools | 03, 09 |
| Multi-step workflows | Multi-agent | 04 |
| Manuals/diagrams/charts | Multimodal RAG | 02 (Ex. 4) |
| Shared tool integrations | MCP server | 12 |
| Customer-facing / financial | + guardrails, approvals | 09 |
| High-volume, narrow-domain | Fine-tune / self-host | 08, 11 |
| Anything in production | + eval, monitoring, cost | 06, 07 |

🧭 This table is also a **complexity ladder** — bottom rows are multi-quarter programs

---

## 3. Scoring and Prioritizing

Score 1-5 on three axes:
- **Impact** — value if it works
- **Feasibility** — how close to a known pattern?
- **Risk** — *inverse*: 5 = low risk (reversible, internal), 1 = high risk

`priority_score = (Impact + Feasibility + Risk) / 3`

| Tier | Profile | Action |
|---|---|---|
| Quick win | High/High/Low-risk-score-high | Scope now |
| Strategic bet | High impact, lower feasibility/risk | Phased plan + sponsorship |
| Fill-in | Moderate impact, easy, low risk | Build momentum, not urgent |
| Reconsider | Low impact, or hard+risky | Revisit later |

`examples/01_use_case_scoring.py` implements this scoring

---

## 4. The One-Pager

1. **Problem** — current process & cost
2. **Proposed approach** — which catalog pattern?
3. **Success metrics** — business + quality/safety
4. **Risks & mitigations** — what happens when it's wrong?
5. **Estimated cost** — API cost × volume + eng effort
6. **Rollout plan** — phased (see Section 7)

`examples/templates/one_pager_template.md` — fill-in-the-blanks version

---

## 5. Scoping with Engineering

Before a sprint starts, can you answer:

- **Inputs:** single prompt, RAG, or live tools?
- **Outputs:** free text or structured?
- **Tools/actions:** owner + allow/approve/block (Module 09) + inline vs. MCP (Module 12)?
- **Eval plan:** how do we know "good enough" before launch? (Module 06)
- **Ops plan:** who watches cost/latency/quality after launch? (Module 07)

🧭 Can't answer all five? That's a **spike**, not a sprint.

---

## 6. Success Metrics & Evals

| Type | Examples |
|---|---|
| Business | Deflection rate, time-to-resolution, CSAT |
| Model/quality | Eval-set accuracy, hallucination rate, override rate |
| Cost & ops | Cost/request, p95 latency, fallback rate |

Pick **one number per row** and a target — *before* launch.

---

## 7. Rollout, Risk, Governance

1. **Shadow mode** — log only, compare against metrics
2. **Human-in-the-loop** — model drafts, human sends
3. **Auto for low-risk, approval for high-risk** (Module 09)
4. **Full automation** — only for proven, low-cost-of-error actions

Each phase needs an **exit metric** that decides advance / hold / rollback

---

## 8. Common PM Pitfalls

| Symptom | Mitigation |
|---|---|
| "Is this working?" unanswerable | Pick metrics + targets before launch |
| Endless "one more accuracy fix" | Build an eval set early, agree a threshold |
| Cost spike at launch | Estimate cost upfront, monitor after |
| Bad output → major incident | Phase rollout, classify actions first |
| Scope keeps growing | Ship "quick win" tier first |
| Eng/PM disagree on "done" | Answer Section 5's five questions before the sprint |

---

## Hands-on

- `examples/01_use_case_scoring.py` — score and tier a backlog
- `examples/02_roi_estimator.py` — savings & payback estimate
- `examples/templates/one_pager_template.md` — business-case template
- `exercises/` — score a backlog, write a one-pager, set a launch gate
  (including a non-coding [PM track](../exercises/pm_track.md))

---

# Questions?

This is the final module — revisit any earlier module as you scope real projects.
