#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# install.sh detects Intel macOS before any clone or package install.
# A stub `uname` on PATH reports the platform; a stub `uv` records every call.
#   A  Intel macOS, no Homebrew/Rust   -> exit != 0, commands named, uv never called
#   B  Intel macOS, prerequisites ok   -> proceeds, OPENSSL_DIR exported to uv
#   C  Apple Silicon macOS             -> no Intel notice
# Usage: bash tests/test_install_intel_mac.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }

stage() {
    # $1 name, $2 uname -m, $3 with_intel_prereqs (yes|no)
    local root="$WORK/$1"
    mkdir -p "$root/repos" "$root/bin" "$root/openssl/include/openssl"
    cp "$HERE/install.sh" "$HERE/repos.yaml" "$HERE/.env.example" "$root/"
    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*name:[[:space:]]*(.+) ]]; then
            mkdir -p "$root/repos/${BASH_REMATCH[1]}"
            : > "$root/repos/${BASH_REMATCH[1]}/pyproject.toml"
        fi
    done < "$HERE/repos.yaml"
    cat > "$root/bin/uname" <<EOS
#!/usr/bin/env bash
case "\${1:-}" in -s) echo Darwin;; -m) echo $2;; *) echo Darwin;; esac
EOS
    cat > "$root/bin/sysctl" <<'EOS'
#!/usr/bin/env bash
echo 0
EOS
    cat > "$root/bin/xcode-select" <<'EOS'
#!/usr/bin/env bash
echo /Library/Developer/CommandLineTools
EOS
    cat > "$root/bin/uv" <<EOS
#!/usr/bin/env bash
echo "uv \$* OPENSSL_DIR=\${OPENSSL_DIR:-unset}" >> "$root/uv.calls"
exit 0
EOS
    printf '#!/usr/bin/env bash\necho 3.12\n' > "$root/bin/python3"
    for t in docker node npm; do printf '#!/usr/bin/env bash\necho v20.0.0\nexit 0\n' > "$root/bin/$t"; done
    if [ "$3" = yes ]; then
        printf '#!/usr/bin/env bash\necho "%s"\n' "$root/openssl" > "$root/bin/brew"
        printf '#!/usr/bin/env bash\nexit 0\n' > "$root/bin/cargo"
        printf '#!/usr/bin/env bash\nexit 0\n' > "$root/bin/rustc"
    fi
    chmod +x "$root"/bin/*
    echo "$root"
}

# Hermetic PATH: system tools only, no host brew/cargo leaking in.
run_install() {
    local root="$1" log="$2" rc
    set +e
    (cd "$root" && PATH="$root/bin:/usr/bin:/bin:/usr/sbin:/sbin" bash ./install.sh) > "$log" 2>&1
    rc=$?
    set -e
    echo "$rc"
}

# A ------------------------------------------------------------------
a="$(stage a x86_64 no)"
rc="$(run_install "$a" "$WORK/a.log")"
echo "A intel, no prerequisites: exit=$rc"
[ "$rc" -ne 0 ] || fail "A: install.sh exited 0 without the from-source prerequisites"
grep -q "Intel macOS detected" "$WORK/a.log" || fail "A: no Intel notice"
grep -q "brew install rust" "$WORK/a.log" || fail "A: Rust command not named"
grep -q "Homebrew" "$WORK/a.log" || fail "A: Homebrew not named"
[ ! -e "$a/uv.calls" ] || fail "A: reached uv before stopping"
grep -q "Cloning\|Building Python" "$WORK/a.log" && fail "A: reached clone or build step"

# B ------------------------------------------------------------------
b="$(stage b x86_64 yes)"
rc="$(run_install "$b" "$WORK/b.log")"
echo "B intel, prerequisites present: exit=$rc"
[ "$rc" -eq 0 ] || { cat "$WORK/b.log"; fail "B: exit $rc with prerequisites present"; }
grep -q "from-source prerequisites found" "$WORK/b.log" || fail "B: no prerequisites-found notice"
grep -q "sync.*OPENSSL_DIR=$b/openssl" "$b/uv.calls" || fail "B: uv did not receive OPENSSL_DIR"

# C ------------------------------------------------------------------
c="$(stage c arm64 no)"
rc="$(run_install "$c" "$WORK/c.log")"
echo "C apple silicon: exit=$rc"
grep -q "Intel macOS" "$WORK/c.log" && fail "C: Intel notice on arm64"
[ "$rc" -eq 0 ] || fail "C: exit $rc on arm64"

echo "PASS"
