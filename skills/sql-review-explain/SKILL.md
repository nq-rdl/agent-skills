---
name: sql-review-explain
license: CC-BY-4.0
description: >-
  Walk a Data Analyst through a SQL file against its review artifacts as an
  interactive, in-session explanation — no new file is produced. Use when
  someone needs SQL explained against its review doc(s) and JSON, wants to see
  how the code maps to the documented assumptions and limitations, or is
  picking up a prior review and asks "what changed?". Triggers on requests to
  explain, walk through, or talk through SQL alongside its `.sqlreview/`
  artifacts, even if the folder isn't named. Resumes a previous explanation via
  git diff and double-checks unchanged code for indirect consequences. Final
  step of the SQL Review suite (after setup, bootstrap, analyse).
argument-hint: "Path to the SQL file to explain (e.g. models/revenue.sql)"
user-invocable: true
metadata:
  repo: https://github.com/nq-rdl/agent-skills
---

# SQL Review — Explain

Interactive, human-in-the-loop walkthrough of a SQL file **against its review
artifacts**, for a Data Analyst. You read the code and the review doc(s)/JSON
the `analyse` step produced, then explain the SQL section by section — showing
how each part maps to the documented **assumptions** and **limitations**.

**This step produces no new artifact.** It is a conversation: explain, pause,
confirm, move on. The value is the analyst leaving with a confident,
cross-referenced understanding of the code — not another document.

This is the final step of the SQL Review suite: `setup` → `bootstrap` →
*[engineer writes SQL]* → `analyse` → **`explain`**.

---

## Shared definitions

`Assumption` and `Limitation` mean specific things across the whole suite. Read
`references/definitions.rst` before you start cross-referencing, and use those
exact meanings — do not improvise your own.

## What `explain` reads

The review artifacts live under `.sqlreview/` and are produced by `analyse`.
The expected layout and JSON shape are documented in
`references/artifact-contract.rst`. **Load that reference when locating or
parsing artifacts**, and treat it as the contract: discover what is actually on
disk, degrade gracefully when fields are missing, and never invent content the
artifacts don't contain.

---

## Step 1 — Locate and confirm the inputs

1. Resolve the **SQL file** under review (from the argument, or ask).
2. Find the matching `.sqlreview/` artifacts for that SQL file (review doc
   markdown + structured JSON). See `references/artifact-contract.rst`.
3. If `.sqlreview/` or the artifacts for this SQL file are missing, stop and
   tell the user to run `/sql-review:analyse` (and `/sql-review:setup` if the
   folder itself is absent) first. `explain` does not generate review content.
4. **Confirm with the human** the resolved set before starting: which SQL file,
   which review doc, which JSON. Don't begin the walkthrough until they agree.

## Step 2 — Choose the mode: full vs. resume

Read the JSON's recorded review baseline (the `baseline_ref` commit the review
was performed against — see the contract).

- **No usable baseline, or first time through** → **full walkthrough** (Step 3).
- **A baseline exists and the SQL has changed since** → **resume / diff
  walkthrough** (Step 4).

If unsure which applies, ask the human whether this is a fresh walkthrough or a
pick-up of a prior review.

## Step 3 — Full walkthrough

Step through the SQL in **logical sections** (CTEs, the final SELECT, joins,
filters, window functions — whatever the code's natural units are). For each
section:

1. **Explain what it does** in plain language — inputs, transformation, output.
2. **Cross-reference the review doc.** Point to the documented assumptions and
   limitations that apply to this section, and show how the code reflects (or
   appears to diverge from) them. This mapping is the core deliverable.
3. **Pause for the human (human-in-the-loop).** At each key point — especially
   where an assumption or limitation attaches, or where the code's behaviour is
   non-obvious — stop and ask the analyst to confirm understanding or raise a
   question before continuing. Use `AskUserQuestion` for explicit confirm/clarify
   forks. Do not dump the whole file at once.

Move through the file at the human's pace. If they flag a mismatch between code
and the documented assumptions/limitations, capture it in the conversation and
suggest it be fed back to `analyse` — do not silently "fix" the artifacts here.

## Step 4 — Resume / diff walkthrough

When picking up a prior review:

1. Compute the delta: `git diff <baseline_ref>..HEAD -- <sql_file>` (and the
   review artifacts, if they moved too).
2. **Walk the human through what changed** — each hunk, in plain language, and
   how it maps back to the review doc's assumptions and limitations. Pause for
   confirmation as in Step 3.
3. **Check the non-diff code for indirect consequences (required).** Changes
   rarely stay local. After the diff walkthrough, deliberately inspect the
   *unchanged* SQL for knock-on effects of the change, e.g.:
   - a renamed/added/dropped column or CTE consumed by untouched downstream code;
   - altered join keys, filters, or grain that change the meaning of rows
     selected elsewhere;
   - an assumption or limitation in the review doc that the change quietly
     invalidates even though that section of code wasn't edited.
   Surface anything you find and confirm it with the human.

If `git` history or the baseline isn't available, say so and fall back to a full
walkthrough (Step 3) rather than guessing the delta.

## Step 5 — Close out

Summarise what was confirmed and any open questions the analyst raised. State
explicitly that no artifact was produced, and point follow-up work (mismatches,
new assumptions/limitations) back to `/sql-review:analyse`.

---

## Principles

- **Human-in-the-loop, always.** Explanation points are checkpoints, not a
  monologue. Pause and confirm.
- **Cross-reference, don't reinvent.** Map code to the *documented* assumptions
  and limitations using the shared definitions. If the doc and code disagree,
  report it; don't paper over it.
- **Read-only.** `explain` neither writes review artifacts nor edits the SQL.
- **Degrade gracefully.** Missing fields or artifacts → say what's missing and
  proceed with what's there; never fabricate review content.
