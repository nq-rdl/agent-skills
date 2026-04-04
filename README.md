# agent-skills

RDL's repository for authoring, documenting, and validating Agent Skills.

## Overview

The core unit in this repo is a **self-contained skill**. Each skill lives in its
own directory under `skills/` and carries the instructions, metadata, and any
supporting files it needs.

These skills follow the [Agent Skills Specification](https://agentskills.io/specification).
The repo-specific format and structure used here are outlined in
[`docs/specification.mdx`](docs/specification.mdx).

At minimum, a skill contains a `SKILL.md` file:

```text
skills/<skill-name>/
|- SKILL.md
|- scripts/      # optional
|- references/   # optional
|- assets/       # optional
```

That packaging model is intentional: skills should be portable, reviewable, and
easy to validate without depending on repo-wide runtime glue.

## Repo Scope

This repo is for:

- authoring skills in `skills/`
- documenting the format and authoring guidance in `docs/`
- validating skills with the reference tooling in `src/skills/ref/`
- testing that validation and prompt-generation behavior in `tests/`

This repo is **not** the packaging or installation layer.

RDL uses [`nq-rdl/agent-extensions`](https://github.com/nq-rdl/agent-extensions)
to package and install skills into the target agent environment.

## Repo Layout

- `skills/`: self-contained skill directories
- `docs/`: specification and authoring documentation
- `src/skills/ref/`: reference validation and prompt-generation code
- `tests/`: tests for the reference tooling

## Validation

Validate all skills in the repo:

```bash
pixi run validate-skills
```

Validate a single skill:

```bash
ref validate skills/<skill-name>
```
