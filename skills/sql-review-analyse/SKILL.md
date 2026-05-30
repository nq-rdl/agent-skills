---
name: sql-review-analyse
license: CC-BY-4.0
description: >-
  Analyse a finished SQL file at handoff and produce its templated review
  artifacts — a human-readable `review.md` and a structured `review.json` under
  `.sqlreview/` — capturing the cohort, data elements, assumptions, and
  limitations. Use when SQL is ready to hand back to an analyst and needs a
  standardised review written, or when updating a prior review after the SQL
  changed. Triggers on requests to analyse, review, or write up a SQL file's
  assumptions and limitations, even if `.sqlreview/` isn't named. Pauses for
  human-in-the-loop sign-off on every assumption and limitation, asks the Data
  Engineer to clarify the cohort/data-element structure when it's unclear, and
  resumes a prior review via git diff with an indirect-consequence check on the
  unchanged code. The analyse step of the SQL Review suite (after setup,
  bootstrap; before explain).
argument-hint: "Path to the SQL file to review (e.g. models/revenue.sql)"
user-invocable: true
metadata:
  repo: https://github.com/nq-rdl/agent-skills
---

# SQL Review — Analyse

Read a finished SQL file and **produce its templated review** for an analyst: a
human-readable `review.md` and a structured `review.json` under `.sqlreview/`.
This is the handoff step — the Data Engineer (DE) runs it when the SQL is ready,
and the artifacts it writes are what the analyst later reads via `explain`.

The review is built around the suite's template: a **cohort** (inclusion/
exclusion criteria) with **data elements** joined to it, plus the **assumptions**
and **limitations** the code embodies. Every assumption and limitation gets
**direct human sign-off** before the artifacts are written.

This is the analyse step of the SQL Review suite: `setup` → `bootstrap` →
*[engineer writes SQL]* → **`analyse`** → `explain`.

---

## Shared definitions

`Assumption`, `Limitation`, `Cohort`, and `Data element` mean specific things
across the whole suite. Read `references/definitions.rst` before you analyse, and
use those exact meanings — do not improvise your own.

The suite assumes every SQL file under review follows one **template structure**:
a **cohort** (defined by inclusion and exclusion criteria) with one or more **data
elements** joined onto it — e.g. a defined patient population, then "all their
eGFR results". Analyse the code against that template and anchor each assumption
and limitation to whichever part it attaches to.

## What `analyse` writes

The review artifacts live under `.sqlreview/` and are consumed downstream by
`explain`. The folder layout, the `review.md` sections, and the `review.json`
machine contract are documented in `references/artifact-contract.rst`. **Load
that reference when writing or updating artifacts** and conform to it exactly —
`explain` reads the shape it describes.

---

## Step 1 — Locate and confirm the inputs

1. Resolve the **SQL file** under review (from the argument, or ask).
2. Confirm the `.sqlreview/` workspace exists. If it doesn't, you can create the
   `reviews/<sql-slug>/` path you need, but tell the user to run the suite's
   **setup** step for the full project config.
3. **Confirm the cohort + data-element structure (DE clarification — required).**
   Check that the SQL decomposes into a **cohort** (inclusion/exclusion criteria)
   with **data elements** joined to it (see `references/definitions.rst`). If it
   does not — no identifiable cohort, missing or implicit inclusion/exclusion
   criteria, or it is unclear which columns are data elements versus
   cohort-defining logic — **stop and ask the Data Engineer** via
   `AskUserQuestion`: what is the intended cohort (its inclusion and exclusion
   criteria), and which data elements are requested against it. `analyse` owns
   this clarification for the whole suite. Do not guess; resume only once the
   structure is clear, and record the clarified structure in the review.

## Step 2 — Choose the mode: fresh vs. resume

Check for an existing review for this SQL file (`review.json` → `baseline_ref`).

- **No prior review** → **fresh analysis** (Step 3).
- **A prior review exists and the SQL has changed since its `baseline_ref`** →
  **resume / diff analysis** (Step 4).

If unsure which applies, ask the DE whether this is a first review or an update.

## Step 3 — Fresh analysis

Read the SQL in **logical sections** (CTEs, the final SELECT, joins, filters,
window functions). Working against the template:

1. **Identify the cohort.** Pin down the inclusion and exclusion criteria and the
   exact code that encodes each.
2. **Identify the data elements** joined to the cohort and where each is attached.
3. **Draft assumptions and limitations.** For each, write the text and a
   `code_ref` to the SQL region it attaches to, using the shared definitions.
   Anchor them to the cohort/data-element structure.

## Step 4 — Resume / diff analysis

When updating a prior review:

1. Compute the delta: `git diff <baseline_ref>..HEAD -- <sql_file>`.
2. **Walk the DE through what changed**, and revise the affected assumptions and
   limitations accordingly.
3. **Check the non-diff code for indirect consequences (required).** Changes
   rarely stay local. Deliberately inspect the *unchanged* SQL for knock-on
   effects of the change, e.g.:
   - a renamed/added/dropped column or CTE consumed by untouched downstream code;
   - altered join keys, filters, or grain that change the cohort or the meaning
     of rows selected elsewhere;
   - an existing assumption or limitation the change quietly invalidates even
     though that section of code wasn't edited.
   Surface anything you find and fold it into the revised review.

If `git` history or the baseline isn't available, say so and fall back to a fresh
analysis (Step 3) rather than guessing the delta.

## Step 5 — Human-in-the-loop sign-off (required)

Before writing anything, **review every assumption and every limitation with the
human, one at a time.** This is the gate, not a formality: for each, use
`AskUserQuestion` to confirm, reword, or drop it. Do not write the artifacts
until the human has signed off on the full set. Capture any new assumptions or
limitations the human raises during this pass.

## Step 6 — Write the artifacts

Write `review.md` and `review.json` under `.sqlreview/reviews/<sql-slug>/`,
conforming to `references/artifact-contract.rst`:

- `review.md` — the narrative, structured as Cohort / Data elements / Assumptions
  / Limitations.
- `review.json` — the machine contract: `sql_path`, `baseline_ref` (the SQL
  file's current HEAD commit), the signed-off `assumptions` and `limitations`
  (each with `id` and `code_ref`), optional `mappings`, `generated_by`,
  `generated_at`.

Keep the two consistent — every assumption/limitation appears in both. On a
resume, update in place under the same slug rather than creating a duplicate.

## Step 7 — Close out

Summarise what was written and where, the recorded `baseline_ref`, and any open
questions. Point the analyst to the `explain` step to walk the code against these
artifacts.

---

## Principles

- **Human-in-the-loop on every assumption and limitation.** They are the
  deliverable and must be signed off directly — never write them unreviewed.
- **Clarify, don't guess.** When the cohort/data-element structure is unclear,
  ask the DE; `analyse` owns that clarification for the suite.
- **Conform to the contract.** `explain` reads what you write; match
  `artifact-contract.rst` exactly and keep `review.md` and `review.json`
  consistent.
- **Use the shared definitions.** Reference `definitions.rst`; do not invent your
  own meanings for assumption, limitation, cohort, or data element.
