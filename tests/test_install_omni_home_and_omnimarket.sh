#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# test_install_omni_home_and_omnimarket.sh (OMN-16259)
# ----------------------------------------------------------------------------
# Drives the REAL install.sh / Makefile / repos.yaml artifacts in this repo
# (never a mock/surrogate) and proves the two OMN-16259 defects are fixed:
#
#   (a) OMNI_HOME is wired + documented, and its resolution fails fast with
#       no silent default.
#   (b) omnimarket is in repos.yaml and `make install` clones it.
#   (c) the Market skill co-install runs (or is documented) so `onex skill`
#       can resolve Market nodes instead of "Unknown node"/"Unknown skill".
#   (d) no hardcoded /Users/ or /Volumes/ paths were introduced.
#
# Test (b)/(c) run a REAL `make install` from a clean clone of this checkout
# (network + uv sync + npm install + the omnimarket co-install) — this is
# slow (multiple minutes) by nature of what it proves. Run directly, not
# under a test framework: there is no pytest/CI harness in this repo (a
# public shell+docs installer), matching its existing convention.
#
# Usage: bash tests/test_install_omni_home_and_omnimarket.sh [--skip-heavy]
#   --skip-heavy  run only the fast, static (a)/(d) checks — skips the real
#                 `make install` clean-clone run for (b)/(c). Useful for a
#                 quick pre-push smoke; the full run is still required once
#                 per change to install.sh/Makefile/repos.yaml.
# ----------------------------------------------------------------------------
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKIP_HEAVY=0
[ "${1:-}" = "--skip-heavy" ] && SKIP_HEAVY=1

PASS=0
FAIL=0

ok()   { echo "  PASS: $*"; PASS=$((PASS + 1)); }
bad()  { echo "  FAIL: $*"; FAIL=$((FAIL + 1)); }
hdr()  { echo ""; echo "=== $* ==="; }

# Portable timeout: prefer GNU `timeout` (Linux, or macOS with coreutils
# installed), fall back to `gtimeout` (macOS + `brew install coreutils`),
# and if neither exists — stock macOS ships neither — background the job
# ourselves and kill it after the deadline, so this test doesn't hard-fail
# with "command not found" on a contractor's unmodified Mac.
if command -v timeout >/dev/null 2>&1; then
    TIMEOUT_BIN="timeout"
elif command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_BIN="gtimeout"
else
    TIMEOUT_BIN=""
fi

run_with_timeout() {
    local secs="$1"
    shift
    if [ -n "$TIMEOUT_BIN" ]; then
        "$TIMEOUT_BIN" "$secs" "$@"
        return $?
    fi
    "$@" &
    local pid=$!
    ( sleep "$secs" && kill -9 "$pid" 2>/dev/null ) &
    local watchdog=$!
    local status=0
    wait "$pid" 2>/dev/null || status=$?
    kill "$watchdog" 2>/dev/null
    wait "$watchdog" 2>/dev/null
    return "$status"
}

# ----------------------------------------------------------------------------
# (a) OMNI_HOME wired + documented
# ----------------------------------------------------------------------------
hdr "(a) OMNI_HOME wiring + docs"

if grep -q 'OMNI_HOME' "$REPO_ROOT/install.sh"; then
    ok "install.sh references OMNI_HOME"
else
    bad "install.sh does not reference OMNI_HOME"
fi

if grep -q 'export OMNI_HOME' "$REPO_ROOT/Makefile"; then
    ok "Makefile exports OMNI_HOME"
else
    bad "Makefile does not export OMNI_HOME"
fi

for doc in README.md docs/GETTING_STARTED.md; do
    if grep -q 'OMNI_HOME' "$REPO_ROOT/$doc"; then
        ok "$doc documents OMNI_HOME"
    else
        bad "$doc does not document OMNI_HOME"
    fi
done

if grep -qi 'drift.*guard\|fail.*open' "$REPO_ROOT/README.md" "$REPO_ROOT/docs/GETTING_STARTED.md"; then
    ok "docs state the drift-guard fail-open consequence"
else
    bad "docs do not state the drift-guard fail-open consequence"
fi

if grep -q 'OMNI_HOME is not set\|contract_sweep' "$REPO_ROOT/README.md" "$REPO_ROOT/docs/GETTING_STARTED.md" 2>/dev/null; then
    ok "docs state the OMNI_HOME-dependent node refusal (contract_sweep) consequence"
else
    bad "docs do not state the OMNI_HOME-dependent node refusal consequence"
fi

# Fail-fast, no silent default: OMNI_HOME must never be defined with a `:-`
# bash-parameter-expansion default anywhere in the changed artifacts, and
# install.sh's own derivation must have an explicit non-empty guard before
# it exports OMNI_HOME.
if grep -qE '\$\{OMNI_HOME(:-|-|:=)' "$REPO_ROOT/install.sh" "$REPO_ROOT/Makefile"; then
    bad "found a silent-default OMNI_HOME expansion (\${OMNI_HOME:-...}) in install.sh/Makefile"
else
    ok "no silent-default OMNI_HOME expansion in install.sh/Makefile"
fi

