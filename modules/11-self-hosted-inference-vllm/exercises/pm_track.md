# Module 11 — PM Track Exercise (No Coding Required)

This exercise covers the same decisions as the coding exercises — API vs.
self-hosted, breakeven volume, and the module's decision framework — using a
written scenario instead of Python. Useful if you want to apply the module's
concepts without running any code.

## Scenario

Your company has shipped an AI feature that classifies incoming support
emails into one of six categories (billing, technical, account access,
feature request, complaint, other) before routing them to the right team.
It currently calls the Anthropic API for every email — roughly 40,000 emails
per month, each a short classification call (around 300 input tokens, 10
output tokens).

An infrastructure engineer proposes self-hosting an open-weight model with
vLLM to handle this classification task instead, on a GPU the company would
provision and run continuously. They estimate the GPU would cost about
$1.50/hour ($1,080/month if run 24/7).

Leadership wants to know whether this is worth pursuing before any
engineering work begins.

## Your task

Work through the following, writing your answers in a few sentences or a
short table each:

1. **Cost shape.** Describe, in plain terms, how the *cost shape* differs
   between the current approach (Anthropic API, pay-per-token) and the
   proposed approach (self-hosted GPU, fixed monthly cost). At roughly
   40,000 short classification calls/month, does this volume sound closer to
   "clearly worth it," "clearly not worth it," or "depends on the details"?
   What additional numbers would you need to be sure?

2. **Quality ceiling.** The module notes that self-hosted open-weight models
   generally sit below frontier hosted models for hard reasoning tasks, but
   email classification into 6 fixed categories is a relatively simple task.
   What would you want to see *before* approving this migration, and which
   module's tooling would you use to check it?

3. **Decision framework.** Using the module's 5-question decision framework
   (volume/steadiness, data residency, model-quality-sufficiency, ML infra
   expertise, latency tolerance), walk through this scenario question by
   question. For each, say whether the answer favors self-hosting,
   the API, or "need more information," and why.

4. **Operational risk.** If this migration goes ahead, what new failure mode
   does the company take on that it didn't have with the API? What would you
   want in place (rollback plan, monitoring, fallback) before cutting over
   production email traffic to the self-hosted model?

5. **Recommendation.** Based on your answers above, what would you recommend
   to leadership: proceed, proceed with a pilot/eval first, or don't pursue
   this right now? Justify in 2-3 sentences.

## Discussion guide

<details>
<summary>Click to expand a sample answer (compare after writing your own)</summary>

1. The API cost scales with usage — 40,000 short calls/month at typical
   per-token pricing for a small classification prompt is likely well under
   $1,080/month (a few hundred dollars at most, since each call is only ~310
   tokens total). The self-hosted GPU costs roughly $1,080/month *regardless*
   of whether it processes 1 email or 1 million. At 40,000 emails/month, this
   sounds closer to "clearly not worth it on cost alone" — but you'd want the
   actual current API bill for this feature, and whether the GPU could also
   be shared across *other* workloads (which would change the math
   considerably, since an idle GPU running one small task is wasteful).

2. Before approving, you'd want to see an eval comparing the candidate
   open-weight model's classification accuracy against the current model's
   accuracy on a representative sample of real emails — using Module 06's
   eval/regression-testing tooling (an LLM-as-judge or, better, a labeled
   dataset with ground-truth categories, since this is a classification task
   with a clear right answer). A drop in accuracy means more misrouted
   emails, which has a real downstream cost (manual re-routing, unhappy
   customers).

3. **Volume/steadiness:** 40,000/month is steady but not especially high for
   a single small task — *leans toward API* unless the GPU would serve other
   workloads too. **Data residency:** nothing in the scenario suggests a
   compliance requirement to keep email content off third-party
   infrastructure — *no strong signal either way, need more information*.
   **Model-quality-sufficiency:** plausible for a 6-category classification
   task, but unverified — *need more information (run the eval)*.
   **ML infra expertise:** not stated whether the team has GPU
   ops experience — *need more information*, and this is a real cost if not
   already in place. **Latency tolerance:** classification for routing is
   probably not latency-critical, so a self-hosted fallback delay would be
   tolerable — *mild lean toward self-hosting*, but this is the weakest
   factor here.

4. The new failure mode is: **if the GPU node goes down, the classification
   feature goes down** (or degrades to "route everything to a default
   queue"), whereas previously an API outage would be Anthropic's incident to
   manage (with the company's own fallback chain from Module 07 as backup).
   Before cutting over, you'd want: a fallback to the Anthropic API if the
   self-hosted server is unreachable (the same fallback-chain pattern from
   Module 07), monitoring/alerting on the GPU server's health and queue
   depth, and a clear rollback plan (route traffic back to the API) that
   doesn't require a code deploy.

5. **Proceed with a pilot/eval first, but be skeptical on cost grounds.**
   At this volume, the fixed GPU cost likely exceeds the current API spend
   for this single feature, so the business case only holds if (a) the GPU
   would be shared across multiple workloads to improve utilization, or (b)
   there's a non-cost driver (e.g., a data-residency requirement) not
   captured in the scenario. Either way, run the Module 06 eval gate before
   committing any infrastructure spend — a quality regression would make the
   migration a net loss even if the cost math worked out.

</details>
