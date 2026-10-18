#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# install.sh provides a supported Python instead of stopping on an old one
# (OMN-21167). Stub `python3`, `uv` and `brew` on a hermetic PATH stand in for
# the host; `uname` reports Apple Silicon so the Intel from-source check is
# skipped. The stub uv records every call with the UV_PYTHON it was given.
#   A  python3 3.11, uv can install a managed Python   -> exit 0, the managed
#      Python is UV_PYTHON for every sync and named in the runtime configuration
#   B  python3 3.11, uv offline, no Homebrew            -> exit != 0, one line
#      names `uv python install 3.12`, nothing cloned or synced
#   C  python3 3.11, uv offline, Homebrew, no consent   -> exit != 0, Homebrew
#      never asked to install, the same one line
#   D  python3 3.11, uv offline, --allow-brew-python    -> exit 0, Homebrew's
#      python@3.12 is UV_PYTHON and named in the runtime configuration
#   E  python3 already 3.12                             -> exit 0, uv never asked
#      to install a Python, python3 named in the runtime configuration
#   F  python3 3.14, above omniclaude's <3.14 cap      -> exit 0, passed over
#      for the uv-managed 3.12
# Usage: bash tests/test_install_python.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }

stage() {
    # $1 name, $2 python3 version, $3 uv mode (uv-ok|offline), $4 brew (yes|no)
    local root="$WORK/$1"
    mkdir -p "$root/repos" "$root/bin" "$root/managed/bin"
    cp "$HERE/install.sh" "$HERE/repos.yaml" "$HERE/.env.example" "$root/"
    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*name:[[:space:]]*(.+) ]]; then
            mkdir -p "$root/repos/${BASH_REMATCH[1]}"
            : > "$root/repos/${BASH_REMATCH[1]}/pyproject.toml"
        fi
    done < "$HERE/repos.yaml"
    cat > "$root/bin/uname" <<'EOS'
#!/usr/bin/env bash
case "${1:-}" in -s) echo Darwin;; -m) echo arm64;; *) echo Darwin;; esac
EOS
    printf '#!/usr/bin/env bash\necho 0\n' > "$root/bin/sysctl"
    printf '#!/usr/bin/env bash\necho %s\n' "$2" > "$root/bin/python3"
    printf '#!/usr/bin/env bash\necho 3.12\n' > "$root/managed/bin/python3.12"
    cat > "$root/bin/uv" <<EOS
#!/usr/bin/env bash
echo "uv \$* UV_PYTHON=\${UV_PYTHON:-unset}" >> "$root/uv.calls"
if [ "\${1:-}" = python ] && [ "\${2:-}" = find ]; then
    [ -e "$root/uv.installed" ] || exit 2
    echo "$root/managed/bin/python3.12"
    exit 0
fi
if [ "\${1:-}" = python ] && [ "\${2:-}" = install ]; then
    if [ "$3" = uv-ok ]; then : > "$root/uv.installed"; exit 0; fi
    echo "error: failed to download" >&2
    exit 1
fi
exit 0
EOS
    for t in node npm; do printf '#!/usr/bin/env bash\necho v20.0.0\nexit 0\n' > "$root/bin/$t"; done
    if [ "$4" = yes ]; then
        mkdir -p "$root/brewpy/bin"
        printf '#!/usr/bin/env bash\necho 3.12\n' > "$root/brewpy/bin/python3.12"
        cat > "$root/bin/brew" <<EOS
