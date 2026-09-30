#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# OMN-20123: the installer offers three install paths and writes the runtime
# configuration for the one chosen.
#
#   local   fully local runtime: in-memory bus, no Docker (the default)
#   docker  self-hosted Docker stack (PostgreSQL, Redpanda, Valkey)
#   cloud   listed as coming later; not selectable yet
#
# Drives the real install.sh in scratch copies of this checkout, with every
# repository in repos.yaml pre-planted (so no clone runs) and stub tools on a
# PATH that holds only the stubs plus /usr/bin and /bin. Docker is present on
# that PATH only in the scenarios that plant a docker stub, and each scenario
# that claims "no Docker" first proves `docker` does not resolve.
#
# The runtime configuration the installer writes is the workspace tier-1
# runtime config, <OMNIBASE_PATH>/config/onex/runtime/runtime_config.yaml:
# the file `onex delegate` reads when OMNIBASE_PATH is bound, and the file the
# runtime kernel reads when ONEX_CONTRACTS_DIR points at <OMNIBASE_PATH>/config/onex.
#
# Usage: bash tests/test_install_paths.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

BASE_PATH="/usr/bin:/bin"
RUNTIME_CONFIG_REL="repos/config/onex/runtime/runtime_config.yaml"
PASSED=0

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "  PASS: $*"; PASSED=$((PASSED + 1)); }

stage() {
    # $1 = scenario name, $2 = "with-docker" or "no-docker"
    local name="$1" docker_mode="$2"
    local root="$WORK/$name"
    mkdir -p "$root/repos" "$root/bin"
    cp "$HERE/install.sh" "$HERE/repos.yaml" "$HERE/.env.example" "$root/"

    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*name:[[:space:]]*(.+) ]]; then
            mkdir -p "$root/repos/${BASH_REMATCH[1]}"
            : > "$root/repos/${BASH_REMATCH[1]}/pyproject.toml"
        fi
    done < "$HERE/repos.yaml"

    # uv records every call so a scenario can prove nothing was synced.
    cat > "$root/bin/uv" <<EOF
#!/usr/bin/env bash
echo "uv \$*" >> "$root/uv.calls"
exit 0
EOF
    cat > "$root/bin/python3" <<'EOF'
#!/usr/bin/env bash
echo 3.12
EOF
    cat > "$root/bin/node" <<'EOF'
