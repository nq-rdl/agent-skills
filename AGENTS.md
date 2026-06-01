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
cd tools/asctl && go build ./... && go test -race -count=1 ./... && go vet ./...
cd skills/jules/scripts && make build && make test && make lint
```

## Code style

Formatted by ruff; run `pixi run format` before committing. Go code uses `gofmt`.

## PR instructions

Add a changie fragment before merge: `changie new`.
Pre-commit / pre-push hooks run via lefthook. Run `lefthook install` once.
