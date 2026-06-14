# Module 02 — PM Track Exercise (No Coding Required)

This exercise covers the same decisions as the coding exercises — chunking
strategy, retrieval-quality triage, and basic vs. advanced RAG — using a
written scenario instead of Python. Useful if you want to apply the module's
concepts without running any code.

## Scenario

Your company is building an internal "Ask HR" assistant on top of its HR
policy wiki, which includes:

- A 60-page "Employee Handbook" PDF (sections on leave, benefits, expenses,
  code of conduct, etc.)
- ~30 short FAQ pages, each answering one specific question (e.g., "How do I
  submit a parental leave request?")
- A spreadsheet of country-specific holiday calendars, one row per
  country/year

Employees will ask natural-language questions like "How many sick days do I
get?", "What's the per-diem for travel to Germany?", and "Is March 17, 2027 a
holiday in our Dublin office?"

Early testing shows the assistant sometimes gives confidently wrong answers —
e.g., citing the wrong number of sick days, or saying "I don't see holiday
information" even though the spreadsheet has it.

## Your task

Work through the following, writing your answers in a few sentences or a
short table each:

1. **Diagnosing the bug.** Per Section 4 of the README, "bad answer" bugs in
   RAG are usually retrieval bugs, not model bugs. For each of the two
   symptoms above (wrong sick-day number, "I don't see holiday information"),
   what's the *first* thing you'd check before assuming the model itself is
   the problem?

2. **Chunking strategy.** The three sources (handbook PDF, FAQ pages, holiday
   spreadsheet) have very different structures. For each, recommend a
   chunking approach from Section 3 (fixed-size, sentence/paragraph-aware, or
   document-aware/structural) and explain why. Pay particular attention to
   the holiday spreadsheet — what would naive fixed-size chunking likely do
   to it?

3. **Vocabulary mismatch.** An employee asks "What's the per-diem for travel
   to Germany?" but the handbook section is titled "International Travel
   Expense Allowances" and never uses the word "per-diem." Using Section 5,
   which advanced RAG pattern(s) would help here, and why?

4. **Basic vs. advanced RAG — prioritization.** Given a limited budget to
   improve this assistant, would you start with hybrid search, re-ranking, or
   query rewriting? Justify your choice using the "fixes / extra cost"
   framing from Section 5, and connect it back to the specific symptoms
   described in the scenario.

5. **Staleness.** The holiday calendar spreadsheet gets updated every January
   with the new year's dates. What's the operational risk if the RAG index
   isn't part of the update process, and what would you ask engineering to
   set up to avoid it (Section 6)?

## Discussion guide

<details>
<summary>Click to expand a sample answer (compare after writing your own)</summary>

1. For the wrong sick-day number: first check what chunk(s) were actually
   retrieved for that query — is the chunk that contains the correct sick-day
   policy even in the top-k, or did the model answer from a chunk about a
   *different* leave type (e.g., parental leave) that happens to mention a
   number? For "I don't see holiday information": check whether the holiday
   spreadsheet was ingested/indexed at all, and if so, whether the relevant
   row (e.g., "Dublin, 2027") was retrieved for that query — it's possible the
   spreadsheet was chunked in a way that separated the country name from its
   dates.

2. The **handbook PDF** is well-suited to document-aware/structural chunking
   — split on its existing headings/sections (e.g., "Sick Leave," "Parental
   Leave") so each chunk corresponds to one policy topic. The **FAQ pages**
   are naturally already small, self-contained units — each FAQ entry (question
   + answer) is essentially one chunk, so minimal further splitting is needed
   (sentence/paragraph-aware at most). The **holiday spreadsheet** is the
   trickiest: naive fixed-size chunking (splitting by characters) would likely
   cut across rows and separate a country name from its dates, or merge
   multiple unrelated countries/years into one chunk. A structural approach —
   one chunk per country (or per country-year), with the country name
   repeated in each chunk's text — would let a query like "Is March 17, 2027 a
   holiday in Dublin?" retrieve the right row.

3. This is a classic **vocabulary mismatch**, which Section 5 says hybrid
   search and query rewriting both help with. Hybrid search alone may not
   help much here since "per-diem" doesn't appear in either document — this
   is really a *semantic* gap, not a keyword gap. **Query rewriting** is the
   better fit: an LLM call could recognize that "per-diem for travel to
   Germany" is asking about the same concept as "International Travel Expense
   Allowances" and rewrite/expand the query accordingly before retrieval, or
   embeddings (semantic search) may already capture this similarity if the
   embedding model is good — but query rewriting adds a safety net for
   cases where it doesn't.

4. Given the two specific symptoms, **re-ranking** is a strong first step:
   it directly addresses "the right chunk exists but ranks just below the k
   cutoff" — likely what's happening with the sick-day policy if a more
   specific chunk is being out-ranked by a more generic one. Re-ranking is
   also relatively cheap to add (one extra model call over already-retrieved
   candidates) and doesn't require restructuring the index. Hybrid search and
   query rewriting are good *next* steps, especially for the per-diem-style
   vocabulary mismatches, but re-ranking has the most direct line to the
   reported symptoms and is the cheapest of the three to bolt onto an
   existing pipeline.

5. If the index isn't refreshed when the spreadsheet updates, the assistant
   will confidently cite **last year's holiday dates** as current — a subtle,
   high-impact staleness bug because employees have no way to know the
   answer is outdated. The fix (Section 6): set up re-indexing triggered by
   changes to the source spreadsheet (event-driven, e.g., on file save/commit,
   or a scheduled nightly re-index given how infrequently this particular
   source changes), and treat "last indexed at" as a piece of metadata that
   could even be surfaced to the user ("holiday information current as of
   [date]") for transparency.

</details>
