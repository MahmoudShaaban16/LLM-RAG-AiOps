# Module 09 — Exercises

Complete these after reading the module README and reviewing the examples.
Solutions are in [`solutions/`](solutions/) — try each exercise yourself first.

## Exercise 1: Write a guardrail function

**File:** [`exercise_01_guardrail.py`](exercise_01_guardrail.py)

You're given a set of tools for an "inbox assistant" agent: `search_emails`,
`read_email`, `archive_email`, `send_email`, and `delete_email`.

1. Write a `check_tool_call(name, tool_input)` guardrail function (following
   the pattern in `examples/02_tool_access_guardrails.py`) that:
   - Allows `search_emails` and `read_email` to run immediately (read-only).
   - Allows `archive_email` to run immediately (low-risk, reversible).
   - Requires human approval for `send_email` and `delete_email`
     (irreversible / external side effects).
   - Blocks any tool not in the allow-list entirely.
2. Write at least 3 test calls (one for each category above) and print
   what the guardrail decides for each.

**Think about:** Why is "reversibility" a useful axis for deciding whether
something needs approval, separate from "is it destructive"?

---

## Exercise 2: Identify injection risks in a prompt template

**File:** [`exercise_02_injection_review.py`](exercise_02_injection_review.py)

You're given a system prompt template for a "meeting notes assistant" that
takes raw meeting transcript text (pasted by users, potentially from
external recording tools) and produces action items.

1. Read the provided `RISKY_SYSTEM_PROMPT` and `build_user_prompt()`.
2. List (as comments or a returned list of strings) at least 3 concrete
   ways this template is vulnerable to prompt injection via the transcript
   content.
3. Rewrite both the system prompt and `build_user_prompt()` to mitigate
   those risks, following the delimiting pattern from
   `examples/01_prompt_injection_demo.py`.

**Think about:** What's different about the risk here vs. the document
summarization example — does it matter that this content might later be
used to populate other systems (e.g., auto-creating tickets from "action
items")?

---

## Exercise 3: Design an approval flow for a risky tool

**File:** [`exercise_03_approval_flow.py`](exercise_03_approval_flow.py)

A team wants to add an `issue_refund(order_id, amount)` tool to their
support agent. Refunds up to $50 are low-risk; refunds over $50 need a
human to sign off.

1. Implement `classify_refund_request(order_id, amount)` that returns
   `"auto_approve"` or `"requires_approval"` based on the amount.
2. Implement a simple `ApprovalQueue` class with `submit(request)` and
   `list_pending()` methods that stores pending high-value refund requests
   (don't execute them).
3. Wire these together in a `handle_refund_tool_call()` function that, given
   a tool_use-style input, either executes the refund (for auto-approve) or
   adds it to the approval queue (for requires-approval) — printing what
   happened in each case.
4. Test with at least 2 refund amounts: one under $50, one over.