#!/usr/bin/env bash
echo "brew \$*" >> "$root/brew.calls"
case "\${1:-}" in --prefix) echo "$root/brewpy";; esac
exit 0
EOS
        chmod +x "$root/brewpy/bin/python3.12"
    fi
    chmod +x "$root"/bin/* "$root/managed/bin/python3.12"
    echo "$root"
}

# Hermetic PATH, no terminal: system tools only, no host uv/brew/python leaking in.
run_install() {
    local root="$1" log="$2" rc
    shift 2
    set +e
    (cd "$root" && PATH="$root/bin:/usr/bin:/bin:/usr/sbin:/sbin" bash ./install.sh "$@") < /dev/null > "$log" 2>&1
    rc=$?
    set -e
    echo "$rc"
}

config_of() { echo "$1/repos/config/onex/runtime/runtime_config.yaml"; }

# Every `uv sync` was handed $2 as UV_PYTHON, and there was at least one.
syncs_use() {
    local calls="$1/uv.calls" want="$2"
    grep -q "^uv sync" "$calls" || return 1
    ! grep "^uv sync" "$calls" | grep -vq "UV_PYTHON=$want\$"
}

# A ------------------------------------------------------------------
a="$(stage a 3.11 uv-ok no)"
rc="$(run_install "$a" "$WORK/a.log")"
echo "A python3 3.11, uv installs a managed Python: exit=$rc"
[ "$rc" -eq 0 ] || { cat "$WORK/a.log"; fail "A: exit $rc instead of providing Python"; }
grep -q "^uv python install 3.12" "$a/uv.calls" || fail "A: uv was not asked to install Python 3.12"
syncs_use "$a" "$a/managed/bin/python3.12" || fail "A: a uv sync did not use the managed Python"
grep -qxF "# python: $a/managed/bin/python3.12" "$(config_of "$a")" || fail "A: runtime configuration does not name the managed Python"

# B ------------------------------------------------------------------
b="$(stage b 3.11 offline no)"
rc="$(run_install "$b" "$WORK/b.log")"
echo "B python3 3.11, uv offline, no Homebrew: exit=$rc"
[ "$rc" -ne 0 ] || fail "B: exit 0 with no Python 3.12+ available"
[ "$(grep -c "uv python install 3.12" "$WORK/b.log")" -eq 1 ] || { cat "$WORK/b.log"; fail "B: not exactly one line naming 'uv python install 3.12'"; }
grep -q "Cloning" "$WORK/b.log" && fail "B: reached the clone step"
grep -q "^uv sync" "$b/uv.calls" && fail "B: reached uv sync"

# C ------------------------------------------------------------------
c="$(stage c 3.11 offline yes)"
rc="$(run_install "$c" "$WORK/c.log")"
echo "C python3 3.11, uv offline, Homebrew without consent: exit=$rc"
[ "$rc" -ne 0 ] || fail "C: exit 0 without consent to use Homebrew"
[ -e "$c/brew.calls" ] && grep -q "install" "$c/brew.calls" && fail "C: Homebrew asked to install without consent"
[ "$(grep -c "uv python install 3.12" "$WORK/c.log")" -eq 1 ] || { cat "$WORK/c.log"; fail "C: not exactly one line naming 'uv python install 3.12'"; }

# D ------------------------------------------------------------------
d="$(stage d 3.11 offline yes)"
rc="$(run_install "$d" "$WORK/d.log" --allow-brew-python)"
echo "D python3 3.11, uv offline, --allow-brew-python: exit=$rc"
[ "$rc" -eq 0 ] || { cat "$WORK/d.log"; fail "D: exit $rc with consent to use Homebrew"; }
grep -q "install python@3.12" "$d/brew.calls" || fail "D: Homebrew was not asked to install python@3.12"
syncs_use "$d" "$d/brewpy/bin/python3.12" || fail "D: a uv sync did not use Homebrew's Python"
grep -qxF "# python: $d/brewpy/bin/python3.12" "$(config_of "$d")" || fail "D: runtime configuration does not name Homebrew's Python"

# E ------------------------------------------------------------------
e="$(stage e 3.12 uv-ok no)"
rc="$(run_install "$e" "$WORK/e.log")"
echo "E python3 already 3.12: exit=$rc"
[ "$rc" -eq 0 ] || { cat "$WORK/e.log"; fail "E: exit $rc with python3 3.12"; }
grep -q "^uv python install" "$e/uv.calls" && fail "E: uv asked to install a Python although python3 is 3.12"
grep -qxF "# python: $e/bin/python3" "$(config_of "$e")" || fail "E: runtime configuration does not name python3"

# F ------------------------------------------------------------------
f="$(stage f 3.14 uv-ok no)"
rc="$(run_install "$f" "$WORK/f.log")"
echo "F python3 3.14, above the supported range: exit=$rc"
[ "$rc" -eq 0 ] || { cat "$WORK/f.log"; fail "F: exit $rc with python3 3.14"; }
syncs_use "$f" "$f/managed/bin/python3.12" || fail "F: a uv sync was forced onto python3 3.14"
grep -qxF "# python: $f/managed/bin/python3.12" "$(config_of "$f")" || fail "F: runtime configuration does not name the managed Python"

echo "PASS"
