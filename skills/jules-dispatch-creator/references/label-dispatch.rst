Label-dispatch workflows
========================

Label-dispatch workflows fire on ``issues: [labeled]`` when a chosen label is
applied to an issue. They are for **categorised, semi-automated triage**: instead
of mentioning a handle in a comment, a maintainer applies a label and Jules acts.
Template: ``jules-label-dispatch.yml.tmpl``.

Read this file when generating a label-dispatch workflow.

Trigger and label
-----------------

The trigger is ``issues: [labeled]``; the job guard is
``github.event.label.name == '[TRIGGER_LABEL]'``. Choose ``[TRIGGER_LABEL]`` to
match the intent:

- ``jules`` — a generic "Jules, take this" label (default).
- ``bug`` — a bug-fixer style workflow that fires when an issue is triaged as a
  bug (mirrors the upstream ``bug-fixer`` example).

Authorisation
-------------

Authorise on the **issue author's** association
(``contains(fromJSON('["OWNER", "MEMBER"]'), github.event.issue.author_association)``),
matching the OWNER/MEMBER convention used by the mention-dispatch templates. Only
repo writers can apply labels, but the author guard additionally avoids acting on
issues opened by outside accounts that happen to receive the label. Do **not** use
the upstream example's hard-coded username allowlist — it does not generalise.

Do **not** add ``@jules-*`` handle guards; those belong only to mention-dispatch.

Prompt structure
----------------

Issue context comes from ``github.event.issue.*`` (there is no triggering comment).
Otherwise follow the standard ordering in ``SKILL.md``: role + project overview,
orientation process, role-specific reference material, the injected issue context,
then the instructions block.

For a bug-fixer style label, the instructions block typically asks Jules to:
analyse the report and identify the root cause, trace the issue through the
codebase, implement a minimal targeted fix, add a regression test that would have
caught the bug, and "open a pull request when complete."

Injection prevention
--------------------

The template reads the issue title and body via ``gh issue view`` and writes them
to ``$GITHUB_OUTPUT`` using a randomised heredoc delimiter
(``DELIM=$(openssl rand -hex 8)``), exactly as the mention-dispatch templates do.
Never use a fixed delimiter.
