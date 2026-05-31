# Skill Grouping (Strategy B) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let the canonical `skills/` source tree group related skills under one subdirectory (e.g. `skills/sql-review/analysis/SKILL.md`) so the repo stays tidy as multi-step workflow plugins grow, while still producing clean `/<plugin>:<skill>` names after packaging.

**Architecture:** Teach the two canonical validators (Go + Python) and the `agent-extensions` sync layer to understand **exactly one** optional level of grouping: a directory directly under `skills/` is either a *skill* (it has a `SKILL.md`) or a *group* (no `SKILL.md`, but its immediate children are skills). At plugin-vendoring time the group prefix is **flattened away** so the installed plugin keeps the one-level `skills/<leaf>/SKILL.md` layout that Claude Code actually discovers. The two-repo split is **kept** (see "Why two repos" below); only the per-skill path convention changes.

**Tech Stack:** Go (`tools/asctl`), Python (`src/skills/ref`), Bash + Python (`agent-extensions/scripts/sync-plugins.sh`), GitHub Actions YAML, registry bundle YAML, `marketplace.json`.

---

## Decision & cross-repo grouping contract (settled 2026-05-31)

**Decision:** our packaging pipeline targets **Claude Code only.** `agent-skills` stays the canonical source and keeps each `SKILL.md` compliant with the [Agent Skills standard](https://agentskills.io) so other hosts *can* consume individual skills — but **how non-Claude hosts consume the tree is out of scope for our automation.** This lets `agent-extensions` flatten/transform freely for Claude Code's one-level plugin model without hedging for other hosts.

**This is Path B (shared source + sync), NOT Path A.** We keep the skills repo; we are *not* authoring plugins directly in extensions. The Claude-Code-only assumption only removes multi-host constraints from the extensions side.

**The contract both repos must honor (this is what makes automation possible):**

1. **`agent-skills` source** — a skill is either
   - flat: `skills/<skill>/SKILL.md` (standalone, unchanged), or
   - grouped: `skills/<group>/<skill>/SKILL.md` — **exactly one level**; the group folder has no direct `SKILL.md`.
   The **group folder name == the Claude Code plugin name.**
2. **`agent-extensions` registry** — a bundle sets `pluginName: <group>` and lists members as `<group>/<skill>`.
3. **`agent-extensions` sync** — `sync-plugins.sh` copies `skills/<group>/<skill>/` → `plugins/<group>/skills/<skill>/`, **dropping the `<group>/` prefix**.
4. **Claude Code** — installs `plugins/<group>/skills/<skill>/SKILL.md` as **`/<group>:<skill>`**.
5. **Both repos' validators enforce the layout** — skills-repo `repo-check` (Go + Python) descends one level into groups; extensions `validate-bundles` resolves path-qualified entries and rejects duplicate leaf names within a bundle.

**What `agent-skills` looks like going forward:**

```
skills/
├── csv/SKILL.md                # flat standalone — unchanged
├── tdd/SKILL.md                # flat standalone — unchanged
└── sql-review/                 # GROUP (= plugin name); no SKILL.md here
    ├── analysis/SKILL.md
    ├── lint/SKILL.md
    └── report/SKILL.md
```

**How `agent-extensions` deals with it:**

```
registry/bundles/sql-review.yaml   pluginName: sql-review
                                   skills: [sql-review/analysis, sql-review/lint, sql-review/report]
        │  sync-plugins.sh   (drops the "sql-review/" prefix → leaf only)
        ▼
plugins/sql-review/skills/{analysis,lint,report}/SKILL.md
        │  marketplace.json  { name: sql-review, source: ./plugins/sql-review }
        ▼
Claude Code   /sql-review:analysis   /sql-review:lint   /sql-review:report
```

Flat standalone skills (`csv`, `tdd`, …) keep mapping to whatever plugin their bundle assigns, exactly as today — **grouping is additive, not a migration.**

---

## Understanding Strategy B (read this first)

You asked to understand B, not just run it. Here is the whole mental model in five facts.

1. **Two repos, one direction of flow.** `agent-skills` (this repo) is the *canonical source*: every skill is a directory `skills/<name>/SKILL.md`. `agent-extensions` is the *Claude Code packaging layer*: it has `plugins/`, a `registry/bundles/*.yaml` that says which skills go in which plugin, and a `.claude-plugin/marketplace.json`. A scheduled workflow (`sync-skills.yml`) copies a tagged release of `agent-skills/skills/` into `agent-extensions/skills/`, then `sync-plugins.sh` vendors real copies into `plugins/<plugin>/skills/`.

2. **The `:` namespace is invented by the plugin, not by folders.** `/sql-review:analysis` means *plugin `sql-review`* + *skill `analysis`*. Claude Code discovers plugin skills **one level deep** — `plugins/<plugin>/skills/<x>/SKILL.md` → `/<plugin>:<x>` (confirmed in `agent-extensions/plugins/hooks/scripts/forced-eval-hook.sh:197`, which scans `skills/*/SKILL.md` and keys as `<plugin>:<leaf>`). Anything deeper, like `plugins/<plugin>/skills/group/x/SKILL.md`, is **never registered** — it just rides along as dead files. The nested `skills/duckdb/query/SKILL.md` in this repo proves it: only `dataops:duckdb` (the *top-level* `SKILL.md`) registers; the 9 nested ones are inert.

3. **So "grouping" can only live in the SOURCE tree, and must be flattened before it becomes a plugin.** A "group" in `agent-skills` maps to a **plugin** in `agent-extensions`. `skills/sql-review/analysis/` (source) must become `plugins/sql-review/skills/analysis/` (vendored, one level) to yield `/sql-review:analysis`. The group name (`sql-review`) becomes the *plugin* name; it is dropped from the skill path.

4. **Today, grouping breaks in two places.** Both are one-level scanners that also require a *direct* `SKILL.md`:
   - **CI validator** (`tools/asctl` Go, run by `.github/workflows/skills-validation.yml` → `asctl repo-check`; mirrored by Python `src/skills/ref/repo_check.py`). `IterSkillDirs` reads only immediate children and `validator.Validate` returns `"missing required file: SKILL.md"` for a dir without one — so a group dir `skills/sql-review/` (no direct `SKILL.md`) fails CI immediately.
   - **The vendor step** (`agent-extensions/scripts/sync-plugins.sh:78-80`) builds `dst` from the *full* registry entry, so a `sql-review/analysis` entry would copy to `plugins/.../skills/sql-review/analysis` (two levels) and never register.

5. **The fix is small and bounded.** Teach the validators to descend exactly one level into group dirs, and teach the vendor step to flatten the group prefix (`dst` uses the *leaf* name). That is the entire idea. Everything below is the careful version of those two edits, plus the housekeeping they imply (stale-copy cleanup, duplicate-leaf guard, docs).

### Key design decision: exactly one level of nesting

A directory directly under `skills/` is classified as:
- a **skill** if it directly contains `SKILL.md` (today's layout — unchanged), or
- a **group** if it has no `SKILL.md` but its immediate children are skills.

We do **not** support arbitrary recursion (no `skills/a/b/c/SKILL.md`). One level keeps names unambiguous, keeps the validators simple, and matches the only thing Claude Code can consume after flattening. If you ever need deeper organization, that is a separate, larger decision — out of scope here.

### Why two repos (don't merge)

The monorepo option was evaluated and rejected. `agent-skills` is intentionally **host-neutral** (its README frames skills as portable across agent implementations); `agent-extensions` is **Claude-Code-specific packaging** (its `docs/ARCHITECTURE.md` calls it a Claude Code extension catalog). `agent-extensions/docs/reviews/2026-05-31-two-repo-consolidation-review.md` already concluded the same: keep the split, fix the *sync* pain via versioned consumption, not by merging. This plan therefore changes only the path convention, on both sides of the existing split.

---

## Cross-repo PR strategy (important for "pick it up later")

This is **two PRs**, because the change spans two repos and the sync consumes a *released tag* of `agent-skills`:

- **PR 1 — `agent-skills`** (this repo): validator changes (Go + Python) + tests, then the new grouped source skills (`skills/sql-review/*`). Merge, then cut a release tag (the existing release flow). Grouped source can only land *after* the validators accept it, so do the validator tasks first within this PR.
- **PR 2 — `agent-extensions`**: `sync-plugins.sh` flattening + duplicate-leaf guard, `sync-skills.yml` grouped cleanup, the duplicate-leaf check in `validate.yml`, the new `registry/bundles/sql-review.yaml`, the `marketplace.json` entry, and doc updates. This PR's CI sync pulls the `agent-skills` release from PR 1, so **PR 1 must merge + release first** (or, for local testing, point sync at a branch — see Task 11).

Within each PR, commit per task (TDD where tests exist). Keep both PRs in **draft** until the end-to-end check in Task 12 passes.

> This plan document lives in PR 1 (`agent-skills/docs/plans/`). Open PR 1 as a draft containing just this doc first if you want a tracking surface before any code lands.

---

## File change map

**`agent-skills` (PR 1)**
| File | Responsibility | Change |
| --- | --- | --- |
| `tools/asctl/internal/repocheck/repocheck.go` | CI skill discovery (authoritative) | `IterSkillDirs` + `SkillDirFromPath` descend one level into group dirs |
| `tools/asctl/internal/repocheck/repocheck_test.go` | Discovery tests | Add grouped-layout cases |
| `src/skills/ref/repo_check.py` | Legacy/parallel validator | Mirror the Go behavior |
| `tests/...` (Python) | Discovery tests | Add grouped-layout cases (locate existing repo_check tests) |
| `skills/sql-review/<step>/SKILL.md` | New grouped source skills | Create the workflow steps |
| `docs/plans/2026-05-31-skill-grouping.md` | This plan | Created |

**`agent-extensions` (PR 2)**
| File | Responsibility | Change |
| --- | --- | --- |
| `scripts/sync-plugins.sh` | Vendor skills into plugins | `dst` uses leaf name; prune keep-set uses leaf names; duplicate-leaf guard |
| `.github/workflows/sync-skills.yml` | Mirror upstream skills | Grouped-aware cleanup before `cp -r` |
| `.github/workflows/validate.yml` | Bundle validation (PR gate) | Add duplicate-leaf-per-bundle error |
| `registry/bundles/sql-review.yaml` | Declare the plugin | New bundle, path-qualified skill entries |
| `.claude-plugin/marketplace.json` | Publish the plugin | Add `sql-review` plugin entry |
| `AGENTS.md` (and any docs saying `skills/<name>/`) | Contributor docs | Document the optional group layout |

---

## Phase 1 — `agent-skills`: teach the validators (PR 1)

### Task 1: Go discovery — descend into group dirs

**Files:**
- Modify: `tools/asctl/internal/repocheck/repocheck.go`
- Test: `tools/asctl/internal/repocheck/repocheck_test.go`

- [ ] **Step 1: Write failing tests for grouped discovery**

Append to `tools/asctl/internal/repocheck/repocheck_test.go`:

```go
// makeGroupedSkill creates root/group/leaf/SKILL.md (group has no direct SKILL.md).
func makeGroupedSkill(t *testing.T, root, group, leaf, description string) string {
	t.Helper()
	dir := filepath.Join(root, group, leaf)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	content := "---\nname: " + leaf + "\ndescription: " + description + "\n---\n"
	if err := os.WriteFile(filepath.Join(dir, "SKILL.md"), []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	return dir
}

func TestIterSkillDirs_grouped(t *testing.T) {
	root := t.TempDir()
	makeSkillDir(t, root, "csv", "flat skill")          // skills/csv/
	makeGroupedSkill(t, root, "sql-review", "analysis", "A") // skills/sql-review/analysis/
	makeGroupedSkill(t, root, "sql-review", "lint", "B")     // skills/sql-review/lint/

	dirs, err := repocheck.IterSkillDirs(root)
	if err != nil {
		t.Fatal(err)
	}
	want := []string{
		filepath.Join(root, "csv"),
		filepath.Join(root, "sql-review", "analysis"),
		filepath.Join(root, "sql-review", "lint"),
	}
	if len(dirs) != len(want) {
		t.Fatalf("got %d dirs %v, want %d", len(dirs), dirs, len(want))
	}
	for i := range want {
		if dirs[i] != want[i] {
			t.Errorf("dirs[%d] = %q, want %q", i, dirs[i], want[i])
		}
	}
}

func TestSkillDirFromPath_grouped(t *testing.T) {
	root := t.TempDir()
	makeGroupedSkill(t, root, "sql-review", "analysis", "A")

	got, ok := repocheck.SkillDirFromPath(
		filepath.Join(root, "sql-review", "analysis", "SKILL.md"), root)
	if !ok {
		t.Fatal("expected to resolve grouped skill path")
	}
	if want := filepath.Join(root, "sql-review", "analysis"); got != want {
		t.Errorf("got %q, want %q (must be the leaf, not the group)", got, want)
	}
}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd tools/asctl && go test ./internal/repocheck/ -run 'Grouped' -v`
Expected: FAIL — `TestIterSkillDirs_grouped` returns the group dir `sql-review` (1 dir) instead of the two leaves; `TestSkillDirFromPath_grouped` returns `.../sql-review` not `.../sql-review/analysis`.

- [ ] **Step 3: Implement one-level group descent**

In `tools/asctl/internal/repocheck/repocheck.go`, add a helper and rewrite the two functions. The `parser` package is already imported.

```go
// hasSkillMD reports whether dir directly contains a SKILL.md/skill.md.
func hasSkillMD(dir string) bool {
	return parser.FindSkillMD(dir) != ""
}

// IterSkillDirs returns every skill directory under skillsRoot, sorted.
// A child of skillsRoot is a SKILL if it directly contains SKILL.md; otherwise
// it is treated as a GROUP and its immediate children that contain SKILL.md are
// skills. Grouping is supported to exactly one level (skills/<group>/<skill>/).
func IterSkillDirs(skillsRoot string) ([]string, error) {
	entries, err := os.ReadDir(skillsRoot)
	if err != nil {
		return nil, err
	}
	var dirs []string
	for _, e := range entries {
		if !e.IsDir() {
			continue
		}
		top := filepath.Join(skillsRoot, e.Name())
		if hasSkillMD(top) {
			dirs = append(dirs, top)
			continue
		}
		children, err := os.ReadDir(top)
		if err != nil {
			return nil, err
		}
		for _, c := range children {
			if c.IsDir() && hasSkillMD(filepath.Join(top, c.Name())) {
				dirs = append(dirs, filepath.Join(top, c.Name()))
			}
		}
	}
	sort.Strings(dirs)
	return dirs, nil
}

// SkillDirFromPath maps any path under skillsRoot to the skill directory that
// owns it: the top-level dir if it is a flat skill, or the depth-2 leaf if the
// top-level dir is a group. Returns "", false if no skill owns the path.
func SkillDirFromPath(path, skillsRoot string) (string, bool) {
	absPath, err := filepath.Abs(path)
	if err != nil {
		return "", false
	}
	absRoot, err := filepath.Abs(skillsRoot)
	if err != nil {
		return "", false
	}
	rel, err := filepath.Rel(absRoot, absPath)
	if err != nil {
		return "", false
	}
	if rel == ".." || strings.HasPrefix(rel, ".."+string(filepath.Separator)) {
		return "", false
	}
	parts := strings.SplitN(rel, string(filepath.Separator), 3)
	if len(parts) == 0 || parts[0] == "" || parts[0] == "." {
		return "", false
	}
	top := filepath.Join(skillsRoot, parts[0])
	info, err := os.Stat(top)
	if err != nil || !info.IsDir() {
		return "", false
	}
	if hasSkillMD(top) {
		return top, true
	}
	if len(parts) >= 2 && parts[1] != "" {
		leaf := filepath.Join(top, parts[1])
		if li, err := os.Stat(leaf); err == nil && li.IsDir() && hasSkillMD(leaf) {
			return leaf, true
		}
	}
	return "", false
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd tools/asctl && go test ./internal/repocheck/ -v`
Expected: PASS, including the pre-existing `TestIterSkillDirs_sorted`, `TestResolveSkillDirs_*`, `TestValidateSkillDirs_*` (flat layout must still work).

- [ ] **Step 5: Run the full asctl suite + vet**

Run: `cd tools/asctl && go build ./... && go test -race -count=1 ./... && go vet ./...`
Expected: all green.

- [ ] **Step 6: Commit**

```bash
git add tools/asctl/internal/repocheck/repocheck.go tools/asctl/internal/repocheck/repocheck_test.go
git commit -m "feat(asctl): discover one level of skill grouping in repo-check"
```

### Task 2: Python discovery — mirror the Go behavior

**Files:**
- Modify: `src/skills/ref/repo_check.py`
- Test: locate the existing repo_check tests first

- [ ] **Step 1: Locate the Python validator tests**

Run: `rg -l "repo_check|iter_skill_dirs|skill_dir_from_path" --glob '*test*.py'`
Expected: a test module (e.g. `tests/test_repo_check.py` or `src/skills/ref/tests/...`). If none exists, create `tests/test_repo_check_grouping.py`. Read the matched file to match its fixture style before writing.

- [ ] **Step 2: Write failing tests for grouped discovery**

Add (adapt paths/imports to the located test module):

```python
from pathlib import Path
from skills.ref.repo_check import iter_skill_dirs, skill_dir_from_path


def _make_skill(root: Path, *parts: str) -> Path:
    d = root.joinpath(*parts)
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(
        f"---\nname: {parts[-1]}\ndescription: x\n---\n"
    )
    return d


def test_iter_skill_dirs_grouped(tmp_path: Path):
    _make_skill(tmp_path, "csv")
    _make_skill(tmp_path, "sql-review", "analysis")
    _make_skill(tmp_path, "sql-review", "lint")
    got = iter_skill_dirs(tmp_path)
    assert got == [
        tmp_path / "csv",
        tmp_path / "sql-review" / "analysis",
        tmp_path / "sql-review" / "lint",
    ]


def test_skill_dir_from_path_grouped(tmp_path: Path):
    _make_skill(tmp_path, "sql-review", "analysis")
    got = skill_dir_from_path(
        tmp_path / "sql-review" / "analysis" / "SKILL.md", tmp_path
    )
    assert got == tmp_path / "sql-review" / "analysis"
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `pixi run -e default test` (or `pytest <located test file> -v`)
Expected: FAIL — current `iter_skill_dirs` returns `[csv, sql-review]`; `skill_dir_from_path` returns `.../sql-review`.

- [ ] **Step 4: Implement the mirror in `src/skills/ref/repo_check.py`**

Add `find_skill_md` to the existing parser import and replace the two functions:

```python
from .parser import find_skill_md, read_properties


def _has_skill_md(d: Path) -> bool:
    return find_skill_md(d) is not None


def iter_skill_dirs(skills_root: Path) -> list[Path]:
    """Return skill directories under skills_root (one optional group level)."""
    if not skills_root.is_dir():
        return []
    dirs: list[Path] = []
    for top in sorted(p for p in skills_root.iterdir() if p.is_dir()):
        if _has_skill_md(top):
            dirs.append(top)
            continue
        for child in sorted(p for p in top.iterdir() if p.is_dir()):
            if _has_skill_md(child):
                dirs.append(child)
    return dirs


def skill_dir_from_path(path: Path, skills_root: Path) -> Path | None:
    """Map a path under skills/ to its owning skill dir (flat or grouped leaf)."""
    resolved_path = path.resolve(strict=False)
    resolved_root = skills_root.resolve(strict=False)
    try:
        relative = resolved_path.relative_to(resolved_root)
    except ValueError:
        return None
    if not relative.parts:
        return None
    top = skills_root / relative.parts[0]
    if not top.is_dir():
        return None
    if _has_skill_md(top):
        return top
    if len(relative.parts) >= 2:
        leaf = top / relative.parts[1]
        if leaf.is_dir() and _has_skill_md(leaf):
            return leaf
    return None
```

Note: `iter_skill_dirs` previously returned `sorted(... iterdir ...)`. The new version still returns a flat sorted-ish list; flat skills and grouped leaves are appended in top-level sorted order, which matches the Go ordering used in Task 1's expectations.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pixi run -e default test`
Expected: PASS, including any pre-existing repo_check tests (flat layout unaffected).

- [ ] **Step 6: Lint + typecheck**

Run: `pixi run -e default lint && pixi run -e default typecheck`
Expected: clean (note `src/skills/ref` may be lint-excluded per `pyproject.toml`; run anyway to confirm no new errors).

- [ ] **Step 7: Commit**

```bash
git add src/skills/ref/repo_check.py tests/
git commit -m "feat(repo-check): mirror one-level skill grouping in python validator"
```

### Task 3: Prove the full validator path on a grouped sample

**Files:** none (uses a throwaway dir)

- [ ] **Step 1: Create a temporary grouped skill and validate it**

Run:
```bash
mkdir -p skills/sql-review/analysis
printf -- '---\nname: analysis\ndescription: Analyze a SQL change for correctness and performance. Use when reviewing SQL.\n---\n\nAnalyze the SQL diff.\n' > skills/sql-review/analysis/SKILL.md
cd tools/asctl && go run ./cmd/asctl repo-check; cd ..
```
Expected: `repo-check` validates the new grouped skill (it appears as a discovered dir) and exits 0. It must NOT report `skills/sql-review: missing required file: SKILL.md`.

- [ ] **Step 2: Clean up the probe (real steps land in Phase 3)**

Run: `rm -rf skills/sql-review`
Expected: tree clean. (Phase 3 recreates these as real skills.)

---

## Phase 2 — `agent-extensions`: flatten on vendor + housekeeping (PR 2)

> Switch repos: `cd /home/schnetlerr/dev/nq-rdl/agent-extensions`. Branch from the latest `agent-skills` release pin (see Task 11 for local testing without a release).

### Task 4: Flatten the group prefix in `sync-plugins.sh`

**Files:**
- Modify: `agent-extensions/scripts/sync-plugins.sh`

- [ ] **Step 1: Make `dst` use the leaf name**

In `sync_skill()` (currently lines 78-94), change `src`/`dst` so the destination drops the group prefix:

```python
def sync_skill(plugin: str, skill: str, bundle_file: Path) -> None:
    src = repo / "skills" / skill            # may be "group/leaf" or "flat"
    leaf = Path(skill).name                  # "leaf" or "flat"
    dst = repo / "plugins" / plugin / "skills" / leaf
    if not src.is_dir():
        warn(
            bundle_file,
            f"Skill '{skill}' has no source skills/{skill}/ — skipped. "
            "Point registry/bundles at an existing skill or remove the entry.",
        )
        return
    if dst.is_symlink() or dst.is_file():
        dst.unlink()
    elif dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, symlinks=False)
    print(f"  ✓ skill {skill} -> {leaf}")
```

- [ ] **Step 2: Make the prune keep-set use leaf names**

In the per-bundle loop (currently line 127), change the skills keep-set:

```python
    prune_entries(repo / "plugins" / plugin / "skills", {Path(s).name for s in skills})
```

(Leave the agents prune-set as-is.)

- [ ] **Step 3: Add a duplicate-leaf guard**

Immediately after `skills = list(data.get("skills") or [])` (line 124), fail fast if two entries flatten to the same leaf within one plugin:

```python
    leaves = [Path(s).name for s in skills]
    dupes = sorted({leaf for leaf in leaves if leaves.count(leaf) > 1})
    if dupes:
        warn(
            bundle_file,
            f"Duplicate skill leaf name(s) {dupes} in bundle '{bundle}': "
            "two grouped skills would collide at plugins/"
            f"{plugin}/skills/<leaf>. Rename one source skill.",
        )
        skills = []  # skip this bundle's skills; validate-bundles (Task 6) fails the PR
```

- [ ] **Step 4: Verify the script still syncs flat skills unchanged**

Run: `python3 -m pip install --user pyyaml >/dev/null 2>&1; bash scripts/sync-plugins.sh dataops`
Expected: `dataops` re-syncs with `✓ skill csv -> csv` etc.; `git status plugins/dataops` shows no diff (flat behavior unchanged).

- [ ] **Step 5: Commit**

```bash
git add scripts/sync-plugins.sh
git commit -m "feat(sync): flatten grouped source skills to one-level plugin skills"
```

### Task 5: Grouped-aware cleanup in `sync-skills.yml`

**Files:**
- Modify: `agent-extensions/.github/workflows/sync-skills.yml`

- [ ] **Step 1: Replace the flat cleanup loop**

Replace lines 51-54 (the `for dir in skills/*/` loop) with a grouped-aware removal that runs before `cp -r`:

```yaml
          # Remove previously-vendored skills (flat skills/<x>/ AND grouped
          # skills/<group>/<x>/), preserving any non-skill files, then re-copy.
          find skills -mindepth 2 -maxdepth 3 -name SKILL.md -printf '%h\0' \
            | xargs -0 -r rm -rf
          # Drop now-empty group containers so renamed/removed groups don't linger.
          find skills -mindepth 1 -maxdepth 1 -type d -empty -delete

          # Copy fresh skills from agent-skills/skills/ → skills/
          cp -r /tmp/agent-skills/skills/* skills/
```

Rationale: `SKILL.md` sits at depth 2 for flat (`skills/csv/SKILL.md`) and depth 3 for grouped (`skills/sql-review/analysis/SKILL.md`); `%h` yields the owning skill dir for both. The second `find` removes a group dir only once it is empty.

- [ ] **Step 2: Dry-run the cleanup logic locally**

Run (in a scratch copy, not the real `skills/`):
```bash
tmp=$(mktemp -d); mkdir -p "$tmp/skills/csv" "$tmp/skills/grp/leaf"
printf 'x' > "$tmp/skills/csv/SKILL.md"; printf 'x' > "$tmp/skills/grp/leaf/SKILL.md"
( cd "$tmp" && find skills -mindepth 2 -maxdepth 3 -name SKILL.md -printf '%h\0' | xargs -0 -r rm -rf && find skills -mindepth 1 -maxdepth 1 -type d -empty -delete )
find "$tmp/skills" ; rm -rf "$tmp"
```
Expected: both `skills/csv` and `skills/grp` are gone; `skills/` is empty.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/sync-skills.yml
git commit -m "fix(sync-skills): grouped-aware cleanup before re-copy"
```

### Task 6: Duplicate-leaf check in the bundle validator (PR gate)

**Files:**
- Modify: `agent-extensions/.github/workflows/validate.yml`

- [ ] **Step 1: Add the dup check to validate-bundles**

In the inline Python (the loop over `data.get("skills")`, around line 40-46), after the existing `is_dir()` check, add a per-bundle leaf-collision check. Insert before the `for name in data.get("skills")` loop:

```python
              skill_entries = data.get("skills") or []
              leaves = [Path(name).name for name in skill_entries]
              for leaf in sorted({x for x in leaves if leaves.count(x) > 1}):
                  print(f"::error file={bundle}::Duplicate skill leaf '{leaf}' — grouped skills would collide in one plugin")
                  exit_code = 1
              for name in skill_entries:
                  if not (repo / "skills" / name).is_dir():
                      print(f"::error file={bundle}::Skill '{name}' not found in skills/")
                      exit_code = 1
                  else:
                      print(f"  ✓ skill:{name}")
```

(The `(repo / "skills" / name).is_dir()` check already resolves path-qualified entries like `sql-review/analysis`, so no other change is needed there.)

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/validate.yml
git commit -m "feat(validate-bundles): reject duplicate grouped skill leaf names"
```

---

## Phase 3 — Scaffold the `sql-review` plugin end-to-end

> This is the lowest-risk demonstration: a brand-new grouped plugin (no existing installs to break). Source skills land in PR 1; bundle + marketplace land in PR 2.

### Task 7: Create the grouped source skills (`agent-skills`, PR 1)

**Files:**
- Create: `skills/sql-review/<step>/SKILL.md` for each step

- [ ] **Step 1: Create the first step skill**

```bash
mkdir -p skills/sql-review/analysis
```
Create `skills/sql-review/analysis/SKILL.md`:

```markdown
---
name: analysis
description: Analyze a SQL change for correctness, performance, and schema impact. Use when reviewing a SQL diff or migration before merge.
---

# SQL Review — Analysis

Given a SQL diff, report: correctness risks, performance/index implications, and schema/migration safety. Output findings as a prioritized list.
```

- [ ] **Step 2: Create the remaining step skills**

Repeat Step 1 for each workflow step, one directory each under `skills/sql-review/`. Use a short, namespace-free `name:` (the directory basename is what becomes the plugin skill name after flattening; keep them equal to avoid confusion). Example set — adjust to the real workflow:

```bash
for step in lint plan migrate-safety rollback report; do
  mkdir -p "skills/sql-review/$step"
done
```
Then author each `SKILL.md` with `name: <step>` and a real description. **No placeholder bodies** — write the actual instructions for each step before committing.

- [ ] **Step 3: Validate the grouped plugin source**

Run: `cd tools/asctl && go run ./cmd/asctl repo-check; cd ..` and `pixi run -e default validate-skills`
Expected: both pass; each `skills/sql-review/<step>` is discovered and validated; no "missing required file" for `skills/sql-review`.

- [ ] **Step 4: Commit (PR 1)**

```bash
git add skills/sql-review
git commit -m "feat(skills): add grouped sql-review workflow skills"
```

### Task 8: Declare the plugin bundle (`agent-extensions`, PR 2)

**Files:**
- Create: `agent-extensions/registry/bundles/sql-review.yaml`

- [ ] **Step 1: Write the bundle with path-qualified skill entries**

```yaml
id: sql-review
displayName: SQL Review
description: Multi-step SQL change review workflow — analysis, lint, migration safety.
owners:
  - rdl
channels:
  - stable
skills:
  - sql-review/analysis
  - sql-review/lint
  - sql-review/plan
  - sql-review/migrate-safety
  - sql-review/rollback
  - sql-review/report
hooks: []
prompts: []
mcp: []
targets:
  claude:
    enabled: true
    pluginName: sql-review
    marketplaceName: rdl
```

(Match the `skills:` list to the directories created in Task 7.)

- [ ] **Step 2: Commit**

```bash
git add registry/bundles/sql-review.yaml
git commit -m "feat(registry): add sql-review bundle with grouped skill entries"
```

### Task 9: Publish the plugin in the marketplace (`agent-extensions`, PR 2)

**Files:**
- Modify: `agent-extensions/.claude-plugin/marketplace.json`

- [ ] **Step 1: Add the plugin entry**

Add to the `plugins` array:

```json
    {
      "name": "sql-review",
      "source": "./plugins/sql-review",
      "description": "Multi-step SQL change review workflow — analysis, lint, migration safety",
      "version": "0.8.0",
      "keywords": ["sql", "review", "migration", "workflow"]
    }
```

- [ ] **Step 2: Validate JSON**

Run: `jq . .claude-plugin/marketplace.json >/dev/null && echo OK`
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat(marketplace): publish sql-review plugin"
```

### Task 10: Update contributor docs

**Files:**
- Modify: `agent-extensions/AGENTS.md` (the `skills/<name>/` description near line 121) and any other doc asserting a flat-only layout (grep first).

- [ ] **Step 1: Find every doc that documents the flat layout**

Run: `rg -n "skills/<name>/|skills/<skill-name>/|skills/\*/SKILL" --glob '*.md'`
Expected: a short list including `AGENTS.md`.

- [ ] **Step 2: Document the optional one-level group**

Edit each hit to state: a skill is `skills/<name>/SKILL.md` **or** a grouped skill is `skills/<group>/<name>/SKILL.md` (one level only); grouped skills are referenced in a bundle as `<group>/<name>` and install as `/<plugin>:<name>`.

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md <other docs>
git commit -m "docs: document optional one-level skill grouping"
```

---

## Phase 4 (verification) — prove it installs as `/sql-review:analysis`

### Task 11: Run the real sync into the plugin tree

**Files:** none (runs the sync script)

- [ ] **Step 1: Point the sync at PR 1's branch/tag (or merged release)**

If PR 1 is merged + released, the scheduled `sync-skills.yml` will pull it. For local end-to-end testing before release, manually mirror the grouped source into `agent-extensions/skills/` (the same thing `sync-skills.yml` does), e.g.:

```bash
# from agent-extensions, with agent-skills checked out adjacent:
cp -r ../agent-skills/skills/sql-review skills/
```

- [ ] **Step 2: Vendor into the plugin**

Run: `bash scripts/sync-plugins.sh sql-review`
Expected: `Syncing sql-review -> plugins/sql-review` then `✓ skill sql-review/analysis -> analysis`, etc.

- [ ] **Step 3: Confirm the vendored tree is ONE level**

Run: `find plugins/sql-review/skills -name SKILL.md | sort`
Expected: `plugins/sql-review/skills/analysis/SKILL.md`, `.../lint/SKILL.md`, … — **no** `plugins/sql-review/skills/sql-review/...` nesting.

### Task 12: Confirm Claude Code discovery

**Files:** none

- [ ] **Step 1: Load the plugin locally**

Run: `claude --plugin-dir ./plugins/sql-review`
Then in-session: `/help` and look for the `sql-review` namespace.

- [ ] **Step 2: Invoke a grouped skill**

In-session: `/sql-review:analysis`
Expected: the skill loads. Confirms group→plugin flattening produced the intended `/<plugin>:<skill>` name.

- [ ] **Step 3: Mark both draft PRs ready**

Once Tasks 1–12 pass, flip PR 1 and PR 2 from draft to ready, ensuring PR 1 merges/releases before PR 2's CI sync runs.

---

## Optional follow-up — migrate `obsidian` to a group

Currently `skills/obsidian-bases`, `skills/obsidian-cli`, `skills/obsidian-markdown` are flat. Grouping them to `skills/obsidian/bases`, `skills/obsidian/cli`, `skills/obsidian/markdown` is mechanically identical to Phase 3, **but it is a rename**: if these skills are already bundled/published, their install names change (e.g. an existing `<plugin>:obsidian-bases` becomes `obsidian:bases`). That is a breaking change for anyone who invokes them. Do this only after: (a) confirming whether they're currently in a bundle, and (b) deciding whether the name change is acceptable. Treat as a separate PR pair with a changelog note. Out of scope for the initial rollout.

---

## Risks & open decisions

- **Two-level-only is a deliberate cap.** If a future workflow wants `skills/a/b/c/`, revisit the design — don't quietly extend recursion in the validators.
- **Duplicate leaves across *different* plugins are fine** (each plugin namespaces independently); only *within one bundle* do they collide. The guards (Tasks 3/6) enforce exactly that scope.
- **`${CLAUDE_SKILL_DIR}` / bundled scripts** keep working — flattening only changes the parent path, and skills reference their own dir via the env var, not a hardcoded path.
- **Release ordering** is the main operational gotcha: PR 1 must be consumable (merged + released, or branch-pinned for testing) before PR 2's sync runs, or the sync warns "no source" and skips the skills.
- **Decision to confirm before Phase 3:** the real list and names of the `sql-review` workflow steps. The plan uses `analysis/lint/plan/migrate-safety/rollback/report` as a placeholder set — replace with the actual steps.

---

## Self-review

- **Spec coverage:** validators (Tasks 1-2), vendor flatten (Task 4), cleanup (Task 5), dup guard (Tasks 3+6), docs (Task 10), scaffold + publish (Tasks 7-9), end-to-end proof (Tasks 11-12), obsidian caveat (follow-up). All four Codex-confirmed fix steps + the three missed hops (dual validators, duplicate-leaf detection, docs) are covered.
- **Backward compatibility:** flat skills still validate (Task 1 Step 4, Task 2 Step 5), still vendor unchanged (Task 4 Step 4), and path-qualified bundle entries pass the existing `is_dir()` check (no change needed in validate.yml beyond the dup guard).
- **Naming consistency:** `IterSkillDirs`/`iter_skill_dirs`, `SkillDirFromPath`/`skill_dir_from_path`, `hasSkillMD`/`_has_skill_md`, and `Path(skill).name` (the "leaf") are used consistently across Go, Python, and the sync script.
