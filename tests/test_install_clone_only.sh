#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# OMN-17427: `./install.sh --clone-only [--repos <file>] [--into <dir>]` is the
# one clone step. It reads the repos file it is handed (default: its own
# repos.yaml), clones each entry into the directory it is handed (default:
# OMNIBASE_PATH), skips a clone that already exists, and fails loud (non-zero,
# the repository named) on a clone that errors. It installs nothing.
#
# Drives the real install.sh. No network: git's url.<base>.insteadOf rewrites
# https://github.com/ to a scratch directory of bare repositories, so the real
# `git clone https://github.com/<repo>.git` call the installer makes is the one
# exercised.
#
# Usage: bash tests/test_install_clone_only.sh
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(cd "$(mktemp -d "${TMPDIR:-/tmp}/omn17427-cloneonly.XXXXXX")" && pwd)"
trap 'rm -rf "$WORK"' EXIT

PASS=0
FAIL=0
ok()  { echo "  PASS: $*"; PASS=$((PASS + 1)); }
bad() { echo "  FAIL: $*"; FAIL=$((FAIL + 1)); }

# Fake remote: two bare repositories with one commit each. A third name,
# "missing", is listed in a repos file but has no bare repository behind it.
FAKE="$WORK/fake"
for name in alpha beta; do
    src="$WORK/src-$name"
    mkdir -p "$src" "$FAKE/OmniNode-ai"
    git -C "$src" init -q -b main
    echo "$name" > "$src/README"
    git -C "$src" add README
    git -C "$src" -c user.name=t -c user.email=t@example.invalid commit -q -m init
    git clone -q --bare "$src" "$FAKE/OmniNode-ai/$name.git"
done

export GIT_CONFIG_COUNT=1
export GIT_CONFIG_KEY_0="url.$FAKE/.insteadOf"
export GIT_CONFIG_VALUE_0="https://github.com/"
export GIT_TERMINAL_PROMPT=0

write_repos() {
    # $1 = file, rest = names
    local file="$1"
    shift
    {
        echo "repositories:"
        for name in "$@"; do
            echo "  - name: $name"
            echo "    repo: OmniNode-ai/$name"
            echo "    type: python"
            echo "    description: scratch repository $name"
            echo ""
        done
    } > "$file"
}

# Installer copy in a scratch root, so nothing is cloned beside the checkout.
ROOT="$WORK/root"
mkdir -p "$ROOT"
cp "$HERE/install.sh" "$ROOT/install.sh"
write_repos "$ROOT/repos.yaml" alpha beta

# ---------------------------------------------------------------------------
# 1. Default file and default directory: clones into <root>/repos.
# ---------------------------------------------------------------------------
echo "=== defaults: own repos.yaml, OMNIBASE_PATH ==="
out1="$(cd "$ROOT" && bash install.sh --clone-only </dev/null 2>&1)"
st1=$?
if [ "$st1" -eq 0 ] && [ -d "$ROOT/repos/alpha/.git" ] && [ -d "$ROOT/repos/beta/.git" ]; then
    ok "clone-only with defaults clones every listed repo into OMNIBASE_PATH (exit 0)"
else
    bad "clone-only with defaults did not clone both repos (exit=$st1): $out1"
fi

# 2. Second run clones nothing and says so for every repo.
out2="$(cd "$ROOT" && bash install.sh --clone-only </dev/null 2>&1)"
st2=$?
if [ "$st2" -eq 0 ] \
    && echo "$out2" | grep -q "alpha already cloned" \
    && echo "$out2" | grep -q "beta already cloned" \
    && echo "$out2" | grep -q "0 cloned, 2 already cloned, 0 failed"; then
    ok "second run clones nothing and reports every repo already cloned"
else
    bad "second run did not report every repo already cloned (exit=$st2): $out2"
fi

# 3. Clone-only installs nothing: no .env, no runtime configuration.
if [ ! -e "$ROOT/.env" ] && [ ! -e "$ROOT/repos/config" ]; then
    ok "clone-only wrote no .env and no runtime configuration"
else
    bad "clone-only wrote install artifacts (.env or repos/config)"
fi

