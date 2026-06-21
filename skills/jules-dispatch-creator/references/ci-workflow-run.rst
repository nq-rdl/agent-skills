CI-workflow-run workflows
=========================

The ``ci-workflow-run`` family is triggered by a **CI failure event**, not a human
mention. It fires when a monitored workflow completes with a failure and asks
Jules to diagnose and fix it. Template: ``jules-ci-review-dispatch.yml.tmpl``.

This is fundamentally different from the mention-dispatch family:

- **No issue context** — there is no issue number, title, body, or labels to
  inject. The prompt receives the failing workflow name, failed job names, and a
  run URL instead.
- **No** ``@jules-ci-review`` **mention guard** — the ``workflow_run`` trigger
  cannot collide with ``issue_comment``-based ``!contains`` guards. Do **not** add
  ``!contains(github.event.comment.body, '@jules-ci-review')`` to any template.
- **Different placeholders** — the template uses three: ``[SECRET_NAME]``,
  ``[PROMPT CONTENT]``, and ``[CI_WORKFLOW_NAMES]`` (a JSON array of workflow name
  strings, e.g. ``["Validate Skills", "Changelog Check"]``).

Loop prevention
---------------

The template's ``if`` guard excludes ``main`` and any branch starting with
``jules/``. If Jules creates fix branches with a ``jules/`` prefix, its own PRs
will not re-trigger the workflow. The ``concurrency`` group
(``cancel-in-progress: true``) ensures only one Jules session runs per branch at
a time, with a newer CI-failure run superseding an older, still-running one —
unlike the issue-driven families, which queue with ``cancel-in-progress: false``.
Verify this convention holds for the jules-action version in use.

Prompt contents
---------------

The prompt should include:

- **Project context** — enough for Jules to navigate the repo (same as other
  families).
- **CI workflow descriptions** — what each monitored workflow does and how to
  reproduce its failure locally (e.g. ``pixi run validate-skills``).
- **Failure context** — injected by GitHub Actions; keep these interpolations
  verbatim:

  - ``${{ github.event.workflow_run.name }}`` — the failing workflow name
  - ``${{ github.event.workflow_run.head_branch }}`` — the branch that triggered it
  - ``${{ steps.failure.outputs.failed_jobs }}`` — comma-separated failed job names
  - ``${{ steps.failure.outputs.run_url }}`` — link to the failed run

- **Diagnosis process** — branch on the workflow name to guide Jules toward the
  right reproduction and fix strategy for each CI check.
- **Fix constraints** — minimal change only; do not modify validation rules unless
  they are the root cause.

The instructions block should end with "Open a pull request with the fix when
complete."
