SQL Review — Artifact Contract (as consumed by ``explain``)
===========================================================

**Load this reference when:** locating or parsing the ``.sqlreview/`` artifacts
for a SQL file.

This describes the inputs ``explain`` **expects** to read. The artifacts
themselves are produced by the suite's **analyse** step and the folder is
created by the **setup** step; this file documents the shape ``explain`` relies
on so those steps have a target to conform to. Until they are built, **discover what
is actually on disk and degrade gracefully** — never fabricate review content.

Folder layout
-------------

The review workspace lives at the repo root::

   .sqlreview/
   ├── config.<ext>                 # created by setup (not required by explain)
   └── reviews/
       └── <sql-slug>/
           ├── review.md            # human-readable review doc
           └── review.json          # structured review (the machine contract)

``<sql-slug>`` is derived from the SQL file's path so a SQL file maps to exactly
one review directory. If the on-disk layout differs, discover the review doc +
JSON that correspond to the target SQL file and proceed; surface the mismatch to
the human rather than failing silently.

``review.md``
-------------

The human-readable review for the analyst, including the **Assumptions**
section (see ``definitions.rst``). ``explain`` reads this to cross-reference
code against the documented narrative. Treat it as the source of the *wording*
presented to the analyst.

``review.json`` — the machine contract
---------------------------------------

Structured form of the review. ``explain`` reads these fields:

.. code-block:: json

   {
     "sql_path": "models/revenue.sql",
     "baseline_ref": "<git commit SHA the review was performed against>",
     "assumptions": [
       { "id": "a1", "text": "...", "code_ref": "lines 10-14 / cte: net_rev" }
     ],
     "mappings": [
       { "code_ref": "...", "assumption_ids": ["a1"] }
     ],
     "generated_by": "sql-review-analyse",
     "generated_at": "<ISO-8601 timestamp>"
   }

Field notes
~~~~~~~~~~~

- **sql_path** — the SQL file this review describes; match it to the target.
- **baseline_ref** — the git commit the review was performed against. This is
  the **diff baseline** for resume mode: ``git diff <baseline_ref>..HEAD --
  <sql_path>``. If absent or not a valid ref, fall back to a full walkthrough.
- **assumptions** — the documented decision points, ideally each with a
  ``code_ref`` pointing at the SQL region it attaches to.
- **mappings** — optional explicit code-region → assumption links. When
  present, drive the section-by-section walkthrough from these. When absent,
  derive the mapping yourself from the ``code_ref`` fields and the SQL.

Graceful degradation
---------------------

- **No ``.sqlreview/``** → tell the user to run the **setup** step, then the
  **analyse** step; stop.
- **Folder present, no review for this SQL** → tell the user to run the
  **analyse** step; stop.
- **``review.json`` missing but ``review.md`` present** → proceed from the
  markdown alone; you lose ``baseline_ref`` (so default to a full walkthrough)
  and explicit mappings.
- **Missing individual fields** → use what's present, name what's missing, and
  never invent assumptions or mappings that the artifacts don't contain.
