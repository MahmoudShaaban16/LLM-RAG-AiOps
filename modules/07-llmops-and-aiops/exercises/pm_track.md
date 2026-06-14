# Module 07 — PM Track Exercise (No Coding Required)

This exercise covers the same decisions as the coding exercises —
fallback strategy, what to log for cost attribution, and how to respond to
quality drift — using a written scenario instead of Python. Useful if you
want to apply the module's concepts without running any code.

## Scenario

Your company has launched an AI-powered "smart reply" feature inside its
customer support email tool. When a support agent opens a ticket, the
feature drafts a suggested reply using an LLM, which the agent can edit and
send. It has been live for two months and is now handling **8,000 ticket
drafts per day**.

Leadership wants to:
- understand what the feature costs per ticket and per support team,
- make sure the feature degrades gracefully if the model provider has an
  outage,
- and put in place a way to catch it if response quality quietly gets worse
  over time.

So far, the only "monitoring" is that an engineer occasionally checks the
provider's status page.

## Your task

Work through the following, writing your answers in a few sentences or a
short table each:

1. **What to log.** Using the module's "minimal shape of what to log per LLM
   call," list the fields you'd want captured for every smart-reply
   generation, and explain how you'd use at least three of them to answer
   the question "what does this feature cost per support team per month?"

2. **Fallback strategy.** The primary model is `claude-sonnet-4-6`. Design a
   fallback chain for this feature: what happens if the primary model returns
   a `429` (rate limit), a `5xx` (server error), or times out? What should
   the support agent *see* in each case — should the feature ever be
   completely unavailable, and if so, when?

3. **Caching opportunity.** Smart replies are generated using a system prompt
   that includes the company's ~15-page support style guide and tone
   policy, plus the specific ticket's content (which is different every
   time). Would prompt caching help here? If so, how should the system
   prompt be structured to take advantage of it — and what's one mistake
   that would silently break the cache?

4. **Detecting quality drift.** Three months after launch, a support manager
   says: "agents are editing the AI drafts a lot more than they used to —
   it feels like the quality dropped." There were no code or prompt changes
   on your side in that window. Using the module's guidance on quality drift,
   describe two possible causes and what you'd set up *now* (proactively,
   not just for this incident) to catch this kind of issue earlier next
   time.

5. **Model deprecation.** The provider announces that `claude-sonnet-4-6`
   will be deprecated in 6 months, with `claude-sonnet-4-7` recommended as
   the replacement. Walk through, in order, what should happen between now
   and the deprecation date. Where does Module 06 (evaluation) fit into this
   process?

## Discussion guide

<details>
<summary>Click to expand a sample answer (compare after writing your own)</summary>

1. Key fields to log per call: `timestamp`, `model`, `feature` (here,
   `"smart_reply"`), a `team_id` or `support_team` identifier (so cost can be
   attributed per team), `input_tokens`, `output_tokens`,
   `cache_read_input_tokens` (if caching is used), `latency_ms`, and
   `estimated_cost_usd`. To answer "cost per support team per month": sum
   `estimated_cost_usd` grouped by `team_id` and month. `input_tokens` /
   `output_tokens` matter because they're the inputs to that cost
   calculation and let you spot whether cost changes are driven by *volume*
   (more tickets) vs. *per-ticket cost* (longer prompts/responses, or a model
   change). `cache_read_input_tokens` matters because if caching is working,
   a large share of input tokens should be "cheap" cache reads — tracking
   this confirms caching is actually saving money, not just configured.

2. A reasonable fallback chain: on a `429` or `5xx` or timeout from
   `claude-sonnet-4-6`, retry with exponential backoff + jitter up to a small
   limit (e.g., 2-3 attempts), and if still failing, fall back to a smaller/
   faster model tier (e.g., Haiku) to generate the draft. The agent should
   still see a draft — possibly with a subtle indicator that it was generated
   by the fallback model, since quality may be slightly lower — rather than
   no draft at all. The feature should only become "fully unavailable" (no
   draft offered, agent writes from scratch as before) if *both* the primary
   and fallback models fail — and even then, this should degrade to "the
   feature silently doesn't appear" rather than an error message that blocks
   the agent from working the ticket. The key product principle: "AI draft
   unavailable" should never mean "agent can't respond to the customer."

3. **Yes, prompt caching is a strong fit here.** The ~15-page style guide and
   tone policy is large, identical across all 8,000 daily requests, and
   doesn't change minute-to-minute — exactly the "large, stable content"
   profile the module describes. The system prompt should be structured with
   the style guide / tone policy **first**, marked with `cache_control`, and
   the ticket-specific content (which varies every request) placed **after**
   it in the user message — never inside the cached block. The mistake that
   would silently break this: including anything dynamic inside the cached
   block — e.g., a timestamp, a per-request ticket ID, or even whitespace
   differences from templating — which would make the "stable" prefix differ
   on every call, so every request looks like a fresh cache write and you get
   none of the cost/latency benefit while still paying the cache-write
   premium.

4. Two possible causes from the module's drift discussion: (a) the **model
   provider updated the underlying model** behind `claude-sonnet-4-6` (a
   "minor" version update can shift behavior on edge cases) even though the
   model ID string didn't change on your side; (b) the **distribution of
   incoming tickets shifted** — e.g., a new product launch is generating a
   wave of ticket types the style guide and prompt weren't tuned for, so the
   "same" prompt is now facing different inputs. To catch this earlier next
   time: run the Module 06 eval suite (with LLM-as-judge) on a **schedule**
   (e.g., nightly) against a fixed set of representative tickets, so a score
   drop shows up even with no code changes; and separately, sample a random
   set of *production* drafts weekly and run judge scoring on those, tracking
   the trend over time. Also track a leading indicator that's already
   available: **edit distance / how much agents change the draft before
   sending** — a rising trend in this metric is exactly the kind of
   "leading indicator" the module recommends watching alongside quality
   scores.

5. Order of operations: (1) note the deprecation date and treat it as a
   tracked dependency upgrade with a deadline; (2) confirm the model ID is
   centralized in config (not hardcoded across the codebase) so the swap is
   a one-line change; (3) **before** switching any production traffic, run
   the Module 06 eval/regression suite comparing `claude-sonnet-4-6` vs.
   `claude-sonnet-4-7` on the existing smart-reply eval dataset — this is
   where Module 06 fits in, since an "API-compatible" model swap is not
   automatically a *quality*-neutral one; (4) review per-case deltas, not
   just the average score, paying special attention to any tone/policy
   adherence cases (the equivalent of the "adversarial" cases from Module
   06); (5) if results look acceptable, roll out the new model ID gradually
   (e.g., a percentage of traffic or one support team first) while watching
   the production quality-drift monitoring from question 4; (6) once
   confirmed, complete the rollout well before the deprecation date, leaving
   buffer time in case issues are found and need to be fixed.

</details>
