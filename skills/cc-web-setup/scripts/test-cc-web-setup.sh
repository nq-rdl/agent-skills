#!/usr/bin/env bash
# scripts/test-cc-web-setup.sh
# Tests for assets/cc-web-setup.sh (the portable pre-snapshot setup script shipped
# by the cc-web-setup skill).
#
# The plugin pre-seed runs against a stubbed `claude` CLI that records every
# subcommand it sees, so the tests assert WHICH marketplaces/plugins are seeded
# (defaults + CC_WEB_* overrides), the no-claude path, and that the optional
# project hook (cc-web-setup.local.sh) is sourced. Run via the harness or by hand.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="${HERE}/../assets/cc-web-setup.sh"
PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); echo "  PASS  $*"; }
fail() { FAIL=$((FAIL+1)); echo "  FAIL  $*"; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/cc-web-setup-test.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

# A `claude` stub that appends every invocation's args to $CLAUDE_LOG. The path is
# passed via env so the same stub works across scenarios.
make_claude_stub() { # <dir>
  local dir="$1"
  cat >"$dir/claude" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$CLAUDE_LOG"
exit 0
EOF
  chmod +x "$dir/claude"
}

new_bin() { # build a PATH dir with coreutils + optional claude
  local d tool real; d="$(mktemp -d "$WORK/bin.XXXXXX")"
  for tool in bash printf cat rm mkdir dirname grep head touch; do
    real="$(command -v "$tool" 2>/dev/null || true)"; [ -n "$real" ] && ln -s "$real" "$d/$tool"
  done
  echo "$d"
}

# run_setup <bin_dir> <project_dir> <out> [env assignments...] — execute the REAL
# script as a subprocess (so main() runs) with an isolated PATH/PROJECT_DIR.
run_setup() {
  local bin="$1" proj="$2" out="$3"; shift 3
  # shellcheck disable=SC2163  # "$@" holds KEY=val assignments to export, intentional
  ( export PATH="$bin" CLAUDE_PROJECT_DIR="$proj" TMPDIR="$WORK" "$@"; bash "$SCRIPT" ) >"$out" 2>&1
}

# --- Test 1: defaults -> seeds rdl marketplace + rdl@rdl ---------------------
test_defaults() {
  local bin proj out clog; bin="$(new_bin)"; proj="$(mktemp -d "$WORK/p1.XXXXXX")"; out="$WORK/t1.out"
  make_claude_stub "$bin"; clog="$WORK/t1-claude.log"; : > "$clog"
  run_setup "$bin" "$proj" "$out" "CLAUDE_LOG=$clog" && ok "defaults: exit 0" || fail "defaults: non-zero exit"
  grep -q 'plugin marketplace add nq-rdl/agent-extensions' "$clog" \
    && ok "defaults: registered the rdl marketplace (nq-rdl/agent-extensions)" \
    || fail "defaults: did not register rdl marketplace. Log: $(cat "$clog")"
  grep -q 'plugin install rdl@rdl --scope project' "$clog" \
    && ok "defaults: pre-seeded rdl@rdl" \
    || fail "defaults: did not pre-seed rdl@rdl. Log: $(cat "$clog")"
}

# --- Test 2: CC_WEB_* overrides honored --------------------------------------
test_overrides() {
  local bin proj out clog; bin="$(new_bin)"; proj="$(mktemp -d "$WORK/p2.XXXXXX")"; out="$WORK/t2.out"
  make_claude_stub "$bin"; clog="$WORK/t2-claude.log"; : > "$clog"
  run_setup "$bin" "$proj" "$out" "CLAUDE_LOG=$clog" \
    "CC_WEB_MARKETPLACES=acme/plugins|acme" "CC_WEB_PLUGINS=foo@acme bar@acme" \
    && ok "overrides: exit 0" || fail "overrides: non-zero exit"
  grep -q 'plugin marketplace add acme/plugins' "$clog" \
    && ok "overrides: registered the overridden marketplace" \
    || fail "overrides: override marketplace not used. Log: $(cat "$clog")"
  grep -q 'plugin install foo@acme --scope project' "$clog" && grep -q 'plugin install bar@acme --scope project' "$clog" \
    && ok "overrides: pre-seeded both overridden plugins" \
    || fail "overrides: override plugins not used. Log: $(cat "$clog")"
  grep -q 'rdl@rdl' "$clog" \
    && fail "overrides: still seeded the default rdl@rdl (override ignored)" \
    || ok "overrides: defaults were replaced, not appended"
}

# --- Test 3: no claude on PATH -> skip pre-seed, still exit 0 -----------------
test_no_claude() {
  local bin proj out; bin="$(new_bin)"; proj="$(mktemp -d "$WORK/p3.XXXXXX")"; out="$WORK/t3.out"
  # No claude stub on this PATH.
  run_setup "$bin" "$proj" "$out" && ok "no-claude: exit 0" || fail "no-claude: non-zero exit"
  grep -q 'claude CLI not on PATH' "$out" \
    && ok "no-claude: logged the skip" \
    || fail "no-claude: did not log the skip. Out: $(cat "$out")"
}

# --- Test 4: project hook sourced --------------------------------------------
test_local_hook() {
  local bin proj out clog; bin="$(new_bin)"; proj="$(mktemp -d "$WORK/p4.XXXXXX")"; out="$WORK/t4.out"
  make_claude_stub "$bin"; clog="$WORK/t4-claude.log"; : > "$clog"
  mkdir -p "$proj/scripts"
  printf 'touch "%s/t4-sentinel"\n' "$WORK" > "$proj/scripts/cc-web-setup.local.sh"
  rm -f "$WORK/t4-sentinel"
  run_setup "$bin" "$proj" "$out" "CLAUDE_LOG=$clog" >/dev/null \
    && ok "local-hook: exit 0 when project hook succeeds" \
    || fail "local-hook: non-zero exit. Out: $(cat "$out")"
  [ -e "$WORK/t4-sentinel" ] \
    && ok "local-hook: cc-web-setup.local.sh was sourced" \
    || fail "local-hook: project hook not sourced. Out: $(cat "$out")"
}

# --- Test 5: sourceable (main-guard) -----------------------------------------
test_sourceable() {
  # Sourcing must NOT run main(): define globals only. Assert MARKETPLACES exists
  # and main() did not exit the shell.
  # shellcheck disable=SC1090
  ( set +e; source "$SCRIPT"; [ "${MARKETPLACES[0]}" = "nq-rdl/agent-extensions|rdl" ] ) \
    && ok "sourceable: source defines globals without running main()" \
    || fail "sourceable: sourcing did not behave (main ran or globals missing)"
}

test_defaults
test_overrides
test_no_claude
test_local_hook
test_sourceable

echo ""
echo "cc-web-setup: ${PASS} passed, ${FAIL} failed"
[ "$FAIL" -eq 0 ]
