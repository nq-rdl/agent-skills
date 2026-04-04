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

4. **Install pre-commit hooks**:

   ```bash
   pixi run hooks-install
   ```

## Making Changes

1. Create a feature branch from `main`:

   ```bash
   git checkout -b feat/my-change main
   ```

2. Make your changes — skills live in `skills/`, tooling in `src/`.

3. **Add a changie fragment** (required for every PR):

   ```bash
   changie new
   ```

   This creates a YAML file in `.changes/unreleased/`. Pick the kind
   (`Added`, `Changed`, `Deprecated`, `Removed`, or `Fixed`) and write a
   short description of your change. See [Changie fragments](#changie-fragments)
   below for details.

4. Commit your work. Pre-commit hooks will automatically run:
   - **Skill validation** — checks `SKILL.md` frontmatter and structure
   - **Ruff lint & format** — enforces Python code style
   - **Lock-file check** — ensures `pixi.lock` stays in sync

   If a hook fails, fix the issue and commit again.

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
   - **Changelog check** — verifies a changie fragment exists

4. Address any review feedback, then your PR will be merged.

## Validating Locally

Run the full validation suite before pushing:

```bash
pixi run validate-skills   # validate all skills
pixi run lint               # ruff lint
pixi run test               # pytest
pixi run hooks-run          # run all pre-commit hooks
```

## Code of Conduct

Be respectful and constructive. We're all here to build useful agent skills.
