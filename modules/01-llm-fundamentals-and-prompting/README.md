# Module 01 — LLM Fundamentals & Prompting

> **Goal:** Understand what an LLM actually is, how it processes text, what governs cost and capability, and how to write prompts that reliably get the output you want.

## Contents

- [1. What is a Large Language Model?](#1-what-is-a-large-language-model)
- [2. Tokens — the unit LLMs actually think in](#2-tokens--the-unit-llms-actually-think-in)
- [3. Context windows](#3-context-windows)
- [4. Choosing a model](#4-choosing-a-model)
- [5. Prompt engineering fundamentals](#5-prompt-engineering-fundamentals)
- [6. Common failure modes](#6-common-failure-modes)
- [Hands-on](#hands-on)

---

## 1. What is a Large Language Model?

An LLM is a model trained to predict the **next token** in a sequence of text, given everything that came before it. That's the entire mechanism — but at sufficient scale, "predict the next token well" turns into the ability to answer questions, write code, reason step-by-step, summarize documents, and follow instructions.

```
"The capital of France is" → [predicts] → " Paris"
```

Repeat that prediction one token at a time, feeding each new token back in as input, and you get everything from a one-word answer to a multi-page report.

🧑‍💼 **PM view:** An LLM is not a database and does not "look things up" by default — it generates plausible text based on patterns learned during training. This is why LLMs can be confidently wrong ("hallucinate"), and why retrieval-augmented generation (Module 02) exists: to ground answers in real documents.

🧑‍💻 **Engineer view:** You interact with LLMs through an API (e.g., the [Anthropic Messages API](https://docs.anthropic.com/)). You send a sequence of messages (a conversation), and the model returns the next message. Everything — system prompts, conversation history, tool definitions, tool results — is just more text in that sequence.

🧭 **Tech lead view:** Because the model is stateless between API calls, *your application* is responsible for managing conversation state, memory, and context. This has direct implications for cost (Section 3) and architecture (every call re-sends the full context).

---

## 2. Tokens — the unit LLMs actually think in

LLMs don't process characters or words directly — they process **tokens**, which are chunks of text produced by a tokenizer. A token is roughly ¾ of an English word on average, but varies:

| Text | Approx. tokens |
|---|---|
| `"Hello"` | 1 |
| `"Hello, world!"` | 4 |
| `"unbelievable"` | 2–3 (e.g., `un` + `believ` + `able`) |
| A typical English paragraph (~100 words) | ~130–150 tokens |

Why this matters:

- **Cost**: API pricing is per-token (input tokens and output tokens are priced separately, with output usually costing more).
- **Limits**: Context windows (next section) and max-output limits are measured in tokens, not words or characters.
- **Non-English text, code, and rare words** often tokenize less efficiently (more tokens per "unit of meaning"), which affects both cost and the effective context available.

🧑‍💼 **PM view:** When estimating costs for a feature, estimate in *tokens*, not "documents" or "messages." A 10-page PDF might be ~5,000–8,000 tokens. If your app re-sends that PDF as context on every turn of a conversation, costs scale with conversation length — this is a common budget surprise.

🧑‍💻 **Engineer view:** Use the `count_tokens` endpoint (or your SDK's token-counting helper) to measure actual usage before shipping, rather than estimating. See [`examples/02_token_counting.py`](examples/02_token_counting.py).

---

## 3. Context windows

The **context window** is the maximum number of tokens (input + output combined, depending on how the model accounts for it) that a model can "see" in a single request. Think of it as the model's working memory for one API call.

| Model | Context Window | Max Output Tokens |
|---|---|---|
| Claude Opus 4.8 | 1,000,000 tokens | 128,000 tokens |
| Claude Sonnet 4.6 | 1,000,000 tokens | 64,000 tokens |
| Claude Haiku 4.5 | 200,000 tokens | 64,000 tokens |

*(Figures current as of mid-2026 — always check the [Models API](https://docs.anthropic.com/) for the latest values, as these change over time.)*

What goes into the context window for a single call:
- The system prompt
- All prior conversation turns (if you're sending history)
- Any retrieved documents / tool results
- The model's own output for this turn

🧑‍💼 **PM view:** A larger context window doesn't mean "unlimited memory" — it means the model can consider more material *in one request*, at a proportional cost. Long-running agents and chat apps need an explicit strategy (summarization, truncation, retrieval) once conversations grow, regardless of window size.

🧭 **Tech lead view:** Two architectural patterns dominate:
- **Stuff everything in context** — simplest, works well up to moderate context sizes, cost grows linearly with history.
- **Retrieve only what's relevant** (RAG, Module 02) — scales to large knowledge bases, but adds retrieval-quality as a new failure mode.

---

## 4. Choosing a model

As of mid-2026, the Claude model family looks like this:

| Model | Model ID | Best for | Input $/1M tokens | Output $/1M tokens |
|---|---|---|---|---|
| Claude Opus 4.8 | `claude-opus-4-8` | Hardest reasoning, long-horizon agentic tasks, highest quality | $5.00 | $25.00 |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | Best balance of speed/intelligence/cost for most production workloads | $3.00 | $15.00 |
| Claude Haiku 4.5 | `claude-haiku-4-5` | High-volume, latency-sensitive, simpler tasks | $1.00 | $5.00 |

*(Prices are illustrative of the relative tiering and were accurate at time of writing — always confirm current pricing on [anthropic.com/pricing](https://www.anthropic.com/pricing).)*

🧑‍💼 **PM view:** A simple framework for model selection:
1. **Start with the cheapest model that could plausibly work** (Haiku-tier) for prototyping.
2. **Move up a tier** if quality isn't good enough — don't default to the most expensive model "to be safe."
3. **Mix tiers in production** — e.g., use a cheap model to classify/triage requests, and an expensive model only for the subset that needs deep reasoning.

🧭 **Tech lead view:** Model choice is not a one-time decision — wrap it in a config value, not a hardcoded string, so you can A/B test and migrate models without code changes. See [`examples/01_first_api_call.py`](examples/01_first_api_call.py) for a config-driven example.

---

## 5. Prompt engineering fundamentals

Prompting is how you steer a general-purpose model toward your specific task. A few principles that consistently improve results:

### a. Be explicit about the task, format, and constraints
Vague: *"Summarize this."*
Better: *"Summarize this support ticket in 2 sentences, written for a non-technical manager. Do not include customer PII."*

### b. Use a system prompt to set role, tone, and ground rules
The system prompt applies to the whole conversation and is the right place for persistent instructions (role, output format, things to avoid).

### c. Show, don't just tell — use examples (few-shot prompting)
If the output format is specific (e.g., a JSON schema, a particular tone), 1–3 examples of input → desired output dramatically improve consistency.

### d. Ask for structured output when you need to parse the result
If your code needs to parse the response, ask for JSON (or use [structured outputs](https://docs.anthropic.com/) / tool calling) rather than parsing free text.

### e. Give the model room to reason for hard problems
For multi-step reasoning, asking the model to work through the problem step-by-step (or using extended thinking) before giving a final answer improves accuracy on hard tasks — at the cost of more output tokens.

### f. Iterate like code, not like a one-shot wish
Treat prompts as versioned artifacts: write a test set of representative inputs, check outputs against expectations, and tune the prompt based on failures (Module 06 covers this systematically).

🧑‍💼 **PM view:** "Prompt engineering" is real engineering work — it benefits from the same rigor as code: version control, test cases, and review. Budget time for prompt iteration, not just initial integration.

---

## 6. Common failure modes

| Symptom | Likely cause | Mitigation |
|---|---|---|
| Inconsistent output format | No explicit format instructions / no examples | Add a schema, use structured outputs, add few-shot examples |
| Confidently wrong facts ("hallucination") | Model relying on training data instead of your data | Use RAG (Module 02) to ground answers in real sources |
| Response cut off mid-sentence | Hit `max_tokens` limit | Increase `max_tokens`, or ask for a more concise answer |
| Slow / expensive responses | Using a high-tier model for a simple task, or sending excessive context | Try a smaller model; trim unnecessary context |
| Model ignores part of a long prompt | Important instructions buried in a huge context | Put critical instructions in the system prompt and/or repeat key constraints near the end of the prompt |

---

## Hands-on

Continue to:
- 📊 [Presentation slides](presentation/slides.md) — a workshop-ready deck covering this module
- 💻 [Code examples](examples/) — runnable scripts demonstrating tokens, context, prompting, and structured output
- ✏️ [Exercises](exercises/) — practice problems with starter code and solutions
