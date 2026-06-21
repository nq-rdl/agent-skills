"""TDD suite for the repo's .devcontainer (local/Codespaces parity).

Static, deterministic, Docker-free checks that lock the devcontainer's contract
so a future edit cannot silently break it. Claude Code on the web does NOT build
from .devcontainer (custom base images are unsupported on web), so this only
guards the local/Codespaces developer experience.

Runs under pytest (CI: ``pixi run test`` / the lefthook ``python-test`` job) and
also as a plain script (``python3 tests/test_devcontainer.py``) for environments
without pytest. An optional Docker-based build smoke test lives separately and is
NOT part of this gating suite.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEVC = REPO / ".devcontainer"
DEVCONTAINER_JSON = DEVC / "devcontainer.json"
DOCKERFILE = DEVC / "Dockerfile"
FIREWALL = DEVC / "init-firewall.sh"
SETUP = DEVC / "setup.sh"

# Hosts the firewall must allow for the container's documented runtime workflow:
# Claude Code (api.anthropic.com + telemetry), npm, and the pixi/Python channels
# the Dockerfile + setup.sh rely on. GitHub is covered separately via the
# api.github.com/meta bootstrap (see test_firewall_allows_github_meta).
REQUIRED_FIREWALL_HOSTS = (
    "api.anthropic.com",
    "registry.npmjs.org",
    "pypi.org",
    "files.pythonhosted.org",
    "conda.anaconda.org",
    "repo.prefix.dev",
    "statsig.anthropic.com",
    "sentry.io",
)


def _load_devcontainer() -> dict:
    return json.loads(DEVCONTAINER_JSON.read_text(encoding="utf-8"))


def _version_tuple(text: str) -> tuple[int, ...]:
    """Normalize a dotted version (e.g. '1.25.0') to an int tuple for comparison,
    so '1.25' and '1.25.0' are handled without brittle string equality."""
    return tuple(int(p) for p in re.findall(r"\d+", text))


# --------------------------------------------------------------------------- #
# 1. Config validity + wiring
# --------------------------------------------------------------------------- #
def test_devcontainer_json_parses():
    assert DEVCONTAINER_JSON.is_file(), "missing .devcontainer/devcontainer.json"
    _load_devcontainer()  # raises on invalid JSON


def test_build_dockerfile_exists():
    cfg = _load_devcontainer()
    dockerfile = cfg.get("build", {}).get("dockerfile")
    assert dockerfile, "devcontainer.json build.dockerfile not set"
    assert (DEVC / dockerfile).is_file(), f"build.dockerfile {dockerfile!r} not found"


def test_postcreate_runs_setup():
    cfg = _load_devcontainer()
    assert "setup.sh" in (cfg.get("postCreateCommand") or ""), \
        "postCreateCommand must run setup.sh"


def test_poststart_runs_firewall():
    cfg = _load_devcontainer()
    assert "init-firewall.sh" in (cfg.get("postStartCommand") or ""), \
        "postStartCommand must run init-firewall.sh"


def test_waitfor_is_poststart():
    # Wait for the firewall to come up before the user/agent starts working.
    cfg = _load_devcontainer()
    assert cfg.get("waitFor") == "postStartCommand", \
        "waitFor must gate on postStartCommand so the firewall is active first"


def test_net_admin_capability_present():
    # iptables/ipset in init-firewall.sh require NET_ADMIN. (NET_RAW is also
    # currently granted; whether it is needed is a separate review item — this
    # test asserts only the firewall-required capability so it is not brittle.)
    cfg = _load_devcontainer()
    run_args = cfg.get("runArgs") or []
    assert "--cap-add=NET_ADMIN" in run_args, \
        "runArgs must grant --cap-add=NET_ADMIN for the iptables firewall"


def test_remote_user_and_workspace():
    cfg = _load_devcontainer()
    assert cfg.get("remoteUser") == "node", "remoteUser must be 'node'"
    assert cfg.get("workspaceFolder") == "/workspace", "workspaceFolder must be /workspace"


def test_named_volume_mount_targets():
    # The Claude config + bash history persist via named volumes; assert both
    # mount targets are declared so a refactor cannot silently drop persistence.
    cfg = _load_devcontainer()
    mounts = " ".join(cfg.get("mounts") or [])
    assert "/home/node/.claude" in mounts, "missing named-volume mount for /home/node/.claude"
    assert "/commandhistory" in mounts, "missing named-volume mount for command history"


def test_claude_code_extension_declared():
    cfg = _load_devcontainer()
    exts = cfg.get("customizations", {}).get("vscode", {}).get("extensions", [])
    assert "anthropic.claude-code" in exts, "anthropic.claude-code VS Code extension not declared"


# --------------------------------------------------------------------------- #
# 2. Firewall: fail-closed + allowlist
# --------------------------------------------------------------------------- #
def test_firewall_default_deny():
    text = FIREWALL.read_text(encoding="utf-8")
    assert re.search(r"iptables\s+-P\s+OUTPUT\s+DROP", text), \
        "init-firewall.sh must set a default-DROP OUTPUT policy (fail closed)"


def test_firewall_final_reject():
    text = FIREWALL.read_text(encoding="utf-8")
    assert re.search(r"OUTPUT\s+-j\s+REJECT", text), \
        "init-firewall.sh must REJECT unmatched outbound traffic"


def test_firewall_allows_github_meta():
    text = FIREWALL.read_text(encoding="utf-8")
    assert "api.github.com/meta" in text, \
        "init-firewall.sh must bootstrap GitHub ranges from api.github.com/meta"


def test_firewall_allowlist_hosts():
    text = FIREWALL.read_text(encoding="utf-8")
    missing = [h for h in REQUIRED_FIREWALL_HOSTS if h not in text]
    assert not missing, f"firewall allowlist missing required hosts: {missing}"


def test_firewall_self_verification():
    # The script must prove it is fail-closed at runtime, not merely mention the
    # hosts. A bare substring check passes even if the verification logic is
    # inverted or deleted, so assert the actual control flow:
    #   * reaching example.com is treated as FAILURE (curl success -> exit 1)
    #   * api.github.com being UNreachable is treated as FAILURE (! curl -> exit 1)
    # The `exit 1` must live in the `then` body: `(?:(?!else|fi)[\s\S])*?` forbids
    # the match from crossing an `else`/`fi` boundary, so moving the `exit 1` into
    # the `else` branch (inverting the guard) no longer satisfies the test.
    text = FIREWALL.read_text(encoding="utf-8")
    then_body = r"(?:(?!\b(?:else|fi)\b)[\s\S])*?"
    assert re.search(
        rf"if\s+curl[^\n]*example\.com[^\n]*;\s*then\b{then_body}\bexit 1\b",
        text,
    ), "init-firewall.sh must fail (exit 1) in the then-branch if it can reach the blocked host example.com"
    assert re.search(
        rf"if\s+!\s+curl[^\n]*api\.github\.com[^\n]*;\s*then\b{then_body}\bexit 1\b",
        text,
    ), "init-firewall.sh must fail (exit 1) in the then-branch if it cannot reach the allowed host api.github.com"


# --------------------------------------------------------------------------- #
# 3. Dockerfile <-> repo coherence + privilege
# --------------------------------------------------------------------------- #
def test_go_version_matches_repo():
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    m = re.search(r"ARG\s+GO_VERSION=([\w.]+)", dockerfile)
    assert m, "Dockerfile must pin GO_VERSION"
    repo_go = (REPO / ".go-version").read_text(encoding="utf-8").strip()
    assert _version_tuple(m.group(1)) == _version_tuple(repo_go), (
        f"Dockerfile GO_VERSION {m.group(1)} != .go-version {repo_go} "
        "(devcontainer Go would drift from go.work's toolchain)"
    )


def test_dockerfile_installs_required_tools():
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    # A bare `needle in dockerfile` substring check yields false positives (e.g.
    # "gh" matches "lefthook" / a URL), so it can't actually lock the install
    # contract. Assert the real install STEP for each tool instead.

    # apt packages must be listed inside the `apt-get install` block, each as its
    # own package entry — not merely present somewhere in the file.
    m = re.search(r"apt-get\s+install\b[^\n]*\\\n(.*?)&&", dockerfile, re.DOTALL)
    assert m, "Dockerfile must contain an apt-get install block"
    apt_block = m.group(1)
    for pkg in ("gh", "sudo"):
        assert re.search(rf"^\s*{re.escape(pkg)}\s*\\?\s*$", apt_block, re.M), \
            f"Dockerfile apt-get install block must list {pkg!r} as its own package"

    # The remaining tools come from release tarballs / installers / npm — assert
    # the actual install STEP for each. These are regexes (not bare substrings)
    # so a tool named only in a comment can't satisfy the check: claude-code and
    # lefthook must appear on the `npm install` line, not in the prose above it.
    install_steps = {
        "changie": r"wget[^\n]*changie/releases",
        "pixi": r"curl[^\n]*pixi\.sh/install\.sh",
        "claude-code": r"npm install[^\n]*@anthropic-ai/claude-code",
        "lefthook": r"npm install[^\n]*lefthook@",
    }
    for tool, pattern in install_steps.items():
        assert re.search(pattern, dockerfile), \
            f"Dockerfile does not install {tool!r} (no line matching {pattern!r})"


def test_firewall_copied_and_sudoers_least_privilege():
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    assert re.search(r"COPY\s+init-firewall\.sh\s+/usr/local/bin", dockerfile), \
        "Dockerfile must COPY init-firewall.sh to /usr/local/bin/"
    # The node user may run ONLY the firewall script as root, by exact absolute
    # path — no broader NOPASSWD grant.
    assert "NOPASSWD: /usr/local/bin/init-firewall.sh" in dockerfile, \
        "sudoers must NOPASSWD only the exact /usr/local/bin/init-firewall.sh path"


# --------------------------------------------------------------------------- #
# 4. Shell scripts are syntactically valid
# --------------------------------------------------------------------------- #
def test_shell_scripts_parse():
    bash = shutil.which("bash")
    assert bash, "bash not available to syntax-check the devcontainer scripts"
    for script in (FIREWALL, SETUP):
        r = subprocess.run([bash, "-n", str(script)], capture_output=True, text=True)
        assert r.returncode == 0, f"{script.name} failed `bash -n`: {r.stderr}"


# --------------------------------------------------------------------------- #
# Plain-script runner (for environments without pytest). pytest ignores this.
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import traceback

    fns = sorted(
        (n, f) for n, f in list(globals().items())
        if n.startswith("test_") and callable(f)
    )
    passed = failed = 0
    for name, fn in fns:
        try:
            fn()
            print(f"  PASS  {name}")
            passed += 1
        except Exception as exc:  # noqa: BLE001 - report any assertion/parse failure
            print(f"  FAIL  {name}: {exc}")
            traceback.print_exc()
            failed += 1
    print(f"\ndevcontainer: {passed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)
