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

Prompt contents
---------------

The prompt receives an unblocked issue's title and body
(``${{ steps.issue.outputs.title }}`` / ``body``). Follow the standard ordering in
``SKILL.md`` and end the instructions block with "open a pull request when
complete." Keep orientation pointed at stable documents, as with the other
families.
