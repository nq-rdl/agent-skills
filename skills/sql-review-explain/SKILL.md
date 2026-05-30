---
name: sql-review-explain
license: CC-BY-4.0
description: >-
  Work through a SQL file with a Data Analyst to confirm the captured
  assumptions are actually borne out by the code — an interactive, in-session
  check; no new file is produced. Use when someone needs to verify that the
  documented assumptions match the SQL, see how each assumption maps to the
  code, or is picking up a prior review and asks "what changed?". Triggers on
  requests to explain, walk through, review, or check SQL against its
  `.sqlreview/` assumptions, even if the folder isn't named. Resumes a previous
  review via git diff and double-checks unchanged code for indirect
  consequences. Verification step of the SQL Review suite (after setup,
  bootstrap, analyse); a separate downstream skill later uses the confirmed
  assumptions to explain the work to the client.
argument-hint: "Path to the SQL file to explain (e.g. models/revenue.sql)"
user-invocable: true
metadata:
  repo: https://github.com/nq-rdl/agent-skills
---

# SQL Review — Explain

Interactive, human-in-the-loop walkthrough of a SQL file **against its review
artifacts**, done **together with a Data Analyst**. You read the code and the
assumptions the `analyse` step captured, then go through the SQL section by
section to **confirm each documented assumption is actually borne out by the
code** — and flag anything that isn't.

**This step produces no new artifact.** It is a working session: walk the code,
check each assumption against it, pause, confirm, move on. The value is leaving
with every captured assumption verified against the code (or its mismatch
flagged) — not another document. Explaining the confirmed assumptions to the
*client* is a separate, downstream skill; this step is about getting the
assumptions right against the code first.

This is the verification step of the SQL Review suite: `setup` → `bootstrap` →
*[engineer writes SQL]* → `analyse` → **`explain`**.

---

## Shared definitions

`Assumption` means something specific across the whole suite. Read
`references/definitions.rst` before you start cross-referencing, and use that
exact meaning — do not improvise your own.

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
   tell the user to run the suite's **analyse** step first (and the **setup**
   step if the `.sqlreview/` folder itself is absent). `explain` does not
   generate review content.
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
2. **Check it against the captured assumptions.** Point to the documented
   assumptions that apply to this section and confirm the code actually embodies
   them — or flag where the code and the assumption diverge. This verification
   is the core deliverable.
3. **Pause for the human (human-in-the-loop).** At each key point — especially
   where an assumption attaches, or where the code's behaviour is
   non-obvious — stop and ask the analyst to confirm understanding or raise a
   question before continuing. Use `AskUserQuestion` for explicit confirm/clarify
   forks. Do not dump the whole file at once.

Move through the file at the human's pace. If they flag a mismatch between code
and the documented assumptions, capture it in the conversation and
suggest it be fed back to `analyse` — do not silently "fix" the artifacts here.

## Step 4 — Resume / diff walkthrough

When picking up a prior review:

1. Compute the delta: `git diff <baseline_ref>..HEAD -- <sql_file>` (and the
   review artifacts, if they moved too).
2. **Walk the human through what changed** — each hunk, in plain language, and
   how it maps back to the review doc's assumptions. Pause for
   confirmation as in Step 3.
3. **Check the non-diff code for indirect consequences (required).** Changes
   rarely stay local. After the diff walkthrough, deliberately inspect the
   *unchanged* SQL for knock-on effects of the change, e.g.:
   - a renamed/added/dropped column or CTE consumed by untouched downstream code;
   - altered join keys, filters, or grain that change the meaning of rows
     selected elsewhere;
   - an assumption in the review doc that the change quietly invalidates even
     though that section of code wasn't edited.
   Surface anything you find and confirm it with the human.

If `git` history or the baseline isn't available, say so and fall back to a full
walkthrough (Step 3) rather than guessing the delta.

## Step 5 — Close out

Summarise which assumptions were confirmed against the code and any mismatches
or open questions raised. State explicitly that no artifact was produced, and
point follow-up work (mismatches, new or corrected assumptions) back to the
**analyse** step, which owns the review artifacts. Explaining the confirmed
assumptions to the client happens later, in a separate downstream skill.

---

## Principles

- **Human-in-the-loop, always.** Explanation points are checkpoints, not a
  monologue. Pause and confirm.
- **Cross-reference, don't reinvent.** Map code to the *documented* assumptions
  using the shared definition. If the doc and code disagree, report it; don't
  paper over it.
- **Read-only.** `explain` neither writes review artifacts nor edits the SQL.
- **Degrade gracefully.** Missing fields or artifacts → say what's missing and
  proceed with what's there; never fabricate review content.
