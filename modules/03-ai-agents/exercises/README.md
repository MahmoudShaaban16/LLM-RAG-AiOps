# Module 03 — Exercises

Complete these after reading the module README and reviewing the examples.
Solutions are in [`solutions/`](solutions/) — try each exercise yourself first.

## Exercise 1: Add a new tool to the agentic loop

**File:** [`exercise_01_add_tool.py`](exercise_01_add_tool.py)

The starter code is a trimmed-down version of
[`examples/02_agentic_loop.py`](../examples/02_agentic_loop.py) with only the
`search_knowledge_base` tool.

1. Add a new tool called `get_order_status` that takes an `order_id` string
   and returns hardcoded order status data (see the `ORDERS` dict in the
   starter file).
2. Add it to the `TOOLS` list and to `run_tool`'s dispatch logic.
3. Update the user message to ask a question that requires *both* tools
   (e.g., "What's our refund policy, and what's the status of order
   `A1003`?") and run the loop. Confirm the model calls both tools and
   produces a final answer that uses both results.

**Think about:** How did you write the tool's `description` so the model
can tell it apart from `search_knowledge_base`?

---

## Exercise 2: Handle a tool that can fail

**File:** [`exercise_02_failing_tool.py`](exercise_02_failing_tool.py)

The starter code includes a `get_order_status` tool whose implementation
raises an exception if the `order_id` isn't found in `ORDERS`.

1. Run the starter code with an order ID that doesn't exist (e.g.,
   `"Z9999"`) and observe what happens when the exception propagates out of
   `run_tool` uninstrumented.
2. Fix `run_tool` so that a failing tool call returns a `tool_result` with
   `"is_error": True` and a descriptive message (e.g.,
   `"error: no order found with id 'Z9999'"`), instead of crashing the loop.
3. Run it again and confirm the model gracefully tells the user the order
   wasn't found, rather than the script crashing.

**Think about:** What's the difference between returning an error message
as a normal string vs. setting `"is_error": True` on the `tool_result`
block? (Hint: both give the model the text, but `is_error` is a signal the
model is trained to recognize as "this attempt failed.")

---

## Exercise 3: Limit max iterations and handle the cap gracefully

**File:** [`exercise_03_max_iterations.py`](exercise_03_max_iterations.py)

The starter code runs the agentic loop with `MAX_ITERATIONS = 3` against a
task that's designed to need more steps than that (the system prompt
encourages the model to call `search_knowledge_base` once per topic, and the
user asks about 4 topics).

1. Run the starter code and observe what happens when the loop exhausts
   `MAX_ITERATIONS` while the model still wants to call tools (i.e., the
   `for...else` branch is hit).
2. Modify the loop so that, when the cap is reached, your code sends one
   final message to the model *without* any tools available (omit `tools`
   from that last call, or set `tool_choice={"type": "none"}`), asking it to
   summarize what it has found so far based on the partial results.
3. Run it again and confirm the user gets a useful partial answer instead of
   nothing.

**Think about:** In a production system, how would you decide what
`MAX_ITERATIONS` should be for a given agent? What's the tradeoff if you set
it too low vs. too high?
