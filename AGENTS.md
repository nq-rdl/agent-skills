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
cd skills/pi-rpc/scripts && make build && make test && make lint
cd tools/asctl && go build ./... && go test -race -count=1 ./... && go vet ./...
cd skills/jules/scripts && make build && make test && make lint
```

## Testing instructions

The file-format skills (`csv`, `docx`, `xlsx`, `pdf`) each have an isolated pixi environment. Run that skill's `test`, `lint`, and `typecheck` tasks directly:

```bash
pixi run -e csv test
pixi run -e csv lint
pixi run -e csv typecheck
pixi run -e docx test
pixi run -e docx lint
pixi run -e docx typecheck
pixi run -e xlsx test
pixi run -e xlsx lint
pixi run -e xlsx typecheck
pixi run -e pdf test
pixi run -e pdf lint
pixi run -e pdf typecheck
```

## Code style

Formatted by ruff; run `pixi run format` before committing. Go code uses `gofmt`.

## PR instructions

Add a changie fragment before merge: `changie new`.
Pre-commit / pre-push hooks run via lefthook. Run `lefthook install` once.