if grep -B6 '^SCRIPT_DIR=' "$REPO_ROOT/install.sh" | grep -q '\-z "\${BASH_SOURCE\[0\]:-}"'; then
    ok "install.sh guards OMNI_HOME derivation with an explicit non-empty check before deriving SCRIPT_DIR"
else
    bad "install.sh does not guard OMNI_HOME derivation before deriving SCRIPT_DIR"
fi

# ----------------------------------------------------------------------------
# Real fail-fast exercise: drive install.sh ITSELF end to end (never an
# extracted/reimplemented snippet, never a forced environment variable the
# script could not actually produce). bash never populates BASH_SOURCE[0]
# for a script it reads from stdin rather than a file — that's exactly what
# happens when install.sh is piped, e.g. `curl ... | bash` or
# `bash < install.sh` — so piping it is a real, reachable way to trigger the
# guard, not a synthetic precondition. This exercises real script bytes,
# real `set -euo pipefail`, the real guard, and the real exit code + stderr
# text a piped-in user would actually see.
# ----------------------------------------------------------------------------
piped_out="$(bash < "$REPO_ROOT/install.sh" 2>&1)"
piped_status=$?
if [ "$piped_status" -ne 0 ] \
    && echo "$piped_out" | grep -q "cannot derive OMNI_HOME" \
    && ! echo "$piped_out" | grep -q "OMNI_HOME resolved to"; then
    ok "piping the real install.sh via stdin (bash < install.sh) fails fast (status=$piped_status) before ever exporting OMNI_HOME"
else
    bad "piping the real install.sh via stdin did not fail fast as expected (status=$piped_status, out=$piped_out)"
fi

# The curl-pipe idiom the docs call out (curl ... | bash) most commonly
# reaches bash as `bash -c "$(curl ...)"` or an equivalent command
# substitution rather than plain stdin redirection; same underlying
# BASH_SOURCE[0]-unset condition, exercised the same real way against the
# same real file.
curlpipe_out="$(bash -c "$(cat "$REPO_ROOT/install.sh")" 2>&1)"
curlpipe_status=$?
if [ "$curlpipe_status" -ne 0 ] \
    && echo "$curlpipe_out" | grep -q "cannot derive OMNI_HOME" \
    && ! echo "$curlpipe_out" | grep -q "OMNI_HOME resolved to"; then
    ok "the curl-pipe idiom (bash -c \"\$(cat install.sh)\") fails fast before ever exporting OMNI_HOME"
else
    bad "the curl-pipe idiom did not fail fast as expected (status=$curlpipe_status, out=$curlpipe_out)"
fi

# And the normal (non-piped) invocation must NOT trip the guard — it must
# resolve and export a real, non-empty OMNI_HOME. Exercised against a mktemp
# copy of install.sh + repos.yaml (the pattern the heavy (b)/(c) block below
# already uses), NEVER against $REPO_ROOT itself: install.sh's own next step
# is `mkdir -p "$REPOS_DIR"` followed by real `git clone`s under
# $SCRIPT_DIR/repos, so running it in-place would create/clone into
# $REPO_ROOT/repos, and the timeout-then-rm-rf that used to follow would
# silently delete a real repos/ tree (and any uncommitted work in it) on any
# machine that had already run `make install` — reproduced live: seeding
# repos/omnibase_core/MY_UNCOMMITTED_WORK.txt then running this test with
# --skip-heavy still exited 0 and deleted repos/ entirely. A mktemp copy
# removes that blast radius while still exercising the real install.sh bytes
# and the real fail-fast guard under a real, non-piped invocation.
# Re-resolved through `cd ... && pwd` (not the raw mktemp -d output) because
# `${TMPDIR:-/tmp}` on macOS already ends in a slash, which mktemp echoes
# straight through as a literal "//" in the path — install.sh's own
# `SCRIPT_DIR="$(cd ... && pwd)"` normalizes that away, so comparing the raw
# mktemp path against install.sh's printed OMNI_HOME would false-FAIL on a
# string mismatch even though both refer to the same directory.
NORMAL_WORK="$(cd "$(mktemp -d "${TMPDIR:-/tmp}/omn16259-normalrun.XXXXXX")" && pwd)"
cp "$REPO_ROOT/install.sh" "$REPO_ROOT/repos.yaml" "$NORMAL_WORK/"
normal_out="$(cd "$NORMAL_WORK" && run_with_timeout 5 bash install.sh </dev/null 2>&1 || true)"
if echo "$normal_out" | grep -q "OMNI_HOME resolved to $NORMAL_WORK/repos"; then
    ok "running install.sh normally (./install.sh) resolves OMNI_HOME to its own checkout's repos/ dir, not silently to something else"
else
    bad "running install.sh normally did not resolve OMNI_HOME as expected: $normal_out"
fi
rm -rf "$NORMAL_WORK" 2>/dev/null || true

# ----------------------------------------------------------------------------
# (d) No hardcoded absolute paths introduced
# ----------------------------------------------------------------------------
hdr "(d) No hardcoded /Users/ or /Volumes/ paths"

