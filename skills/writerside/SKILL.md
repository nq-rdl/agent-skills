---
name: writerside
description: >-
  Use when the user asks about Writerside topics, markup tags, documentation
  templates, or building/deploying Writerside projects. Covers semantic XML
  markup, topic structure, procedures, code blocks, templates, Docker-based
  builds, and documentation quality inspections for JetBrains Writerside.
compatibility: >-
  Requires JetBrains Writerside or Docker for builds
metadata:
  repo: https://github.com/nq-rdl/agent-skills
---

# Writerside Skill

Navigate JetBrains Writerside's semantic markup, project structure, and quality tooling to produce well-structured technical documentation.

---

## Scope

This skill covers **Writerside tool mechanics only** — how to use the markup, structure topics, build with Docker, and run quality checks.

It does **not** cover:
- General technical writing craft (use a copywriting or editing skill)
- Content review or style guidelines (use a review skill)
- Documentation strategy or information architecture (separate concern)

---

## Key Concepts

**Topics** — The fundamental unit of Writerside content. Topics can be authored as `.md` (Markdown) or `.topic` (semantic XML) files. Both formats can be mixed within a single project, and Markdown files can embed semantic XML tags.

**Instances** — A build target that produces one documentation website. A Writerside project can contain multiple instances (e.g., user guide, API reference), each defined in a module configuration. Docker builds target a specific instance via `MODULE_INSTANCE`.

**Semantic markup** — Writerside's XML tag system that adds meaning beyond formatting. Tags like `<procedure>`, `<step>`, `<chapter>`, `<deflist>`, and `<tldr>` encode document structure so the builder can generate navigation, search, and cross-references automatically.

**Chapters** — Hierarchical sections within a topic, created with `<chapter>` tags (XML) or `##` headings (Markdown). Chapters support nesting, collapsibility, and per-instance filtering.

**Procedures** — Step-by-step instruction blocks using `<procedure>` and `<step>` tags. These render as numbered sequences with clear visual separation — the primary pattern for how-to content.

**Inspections** — Built-in quality checks that run in the IDE editor and during Docker builds. They catch invalid markup, broken references, duplicate IDs, and structural issues.

---

## Authoring Mode Decision

| Factor | Markdown (`.md`) | Semantic XML (`.topic`) |
|--------|------------------|------------------------|
| Learning curve | Familiar CommonMark syntax | Requires learning Writerside XML tags |
| Best for | Small docs, quick content, developer-facing | Large projects, multi-contributor, formal docs |
| Semantic features | Embed XML tags inline as needed | Full access to all semantic elements |
| Recommended when | Speed matters, contributors know Markdown | Structure matters, content is reused across instances |

Writerside does not require choosing one mode — Markdown files can contain semantic XML tags directly.

---

## Reference Files

| File | Contents |
|------|----------|
| [references/markup-reference.md](references/markup-reference.md) | Complete semantic XML tag reference — block elements, inline elements, metadata, conditional content, with examples |
| [references/docker-deployment.md](references/docker-deployment.md) | Docker build process — commands, environment variables, CI/CD integration, multi-instance builds |
| [references/documentation-quality.md](references/documentation-quality.md) | Built-in inspections, quality workflow, suppressing warnings, CI integration |
| [references/templates.md](references/templates.md) | How-to guide template and Standard Operating Procedure template with Writerside XML examples |
| [references/linting.md](references/linting.md) | Linting strategy — Writerside inspections as primary, optional external tools, recommended workflow |
