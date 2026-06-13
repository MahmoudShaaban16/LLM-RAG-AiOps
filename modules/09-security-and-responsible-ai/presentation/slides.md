---
marp: true
title: Security & Responsible AI
paginate: true
---

# Security & Responsible AI
### Module 09

A practical introduction for PMs, engineers, and tech leads

---

## Agenda

1. Prompt injection
2. Data privacy
3. Guardrails
4. Responsible AI considerations
5. Governance
6. Common failure modes

---

## 1. Prompt Injection

- Untrusted content (documents, tool results, web pages) can contain text the model treats as **instructions**
- Everything in the context window is just text — the model has no built-in "this part is data" signal
- **RAG and agents are especially exposed**: retrieved docs and tool results are attacker-reachable surfaces

> The "SQL injection" of LLM apps

---

## Prompt Injection — Mitigations

| Mitigation | What it does |
|---|---|
| Delimit untrusted content | XML tags + "treat as data, not instructions" |
| Privilege separation | Don't grant tools the task doesn't need |
| Treat tool results as untrusted | Same delimiting for fetched/tool content |
| Least-privilege tool design | Narrow, structured tools — not `run_sql` |
| Human-in-the-loop | Approval gate for risky actions |

**No prompting trick fully solves this** — the real boundary is *what the model is allowed to do*.

---

## 2. Data Privacy

- Every API call sends the **full context** — system prompt, history, retrieved docs, tool I/O — to the provider
- Check your provider's **retention policy** (training use, abuse monitoring, zero-data-retention agreements)
- **PII handling**: redact before it enters the prompt; re-insert real values client-side if needed
- Logging is part of your data footprint too

**PM takeaway:** "Can we send this data to the model?" is a legal/compliance question — answer it before designing the feature.

---

## 3. Guardrails

- **Input filtering** — sanitize before the model sees it
- **Output filtering** — check before the user/system sees it
- **Tool-access allow-lists** — validate every `tool_use` call before executing
- **Human-in-the-loop** — required approval for destructive/high-impact actions (delete, send, refund)

> The model's response is a **proposal**. Your code decides what actually runs.

---

## 4. Responsible AI

- **Bias** — evaluate outputs across groups/inputs for consequential decisions
- **Transparency** — disclose AI involvement in decisions that affect people
- **Appropriate use** — define out-of-scope topics explicitly; LLM supports, doesn't replace, authoritative sources for deterministic tasks

**Tech lead takeaway:** Out-of-scope behavior is testable — add it to your Module 06 eval set.

---

## 5. Governance

- **Prompt/model approval** — system prompts are config that affects security & behavior; review like code
- **Model version pinning** — upgrades are changes requiring re-evaluation
- **Audit trails** — what did the model see, output, do, and who approved it
- **Incident response** — detect, roll back, assess impact

---

## 6. Common Failure Modes

| Symptom | Mitigation |
|---|---|
| Model reveals system prompt | Delimit untrusted content + explicit instructions |
| Agent takes a destructive action | Tool allow-list + human approval gate |
| PII in logs / sent to provider | Redaction pipeline + logging review |
| Confident out-of-scope answers | Explicit scope boundaries + eval coverage |
| Can't reconstruct an incident | Structured audit trail from day one |
| Prompt change ships without review | Treat prompts as reviewed artifacts |

---

## Hands-on

- `examples/01_prompt_injection_demo.py`
- `examples/02_tool_access_guardrails.py`
- `exercises/` — guardrail design + injection-risk review

---

# Questions?

Next module: **Production Capstone** →
