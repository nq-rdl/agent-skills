# AGENTS.md

Agent guidance for this repository. Use this alongside the README for project context specific to coding agents.

## Setup commands

```bash
pixi install
```

## Build, test, lint

```bash
pixi run format
pixi run lint
pixi run test
pixi run typecheck
pixi run validate-skills
cd skills/pi-rpc/scripts && make build test lint
cd tools/asctl && make build test lint
cd skills/jules/scripts && make build test lint
```

## Testing instructions

The file-format skills (`csv`, `docx`, `xlsx`, `pdf`) each have an isolated pixi environment:

```bash
pixi run -e csv test
pixi run -e docx test
pixi run -e xlsx test
pixi run -e pdf test
```

## Code style

Formatted by ruff; run `pixi run format` before committing. Go code uses `gofmt`.

## PR instructions

Add a changie fragment before merge: `changie new`.
Pre-commit / pre-push hooks run via lefthook. Run `lefthook install` once.
