SQL Review — Shared Definitions
===============================

**Load this reference when:** cross-referencing SQL code against its review
artifacts, or whenever you need to say what an "assumption" is in the SQL
Review workflow.

This definition is the **canonical, cross-suite source of truth** for the
whole SQL Review suite (``setup``, ``bootstrap``, ``analyse``, ``explain``).
Reference it — do not redefine it per skill, and do not improvise your own
wording during a walkthrough. This file stays the single place the term is
defined.

.. note::

   This is an **initial, working definition** — deliberately usable now and
   meant to be refined later, not frozen. Governance is in progress: the
   ``Assumption`` definition is being standardised for the Service Desk in
   issue #105. When that governance lands, update *this file* and the rest of
   the suite follows. Until then, use the wording below as-is; do not invent a
   stricter or looser meaning during a walkthrough. If a precise ruling is
   needed, ask the human or defer to the governance issue.

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
