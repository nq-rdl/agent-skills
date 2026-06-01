Issue-lifecycle workflows
=========================

Issue-lifecycle workflows fire on ``issues: [closed]``. They are for
**dependency-driven follow-on work**: when an issue is closed, find the issues it
was blocking that are now ready and start Jules on each. Template:
``jules-issue-lifecycle.yml.tmpl``.

Read this file when generating an issue-lifecycle workflow.

Two-job structure
-----------------

The template has two jobs:

1. ``detect-unblocked`` — finds open issues that were blocked by the just-closed
   issue and whose blockers are now all closed, and outputs a JSON matrix of their
   numbers (plus a ``found`` flag).
2. ``implement`` — runs only when ``found == 'true'``; fans out over the matrix and
   invokes Jules once per unblocked issue.

Detection (no phantom action)
-----------------------------

The upstream ``unblocked-issues`` example references
``google-labs-code/on-unblocked@v1`` (and ``google-labs-code/jules-invoke@v1``).
Neither is a real published action — ``google-labs-code/jules-action`` is a single
composite action, which RDL forks and pins as ``nq-rdl/jules-action``. So the
detect job implements the logic **inline** with ``actions/github-script@v7``
(real, pinnable, already used by ``ci-workflow-run``) rather than referencing a
non-existent action.

The default detection encodes a ``blocked by #N`` / ``depends on #N`` convention:
it scans open issues, keeps those whose body references the just-closed issue, and
confirms every referenced blocker is closed before marking the issue ready. Adjust
the regex to match the project's actual dependency-tracking convention (some teams
use task lists, a ``Depends-On:`` trailer, or a project board).

Authorisation
-------------

Authorise **per unblocked issue** on its ``author_association`` (OWNER/MEMBER).
``gh issue view`` does not expose ``author_association``, so the ``implement`` job
fetches each issue through the REST API via ``actions/github-script``
(``github.rest.issues.get``) and gates the Jules invocation on the result.
``github-script``'s ``core.setOutput`` is injection-safe, so no randomised bash
heredoc is needed here.

Do **not** add ``@jules-*`` handle guards; those belong only to mention-dispatch.

Concurrency and the closing actor
---------------------------------

A workflow-level ``concurrency`` group keyed on the closed issue
(``jules-issue-lifecycle-${{ github.event.issue.number }}``,
``cancel-in-progress: false``) serialises the pipeline so a rapid
close/reopen/close on the same issue does not launch overlapping detection
sweeps. The ``implement`` job's matrix uses ``fail-fast: false`` so that a failed
dispatch on one unblocked issue does not cancel the others — each is independent
work.

The ``detect-unblocked`` job runs on **every** ``issues: closed`` event, with no
guard on who closed the issue. This is deliberate: gating the scan on the closing
issue's author would skip legitimate cases where closing an *externally* authored
issue (e.g. a community bug report) unblocks internal work. Jules is never invoked
incorrectly — the per-issue ``author_association`` check still gates every actual
invocation — but be aware that a Triage-role actor can drive repeated (read-only)
API scans by closing issues. If that denial-of-wallet surface matters for your
repo, add a job-level ``if:`` on ``github.event.issue.author_association`` or a
``github.actor`` allowlist to ``detect-unblocked``.

Prompt contents
---------------

The prompt receives an unblocked issue's title and body
(``${{ steps.issue.outputs.title }}`` / ``body``). Follow the standard ordering in
``SKILL.md`` and end the instructions block with "open a pull request when
complete." Keep orientation pointed at stable documents, as with the other
families.
