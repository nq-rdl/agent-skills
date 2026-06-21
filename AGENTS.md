# AGENTS.md

Agent guidance for this repository. Use this alongside the README and CONTRIBUTING.md for full project context and contributor workflows.

## Setup commands

```bash
pixi install
lefthook install
```

## Build, test, lint

```bash
pixi run -e default format
pixi run -e default lint
pixi run -e default test
pixi run -e default typecheck
pixi run -e default validate-skills
pixi run -e default skillspector   # NVIDIA SkillSpector security scan (Docker)
cd tools/asctl && go build ./... && go test -race -count=1 ./... && go vet ./...
cd skills/jules/scripts && make build && make test && make lint
```

## Code style

Formatted by ruff; run `pixi run format` before committing. Go code uses `gofmt`.

## PR instructions

Add a changie fragment before merge: `changie new`.
Pre-commit / pre-push hooks run via lefthook. Run `lefthook install` once.
On pre-push, NVIDIA SkillSpector scans `skills/` via Docker (requires Docker; also
run in CI). It is **informational** — it reports findings but does not block the
push or gate the PR; CI uploads the same findings as SARIF to the Security tab.
Override the pinned version with `SKILLSPECTOR_REF`, or skip with `SKILLSPECTOR_SKIP=1`.
