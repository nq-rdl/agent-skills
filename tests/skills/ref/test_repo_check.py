from pathlib import Path

from skills.ref.repo_check import (
    resolve_skill_dirs,
    skill_dir_from_path,
    validate_skill_dirs,
)


def _write_skill(skill_dir: Path, description: str = "A test skill") -> None:
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: {skill_dir.name}
description: {description}
---
# {skill_dir.name}
"""
    )


def test_skill_dir_from_nested_file(tmp_path):
    skills_root = tmp_path / "skills"
    nested_file = skills_root / "demo-skill" / "references" / "notes.md"
    nested_file.parent.mkdir(parents=True)
    nested_file.write_text("notes")

    assert skill_dir_from_path(nested_file, skills_root) == skills_root / "demo-skill"


def test_resolve_skill_dirs_defaults_to_all_immediate_dirs(tmp_path):
    skills_root = tmp_path / "skills"
    (skills_root / "alpha").mkdir(parents=True)
    (skills_root / "beta").mkdir()

    assert resolve_skill_dirs([], skills_root) == [
        skills_root / "alpha",
        skills_root / "beta",
    ]


def test_skill_dir_from_root_level_file_returns_none(tmp_path):
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    readme = skills_root / "README.md"
    readme.write_text("overview")

    assert skill_dir_from_path(readme, skills_root) is None


def test_validate_skill_dirs_accepts_valid_skills(tmp_path):
    skills_root = tmp_path / "skills"
    alpha = skills_root / "alpha"
    beta = skills_root / "beta"
    _write_skill(alpha)
    _write_skill(beta)

    assert validate_skill_dirs([alpha, beta]) == []


def test_validate_skill_dirs_reports_invalid_skill(tmp_path):
    skills_root = tmp_path / "skills"
    invalid = skills_root / "invalid"
    invalid.mkdir(parents=True)

    errors = validate_skill_dirs([invalid])

    assert errors == [f"{invalid}: Missing required file: SKILL.md"]
