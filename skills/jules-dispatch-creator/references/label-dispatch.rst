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
matching the OWNER/MEMBER convention used by the mention-dispatch templates. Do
**not** use the upstream example's hard-coded username allowlist — it does not
generalise.

This gates on the issue **author**, not on whoever applied the label — GitHub's
``labeled`` event does not expose the labeler's association in a comparable field.
Be aware of the limitation: the **Triage** role can apply labels *without* write
access, so on a repo that grants Triage to outside collaborators, a Triage actor
could apply the trigger label to an OWNER/MEMBER-authored issue and start Jules.
The worst case is wasted API quota / an unsolicited PR (no secret exposure, no
privilege escalation), but if your threat model cares, add a labeler check on
``github.event.sender.login`` against a CODEOWNERS/allowlist, or restrict label
application via repository settings. A ``concurrency`` group keyed on the issue
number (``jules-label-${{ github.event.issue.number }}``) serialises repeated
labelling of the same issue. It uses ``cancel-in-progress: false`` so a re-label
queues behind an in-flight dispatch rather than cancelling it: the Jules
invocation is dispatched asynchronously, so cancelling the workflow mid-run would
not stop Jules — it would only suppress the confirmation comment and leave the
session running unannounced.

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
