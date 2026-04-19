# Contributing to agent-skills

Thank you for contributing! This guide gets you from fork to PR.

## 1. Quick Start

Prerequisites: [pixi](https://pixi.sh), [lefthook](https://lefthook.dev), Go 1.25+
(pinned in `.go-version`), and [changie](https://changie.dev).

```bash
# 1. Fork + clone
git clone git@github.com:<your-user>/agent-skills.git
cd agent-skills

# 2. Python deps (for Python skills + dev tooling)
pixi install

# 3. Git hooks (runs on every commit + push)
lefthook install

# 4. Optional: build asctl for local skill validation
cd tools/asctl && go build -o /usr/local/bin/asctl ./cmd/asctl/ && cd -
```

From here, `git commit` triggers pre-commit hooks and `git push` triggers
pre-push tests automatically.

## 2. Repo Layout

```
agent-skills/
├── skills/                   # The skills themselves (52 of them)
│   ├── pi-rpc/               # Each skill = a directory with SKILL.md
│   │   ├── SKILL.md          # Frontmatter + body; the public contract
│   │   └── scripts/          # Per-skill runtime code (Go here: pi-server, pi-cli, pi-mcp)
│   ├── jules/scripts/        # Go skill
│   ├── csv/                  # Python skill (+ pyproject.toml for deps)
│   └── ...
├── tools/
│   └── asctl/                # Go CLI for skill validation + prompt rendering
│       ├── cmd/asctl/        # main package
│       └── internal/         # validator, parser, prompt, repocheck, frontmatter
├── src/skills/ref/           # Legacy Python validator (being replaced by asctl)
├── docs/skill-creation/      # Authoring guides for skill contributors
├── .changes/unreleased/      # Changie fragments (one YAML per PR)
├── go.work                   # Go workspace spanning all Go modules
├── lefthook.yml              # Hook config (Go + Python)
├── .goreleaser.yaml          # Multi-binary release matrix
└── pyproject.toml            # Python deps + per-skill pixi features
```

**Per-module `go.mod`** — each Go-bearing skill keeps its own module.
`go.work` only unifies the dev loop; modules publish independently.

## 3. Development Workflows

### Creating or editing a skill

Skills live in `skills/<name>/`. The required file is `SKILL.md` with YAML
frontmatter (`name`, `description`, optional `license`, `metadata`). See
`docs/skill-creation/` for the authoring guide.

### Go skills and tools

Each Go module (`skills/pi-rpc/scripts`, `skills/jules/scripts`, `tools/asctl`)
has its own `go.mod` and is built/tested independently:

```bash
cd skills/pi-rpc/scripts && make build && make test
cd tools/asctl           && go build ./... && go test -race ./...
```

From the repo root, `go.work` lets you test everything at once:

```bash
go test ./...
```

Follow the modern-Go patterns documented in
[`skills/modern-go-guidelines`](skills/modern-go-guidelines/) — `any` not
`interface{}`, `slices.Contains` not manual loops, `wg.Go()` not
`wg.Add(1)`/`wg.Done()`, `t.Context()` in tests, and so on.

### Python skills

The four file-format skills (`csv`, `docx`, `xlsx`, `pdf`) each have an
isolated pixi environment:

```bash
pixi run -e csv  test       # pytest for csv skill only
pixi run -e csv  lint       # ruff lint
pixi run -e csv  typecheck  # ty typecheck
pixi run -e docx test
pixi run -e xlsx test
pixi run -e pdf  test
```

### MCP servers

A skill that ships an MCP server lives as a Cobra subcommand in the skill's
`scripts/cmd/<name>-mcp/` directory. `skills/pi-rpc/scripts/cmd/pi-mcp/` is
the reference implementation — embeds the session manager directly, uses
`mark3labs/mcp-go` over stdio. See
[`docs/skill-creation/scripts-languages.mdx`](docs/skill-creation/scripts-languages.mdx)
for the pattern.

### TDD discipline

For any non-trivial change, run the `/tdd` skill workflow: write a failing
test first, implement until green, refactor. The `asctl` port from Python
follows this — every Python test case became a Go test before implementation.

Golden-file tests (see `tools/asctl/internal/prompt/`) are the preferred
pattern when output format stability matters.

### Using sibling skills during development

This repo's own skills help you work on it:

- `infra:lefthook` — hook config guidance
- `swe:tdd` — test-first workflow
- `swe:changie` — changelog fragments
- `astral:ty`, `astral:ruff` — Python static analysis
- `modern-go-guidelines:use-modern-go` — idiomatic Go by version
- `mcp-server-dev:build-mcp-server` — MCP server patterns

## 4. Validation & Testing

### Pre-commit hooks (run on every commit)

Lefthook runs these in parallel:

| Hook | What it checks |
|---|---|
| `go-vet-*` / `go-format-*` / `go-build-*` | Per-module Go vet, gofmt, build (pi-rpc, jules, asctl) |
| `ruff-lint` / `ruff-format` | Python style |
| `typecheck` | Python type checking via `ty` |
| `validate-skills` | SKILL.md frontmatter + structure |
| `pixi-lock-check` | `pixi.lock` stays in sync with `pyproject.toml` |
| `lychee-links` | URLs in skill `.md` files are reachable (optional — skips if `lychee` not on PATH) |

### Pre-push hooks (run on `git push`)

| Hook | What it checks |
|---|---|
| `go-test-*` | Full test suite per Go module, `-race -count=1` |
| `python-test` | `pytest` |

### Validating manually

```bash
# Full validation suite
asctl repo-check               # validate all skills (Go binary, <2s)
pixi run validate-skills       # same via legacy Python path (identical output)
pixi run typecheck             # ty check src/ skills/
pixi run lint                  # ruff check
pixi run test                  # pytest

# Run hook stages on demand
lefthook run pre-commit
lefthook run pre-push
```

**Note:** `asctl repo-check` and `pixi run validate-skills` currently both
work and produce identical output. Once `src/skills/ref/` is retired in a
follow-up PR, the pixi task will be dropped.

### What CI runs

Pull requests trigger:

- `.github/workflows/skills-validation.yml` — builds `asctl` and runs `asctl repo-check`
- Per-module Go test workflows (matrix across Go versions where applicable)
- Changelog check — fails the PR if no new fragment in `.changes/unreleased/`

## 5. Submitting Changes

### Branch + commit

```bash
git checkout -b feat/my-change main
# ... make changes ...
```

Use [conventional commits](https://www.conventionalcommits.org/):
`feat(pi-rpc): …`, `fix(asctl): …`, `chore: …`, `docs: …`.

### Add a changie fragment (required)

Every PR must include one YAML file in `.changes/unreleased/`:

```bash
changie new
```

If changie isn't installed, create manually:

```yaml
# .changes/unreleased/<unique-name>.yaml
kind: Added  # or Changed, Deprecated, Removed, Fixed, Security
body: Short description of what changed.
```

CI fails the PR if no new fragment is found. For purely internal changes
(CI config, typo fixes), add the `skip-changelog` label.

### Push + open PR

```bash
git push origin feat/my-change
# then open PR against main at nq-rdl/agent-skills
```

### Release process (maintainers)

Tagging `v*` triggers `.github/workflows/release.yml`:

1. Verifies the tag points to a commit on `main`
2. Batches unreleased changie fragments into `.changes/<version>.md`
3. Updates `CHANGELOG.md`, force-moves the tag to include the changelog commit
4. Runs `goreleaser` — builds all binaries (pi-server, pi-cli, pi-mcp, jules,
   asctl) for `linux/{amd64,arm64}` and `darwin/{amd64,arm64}`, uploads
   archives + checksums + SBOM to the GitHub Release
5. Dispatches `agent-skills-release` event to `agent-extensions` so the
   downstream plugin registry can pull the new artifacts

### Cross-repo note

Go binaries released here are consumed by
[`nq-rdl/agent-extensions`](https://github.com/nq-rdl/agent-extensions) via
GitHub Release assets. If you change a binary's CLI surface, coordinate with
the plugin manifest in `agent-extensions/plugins/dev-tools/`.
