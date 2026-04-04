---
icon: lucide/book-open
---

# Skills Catalog

Portable, provider-agnostic skills following the [agentskills.io specification](https://agentskills.io/specification). Each skill is self-contained: a directory under `skills/` with a `SKILL.md` plus any optional scripts, references, templates, or assets it needs.

This repo documents and validates those skills. The repo-specific structure used here is outlined in [`specification.mdx`](specification.mdx).

## Repo Scope

This repository is for authoring skills and maintaining the reference tooling around them.

It is not the packaging or installation layer.

RDL uses [nq-rdl/agent-extensions](https://github.com/nq-rdl/agent-extensions) to package and install skills into target agent environments.

## Skill Index

### Go Development

| Skill | Description |
|-------|-------------|
| [go-naming](../skills/go-naming/) | Go naming conventions — packages, variables, functions, interfaces, receivers, initialisms. Sources: Effective Go, Google Style Guide. |
| [go-secure](../skills/go-secure/) | Secure error handling and information leakage prevention — domain error types, trust boundary translation, slog redaction, opaque wrapping. |
| [go-gh](../skills/go-gh/) | GitHub Actions CI/CD for Go — setup-go v5, version matrix, caching, build/test patterns, artifact uploads. |

### Data & Analytics

| Skill | Description |
|-------|-------------|
| [starrocks](../skills/starrocks/) | StarRocks analytical data warehouse — SQL authoring, table design, partitioning, materialized views, external catalogs. |

### Developer Workflow

| Skill | Description |
|-------|-------------|
| [tdd](../skills/tdd/) | Test-driven development — red/green/refactor cycle, test quality rules, anti-patterns. |
| [changie](../skills/changie/) | Changelog entry creation with Changie — non-interactive usage, entry quality, fragment naming. |
| [husky](../skills/husky/) | Git hooks with husky v9 — installation, hook authoring, CI integration. |
| [lefthook](../skills/lefthook/) | Git hooks with Lefthook — Go-based, language-agnostic alternative to husky. |
| [document-release](../skills/document-release/) | Post-ship documentation review — ensures README, CHANGELOG, CLAUDE.md, and project docs stay in sync. |
| [report-skill-issue](../skills/report-skill-issue/) | File bug reports for broken skills to their upstream repository. |
| [skill-review](../skills/skill-review/) | Self-improvement loop — spawns a reviewer subagent to audit skills worked on in the current session. |
| [cc-hooks](../skills/cc-hooks/) | Create, manage, and debug Claude Code hooks — guardrails, safety rules, context injection, completion checklists. |

### AI Agent Backends

| Skill | Description |
|-------|-------------|
| [dispatch](../skills/dispatch/) | Tool-agnostic task dispatch — identify task, choose backend, invoke backend skill, track status. Works with any installed dispatch target. |
| [opencode](../skills/opencode/) | Drive OpenCode programmatically via its REST API — sessions, prompts, SSE monitoring, permissions, extension authoring. |

### Documentation & Design

| Skill | Description |
|-------|-------------|
| [writerside](../skills/writerside/) | JetBrains Writerside — semantic XML markup, topic structure, Docker builds, quality inspections. |
| [canvas-design](../skills/canvas-design/) | Visual art and design in .png/.pdf — design philosophy creation expressed on canvas. Ships 81 bundled fonts. |

### R Language

| Skill | Description |
|-------|-------------|
| [r-expert](../skills/r-expert/) | R language expert — writing, reviewing, and debugging R code with idiomatic best practices. |

## Frontmatter Specification

All skills follow the [agentskills.io spec](https://agentskills.io/specification). Required fields:

```yaml
---
name: skill-name          # must match directory name, lowercase + hyphens
description: >-           # what it does + when to activate (max 1024 chars)
  Description text here.
metadata:
  repo: https://github.com/nq-rdl/agent-skills
---
```

Optional fields used in this repo:

| Field | Used by | Purpose |
|-------|---------|---------|
| `license` | canvas-design | License reference for bundled assets |
| `compatibility` | changie, husky, lefthook, opencode, r-expert, starrocks, writerside | Runtime environment requirements |

## Portability Rules

Skills are platform-agnostic. Two rules follow from this:

1. **No hooks in skills** — Hook configs (JSON + shell scripts that register as event handlers) are platform-specific and must not ship inside a skill directory. If a skill benefits from a companion hook, document the hook pattern in the skill and implement it in the platform's extension layer. See [Best practices: Skills must not ship hooks](/skill-creation/best-practices#skills-must-not-ship-hooks).

2. **No platform-specific imports** — Skills should not import or require platform-specific SDKs or APIs in their `SKILL.md` instructions. Scripts under `scripts/` may use platform tools (e.g., `gh` CLI, `bun`), but these should be documented in the `compatibility` field.
