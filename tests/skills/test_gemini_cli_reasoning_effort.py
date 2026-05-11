"""Contract tests for the gemini-cli skill's reasoning-effort support (issue #99).

These tests pin down the structural promises of the skill so that future edits
can't silently drop the reasoning/thinking guidance. They run against the
checked-in skill files, not synthetic fixtures.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "skills" / "gemini-cli"
REFERENCE_FILE = SKILL_DIR / "references" / "reasoning-effort.rst"
SKILL_MD = SKILL_DIR / "SKILL.md"


@pytest.fixture(scope="module")
def reference_text() -> str:
    return REFERENCE_FILE.read_text()


@pytest.fixture(scope="module")
def skill_md_text() -> str:
    return SKILL_MD.read_text()


def test_reference_file_exists():
    assert REFERENCE_FILE.is_file(), (
        f"Expected {REFERENCE_FILE.relative_to(REPO_ROOT)} to exist — "
        "the skill must document Gemini's reasoning/thinking configuration."
    )


def test_reference_uses_rst_format(reference_text: str):
    # Heuristic: rst files use ==== / ---- underlines under headings, not # markers.
    assert "====" in reference_text or "----" in reference_text, (
        "reasoning-effort.rst should use reStructuredText section underlines "
        "to match the rest of references/ (automation.rst, headless.rst, cli-reference.rst)."
    )


@pytest.mark.parametrize(
    "concept",
    [
        "modelConfigs",
        "thinkingConfig",
        "thinkingBudget",
        "thinkingLevel",
        "settings.json",
    ],
)
def test_reference_covers_core_concept(reference_text: str, concept: str):
    assert concept in reference_text, (
        f"reasoning-effort.rst must mention `{concept}` — it's a load-bearing concept "
        "for Gemini's reasoning configuration."
    )


@pytest.mark.parametrize("model_id", ["gemini-2.5-pro", "gemini-3-pro-preview"])
def test_reference_names_both_model_families(reference_text: str, model_id: str):
    assert model_id in reference_text, (
        f"reasoning-effort.rst must name `{model_id}` — the parameter choice "
        "(thinkingBudget vs thinkingLevel) depends on the model family."
    )


@pytest.mark.parametrize("scope", ["customAliases", "overrides"])
def test_reference_covers_both_scopes(reference_text: str, scope: str):
    assert scope in reference_text, (
        f"reasoning-effort.rst must explain `{scope}` — users need to know "
        "whether to redefine an alias globally or override per-agent."
    )


def test_reference_documents_thinkingbudget_sentinels(reference_text: str):
    # The integer sentinels for Gemini 2.5 are -1 (dynamic), 0 (off), 8192 (default).
    for sentinel in ("-1", "8192"):
        assert sentinel in reference_text, (
            f"reasoning-effort.rst must document the `{sentinel}` thinkingBudget value."
        )


def test_reference_documents_thinkinglevel_enum(reference_text: str):
    for level in ("HIGH", "LOW"):
        assert level in reference_text, (
            f"reasoning-effort.rst must document the `{level}` thinkingLevel value."
        )


def test_reference_maps_reasoning_effort_concept(reference_text: str):
    # Users coming from OpenAI/Anthropic will search for `reasoning_effort` — the doc
    # must bridge that vocabulary to Gemini's `thinkingLevel`.
    assert "reasoning_effort" in reference_text or "reasoning effort" in reference_text, (
        "reasoning-effort.rst must reference `reasoning_effort` so users coming from "
        "OpenAI/Anthropic APIs can find the Gemini equivalent."
    )


def test_reference_warns_about_deep_merge(reference_text: str):
    # Clobbering unrelated keys (general, ide, security, ui) is the trap; the doc
    # should explicitly call out merging rather than overwriting.
    lower = reference_text.lower()
    assert "merge" in lower, (
        "reasoning-effort.rst must explain how to merge into existing settings.json "
        "without clobbering unrelated keys."
    )


def test_skill_md_links_reference(skill_md_text: str):
    assert "references/reasoning-effort.rst" in skill_md_text, (
        "SKILL.md must link to references/reasoning-effort.rst so Claude knows "
        "to load it when reasoning/thinking topics come up."
    )


@pytest.mark.parametrize(
    "phrase",
    ["reasoning", "thinking"],
)
def test_skill_md_description_includes_trigger_phrase(skill_md_text: str, phrase: str):
    # Extract the YAML frontmatter description so we don't accidentally match
    # a body mention that doesn't help triggering.
    parts = skill_md_text.split("---", 2)
    assert len(parts) >= 3, "SKILL.md is missing frontmatter"
    frontmatter = parts[1].lower()
    assert phrase in frontmatter, (
        f"SKILL.md frontmatter description must include `{phrase}` so the skill "
        "triggers on reasoning/thinking-related user prompts."
    )
