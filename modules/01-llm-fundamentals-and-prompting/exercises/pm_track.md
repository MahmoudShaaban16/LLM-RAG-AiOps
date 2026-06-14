# Module 01 — PM Track Exercise (No Coding Required)

This exercise covers the same decisions as the coding exercises — token/cost
estimation, model selection, and prompt design — using a written scenario
instead of Python. Useful if you want to apply the module's concepts without
running any code.

## Scenario

Your company wants to add an "Explain this invoice" feature to its billing
portal. When a customer clicks the button on an invoice, the system sends
the invoice's line items (roughly 800 words of text) plus a short system
prompt to an LLM, and shows the customer a plain-language summary of what
they're being charged for and why.

Product leadership expects this feature to be used on **40,000 invoices per
month**, and wants a rough cost estimate before committing engineering time,
plus confidence that the output will be consistent enough to show customers
without a human reviewing every response.

## Your task

Work through the following, writing your answers in a few sentences or a
short table each:

1. **Token estimation.** Using the rule of thumb that ~100 words ≈ 130–150
   tokens, estimate the input tokens for one request (system prompt +
   ~800-word invoice text — assume the system prompt adds ~100 tokens).
   Assume the output summary is about 150 words. Estimate total tokens per
   request.

2. **Cost estimation.** Using the pricing table in the module README, pick a
   model tier and calculate the estimated cost for one request, then for
   40,000 requests/month. Would you recommend Haiku, Sonnet, or Opus for this
   feature, and why?

3. **Context window check.** Is there any risk of this request exceeding a
   model's context window? Why or why not? What would change your answer if
   invoices sometimes ran to 50 pages instead of one?

4. **Prompt design.** Write a system prompt (2-4 sentences) for this feature
   that addresses: tone (customer-facing), format (e.g., bullet points vs.
   prose), and what to do if a line item is unclear or ambiguous. Use at
   least one principle from Section 5 of the README (be explicit, structured
   output, etc.) and name which principle you used.

5. **Model selection over time.** The README argues model choice shouldn't be
   a one-time, hardcoded decision. Suggest two ways this feature's
   architecture should account for that (e.g., for A/B testing a cheaper
   model, or migrating to a newer model later).

## Discussion guide

<details>
<summary>Click to expand a sample answer (compare after writing your own)</summary>

1. ~800 words ≈ 1,040–1,200 input tokens for the invoice, plus ~100 tokens
   for the system prompt → roughly **1,100–1,300 input tokens**. The ~150-word
   output summary is roughly **200–225 output tokens**. Total per request is
   roughly **1,300–1,500 tokens**.

2. Using Claude Haiku 4.5 ($1.00/1M input, $5.00/1M output): one request costs
   roughly (1,200/1,000,000 × $1.00) + (225/1,000,000 × $5.00) ≈ **$0.0024**.
   At 40,000 requests/month, that's roughly **$96/month**. With Sonnet
   ($3/$15), the same request costs roughly **$0.0072**, or about
   **$288/month**. This is a strong candidate for Haiku: the task (summarizing
   a structured invoice in plain language) is relatively simple and doesn't
   need the deepest reasoning — start cheap and only move up a tier if a
   sample of outputs aren't good enough.

3. No meaningful risk for a single ~800-word invoice — even Haiku's 200K
   context window easily fits ~1,300 tokens. If invoices could run to 50
   pages (tens of thousands of tokens), this changes the calculus: cost per
   request grows substantially, and at some size it may make more sense to
   retrieve/summarize only the relevant line items (RAG-style, Module 02)
   rather than stuffing the entire document into context every time.

4. Example system prompt: *"You are explaining a customer's invoice in plain,
   friendly language for someone with no accounting background. Respond with
   3-5 short bullet points, one per major charge category, in plain English.
   If a line item's purpose isn't clear from the data provided, say so
   explicitly rather than guessing what it might be."* This uses principle
   (a) "be explicit about task, format, and constraints" — specifying the
   exact format (3-5 bullets) and tone (plain, friendly), and principle (f)
   in spirit by explicitly handling the ambiguous case rather than letting
   the model improvise.

5. Two suggestions: (1) Store the model ID (e.g., `claude-haiku-4-5`) in a
   config value or environment variable rather than hardcoding it in the
   billing code, so it can be swapped without a code change — this also
   enables A/B testing Haiku vs. Sonnet on a subset of invoices to compare
   summary quality. (2) Build a small "eval set" of representative invoices
   with example good summaries, so that whenever a new model version is
   released, you can quickly re-run the eval set and confirm quality hasn't
   regressed before migrating production traffic.

</details>
