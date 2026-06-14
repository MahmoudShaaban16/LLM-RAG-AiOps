# Module 13 — AI Use Cases & Project Management for PMs

> **Goal:** Give project managers, product managers, and business stakeholders a practical framework for spotting good AI use cases, prioritizing them, writing a business case, working with engineering on scoping, defining success metrics, and managing rollout and risk — using the patterns from Modules 01-12 as the underlying toolkit.

## Contents

- [1. A framework for spotting AI use cases](#1-a-framework-for-spotting-ai-use-cases)
- [2. Use-case catalog: patterns and where they fit in this curriculum](#2-use-case-catalog-patterns-and-where-they-fit-in-this-curriculum)
- [3. Scoring and prioritizing](#3-scoring-and-prioritizing)
- [4. Writing the one-pager / business case](#4-writing-the-one-pager--business-case)
- [5. Working with engineering: scoping a project](#5-working-with-engineering-scoping-a-project)
- [6. Defining success metrics and evals](#6-defining-success-metrics-and-evals)
- [7. Rollout, risk, and governance](#7-rollout-risk-and-governance)
- [8. Common PM pitfalls](#8-common-pm-pitfalls)
- [Tools & Resources](#tools--resources)
- [Hands-on](#hands-on)

---

## 1. A framework for spotting AI use cases

Not every process is a good fit for an LLM. Before scoping anything, check
the task against these signals.

**Good signals:**

- **Language in, language out (or close to it)** — reading, summarizing,
  drafting, classifying, extracting structured data from unstructured text
- **High volume, repetitive** — the same kind of judgment call made hundreds
  or thousands of times
- **Existing examples/data** — past tickets, transcripts, documents that show
  what "good" looks like (feeds Module 02 RAG and Module 06 evals)
- **Tolerant of an error rate, with a human or system safety net** — a wrong
  draft that a human edits is fine; a wrong action with no review is not

**Red-flag signals:**

- Requires near-100% accuracy with no review step (e.g., directly debiting a
  customer's account)
- The "right answer" requires information the model can't access and that
  isn't easy to retrieve (Module 02/05) or expose as a tool (Module 03/12)
- The task is really a data/process problem (e.g., the underlying system
  doesn't track the data you'd need) — an LLM won't fix that

🧑‍💼 **PM view:** The fastest way to de-risk a proposal is to identify, up
front, what happens when the model is wrong — who reviews it, and what's the
cost of an error (Module 09's "cost of error" axis). If you can't answer that,
the use case isn't ready to scope yet.

---

## 2. Use-case catalog: patterns and where they fit in this curriculum

Most AI features map onto one of a small number of patterns. Use this table
to translate a business idea into "which modules' techniques apply."

| Use case | Pattern | Relevant modules |
|---|---|---|
| Drafting replies, summarizing calls/emails, classifying tickets | Single prompt, structured output | Module 01 |
| Internal knowledge search / "ask the docs" assistant | Retrieval-augmented generation (RAG) | Module 02, 05 |
| Support assistant that can look up orders, check statuses, take simple actions | Agent with tools | Module 03, 09 |
| Multi-step workflows split across specialists (e.g., triage → draft → review) | Multi-agent orchestration | Module 04 |
| Document/image-heavy knowledge bases (manuals, diagrams, charts) | Multimodal RAG | Module 02 (Exercise 4) |
| "Chat with our codebase / repo" developer assistant | Agent + read-only API tools | Module 03 |
| Shared tool integrations used by multiple internal agents | MCP server | Module 12 |
| Anything customer-facing or with financial/account impact | + guardrails, approval flows, injection defenses | Module 09 |
| High-volume, latency- or cost-sensitive, narrow-domain task | Fine-tuning or self-hosting evaluation | Module 08, 11 |
| Any of the above, in production | + evaluation, monitoring, cost tracking | Module 06, 07 |

🧭 **Tech lead view:** This table is also a rough **complexity ladder** — a
proposal that lands in the bottom rows (multi-agent + guardrails +
self-hosting) is a multi-quarter program, not a sprint. Most "quick win" AI
features live in the top three rows.

---

## 3. Scoring and prioritizing

Score each candidate use case on three axes, 1 (low) to 5 (high):

- **Impact** — time saved, revenue protected/generated, or risk reduced if it
  works
- **Feasibility** — how close is this to a pattern in Section 2 that's
  already well-understood? Do the data/tools/APIs needed already exist?
- **Risk** — *inverse* score: 5 = very low risk (read-only, internal,
  reversible), 1 = high risk (customer-facing, financial, irreversible)

A simple **priority score** = `(Impact + Feasibility + Risk) / 3`. Use it to
sort into tiers:

| Tier | Typical profile | What to do |
|---|---|---|
| **Quick win** | High impact, high feasibility, low risk | Scope now (Section 5) |
| **Strategic bet** | High impact, lower feasibility/risk | Needs a phased plan (Section 7) and explicit sponsorship |
| **Fill-in** | Moderate impact, high feasibility, low risk | Good for building team momentum/learning, not urgent |
| **Reconsider** | Low impact, or low feasibility *and* high risk | Don't scope yet — revisit after a quick win ships |

[`examples/01_use_case_scoring.py`](examples/01_use_case_scoring.py) implements
this scoring and tiering over a sample list of candidate use cases.

---

## 4. Writing the one-pager / business case

Before requesting engineering time, write a one-pager covering:

1. **Problem** — what's the current process, and what does it cost (time,
   money, missed opportunities)?
2. **Proposed approach** — which pattern from Section 2, in plain language
   (no architecture diagrams needed yet)
3. **Success metrics** — see Section 6; include both a business metric and a
   quality/safety metric
4. **Risks & mitigations** — what happens when it's wrong, and what's the
   review/approval story (Module 09)?
5. **Estimated cost** — rough API cost per request × expected volume (Module
   07's cost-tracking framing; Module 11 if self-hosting is on the table),
   plus engineering effort
6. **Rollout plan** — see Section 7

A fill-in-the-blanks version is at
[`examples/templates/one_pager_template.md`](examples/templates/one_pager_template.md).

---

## 5. Working with engineering: scoping a project

A one-pager becomes a scope once engineering can answer:

- **Inputs:** What does the model see — a single prompt (Module 01), a
  knowledge base needing retrieval (Module 02/05), or live data via tools
  (Module 03/12)?
- **Outputs:** Free text, or structured output the rest of the system
  consumes?
- **Tools/actions:** What can the model *do*, not just say? Each tool needs
  an owner, an allow/approve/block classification (Module 09), and (if shared
  across teams) a decision on inline vs. MCP (Module 12).
- **Eval plan:** How will "is this good enough to ship" be measured *before*
  launch (Module 06)?
- **Ops plan:** Who watches cost/latency/quality after launch, and what's the
  fallback if the model/API has an outage (Module 07)?

🧭 **Tech lead view:** A scope that can't answer all five bullets isn't ready
for a sprint — it's ready for a *spike* to answer the open questions.

---

## 6. Defining success metrics and evals

Separate **business metrics** (does this matter to the company) from **model
metrics** (is the AI component doing its job):

| Type | Examples |
|---|---|
| Business | Ticket deflection rate, time-to-resolution, CSAT, revenue per rep-hour |
| Model/quality | Accuracy vs. an eval set (Module 06), hallucination rate, escalation/override rate |
| Cost & ops | Cost per request, p95 latency, error/fallback rate (Module 07) |

Pick **one number from each row** before launch, and write down the target —
"good enough to ship" should be a number agreed in advance, not a vibe check
after the fact.

---

## 7. Rollout, risk, and governance

Phase the rollout by **how much the model can do without a human**:

1. **Shadow mode** — model runs alongside the existing process; output is
   logged but not shown to users. Compare against Section 6 metrics.
2. **Human-in-the-loop** — model drafts, a human reviews/sends. Measures
   real-world quality with a safety net.
3. **Auto for low-risk, approval for high-risk** — apply Module 09's
   allow/approve/block split per action.
4. **Full automation** — only for actions that have proven reliable *and*
   are individually low-cost-of-error.

Each phase should have an exit metric (from Section 6) that decides whether
to advance, hold, or roll back.

---

## 8. Common PM pitfalls

| Symptom | Likely cause | Mitigation |
|---|---|---|
| "Is this even working?" can't be answered after launch | No success metric defined before launch (Section 6) | Pick metrics and targets in the one-pager, before scoping |
| Project stalls in "just one more accuracy improvement" | No eval set, so "good enough" is subjective | Build an eval set early (Module 06) and agree a launch threshold |
| Launch surprises everyone with a cost spike | No cost estimate, or estimate ignored volume growth | Use Section 4's cost estimate; revisit with Module 07's monitoring post-launch |
| A single bad output becomes a major incident | Went straight to full automation on a risky action | Phase rollout (Section 7); classify actions (Module 09) before automating |
| Scope keeps growing ("while we're at it...") | Trying to cover every edge case before shipping | Ship the "quick win" tier first (Section 3); strategic bets get their own phased plan |
| Engineering and PM disagree on "done" | Scope didn't answer Section 5's five questions | Don't start the sprint until inputs/outputs/tools/eval/ops are all defined |

---

## Tools & Resources

🧑‍💼 **PM view — templates & frameworks**

| Resource | What it's for |
|---|---|
| [`examples/templates/one_pager_template.md`](examples/templates/one_pager_template.md) | Fill-in-the-blanks business case template (Section 4) |
| [`examples/01_use_case_scoring.py`](examples/01_use_case_scoring.py) | Impact/Feasibility/Risk scoring and tiering (Section 3) |
| [`examples/02_roi_estimator.py`](examples/02_roi_estimator.py) | Rough monthly savings and payback-period estimate from cost/volume assumptions |

📚 **Further reading**

- [Anthropic — Building effective agents](https://www.anthropic.com/research/building-effective-agents) — useful vocabulary when scoping with engineering (Section 5)
- [Anthropic — Claude overview & pricing](https://docs.anthropic.com/en/docs/about-claude/models/overview) — current model capabilities/pricing for cost estimates (Section 4)

🧑‍💻 **Engineer/Tech-lead view:** This module is the "front door" — once a
use case is scoped, the relevant numbered module(s) from Section 2's table
cover the implementation in depth.

---

## Hands-on

Continue to:
- 📊 [Presentation slides](presentation/slides.md) — a workshop-ready deck covering this module
- 💻 [Code examples](examples/) — use-case scoring, ROI estimation, and a one-pager template
- ✏️ [Exercises](exercises/) — score a backlog of use cases, write a one-pager, and define launch metrics (including a non-coding [PM track](exercises/pm_track.md))

This is the final module — revisit any earlier module as you scope real projects.
