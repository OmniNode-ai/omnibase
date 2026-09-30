#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# OMN-20121: install.sh must fail closed.
#
# Drives the real install.sh in a scratch copy of this checkout with every
# repository pre-planted (so no clone happens) and a stub `uv` on PATH whose
# `sync` exits 1. Before the fix the script printed "Installation complete!"
# and exited 0 with eight of nine environments unbuilt (outside-user run,
# 2026-09-28). After the fix it must exit non-zero, name each failed
# repository, and never print the completion banner.
#
# Two scenarios, both required:
#   RED    every sync fails            -> expect exit != 0, no banner, names
#   GREEN  every sync succeeds         -> expect exit 0 and the banner
#
# Usage: bash tests/test_install_fails_closed.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

stage() {
    # $1 = scenario name, $2 = exit code the stub uv returns for `sync`
    local name="$1" uv_rc="$2"
    local root="$WORK/$name"
    mkdir -p "$root/repos" "$root/bin"
    cp "$HERE/install.sh" "$HERE/repos.yaml" "$HERE/.env.example" "$root/"

    # Pre-plant every repository named in repos.yaml so the clone step is
    # skipped, each with a pyproject.toml so the sync step runs on it.
    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*name:[[:space:]]*(.+) ]]; then
            mkdir -p "$root/repos/${BASH_REMATCH[1]}"
            : > "$root/repos/${BASH_REMATCH[1]}/pyproject.toml"
        fi
    done < "$HERE/repos.yaml"

    # Stubs for the prerequisites the script checks, so the test does not
    # depend on Docker or Node being installed on the host running it.
    cat > "$root/bin/uv" <<EOF
#!/usr/bin/env bash
if [ "\${1:-}" = "sync" ]; then echo "stub uv sync in \$PWD"; exit $uv_rc; fi
exit 0
EOF
    cat > "$root/bin/docker" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
    cat > "$root/bin/node" <<'EOF'
#!/usr/bin/env bash
echo v20.0.0
EOF
    cat > "$root/bin/npm" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
    chmod +x "$root"/bin/*
    echo "$root"
}

run_install() {
    # Runs install.sh with the stubs first on PATH; prints exit code last.
    local root="$1" log="$2"
    set +e
    (cd "$root" && PATH="$root/bin:$PATH" bash ./install.sh) > "$log" 2>&1
    local rc=$?
    set -e
    echo "$rc"
}

fail() { echo "FAIL: $*" >&2; exit 1; }

# ---------------------------------------------------------------- RED ----
red_root="$(stage red 1)"
red_rc="$(run_install "$red_root" "$WORK/red.log")"
echo "RED scenario (every uv sync fails): exit=$red_rc"
if [ "$red_rc" -eq 0 ]; then
    fail "install.sh exited 0 although every repository sync failed"
fi
if grep -q "Installation complete!" "$WORK/red.log"; then
    fail "install.sh printed the completion banner after failed syncs"
fi
# Every planted repository must be named in the failure summary.
while IFS= read -r line; do
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*name:[[:space:]]*(.+) ]]; then
        repo="${BASH_REMATCH[1]}"
        grep -q "$repo" "$WORK/red.log" || fail "failure summary does not name $repo"
    fi
done < "$HERE/repos.yaml"
echo "RED scenario: refused, banner absent, every failed repository named"

# -------------------------------------------------------------- GREEN ----
green_root="$(stage green 0)"
green_rc="$(run_install "$green_root" "$WORK/green.log")"
echo "GREEN scenario (every uv sync succeeds): exit=$green_rc"
if [ "$green_rc" -ne 0 ]; then
    sed 's/^/    /' "$WORK/green.log" >&2
    fail "install.sh exited $green_rc on a clean run"
fi
grep -q "Installation complete!" "$WORK/green.log" || fail "clean run did not print the completion banner"
echo "GREEN scenario: exit 0 with the completion banner"

echo "PASS: install.sh fails closed on sync failure and completes on success"
