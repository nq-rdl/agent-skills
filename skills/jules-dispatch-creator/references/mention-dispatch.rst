Mention-dispatch workflows
==========================

Mention-dispatch workflows fire on ``issue_comment`` when a maintainer mentions a
``@jules-<handle>`` in a comment on an issue. They are for **human-initiated,
free-form** work: a person decides Jules should act on a specific issue and says
so. Templates: ``jules-{swe,security,docs,infra}-dispatch.yml.tmpl``.

Read this file when generating any mention-dispatch role. It carries the per-role
prompt guidance, the canonical handle set, and the guard rule that keeps the
templates from double-firing.

General roles
-------------

The skill ships templates for four general starter personas. Match the density of
each prompt's instruction block to what the role actually needs (see
"Instruction density" in ``SKILL.md``).

SWE
~~~

Keep the prompt thin. If a comprehensive ``CLAUDE.md`` exists, reference it
explicitly — Jules will read it — and do **not** reproduce its contents, which
creates a second source of truth that diverges from the real one.

Orientation notes must point to documents, not encode facts. If Phase 1 reveals a
non-obvious layout (e.g. Python under ``backend/`` rather than the repo root),
resist encoding that fact in the prompt. Point Jules to the stable document that
describes it — ``docs/ARCHITECTURE.md`` or wherever the layout lives. A prompt
that says "all Python source lives under ``backend/``" becomes wrong the moment a
PR moves things and the docs are updated; "read ``docs/ARCHITECTURE.md`` for the
current project layout" stays accurate indefinitely, and Jules benefits from every
docs improvement. This applies to any structural fact that can change: entry
points, module names, directory conventions. If the structural documentation is
missing or stale, file a GitHub issue — do not correct it in the system prompt.

::

   You are a Software Engineer working on [project name] — [one-sentence description].

   Read `CLAUDE.md` at the repo root for the authoritative project layout, commands,
   testing strategy, and conventions before starting work. Read `docs/ARCHITECTURE.md`
   for the current system topology and entry points.

   [Add only what neither CLAUDE.md nor ARCHITECTURE.md covers.]

   ## GitHub Issue ...
   ## Triggering comment
   ## Instructions
   Implement the request described in the issue. Open a pull request when complete.

If no ``CLAUDE.md`` exists, include enough pattern-based context to navigate
(architecture style, key directories, test runner) — but prefer conventions over
exhaustive file lists, which go stale.

Security
~~~~~~~~

Describe risk *patterns* tied to this stack, not specific files. The issue tells
Jules where to focus; the system prompt should help Jules recognise *what kind of
threats* to look for. Specific file paths become incorrect as the code evolves.

Point Jules to ``docs/ARCHITECTURE.md`` (and ``CLAUDE.md`` if present) for
orientation — encode the *process* of reading stable documents, not the structural
facts those documents contain. Pattern-based guidance looks like:

- "This stack generates SQL from config files — SQL injection from config values
  is a risk class to assess."
- "User-controlled strings are used to construct filesystem paths — path traversal
  is a risk class."
- "Credentials are passed through environment variables — check for leakage into
  logs or error responses."

Keep the severity model and PR conventions stable. The instructions block should
specify: what to produce (findings as PR comments or a report file), the severity
classification expected (e.g. critical / high / medium / low), whether to fix or
only report, and "Open a pull request with your findings when complete."

Docs
~~~~

Reference the three structural doc files if present (discovered in Phase 1) — they
are stable anchors, not ephemeral ``docs/`` subpaths:

- ``ARCHITECTURE.md`` — system topology, infra, languages, setup
- ``DESIGN.md`` — component layout, design decisions
- ``CONTRIBUTING.md`` — contribution patterns; often LLM-specific conventions

Do **not** list ad-hoc files under ``docs/``; those paths change frequently and
listing them leads Jules to edit the wrong files or create duplicates. Instead
describe the process: read source code first and treat existing docs as
potentially outdated until verified; verify every claim against code before
writing; follow the project's writing standards (tone, tense, heading style,
``docs:`` commit prefix). The instructions block should name the files in scope
(the structural files above plus ``README.md``; avoid open-ended lists), the
commit prefix, and end with "Open a pull request when complete."

Infra
~~~~~

Infrastructure changes carry real operational risk. Give Jules a hard boundary: it
writes and validates IaC in the repository, but has **no access to live
infrastructure** — no CLI calls, no API calls, no applying changes.

Include: stable architecture context (tools, platforms, layout; reference
``ARCHITECTURE.md`` if present); per-tool conventions (naming, module structure,
coding standards for each IaC tool — Ansible, Terraform, Helm; reference
``CONTRIBUTING.md`` if it covers these); and explicit constraints —

- No live infra access — no ``terraform apply``, no ``ansible-playbook``, no
  ``kubectl apply``.
- Validation is repo-local only: ``terraform validate``, ``ansible-lint``,
  ``helm lint``, etc.

Expect Jules to follow existing patterns before introducing new abstractions and
to validate all changes before committing. The instructions block ends with "Open
a pull request with the implementation when complete."

Project-specific personas (example)
------------------------------------

Some repos add personas beyond the four general roles. For example,
``nq-rdl/agent-skills`` deploys ``@jules-review`` (an issue reviewer) and
``@jules-skills`` (a skill engineer) whose prompts are hardwired to that project.
The skill does **not** ship general templates for these — their prompts are too
project-specific to generalise — but the canonical handle set below includes them
because every deployed ``issue_comment`` workflow must guard against every handle
present in the target repo. When a project wants such a persona, copy a general
mention-dispatch template, write the project-specific prompt, and add the new
handle to the canonical set in that repo.

Canonical handle set & guard rule
----------------------------------

Every mention-dispatch workflow guards against **all other** ``@jules-*`` handles,
so that a comment naming two handles dispatches only the intended one. The
canonical handle set is the single source of truth for which guards each template
carries.

For ``nq-rdl/agent-skills`` the canonical set is:

- ``swe``, ``security``, ``docs``, ``infra`` — general roles
- ``review``, ``skills`` — project-specific personas

The rule: **every** ``issue_comment`` **template must trigger on its own handle
(**``contains(github.event.comment.body, '@jules-<own>')``**) and guard
(**``!contains(...)``**) against every other handle in the canonical set.**
``author_association`` must be ``OWNER`` or ``MEMBER`` only — never
``COLLABORATOR``.

Adding a handle therefore means updating the ``!contains`` guard in *every*
existing ``issue_comment`` template — the templates in ``templates/`` are the
canonical source, so update them and regenerate any deployed workflows. This
invariant is enforced automatically by
``tests/skills/test_jules_dispatch_creator_templates.py`` (the ``MENTION_HANDLES``
tuple is the single source of truth there); keep that tuple in sync with this list.

**Exception —** ``ci-workflow-run``**:** that family uses ``workflow_run`` and does
**not** use ``!contains`` guards. Never add a ``@jules-*`` guard to it. The same
applies to the other non-``issue_comment`` families (``label-dispatch``,
``scheduled``, ``issue-lifecycle``).

Injection prevention
--------------------

Every mention-dispatch template uses a randomised heredoc delimiter
(``DELIM=$(openssl rand -hex 8)``) when writing the issue ``title`` and ``body`` to
``$GITHUB_OUTPUT``. This prevents a crafted issue title or body that contains a
fixed delimiter string on its own line from breaking out of the heredoc and
injecting arbitrary output. Never use a fixed string like ``ISSUE_EOF`` as a
heredoc delimiter.
