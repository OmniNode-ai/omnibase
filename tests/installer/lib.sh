# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# OMN-21309: shared harness for the installer finish-step tests. Sourced, not
# run. It drives scripts/install_finish_step.sh, the code install.sh sources,
# with stub `say`, `afplay`, `id` and `uname` first on PATH, so no audio plays
# and the host's own account name never leaks into a result. Each stub appends
# one line to $CALLS, which the tests read back.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORK="$(cd "$(mktemp -d "${TMPDIR:-/tmp}/omn21309-finish.XXXXXX")" && pwd)"
trap 'rm -rf "$WORK"' EXIT

PASS=0
FAIL=0
ok()  { echo "  PASS: $*"; PASS=$((PASS + 1)); }
bad() { echo "  FAIL: $*"; FAIL=$((FAIL + 1)); }
summary() {
    echo "Results: $PASS passed, $FAIL failed"
    [ "$FAIL" -eq 0 ]
}

BIN="$WORK/bin"
CALLS="$WORK/calls.log"
OUT="$WORK/out.log"
mkdir -p "$BIN"

# say -v <voice> ... -o <file> <text>: records the call and writes a real WAV
# (a copy of a recorded clip) so the clip builder has something to join.
cat > "$BIN/say" <<EOF
#!/usr/bin/env bash
echo "say \$*" >> "$CALLS"
out=""
while [ \$# -gt 0 ]; do
    case "\$1" in -o) out="\$2"; shift 2 ;; *) shift ;; esac
done
[ -n "\$out" ] && cp "$HERE/assets/finish/welcome.wav" "\$out"
exit 0
EOF
cat > "$BIN/afplay" <<EOF
#!/usr/bin/env bash
echo "afplay \$*" >> "$CALLS"
EOF
# id -F answers FAKE_FULLNAME; every other id call is the real one.
cat > "$BIN/id" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = "-F" ]; then printf '%s\n' "${FAKE_FULLNAME:-}"; exit 0; fi
exec /usr/bin/id "$@"
EOF
cat > "$BIN/uname" <<'EOF'
#!/usr/bin/env bash
echo "${FAKE_UNAME:-Darwin}"
EOF
chmod +x "$BIN"/*

# The driver: what install.sh does with the finish step, minus the install.
# finish_prepare starts the clip build in the background; the driver waits for
# it (as the rest of a real install would) and then calls finish_greeting.
DRIVER="$WORK/driver.sh"
cat > "$DRIVER" <<EOF
#!/usr/bin/env bash
set -uo pipefail
SCRIPT_DIR="$HERE"
warn() { echo "warn: \$*" >&2; }
. "$HERE/scripts/install_finish_step.sh"
finish_prepare
if [ -n "\$finish_work" ]; then
    for _ in \$(seq 1 150); do
        [ -f "\$finish_work/finish.wav" ] && break
        sleep 0.1
    done
fi
echo "FINISH_NAME=\$finish_name"
finish_greeting
EOF

# overlay <value|none>: writes the onboarding overlay under a fresh root.
overlay() {
    rm -rf "$WORK/overlay"
    mkdir -p "$WORK/overlay/node_onboarding"
    [ "$1" = "none" ] && return 0
    printf 'finish_greeting_enabled: "%s"\n' "$1" > "$WORK/overlay/node_onboarding/overlay.yaml"
}

# home <dirname>: a fresh HOME whose basename is <dirname>.
home() {
    rm -rf "$WORK/homes"
    mkdir -p "$WORK/homes/$1"
    printf '%s\n' "$WORK/homes/$1"
}

# run_finish <tty|notty> <stdin text>: runs the driver with the stubs first on
# PATH. Extra environment comes from the caller (FAKE_FULLNAME, FAKE_UNAME,
# HOME, SSH_CONNECTION, ONEX_SKILL_OVERLAY_ROOTS). Output goes to $OUT.
run_finish() {
    local mode="$1" input="$2"
    : > "$CALLS"
    : > "$OUT"
    if [ "$mode" = "tty" ]; then
        # The answer is typed a moment after start: written at once, it reaches
        # the terminal before the prompt reads it and arrives as an empty line.
        if [ "$(/usr/bin/uname -s)" = "Darwin" ]; then
            { sleep 1; printf '%s' "$input"; sleep 1; } \
                | PATH="$BIN:$PATH" script -q /dev/null bash "$DRIVER" > "$OUT" 2>&1
        else
            { sleep 1; printf '%s' "$input"; sleep 1; } \
                | PATH="$BIN:$PATH" script -qec "bash $DRIVER" /dev/null > "$OUT" 2>&1
        fi
    else
        printf '%s' "$input" | PATH="$BIN:$PATH" bash "$DRIVER" > "$OUT" 2>&1
    fi
}

calls_of() { grep -c "^$1 " "$CALLS" 2>/dev/null || true; }
prompted() { grep -q "What should we call you?" "$OUT"; }
# The terminal recorder may put control bytes (^D, backspaces) before a line.
finish_name_was() { tr -d '\r\004\010' < "$OUT" | grep -Eq "(^|[^A-Za-z])FINISH_NAME=$1\$"; }
