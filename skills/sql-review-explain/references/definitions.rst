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

An **assumption is a decision the RDL had to make to execute the work** — and
that the client needs to be told about. A client brief is rarely complete:
where a requirement is missing, ambiguous, or can't be confirmed, the RDL
chooses how to proceed. Each such choice is an assumption. It could have gone
another way, and if it doesn't match what the client actually meant, the SQL
answers the wrong question even though it runs correctly.

Because the deliverable is client-facing, every assumption must eventually be
**reported** (typically in the README). When reviewing, tie each assumption to
the specific code that embodies it (a filter, a join, a default, a date
boundary, a dedup rule) so you can confirm the captured assumption is in fact
borne out by the code, and so it can later be stated plainly for the client to
confirm or correct.
