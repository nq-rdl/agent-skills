SQL Review — Artifact Contract (as produced by ``analyse``)
===========================================================

**Load this reference when:** writing or updating the ``.sqlreview/`` artifacts
for a SQL file.

This describes the outputs ``analyse`` **produces**. They are consumed downstream
by the suite's **explain** step, so this is a contract: ``explain`` reads exactly
the shape described here. Conform to it. The ``.sqlreview/`` folder itself is
created by the **setup** step; if it is absent, create the ``reviews/<sql-slug>/``
path you need and tell the user to run **setup** for the full project config.

Folder layout
-------------

The review workspace lives at the repo root::

   .sqlreview/
   ├── config.<ext>                 # created by setup (analyse does not own it)
   └── reviews/
       └── <sql-slug>/
           ├── review.md            # human-readable review doc
           └── review.json          # structured review (the machine contract)

``<sql-slug>`` is derived from the SQL file's path so a SQL file maps to exactly
one review directory. Use the same slug on re-run so a review is updated in place
rather than duplicated.

``review.md``
-------------

The human-readable review for the analyst. ``analyse`` writes it; ``explain``
reads it for the *wording* presented to the analyst. Structure it around the
cohort + data-element template (see ``definitions.rst``):

- **Cohort** — the population and its inclusion/exclusion criteria, each tied to
  the code that encodes it.
- **Data elements** — what is requested for the cohort, and where each is joined.
- **Assumptions** — decision points made by the RDL (see ``definitions.rst``),
  each pointing at the code that embodies it.
- **Limitations** — known boundaries/caveats (provisional definition; see #105).

``review.json`` — the machine contract
---------------------------------------

Structured form of the review. Write these fields so ``explain`` can read them:

.. code-block:: json

   {
     "sql_path": "models/revenue.sql",
     "baseline_ref": "<git commit SHA this review was performed against>",
     "assumptions": [
       { "id": "a1", "text": "...", "code_ref": "lines 10-14 / cte: net_rev" }
     ],
     "limitations": [
       { "id": "l1", "text": "...", "code_ref": "..." }
     ],
     "mappings": [
       { "code_ref": "...", "assumption_ids": ["a1"], "limitation_ids": [] }
     ],
     "generated_by": "sql-review-analyse",
     "generated_at": "<ISO-8601 timestamp>"
   }

Field notes
~~~~~~~~~~~

- **sql_path** — the SQL file this review describes.
- **baseline_ref** — the git commit the review was performed against. Record the
  SQL file's current HEAD commit at analysis time; **explain** uses it as the
  diff baseline (``git diff <baseline_ref>..HEAD -- <sql_path>``) in resume mode.
- **assumptions / limitations** — give each a stable ``id`` and, wherever
  possible, a ``code_ref`` pointing at the SQL region it attaches to. The
  cohort's inclusion/exclusion criteria and the data-element joins are the
  richest source of these.
- **mappings** — optional explicit code-region → assumption/limitation links.
  Emit them when the section-by-section structure is clear; ``explain`` drives
  its walkthrough from them when present.
- Keep ``review.md`` and ``review.json`` consistent: every assumption/limitation
  in the JSON should appear in the markdown narrative and vice versa.
