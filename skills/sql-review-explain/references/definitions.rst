SQL Review — Shared Definitions
===============================

**Load this reference when:** cross-referencing SQL code against its review
artifacts, or whenever you need to say what an "assumption" or a "limitation"
is in the SQL Review workflow.

These definitions are the **canonical, cross-suite source of truth** for the
whole SQL Review suite (``setup``, ``bootstrap``, ``analyse``, ``explain``).
Reference them — do not redefine them per skill, and do not improvise your own
wording during a walkthrough. They may still evolve (the ``Limitation``
definition is being finalised in governance issue #105), but this file stays the
single place they are defined.

Assumption
----------

A **decision point made by the RDL**: a choice taken during the SQL work in the
absence of — or in place of — an explicit requirement. Assumptions are the
things that, if wrong, would make the SQL answer the wrong question even though
it runs correctly.

When explaining, tie each documented assumption to the specific code that
embodies it (a filter, a join, a default, a date boundary, a dedup rule) so the
analyst can judge whether the decision still holds.

Limitation
----------

**TBD — to be defined** (see governance issue #105). Until a formal definition
lands, treat a limitation as a **known boundary or caveat on what the SQL can be
trusted to do** — data it doesn't cover, edge cases it doesn't handle, or
accuracy/timeliness constraints — and flag in the walkthrough that the
definition is still provisional.

Do not invent a stricter definition than this; if a precise meaning is needed,
ask the human or defer to #105.
