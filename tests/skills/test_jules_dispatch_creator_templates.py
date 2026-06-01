"""Structural tests for the jules-dispatch-creator workflow templates.

The templates are GitHub Actions workflow YAML containing [PLACEHOLDER] tokens
that the skill fills in at generation time. The tokens sit in string/scalar
positions, so the templates parse as valid YAML as-is.

YAML 1.1 gotcha: GitHub Actions' `on:` key parses to the boolean key ``True``
(``yaml.safe_load`` returns keys ``['name', True, 'jobs']``), so trigger lookups
use that key, not the string ``"on"``.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

TEMPLATES_DIR = (
    Path(__file__).resolve().parents[2] / "skills" / "jules-dispatch-creator" / "templates"
)

# Canonical @jules-* handle set for issue_comment (mention-dispatch) workflows.
# Adding a handle here makes the guard-completeness test enforce it everywhere.
MENTION_HANDLES = ("swe", "security", "docs", "infra", "review", "skills")

# Mention-dispatch templates mapped to the handle each one triggers on.
MENTION_TEMPLATES = {
    "jules-swe-dispatch.yml.tmpl": "swe",
    "jules-security-dispatch.yml.tmpl": "security",
    "jules-docs-dispatch.yml.tmpl": "docs",
    "jules-infra-dispatch.yml.tmpl": "infra",
}

# Templates whose triggers can fire repeatedly/automatically and so need a
# concurrency group to avoid overlapping or duplicate Jules sessions. Mention
# templates are excluded: a human types one mention at a time.
CONCURRENCY_TEMPLATES = (
    "jules-scheduled.yml.tmpl",
    "jules-ci-review-dispatch.yml.tmpl",
    "jules-label-dispatch.yml.tmpl",
    "jules-issue-lifecycle.yml.tmpl",
)

# Every template the skill ships, mapped to the trigger key expected in its
# `on:` block (which parses to the boolean key True). For `issues` triggers the
# value also names the event type that must appear under `types:`.
EXPECTED_TRIGGERS = {
    "jules-swe-dispatch.yml.tmpl": ("issue_comment", None),
    "jules-security-dispatch.yml.tmpl": ("issue_comment", None),
    "jules-docs-dispatch.yml.tmpl": ("issue_comment", None),
    "jules-infra-dispatch.yml.tmpl": ("issue_comment", None),
    "jules-ci-review-dispatch.yml.tmpl": ("workflow_run", None),
    "jules-label-dispatch.yml.tmpl": ("issues", "labeled"),
    "jules-scheduled.yml.tmpl": ("schedule", None),
    "jules-issue-lifecycle.yml.tmpl": ("issues", "closed"),
}

PINNED_JULES_ACTION = re.compile(r"nq-rdl/jules-action@[0-9a-f]{40}")


def _read(name: str) -> str:
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")


def _on_block(doc: dict):
    # `on:` becomes the boolean key True under YAML 1.1.
    return doc.get(True, doc.get("on"))


@pytest.mark.parametrize("name", sorted(EXPECTED_TRIGGERS))
def test_template_file_exists(name):
    assert (TEMPLATES_DIR / name).is_file(), f"missing template: {name}"


@pytest.mark.parametrize("name", sorted(EXPECTED_TRIGGERS))
def test_template_parses_as_yaml(name):
    doc = yaml.safe_load(_read(name))
    assert isinstance(doc, dict)
    assert "jobs" in doc
    assert _on_block(doc) is not None


@pytest.mark.parametrize("name", sorted(EXPECTED_TRIGGERS))
def test_template_declares_expected_trigger(name):
    trigger, event_type = EXPECTED_TRIGGERS[name]
    on = _on_block(yaml.safe_load(_read(name)))
    assert trigger in on, f"{name}: expected trigger {trigger!r} in {sorted(on)}"
    if event_type is not None:
        types = on[trigger].get("types", [])
        assert event_type in types, f"{name}: expected {event_type!r} in types {types}"
    if name == "jules-scheduled.yml.tmpl":
        assert "workflow_dispatch" in on, f"{name}: scheduled must allow manual runs"


@pytest.mark.parametrize("name", sorted(EXPECTED_TRIGGERS))
def test_template_uses_nq_rdl_conventions(name):
    text = _read(name)
    assert PINNED_JULES_ACTION.search(text), f"{name}: missing pinned nq-rdl/jules-action"
    assert "secrets.[SECRET_NAME]" in text, f"{name}: missing [SECRET_NAME] placeholder"
    assert "[PROMPT CONTENT]" in text, f"{name}: missing [PROMPT CONTENT] placeholder"
    # Must not copy the upstream example's invocation or secret name.
    assert "google-labs-code/jules-invoke" not in text
    assert "secrets.JULES_API_KEY" not in text


@pytest.mark.parametrize("name", sorted(MENTION_TEMPLATES))
def test_mention_guard_completeness(name):
    text = _read(name)
    own = MENTION_TEMPLATES[name]
    assert f"contains(github.event.comment.body, '@jules-{own}')" in text, (
        f"{name}: must trigger on its own handle @jules-{own}"
    )
    for other in MENTION_HANDLES:
        if other == own:
            continue
        assert f"!contains(github.event.comment.body, '@jules-{other}')" in text, (
            f"{name}: must guard against @jules-{other}"
        )


@pytest.mark.parametrize("name", CONCURRENCY_TEMPLATES)
def test_repeatable_templates_have_concurrency(name):
    assert "concurrency:" in _read(name), (
        f"{name}: a repeatable/automatic trigger needs a concurrency group to "
        f"avoid overlapping Jules sessions"
    )


def test_issue_lifecycle_matrix_is_fail_safe():
    # Unblocked issues are independent work — one failing dispatch must not
    # cancel the others, so the matrix must opt out of fail-fast.
    text = _read("jules-issue-lifecycle.yml.tmpl")
    assert "fail-fast: false" in text, (
        "jules-issue-lifecycle.yml.tmpl: matrix over independent issues must set fail-fast: false"
    )


@pytest.mark.parametrize("name", sorted(EXPECTED_TRIGGERS))
def test_no_fixed_heredoc_delimiter(name):
    # SKILL.md rule: never use a fixed heredoc delimiter for issue content.
    text = _read(name)
    for bad in ("<<EOF", "<<'EOF'", "ISSUE_EOF"):
        assert bad not in text, f"{name}: fixed heredoc delimiter {bad!r} is injection-prone"
    # Any bash heredoc writing to GITHUB_OUTPUT must use a random delimiter.
    if '"$GITHUB_OUTPUT"' in text and "<<" in text:
        assert "openssl rand -hex 8" in text, (
            f"{name}: bash heredoc to GITHUB_OUTPUT must use a random delimiter"
        )