changed_files="install.sh Makefile repos.yaml README.md docs/GETTING_STARTED.md"
hardcoded_hits=""
for f in $changed_files; do
    hits="$(grep -nE '/Users/|/Volumes/' "$REPO_ROOT/$f" 2>/dev/null || true)"
    if [ -n "$hits" ]; then
        hardcoded_hits="$hardcoded_hits\n$f:\n$hits"
    fi
done
if [ -n "$hardcoded_hits" ]; then
    bad "hardcoded absolute path(s) found:$hardcoded_hits"
else
    ok "zero /Users/ or /Volumes/ hits in changed files"
fi

# ----------------------------------------------------------------------------
# (b) repos.yaml gains omnimarket with correct metadata
# ----------------------------------------------------------------------------
hdr "(b) repos.yaml omnimarket entry"

if grep -A2 'name: omnimarket' "$REPO_ROOT/repos.yaml" | grep -q 'repo: OmniNode-ai/omnimarket'; then
    ok "repos.yaml has an omnimarket entry with repo: OmniNode-ai/omnimarket"
else
    bad "repos.yaml is missing a correctly-shaped omnimarket entry"
fi

if [ "$SKIP_HEAVY" -eq 1 ]; then
    echo ""
    echo "--skip-heavy passed: skipping the real make install clean-clone run for (b)/(c)."
    echo ""
    echo "Results: $PASS passed, $FAIL failed (heavy checks skipped)"
    [ "$FAIL" -eq 0 ]
    exit $?
fi

# ----------------------------------------------------------------------------
# (b)+(c) REAL make install from a clean clone; omnimarket clones; Market
# skill co-install runs; onex skill resolves a Market node.
# ----------------------------------------------------------------------------
hdr "(b)+(c) real 'make install' from a clean clone"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/omn16259-installtest.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

# Plain copy (not `git worktree add`) so uncommitted working-tree edits are
# included — this is what a real clean-clone user would get once the diff
# lands, minus needing a commit first. Excludes repos/ (never populated yet
# here) and .git (irrelevant to install.sh, which is pure filesystem).
echo "copying this checkout (with local changes) into $WORK/omnibase ..."
mkdir -p "$WORK/omnibase"
if ! (cd "$REPO_ROOT" && tar cf - --exclude=repos --exclude=.git . | (cd "$WORK/omnibase" && tar xf -)); then
    bad "could not copy the current checkout into a clean-clone test dir"
else
    (
        cd "$WORK/omnibase" || exit 1
        echo "running make install (this clones ~10 repos, uv-syncs each, npm-installs omnidash, and co-installs omnimarket into the infra venv — this takes several minutes)..."
        make install
    ) >"$WORK/install.log" 2>&1
    install_status=$?
    echo "  (full log: $WORK/install.log, tail below)"
    tail -30 "$WORK/install.log"

    if [ "$install_status" -ne 0 ]; then
        bad "make install exited non-zero ($install_status)"
    else
        ok "make install completed"
    fi

    if [ -d "$WORK/omnibase/repos/omnimarket/.git" ]; then
        ok "repos/omnimarket was cloned"
        commit="$(git -C "$WORK/omnibase/repos/omnimarket" rev-parse HEAD 2>/dev/null)"
        if [ -n "$commit" ]; then
            ok "repos/omnimarket is at a valid commit ($commit)"
        else
            bad "repos/omnimarket has no resolvable HEAD commit"
        fi
    else
        bad "repos/omnimarket was NOT cloned by make install"
    fi

    infra_python="$WORK/omnibase/repos/omnibase_infra/.venv/bin/python"
    if [ -x "$infra_python" ]; then
        ep_check="$("$infra_python" - <<'PYEOF'
import sys
from importlib.metadata import entry_points
eps = {e.name for e in entry_points(group="onex.nodes")}
required = {"node_pr_lifecycle_orchestrator", "node_session_orchestrator", "node_aislop_sweep"}
missing = sorted(required - eps)
if missing:
    print(f"MISSING:{missing}")
    sys.exit(1)
print(f"OK:{len(eps)}")
PYEOF
)"
        ep_status=$?
        if [ "$ep_status" -eq 0 ]; then
            ok "Market nodes resolve via onex.nodes entry points in the infra venv ($ep_check)"
        else
            bad "Market nodes did not resolve via onex.nodes entry points ($ep_check)"
        fi

        skill_out="$(cd "$WORK/omnibase/repos/omnibase_infra" && OMNI_HOME="$WORK/omnibase/repos" "$infra_python" -c "
from omnibase_infra.cli.cli_node import _resolve_packaged_contract
try:
    path = _resolve_packaged_contract('node_aislop_sweep')
    print(f'RESOLVED:{path}')
except Exception as e:
    print(f'FAILED:{e}')
" 2>&1)"
        if echo "$skill_out" | grep -q '^RESOLVED:'; then
            ok "onex resolves the Market node 'node_aislop_sweep' to a packaged contract (not Unknown node): $skill_out"
        else
            bad "onex could not resolve the Market node 'node_aislop_sweep': $skill_out"
        fi
    else
        bad "no omnibase_infra venv python found at $infra_python — cannot verify Market node resolution"
    fi
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
