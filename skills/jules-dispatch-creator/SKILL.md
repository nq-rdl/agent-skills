---
name: jules-dispatch-creator
license: CC-BY-4.0
description: >-
  Use when the user wants to set up, add, configure, or adapt Jules GitHub
  Actions dispatch workflows for a repository. Triggers when they say "adapt
  the Jules workflows", "set up Jules dispatch", "add Jules to my repo", "wire
  up Jules", "write Jules prompts for this project", "configure Jules for this
  repo", "integrate Jules", or "onboard Jules as a coding agent". Also applies
  when adding Jules to an existing GitHub project that needs tailored workflow
  YAML files, including multiple trigger families — comment mentions, issue
  labels, scheduled/cron maintenance, CI-failure repair, and issue-lifecycle
  automation.
metadata:
  repo: https://github.com/nq-rdl/agent-skills
---

# Jules Dispatch Workflow Adapter

Your job is to write Jules GitHub Actions dispatch workflows tailored to the
current project. Jules is Google's async AI coding agent. A workflow fires on
some GitHub event, hands Jules a `prompt:` with enough context to work, and lets
it open a PR. The only thing that varies between projects is the `prompt:` block;
the surrounding YAML is fixed boilerplate provided as template files in this skill.

Workflows are grouped into **trigger families** by the GitHub event that starts
them. Each family has a template in `templates/` and a reference file in
`references/` with the persona guidance, trigger mechanics, and authorisation
model for that family:

| Family | Trigger | Use for | Reference |
|--------|---------|---------|-----------|
| mention-dispatch | `issue_comment` + `@jules-<handle>` | human-initiated, free-form tasks on an issue | `references/mention-dispatch.rst` |
| label-dispatch | `issues: [labeled]` | categorised, semi-automated triage | `references/label-dispatch.rst` |
| scheduled | `schedule` + `workflow_dispatch` | repo-controlled recurring maintenance | `references/scheduled.rst` |
| ci-workflow-run | `workflow_run` (failure) | automatic repair of a failing pipeline | `references/ci-workflow-run.rst` |
| issue-lifecycle | `issues: [closed]` | dependency-driven follow-on work | `references/issue-lifecycle.rst` |

Work through the following phases.

---

## Phase 0 — Configure

Before reading the codebase, ask the user two quick questions:

1. **Which workflow(s)?** Choose by trigger family (see the table above). Within
   `mention-dispatch`, also choose roles: `swe`, `security`, `docs`, `infra`. If
   the user doesn't specify, generate the families and roles that apply to the
   project.
2. **Secret name** — What GitHub Actions secret holds the Jules API key? (Each
   team member typically has their own token; name it accordingly, e.g.
   `JK_JULES_API`, `AB_JULES_API`.)

Store the secret name — it replaces `[SECRET_NAME]` in every template.

---

## Phase 1 — Assess the project

Build an accurate picture of the project by reading in parallel:

- **`CLAUDE.md`** at the repo root — project conventions, commands, architecture.
  Note whether it is comprehensive; if so, the SWE prompt can defer to it rather
  than reproducing its contents.
- **Root `README.md`** — first-impression overview.
- **Structural doc files** — if any of these exist, read them; they provide
  stable context worth including in prompts:
  - `ARCHITECTURE.md` — system/infra topology, languages, deployment setup
  - `DESIGN.md` — layout decisions, component rationale
  - `CONTRIBUTING.md` — contribution patterns, LLM-specific conventions
