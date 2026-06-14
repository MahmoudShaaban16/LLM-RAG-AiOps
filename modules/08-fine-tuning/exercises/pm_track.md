# Module 08 — PM Track Exercise (No Coding Required)

This exercise covers the same decisions as the coding exercises — whether
fine-tuning is justified, what "ready" training data looks like, and how to
evaluate a fine-tuned model before shipping it — using a written scenario
instead of Python. Useful if you want to apply the module's concepts without
running any code.

## Scenario

Your company sells project-management software. Customer support agents use
an LLM assistant (built in earlier modules) to draft replies to support
tickets. The drafts are generally accurate, but support leadership has two
complaints:

- The drafts don't consistently match the company's "warm but concise" brand
  voice — some are too formal, some are too long.
- For tickets in the "billing dispute" category specifically, the assistant
  often gives generic responses instead of following the company's specific
  6-step billing dispute resolution script.

An engineer on the team has proposed: "Let's fine-tune a model on 500 of our
best past ticket responses to fix both issues."

## Your task

Work through the following, writing your answers in a few sentences or a
short table each:

1. **Apply the decision framework.** Using the framework from Section 1
   (prompting vs. RAG vs. tool use vs. fine-tuning), what would you want to
   know *before* agreeing to a fine-tuning project here? For each of the two
   complaints (brand voice, billing dispute script), is fine-tuning the right
   first tool — or is there something cheaper to try first?

2. **What fine-tuning can and can't fix.** Section 2 distinguishes "how the
   model responds" from "what it knows." Classify each of the two complaints
   against this distinction. Does either complaint risk being a *knowledge*
   problem in disguise (e.g., the billing dispute script changes periodically)
   — and if so, what does that imply about fine-tuning as a fix?

3. **Data readiness.** The engineer wants to use "500 of our best past ticket
   responses" as training data. List 3 questions you'd ask about this dataset
   before considering it "ready," based on Section 3's criteria (consistency,
   coverage, volume, quality, sensitive data).

4. **Evaluation plan.** Before this fine-tuned model could replace the current
   prompt-based assistant, what would you require the team to show you
   (Section 4)? Sketch, in plain English, what a "before vs. after" comparison
   should measure — and name one thing that could look *better* on the target
   task but should still block shipping.

5. **Ownership.** If you greenlight this project, who needs to own retraining
   when the billing dispute script changes next quarter (Section 5)? What
   happens if nobody owns that?

## Discussion guide

<details>
<summary>Click to expand a sample answer (compare after writing your own)</summary>

1. Before agreeing, ask: have we tried fixing this with a better system
   prompt and a few well-chosen examples first? For **brand voice**,
   this is a strong candidate for prompting — "warm but concise" with 2-3
   example responses in the system prompt is exactly the kind of stylistic
   guidance prompting handles well, and it's far cheaper to iterate on. For
   the **billing dispute script**, the issue might not be style at all — it
   might be that the assistant doesn't reliably *know* the 6-step script.
   That's arguably closer to a RAG or tool-use problem (retrieve the current
   script, or expose it as a structured reference) than a fine-tuning
   problem. Neither complaint clearly clears the bar of "we tried prompting
   and RAG and there's a specific, measured gap."

2. **Brand voice** is squarely a "how it responds" problem — a good fit for
   fine-tuning *in principle*, though prompting should be tried first. The
   **billing dispute script** is more likely a "what it knows / has access
   to" problem — if the assistant doesn't follow the script because it
   doesn't reliably have the script's steps in context, fine-tuning on past
   responses risks teaching the model to *mimic the style* of script-following
   answers without reliably reproducing the current script — and if the
   script changes, the fine-tuned model will quietly keep using the old one.
   This is the classic "fine-tuning for knowledge" trap from Section 2 — RAG
   (retrieving the current script) is the more durable fix.

3. Questions to ask about the 500 examples: (a) **Consistency** — were these
   500 responses written in a genuinely consistent voice, or do they span
   multiple agents/eras with different styles (inconsistent examples teach
   inconsistent behavior)? (b) **Coverage** — do they cover the range of
   ticket types and edge cases the assistant sees in production, or mostly
   "easy" tickets? (c) **Sensitive data** — do these real ticket responses
   contain customer PII (names, account numbers, emails) that would need
   redaction before being used as training data, separate from the inference-
   time data policy?

4. Require a side-by-side eval report (Module 06-style) comparing the current
   prompt-based assistant against the fine-tuned model on the *same* eval set,
   covering: (a) brand-voice match on a sample of tickets, (b) billing dispute
   script adherence, and (c) a set of "everything else" cases — categories and
   tasks *outside* the fine-tuning focus, to catch regressions. Something that
   could look better on brand voice but should still block shipping: the
   fine-tuned model performing *worse* on out-of-scope or edge-case tickets it
   used to handle fine (catastrophic forgetting) — "the target metric improved"
   is not sufficient if something else got worse.

5. Someone — likely a support-ops or content owner, not just an engineer —
   needs to own (a) updating the training data whenever the billing dispute
   script or brand guidelines change, and (b) triggering and evaluating a
   retraining run. If nobody owns this, the fine-tuned model will quietly
   drift out of sync with the actual (updated) script, and the team will be
   back to the original complaint within a quarter — except now harder to
   diagnose, because "the assistant sounds right" but is following an
   outdated process.

</details>