#!/usr/bin/env bash
echo v20.0.0
EOF
    cat > "$root/bin/npm" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
    cat > "$root/bin/git" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
    if [ "$docker_mode" = "with-docker" ]; then
        cat > "$root/bin/docker" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
    fi
    chmod +x "$root"/bin/*
    echo "$root"
}

run_install() {
    # $1 = root, $2 = log, rest = install.sh arguments. Stdin is /dev/null, so
    # the run is non-interactive exactly as an agent or CI run would be.
    local root="$1" log="$2"
    shift 2
    set +e
    (cd "$root" && PATH="$root/bin:$BASE_PATH" bash ./install.sh "$@") < /dev/null > "$log" 2>&1
    local rc=$?
    set -e
    echo "$rc"
}

assert_no_docker() {
    local root="$1"
    if PATH="$root/bin:$BASE_PATH" command -v docker > /dev/null 2>&1; then
        fail "positive control: docker resolves on the scenario PATH, so a no-Docker claim would be unproven"
    fi
}

bus_type() {
    # The event_bus.type the written runtime config declares.
    awk '/^event_bus:/{inbus=1; next} inbus && /^[^[:space:]]/{inbus=0} inbus && /^[[:space:]]+type:/{gsub(/"/,"",$2); print $2; exit}' "$1"
}

show_log() { sed 's/^/    /' "$1" >&2; }

echo "=== install paths (OMN-20123) ==="

# 1. Default, non-interactive, no Docker anywhere: installs the local path.
root="$(stage default no-docker)"
assert_no_docker "$root"
rc="$(run_install "$root" "$WORK/default.log")"
[ "$rc" -eq 0 ] || { show_log "$WORK/default.log"; fail "default install exited $rc on a host with no Docker"; }
grep -qi "docker" "$WORK/default.log" && grep -q "Missing prerequisites" "$WORK/default.log" \
    && fail "default install listed Docker as a missing prerequisite"
[ -f "$root/$RUNTIME_CONFIG_REL" ] || fail "default install wrote no runtime config at $RUNTIME_CONFIG_REL"
[ "$(bus_type "$root/$RUNTIME_CONFIG_REL")" = "inmemory" ] || fail "default install's runtime config does not declare the in-memory bus"
grep -q '^# install-path: local$' "$root/$RUNTIME_CONFIG_REL" || fail "default install did not record install path local"
pass "no flag, no TTY, no Docker: local path installed, in-memory runtime config written"

# 2. Explicit local path, no Docker.
root="$(stage local no-docker)"
assert_no_docker "$root"
rc="$(run_install "$root" "$WORK/local.log" --path local)"
[ "$rc" -eq 0 ] || { show_log "$WORK/local.log"; fail "--path local exited $rc with no Docker"; }
[ "$(bus_type "$root/$RUNTIME_CONFIG_REL")" = "inmemory" ] || fail "--path local did not write the in-memory runtime config"
pass "--path local with no Docker installed"

# 3. Docker path with no Docker: refused at the prerequisite step, naming docker.
root="$(stage docker-missing no-docker)"
assert_no_docker "$root"
rc="$(run_install "$root" "$WORK/docker-missing.log" --path docker)"
[ "$rc" -ne 0 ] || fail "--path docker exited 0 on a host with no Docker"
grep -q "Missing prerequisites" "$WORK/docker-missing.log" || fail "--path docker without Docker did not report missing prerequisites"
grep -qi "docker" "$WORK/docker-missing.log" || fail "--path docker without Docker did not name docker"
[ ! -f "$root/$RUNTIME_CONFIG_REL" ] || fail "--path docker without Docker still wrote a runtime config"
pass "--path docker without Docker refused at the prerequisite check"

# 4. Docker path with Docker: the Kafka runtime config.
root="$(stage docker with-docker)"
rc="$(run_install "$root" "$WORK/docker.log" --path docker)"
[ "$rc" -eq 0 ] || { show_log "$WORK/docker.log"; fail "--path docker exited $rc with Docker present"; }
[ "$(bus_type "$root/$RUNTIME_CONFIG_REL")" = "kafka" ] || fail "--path docker did not write the kafka runtime config"
grep -q '^# install-path: docker$' "$root/$RUNTIME_CONFIG_REL" || fail "--path docker did not record install path docker"
pass "--path docker with Docker: kafka runtime config written"

# 5. Cloud is listed but not selectable.
root="$(stage cloud with-docker)"
rc="$(run_install "$root" "$WORK/cloud.log" --path cloud)"
[ "$rc" -ne 0 ] || fail "--path cloud was accepted"
grep -qi "not available yet" "$WORK/cloud.log" || fail "--path cloud refusal does not say it is not available yet"
[ ! -f "$root/$RUNTIME_CONFIG_REL" ] || fail "--path cloud wrote a runtime config"
pass "--path cloud refused as not available yet"

# 6. An unknown path is a usage error.
root="$(stage bogus with-docker)"
rc="$(run_install "$root" "$WORK/bogus.log" --path bogus)"
[ "$rc" -ne 0 ] || fail "--path bogus was accepted"
pass "--path bogus refused"

# 7. Switching path later rewrites the runtime config and installs nothing.
root="$(stage switch with-docker)"
rc="$(run_install "$root" "$WORK/switch-install.log")"
[ "$rc" -eq 0 ] || { show_log "$WORK/switch-install.log"; fail "install before switch exited $rc"; }
[ "$(bus_type "$root/$RUNTIME_CONFIG_REL")" = "inmemory" ] || fail "install before switch was not local"
: > "$root/uv.calls"
rc="$(run_install "$root" "$WORK/switch.log" --switch-path docker)"
[ "$rc" -eq 0 ] || { show_log "$WORK/switch.log"; fail "--switch-path docker exited $rc"; }
[ "$(bus_type "$root/$RUNTIME_CONFIG_REL")" = "kafka" ] || fail "--switch-path docker did not rewrite the runtime config to kafka"
grep -q '^# install-path: docker$' "$root/$RUNTIME_CONFIG_REL" || fail "--switch-path docker did not record install path docker"
if grep -q "sync" "$root/uv.calls"; then fail "--switch-path ran uv sync; it must only rewrite the runtime config"; fi
rc="$(run_install "$root" "$WORK/switch-back.log" --switch-path local)"
[ "$rc" -eq 0 ] || { show_log "$WORK/switch-back.log"; fail "--switch-path local exited $rc"; }
[ "$(bus_type "$root/$RUNTIME_CONFIG_REL")" = "inmemory" ] || fail "--switch-path local did not rewrite the runtime config back to inmemory"
pass "--switch-path docker then local rewrites the runtime config and syncs nothing"

# 8. A runtime config the installer did not write is never overwritten.
root="$(stage handwritten with-docker)"
mkdir -p "$(dirname "$root/$RUNTIME_CONFIG_REL")"
printf 'name: mine\nevent_bus:\n  type: kafka\n' > "$root/$RUNTIME_CONFIG_REL"
rc="$(run_install "$root" "$WORK/handwritten.log" --switch-path local)"
[ "$rc" -ne 0 ] || fail "--switch-path overwrote a runtime config the installer did not write"
grep -q '^name: mine$' "$root/$RUNTIME_CONFIG_REL" || fail "a hand-written runtime config was modified"
pass "a hand-written runtime config is refused, not overwritten"

# 9. The guides agree with the installer.
for doc in README.md docs/GETTING_STARTED.md; do
    for p in local docker cloud; do
        grep -qiE "\\b$p\\b" "$HERE/$doc" || fail "$doc does not describe the $p install path"
    done
    grep -q -- "--path docker" "$HERE/$doc" || fail "$doc does not show how to choose the docker path"
    grep -q "switch-path" "$HERE/$doc" || fail "$doc does not say how to switch path later"
    grep -q "onex-plugin-quickstart" "$HERE/$doc" || fail "$doc does not point at the PyPI quickstart"
    # No prerequisites table row may list Docker as required for every path.
    if grep -E '^\|[[:space:]]*Docker[[:space:]]*\|' "$HERE/$doc" | grep -qvi "docker path"; then
        fail "$doc lists Docker in a requirements table without scoping it to the docker path"
    fi
done
if grep -q '^- Docker + Docker Compose$' "$HERE/README.md"; then
    fail "README requirements still list Docker as required for every path"
fi
pass "README and GETTING_STARTED describe the three paths and scope Docker to the docker path"

echo "PASS: $PASSED install-path checks"
