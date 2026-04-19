# Contributing to agent-skills

Thank you for contributing! This guide walks you through the process.

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:

   ```bash
   git clone git@github.com:<your-user>/agent-skills.git
   cd agent-skills
   ```

3. **Install dependencies** (requires [pixi](https://pixi.sh)):

   ```bash
   pixi install
   ```

4. **Install git hooks** (requires [lefthook](https://lefthook.dev)):

   ```bash
   lefthook install
   ```

   Hooks cover Go (vet, format, build) and Python (lint, typecheck, validate-skills)
   on `pre-commit`, and all tests on `pre-push`.

## Making Changes

1. Create a feature branch from `main`:

   ```bash
   git checkout -b feat/my-change main
   ```

2. Make your changes — skills live in `skills/`, Go tooling in `tools/` and skill
   `scripts/` directories, Python tooling in `src/`.

3. **Add a changie fragment** (required for every PR):

   ```bash
   changie new
   ```

   This creates a YAML file in `.changes/unreleased/`. Pick the kind
   (`Added`, `Changed`, `Deprecated`, `Removed`, or `Fixed`) and write a
   short description of your change. See [Changie fragments](#changie-fragments)
   below for details.

4. Commit your work. Lefthook hooks will automatically run:
   - **Go** — `go vet`, `gofmt`, `go build` for each module (pi-rpc, jules, asctl)
   - **Skill validation** — checks `SKILL.md` frontmatter and structure
   - **Ruff lint & format** — enforces Python code style
   - **ty typecheck** — Python type checking via Astral ty
   - **Lock-file check** — ensures `pixi.lock` stays in sync
   - **Link check** — verifies URLs in skill files (requires [lychee](https://github.com/lycheeverse/lychee) on PATH)

   If a hook fails, fix the issue and commit again.

## Development Workflows

### Go skills

Each Go skill has its own module. Build and test independently:

```bash
cd skills/pi-rpc/scripts && make build && make test
cd skills/jules/scripts  && make build && make test
cd tools/asctl           && go build ./... && go test -race ./...
```

The root `go.work` unifies all modules for IDE support and `go test ./...` from root.

### Python skills

Each Python skill (`csv`, `docx`, `xlsx`, `pdf`) has its own pixi environment:

```bash
pixi run -e csv      test       # run csv skill tests
pixi run -e csv      lint       # ruff lint csv skill
pixi run -e csv      typecheck  # ty typecheck csv skill
pixi run -e docx     test
pixi run -e xlsx     test
pixi run -e pdf      test
```

Global Python tooling (validation, testing `src/`):

```bash
pixi run test            # pytest
pixi run lint            # ruff check
pixi run typecheck       # ty check src/ skills/
pixi run validate-skills # validate all skill SKILL.md files
```

### TDD workflow

Use the `/tdd` skill when modifying any skill. The cycle is:

1. Write a failing test
2. Implement until green
3. Refactor

For Go: `go test -race -count=1 ./...` from the module directory.
For Python: `pixi run -e <skill> test` from the repo root.

## Changie Fragments

We use [changie](https://changie.dev) to manage our changelog. Every PR
**must** include at least one unreleased fragment file in
`.changes/unreleased/`.

### Creating a fragment

```bash
changie new
```

If you don't have changie installed, you can create the file manually:

```yaml
# .changes/unreleased/<unique-name>.yaml
kind: Added
body: Short description of what changed.
```

Use one of these kinds: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`.

### Why fragments?

Each change gets its own file, so multiple PRs never conflict on the same
changelog line. At release time the fragments are batched into `CHANGELOG.md`.

### CI enforcement

A GitHub Actions check will **fail your PR** if no new fragment is found in
`.changes/unreleased/`. If your PR is purely internal (CI config, docs typo,
etc.) and genuinely needs no changelog entry, add the `skip-changelog` label
to the PR.

## Submitting a Pull Request

1. Push your branch to your fork:

   ```bash
   git push origin feat/my-change
   ```

2. Open a Pull Request against `main` on
   [nq-rdl/agent-skills](https://github.com/nq-rdl/agent-skills).

3. CI will run:
   - **Skill validation** — same checks as pre-commit, on all skills
   - **Go CI** — build + test for each Go module
   - **Changelog check** — verifies a changie fragment exists

4. Address any review feedback, then your PR will be merged.

## Validating Locally

Run the full validation suite before pushing:

```bash
pixi run validate-skills   # validate all skills
pixi run lint               # ruff lint
pixi run typecheck          # ty typecheck
pixi run test               # pytest
lefthook run pre-commit     # run all pre-commit hooks
lefthook run pre-push       # run all pre-push hooks (includes tests)
```
