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

The cohort + data-element template (assumed across the suite)
------------------------------------------------------------

Every ``sql-review-*`` skill **assumes the SQL under review follows one template
structure**: a **cohort** (defined by inclusion and exclusion criteria) that one
or more **data elements** are joined onto. Concretely, the client first asks for
a defined population — *the cohort* — and then asks for specific results about
that population — *the data elements*. For example: "patients meeting X (and not
Y)" is the cohort, and "all their eGFR results" is a data element joined to it.

Read the SQL against this template: first identify the cohort (the
population-defining logic), then the data elements joined to it. Anchor your
assumptions and limitations to whichever part they attach to.

**If the SQL does not decompose this way** — you cannot identify a cohort, the
inclusion/exclusion criteria are absent or implicit, or it is unclear which
columns are data elements versus cohort-defining logic — **do not guess.** Who
resolves the gap depends on the step:

- **analyse** owns the clarification with the **Data Engineer (DE)**. This is
  the step that asks the DE — via an ``AskUserQuestion`` prompt — what the
  intended cohort (its inclusion and exclusion criteria) is and which data
  elements are requested against it, and records the answer in the artifacts.
- **other steps (e.g. explain)** are downstream and must not invent the
  structure or prompt the DE. They **flag the gap to their audience** (for
  ``explain``, the Data Analyst) and route it back to **analyse** / the DE.

Cohort
------

The **population the analysis is about**, defined by explicit **inclusion
criteria** (who is in) and **exclusion criteria** (who is removed). In the SQL,
the cohort is the population-defining logic — the filters, CTEs, and joins that
produce the base set of subjects *before* any requested results are attached. The
cohort answers **"who are we looking at?"**

When explaining, point to the exact code that encodes each inclusion and
exclusion criterion so the analyst can confirm the population is the one the
client meant.

Data element
------------

A specific attribute, measurement, or result requested **for the cohort** — e.g.
all eGFR results. In the SQL, data elements are the columns, tables, or
measurements joined onto the cohort. They answer **"what do we want to know about
this population?"** A single review usually has one cohort and one or more data
elements joined to it.

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
