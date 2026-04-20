# agent-skills

RDL's repository for authoring, validating, and releasing Agent Skills — self-contained
instruction bundles consumed by `nq-rdl/agent-extensions`.

## Commands

```bash
# Python / default env
pixi run validate-skills   # validate all SKILL.md files (legacy Python path)
pixi run test              # pytest (src/ + tests/)
pixi run lint              # ruff check
pixi run typecheck         # ty check src/
pixi run format            # ruff format

# Per-skill Python envs (csv / docx / xlsx / pdf)
pixi run -e csv  test
pixi run -e csv  lint
pixi run -e csv  typecheck
# same pattern for docx, xlsx, pdf

# Go: asctl (preferred validator)
cd tools/asctl && go build ./... && go test -race ./...
asctl repo-check           # validate all skills in <2s (preferred over pixi validate-skills)

# Go: per-skill scripts
cd skills/pi-rpc/scripts && make build && make test
cd skills/jules/scripts  && go build ./... && go test -race ./...

# Run from repo root (go.work unifies all modules)
go test ./...

# Git hooks
lefthook install           # install once after cloning
lefthook run pre-commit    # run hook stages manually
lefthook run pre-push
```

## Architecture

```
agent-skills/
├── skills/                   # 50+ self-contained skills
│   ├── <name>/SKILL.md       # Required: YAML frontmatter + instructions
│   ├── <name>/scripts/       # Optional: Go or Python runtime code
│   ├── <name>/references/    # Optional: reference docs
│   └── <name>/assets/        # Optional: templates / resources
├── tools/asctl/              # Go CLI: skill validator + prompt renderer (replacing src/skills/ref/)
│   ├── cmd/asctl/            # main package
│   └── internal/             # validator, parser, prompt, repocheck, frontmatter
├── src/skills/ref/           # Legacy Python validator — being retired, excluded from linting
├── docs/                     # Authoring guides (skill-creation/, specification.mdx)
├── tests/                    # pytest suite for reference tooling
├── go.work                   # Go workspace spanning all Go modules
├── pyproject.toml            # Python deps + per-skill pixi feature envs
└── lefthook.yml              # Pre-commit + pre-push hooks
```

## Skill Format

Every skill needs `skills/<name>/SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name          # lowercase, hyphens only, max 64 chars
description: >-           # required, max 1024 chars; what it does + when to use it
  Short description.
license: Apache-2.0       # optional
metadata:                 # optional key-value
  author: example-org
---
```

See `docs/specification.mdx` and `docs/skill-creation/` for the full authoring guide.

## Go Module Layout

Each Go-bearing skill (`skills/pi-rpc/scripts`, `skills/jules/scripts`) has its own
`go.mod` and publishes independently. `tools/asctl` is the repo's own Go tool.
`go.work` unifies them for the dev loop only — changing one module's API requires
coordinating with `agent-extensions` if that module is a released binary.

Follow idiomatic Go patterns from `skills/modern-go-guidelines/`: use `any` not
`interface{}`, `slices.Contains` not manual loops, `t.Context()` in tests, etc.

MCP servers live as Cobra subcommands in `skills/<name>/scripts/cmd/<name>-mcp/`;
`skills/pi-rpc/scripts/cmd/pi-mcp/` is the reference implementation.

## Changelog (required for every PR)

CI will fail without a changie fragment:

```bash
changie new   # interactive; creates .changes/unreleased/<slug>.yaml
```

Kinds: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.
For CI/docs-only changes with no user-facing impact, add the `skip-changelog` label
to the PR instead.

## Pre-commit Hooks (lefthook)

`git commit` runs in parallel: `go vet`, `gofmt`, `go build` (pi-rpc, jules, asctl),
`ruff lint`, `ruff format --check`, `ty typecheck`, `validate-skills`,
`pixi install --locked`. `git push` adds per-module Go tests and `pytest`.

Lychee link-checking is optional — skipped if `lychee` is not on PATH.

## Key Conventions

- `asctl repo-check` is the canonical validator; `pixi run validate-skills` (Python)
  produces identical output and will be removed once `src/skills/ref/` is retired.
- Per-skill Python scripts are linted in their own pixi env, not the default env
  (see `extend-exclude` in `pyproject.toml`).
- Conventional commits: `feat(skill-name): …`, `fix(asctl): …`, `chore: …`, `docs: …`.
- Go binaries released here are consumed by `nq-rdl/agent-extensions` via GitHub
  Release assets — coordinate CLI surface changes with that repo's plugin manifest.
