# Module 09 — Security & Responsible AI

> Status: 🚧 Planned — structure below shows what this module will contain.

## What you'll learn

- Prompt injection: what it is, why RAG and agents are especially exposed, and mitigations
- Data privacy: what gets sent to the model, retention policies, PII handling
- Guardrails: input/output filtering, allow-lists for tool use, human-in-the-loop for risky actions
- Responsible AI considerations: bias, transparency, appropriate use cases
- Governance: who approves prompts/models for production, audit trails

🧑‍💼 **PM view:** Prompt injection is the "SQL injection" of LLM apps — any system that lets an LLM read untrusted content (web pages, emails, documents) and then take action needs a threat model for it.

🧭 **Tech lead view:** The highest-leverage mitigation is often architectural: limit what tools an agent can call and what data it can access, rather than relying solely on prompting the model to "be careful."

## Planned contents

```
modules/09-security-and-responsible-ai/
├── README.md
├── presentation/slides.md
├── examples/
│   ├── 01_prompt_injection_demo.py
│   └── 02_tool_access_guardrails.py
└── exercises/
```
