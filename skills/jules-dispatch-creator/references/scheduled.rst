Scheduled workflows
===================

Scheduled workflows fire on a ``schedule`` (cron) and on ``workflow_dispatch``
(manual run). They are for **repo-controlled, recurring maintenance** with no human
actor and no issue context — codebase cleanup, performance sweeps, dependency
hygiene. Template: ``jules-scheduled.yml.tmpl``.

Read this file when generating a scheduled workflow.

Trigger and concurrency
-----------------------

The trigger is ``schedule`` with ``- cron: "[CRON_SCHEDULE]"`` plus a bare
``workflow_dispatch:`` for manual runs. Choose ``[CRON_SCHEDULE]`` for the cadence,
e.g. ``0 2 * * 1`` (Mondays 02:00 UTC) for a weekly cleanup or ``0 4 * * *`` for a
daily performance pass.

A ``concurrency`` group prevents overlapping runs from racing each other (a slow
maintenance run should not collide with the next scheduled tick). It uses
``cancel-in-progress: false`` so a manual ``workflow_dispatch`` or the next cron
tick queues behind an in-flight pass rather than killing a long-running
maintenance session.

No authorisation guard
----------------------

There is **no triggering actor** and **no issue context**, so this family uses
**no** ``author_association`` check and **no** ``@jules-*`` handle guards — only
repo writers can edit the cron or click "Run workflow". Adding such guards would be
meaningless here.

Prompt contents
---------------

Scheduled prompts describe **stable focus areas and an orientation process**, not a
snapshot of the codebase (snapshots go stale; process does not). Typical focus
areas for a cleanup pass:

- dead-code removal (unused symbols, commented-out blocks, unreachable paths)
- duplication (refactor into reusable functions; apply DRY)
- complexity reduction (simplify and decompose large functions; reduce nesting)
- naming improvements and formatting/import organisation

For a performance pass, describe the categories to scan (e.g. re-renders and code
splitting on the frontend, N+1 queries and caching on the backend, algorithms and
data structures generally).

**Critical guardrail.** Because the workflow runs unattended, instruct Jules to
open a pull request **only** when it has a validated, impactful change — make
incremental, safe refactorings, preserve existing functionality, run tests to
verify, and "do not open a PR without a validated and impactful change." This
mirrors the upstream ``weekly-cleanup`` and ``performance-improver`` guidance and
prevents a stream of low-value automated PRs.