- **`docs/`** — skim (don't exhaustively read) to understand the project domain
  and any explicit quality standards already in use for writing.
- **Source tree** — launch an Explore subagent to scan the codebase. Direct
  reads are sufficient for well-known top-level files (CLAUDE.md, README.md),
  but the source tree assessment should use the Explore agent because it follows
  nested directories and surfaces non-obvious files that glob patterns miss:
  infrastructure configs, Compose files, CI definitions, test fixtures, and
  supporting scripts. If you rely only on direct tool calls here you will miss
  files that matter for the prompts — for example, a Compose file that defines
  the local development cluster, or a CI workflow that constrains what Jules
  can validate.

### Conflicting sources

Treat docs and code differently:

- **Docs = stated intention.** Content describing planned or in-progress work is
  aspirational — Jules is expected to close those gaps. Never weaken or remove it.
- **Code = current reality.** If a doc describes something the code contradicts
  (a renamed module, a removed command, a missing directory), that is a factual
  error. Note it, but do *not* try to encode the fix into the Jules system prompt.
  Factual errors belong in a GitHub issue or `TODO.md` — encoding them in the
  system prompt creates stale context that misleads Jules over time.

### Report before proceeding

Summarise your findings:

1. A 2–4 sentence project description (domain, stack, key concepts).
2. Which structural doc files were found (`ARCHITECTURE.md`, `DESIGN.md`,
   `CONTRIBUTING.md`) — these will be referenced in the relevant prompts.
3. Any factual errors found — file and discrepancy — with a suggestion to file
   them as GitHub issues or TODO entries rather than embedding fixes in the prompt.
4. Ask: "Anything else Jules should know before I draft the prompts?"

Wait for the user's response before moving to Phase 2.

---

## Phase 2 — Draft the prompts

For each requested workflow, draft a `prompt:` block that gives Jules enough
context to work autonomously. The goal is to teach Jules *how to orient itself*,
not to pre-load it with a snapshot of the codebase. Snapshots go stale; process
doesn't.

**For each family you are generating, read `references/<family>.rst` before
drafting the prompt.** Each reference carries the persona guidance, trigger
mechanics, authorisation model, and instruction-block expectations for that
family — the detail that used to live inline here.

### Prompt structure (follow this order for every workflow)

```
[Role + project overview — one sentence]

[Orientation process or key conventions — stable, non-stale guidance]

[Role-specific reference material — see the family reference]

[Event context — injected by GitHub Actions, keep interpolations verbatim.
 The shape depends on the family. mention-dispatch: the issue title/body/labels
 come from `${{ steps.issue.outputs.* }}` (fetched via `gh`), and the triggering
 comment from `${{ github.event.comment.body }}` directly (it is not extracted to
 a step output). label-dispatch: the issue via `${{ steps.issue.outputs.* }}`,
 no comment. scheduled: none. ci-workflow-run: the failing-run details.
 issue-lifecycle: the unblocked issue via `${{ steps.issue.outputs.* }}`.]

[Instructions — family-specific, ends with "open a PR when complete"]
```

### Instruction density

Match the density and specificity of the instructions block to what Jules
actually needs for that role:

- **SWE** — keep sparse. The task is free-form; CLAUDE.md covers conventions.
  Over-specifying the instructions poisons context when the issue asks for
  something slightly different. A brief "implement the request; open a PR" is
  enough.
- **Security / docs / infra / label / scheduled / issue-lifecycle** — use
  structured constraints. These roles have narrower operational boundaries and
  Jules benefits from explicit expectations: what it is allowed to do, what it
  must not do, what output format is expected, and a clear action to close with
  ("open a pull request").

### Presenting the drafts

Show all requested draft prompts to the user before writing any files. For each:

- State what family/role/persona was assigned.
- Flag any decisions where the best choice was unclear.
- Highlight gaps (e.g. no writing standards found in existing docs — ask the user
  to describe their preferred style before continuing).

Wait for targeted feedback or approval before writing any files.

---

## Phase 3 — Write the finished workflows

Once the user approves, write only the workflow file(s) requested in Phase 0.

Read the relevant template from `templates/jules-<role>-dispatch.yml.tmpl`
(mention-dispatch family, e.g. `jules-swe-dispatch.yml.tmpl`) or
`templates/jules-<family>.yml.tmpl` (newer families, e.g.
`jules-label-dispatch.yml.tmpl`, `jules-scheduled.yml.tmpl`), located in the same
directory as this SKILL.md — not the project's working directory. Replace
`[PROMPT CONTENT]` with the approved prompt, indented **12 spaces** (the YAML
literal block scalar level in the template). Replace `[SECRET_NAME]` with the
secret name from Phase 0, and any family-specific placeholders (e.g.
`[TRIGGER_LABEL]`, `[CRON_SCHEDULE]`, `[CI_WORKFLOW_NAMES]`). Reproduce all other
YAML exactly — do not reformat, reorder, or simplify it.

### Trigger-family rules at a glance

| Family | `@jules-*` guards | Issue context source | Actor authorisation | Concurrency |
|--------|-------------------|----------------------|---------------------|-------------|
| mention-dispatch | yes (all other handles) | `steps.issue.outputs.*` (fetched via `gh`) + `github.event.comment.body` for the triggering comment | comment `author_association` OWNER/MEMBER | — |
| label-dispatch | no | `steps.issue.outputs.*` (fetched via `gh`) | issue `author_association` OWNER/MEMBER | yes (per issue) |
| scheduled | no | none | none (repo-controlled) | yes |
| ci-workflow-run | no | none (CI failure context) | none | yes (per branch) |
| issue-lifecycle | no | per-issue via github-script | per-issue `author_association` | yes (per closed issue) |

**Do not add `@jules-*` guards to any family except mention-dispatch.** The
`workflow_run`, `schedule`, and `issues` triggers cannot collide with
`issue_comment` mentions, so a guard there is meaningless.

### Handle-guard rules — mention-dispatch only

Every `issue_comment` template triggers on its own handle and guards
(`!contains`) against **every other** `@jules-*` handle in the canonical set, so a
comment naming two handles dispatches only the intended one. The canonical handle
set and the maintenance rule (and how the test enforces it) live in
`references/mention-dispatch.rst` — treat that file plus the `templates/` files as
the single source of truth. When you add a new `issue_comment` handle, update the
`!contains` guard in *every* mention-dispatch template and the `MENTION_HANDLES`
tuple in `tests/skills/test_jules_dispatch_creator_templates.py`.

### Injection prevention — issue_comment and label templates

Templates that read an issue `title`/`body` in a bash step and write them to
`$GITHUB_OUTPUT` use a randomised heredoc delimiter (`openssl rand -hex 8`). This
prevents a crafted issue title or body from breaking out of the heredoc and
injecting arbitrary output. Never use a fixed string like `ISSUE_EOF`. The
`issue-lifecycle` template avoids the issue entirely by reading issue details
through `actions/github-script` (`core.setOutput` is injection-safe).
