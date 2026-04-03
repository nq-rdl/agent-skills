"""Repository-level validation helpers for skills/ content."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from .errors import SkillError
from .parser import read_properties
from .prompt import to_prompt
from .validator import validate


def iter_skill_dirs(skills_root: Path) -> list[Path]:
    """Return immediate child directories under the skills root."""
    if not skills_root.is_dir():
        return []

    return sorted(path for path in skills_root.iterdir() if path.is_dir())


def skill_dir_from_path(path: Path, skills_root: Path) -> Path | None:
    """Map a path under skills/ to its top-level skill directory."""
    resolved_path = path.resolve(strict=False)
    resolved_root = skills_root.resolve(strict=False)

    try:
        relative = resolved_path.relative_to(resolved_root)
    except ValueError:
        return None

    if not relative.parts:
        return None

    skill_dir = skills_root / relative.parts[0]
    if skill_dir.exists() and not skill_dir.is_dir():
        return None

    return skill_dir


def resolve_skill_dirs(paths: Sequence[Path], skills_root: Path) -> list[Path]:
    """Resolve changed paths to the set of skill directories to validate."""
    if not paths:
        return iter_skill_dirs(skills_root)

    selected: list[Path] = []
    for path in paths:
        skill_dir = skill_dir_from_path(path, skills_root)
        if skill_dir is not None and skill_dir not in selected:
            selected.append(skill_dir)

    return sorted(selected)


def validate_skill_dirs(skill_dirs: Sequence[Path]) -> list[str]:
    """Validate skill directories and ensure prompt generation still works."""
    errors: list[str] = []

    for skill_dir in skill_dirs:
        problems = validate(skill_dir)
        if problems:
            errors.extend(f"{skill_dir}: {problem}" for problem in problems)
            continue

        try:
            read_properties(skill_dir)
        except SkillError as exc:
            errors.append(f"{skill_dir}: {exc}")

    if errors:
        return errors

    try:
        to_prompt(list(skill_dirs))
    except SkillError as exc:
        errors.append(f"prompt generation failed: {exc}")

    return errors


def main(argv: Sequence[str] | None = None) -> int:
    """Run repository-level skill validation."""
    args = list(argv) if argv is not None else sys.argv[1:]
    skills_root = Path("skills")

    if not skills_root.is_dir():
        print(f"Skills root not found: {skills_root}", file=sys.stderr)
        return 1

    skill_dirs = resolve_skill_dirs([Path(arg) for arg in args], skills_root)
    if not skill_dirs:
        print("No skill directories selected for validation.")
        return 0

    errors = validate_skill_dirs(skill_dirs)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"Validated {len(skill_dirs)} skill(s) and generated <available_skills> XML.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