# ---------------------------------------------------------------------------
# 4. --repos and --into: a handed file and a handed directory.
# ---------------------------------------------------------------------------
echo "=== --repos and --into ==="
HANDED="$WORK/handed.yaml"
write_repos "$HANDED" beta
INTO="$WORK/elsewhere"
out4="$(cd "$ROOT" && bash install.sh --clone-only --repos "$HANDED" --into "$INTO" </dev/null 2>&1)"
st4=$?
if [ "$st4" -eq 0 ] && [ -d "$INTO/beta/.git" ] && [ ! -e "$INTO/alpha" ]; then
    ok "--repos/--into clone exactly the handed file's entries into the handed directory"
else
    bad "--repos/--into did not clone as handed (exit=$st4): $out4"
fi

# ---------------------------------------------------------------------------
# 5. A clone that errors fails loud, names the repo, and the rest still clone.
# ---------------------------------------------------------------------------
echo "=== a failing clone fails loud ==="
BROKEN="$WORK/broken.yaml"
write_repos "$BROKEN" alpha missing beta
INTO5="$WORK/into-broken"
out5="$(cd "$ROOT" && bash install.sh --clone-only --repos "$BROKEN" --into "$INTO5" </dev/null 2>&1)"
st5=$?
if [ "$st5" -ne 0 ] \
    && echo "$out5" | grep -q "OmniNode-ai/missing" \
    && echo "$out5" | grep -q "1 failed"; then
    ok "an unreadable repo makes clone-only exit non-zero and names OmniNode-ai/missing (exit=$st5)"
else
    bad "a failing clone was not loud (exit=$st5): $out5"
fi
if [ -d "$INTO5/alpha/.git" ] && [ -d "$INTO5/beta/.git" ] && [ ! -e "$INTO5/missing" ]; then
    ok "the repos either side of the failing one were still cloned"
else
    bad "the repos beside the failing one were not cloned"
fi

# ---------------------------------------------------------------------------
# 6. Refusals: no repos file, an empty repos file, a path-escaping name, flags
#    that need --clone-only, and --clone-only beside an install flag.
# ---------------------------------------------------------------------------
echo "=== refusals ==="
out6="$(cd "$ROOT" && bash install.sh --clone-only --repos "$WORK/does-not-exist.yaml" --into "$WORK/x6" </dev/null 2>&1)"
st6=$?
if [ "$st6" -ne 0 ] && echo "$out6" | grep -q "does-not-exist.yaml"; then
    ok "a missing repos file is refused and named (exit=$st6)"
else
    bad "a missing repos file was not refused (exit=$st6): $out6"
fi

printf 'repositories:\n' > "$WORK/empty.yaml"
out7="$(cd "$ROOT" && bash install.sh --clone-only --repos "$WORK/empty.yaml" --into "$WORK/x7" </dev/null 2>&1)"
st7=$?
if [ "$st7" -ne 0 ] && echo "$out7" | grep -qi "no repositories"; then
    ok "a repos file with no entries is refused, not a silent success (exit=$st7)"
else
    bad "an empty repos file was not refused (exit=$st7): $out7"
fi

cat > "$WORK/escape.yaml" <<'EOF'
repositories:
  - name: ../escape
    repo: OmniNode-ai/alpha
    type: python
EOF
out8="$(cd "$ROOT" && bash install.sh --clone-only --repos "$WORK/escape.yaml" --into "$WORK/x8" </dev/null 2>&1)"
st8=$?
if [ "$st8" -ne 0 ] && [ ! -e "$WORK/escape" ] && echo "$out8" | grep -q "../escape"; then
    ok "a name that escapes the target directory is refused and named (exit=$st8)"
else
    bad "a path-escaping name was not refused (exit=$st8): $out8"
fi

out9="$(cd "$ROOT" && bash install.sh --repos "$HANDED" </dev/null 2>&1)"
st9=$?
if [ "$st9" -eq 2 ] && echo "$out9" | grep -q -- "--clone-only"; then
    ok "--repos without --clone-only is refused (exit 2)"
else
    bad "--repos without --clone-only was not refused with exit 2 (exit=$st9): $out9"
fi

out10="$(cd "$ROOT" && bash install.sh --clone-only --path local </dev/null 2>&1)"
st10=$?
if [ "$st10" -eq 2 ] && echo "$out10" | grep -q -- "--clone-only only clones"; then
    ok "--clone-only beside --path is refused (exit 2)"
else
    bad "--clone-only beside --path was not refused with exit 2 (exit=$st10): $out10"
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
