SQL Review — Shared Definitions
===============================

**Load this reference when:** cross-referencing SQL code against its review
artifacts, or whenever you need to say what an "assumption" or a "limitation"
is in the SQL Review workflow.

These definitions are the **canonical, cross-suite source of truth** for the
whole SQL Review suite (``setup``, ``bootstrap``, ``analyse``, ``explain``).
Reference them — do not redefine them per skill, and do not improvise your own
wording during a walkthrough. They stay the single place these terms are
defined.

.. note::

   These are **initial, working definitions** — deliberately usable now and
   meant to be refined later, not frozen. Governance is in progress: the
   ``Assumption`` definition is being standardised for the Service Desk in
   issue #105, and ``Limitation`` is expected to be locked in alongside it.
   When that governance lands, update *this file* and the rest of the suite
   follows. Until then, use the wording below as-is; do not invent a stricter
   or looser meaning during a walkthrough. If a precise ruling is needed, ask
   the human or defer to the governance issue.

Assumption
----------

A **decision point made by the RDL**: a choice taken during the SQL work in the
absence of — or in place of — an explicit requirement. Assumptions are the
things that, if wrong, would make the SQL answer the wrong question even though
it runs correctly. An assumption *could have gone another way* — that is what
makes it reviewable.

When explaining, tie each documented assumption to the specific code that
embodies it (a filter, a join, a default, a date boundary, a dedup rule) so the
analyst can judge whether the decision still holds.

Limitation
----------

A **known boundary on what the SQL can be trusted to do** that holds *even when
every assumption is correct and the query runs exactly as intended*. A
limitation is not a choice the RDL made and could revisit; it is a constraint
imposed from outside the SQL — by the available data, the source systems, or
the method — that the analyst must keep in mind when interpreting the result.

Typical limitations:

- **Coverage** — facts the query cannot include because the data doesn't exist
  or doesn't reach back far enough (missing history, late-arriving records,
  sources not yet onboarded).
- **Scope** — edge cases or populations deliberately left out of the query.
- **Fidelity** — accuracy, timeliness, or grain constraints inherited from the
  source (a daily snapshot can't answer intraday questions; a rounded or
  derived field can't be more precise than its input).

The line to hold: an **assumption** is a decision that might be *wrong*; a
**limitation** is a constraint that is simply *true* and bounds how far the
result can be trusted. When explaining, tie each documented limitation to the
code or data it stems from, and make clear what conclusions it rules out.
