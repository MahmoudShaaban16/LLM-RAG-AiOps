# Module 04 — Exercises

Complete these after reading the module README and reviewing the examples.
Solutions are in [`solutions/`](solutions/) — try each exercise yourself first.

> **Not coding this module?** [`pm_track.md`](pm_track.md) covers the same
> decisions (orchestration pattern choice, agent handoff design, and
> cost/latency tradeoffs) as a written exercise — no code required.

## Exercise 1: Add a third worker to the supervisor

**File:** [`exercise_01_add_worker.py`](exercise_01_add_worker.py)

The starter code is a trimmed-down version of
[`examples/01_supervisor_worker.py`](../examples/01_supervisor_worker.py) with
only the "pros" worker.

1. Add a second worker, `run_risks_worker`, with its own system prompt
   (an analyst who argues against the proposed change).
2. Add a third worker, `run_cost_worker`, whose system prompt focuses
   specifically on rough cost/effort considerations (engineering time,
   ongoing operational cost, etc.).
3. Update `run_supervisor` to accept and synthesize all three workers'
   outputs into one recommendation.

**Think about:** As you add more workers, the supervisor's synthesis prompt
has to summarize more input. At what point would you worry about the
synthesis call itself running into context or cost issues?

---

## Exercise 2: Make the pipeline stages structured

**File:** [`exercise_02_structured_handoff.py`](exercise_02_structured_handoff.py)

The starter code is a 2-stage pipeline (research → writer) where the
research agent returns free-text bullet points, which the writer agent then
has to parse informally from prose.

1. Change the research agent to return **structured output** using a tool
   schema (following the pattern from Module 01's
   `examples/04_structured_output.py`): a JSON object with a `key_points`
   array of strings and a `recommended_tone` field (`"technical"` or
   `"accessible"`).
2. Update the writer agent's prompt to take this structured data as input
   (e.g., format the `key_points` list explicitly, and use
   `recommended_tone` to adjust its system prompt or instructions).
3. Run the pipeline and compare the writer's output to what you'd get from
   passing raw free text.

**Think about:** What's the tradeoff of adding a tool-call step to the
research agent (an extra constraint on its output) versus just trusting it
to format bullet points consistently in free text?

---

## Exercise 3: Handle a failed worker in the supervisor pattern

**File:** [`exercise_03_failed_worker.py`](exercise_03_failed_worker.py)

The starter code calls two workers and a supervisor synthesis step. The
`run_risks_worker` function in the starter code is rigged to simulate a
failure (it raises an exception) some of the time.

1. Wrap each worker call in error handling so that if a worker fails, the
   supervisor still runs — but its prompt is told that one worker's input is
   unavailable, and it should produce a recommendation based on what *is*
   available (and note what's missing).
2. Run the script multiple times and confirm it produces a sensible result
   both when both workers succeed and when `run_risks_worker` fails.
3. **Bonus:** Add a simple retry (one retry attempt) for a failed worker
   before falling back to "unavailable."

**Think about:** In Module 03, a failing tool returned a `tool_result` with
`is_error: True` so the *same* agent could see and react to the failure.
Here, the failure happens in a separate call entirely — how does the
supervisor "find out" about it, and what design choices affect how
gracefully it can respond?
