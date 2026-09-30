#!/usr/bin/env bash
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}==>${NC} $*"; }
warn()  { echo -e "${YELLOW}==>${NC} $*"; }
error() { echo -e "${RED}ERROR:${NC} $*" >&2; }

# ------------------------------------------------------------------
# 0. Resolve and export OMNIBASE_PATH
# ------------------------------------------------------------------
# OMNIBASE_PATH is the canonical workspace root that every sibling repo
# clone hangs off of ($OMNIBASE_PATH/<repo>). It is the product name for
# that root, and it is the only name this installer asks you to export
# (OMN-16849 / OMN-16855).
#
# A second variable, OMNI_HOME, is exported to the SAME directory a few
# lines below. It is a temporary bridge, not a second parameter: some
# packaged tools still read that older spelling, and the bridge is removed
# by OMN-16856 once they move. See the comment at that export.
#
# Derived, never hardcoded: OMNIBASE_PATH=$REPOS_DIR, computed from this
# script's own resolved location. Fails fast — no silent default — when
# that location cannot be determined, which is exactly the "piped via
# stdin" case (curl ... | bash, or bash < install.sh): bash never
# populates BASH_SOURCE[0] for a script read from stdin, so this is
# checked explicitly, before ever calling dirname/cd on it — a plain
# `${BASH_SOURCE[0]}` reference under `set -u` would abort on "unbound
# variable" here instead of reaching this message, and `dirname ""`
# resolves to "." (the caller's $PWD), which would silently derive
# OMNIBASE_PATH from the wrong directory instead of failing at all.
if [ -z "${BASH_SOURCE[0]:-}" ]; then
    error "Could not determine this script's own location — cannot derive OMNIBASE_PATH."
    error "This installer must be run as './install.sh' or 'bash install.sh' from a real checkout, not piped via stdin (e.g. 'curl ... | bash')."
    exit 1
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS_DIR="$SCRIPT_DIR/repos"
export OMNIBASE_PATH="$REPOS_DIR"
info "OMNIBASE_PATH resolved to $OMNIBASE_PATH"

# TEMPORARY BRIDGE — remove with OMN-16856.
# The omnimarket sweep and orchestration nodes (contract_sweep, dod_verify,
# runtime_sweep and the rest of that family) still resolve the workspace
# root from OMNI_HOME, and so does the Market skill co-install script. They
# are not renamed yet: whether a self-hoster runs those nodes against their
# own tree is an open scope question on OMN-16856, and renaming the reads
# before it is answered would move ~200 sites on a guess. Until then this
# installer sets BOTH names to the SAME derived directory, so following the
# documented OMNIBASE_PATH instructions cannot leave those nodes unable to
# resolve a root. Nothing reads two names; one directory has two labels.
export OMNI_HOME="$OMNIBASE_PATH"

# ------------------------------------------------------------------
# 0b. Choose the install path (OMN-20123)
# ------------------------------------------------------------------
# Three install paths, and Docker belongs to exactly one of them:
#   local   fully local runtime: in-memory event bus, local SQLite state,
#           no Docker, Kafka or Postgres. The default.
#   docker  self-hosted Docker stack (PostgreSQL, Redpanda, Valkey) started
#           from repos/omnibase_infra; the runtime uses its Kafka bus.
#   cloud   coming later; listed so the choice is visible, not selectable.
# Chosen by --path, or asked for when run in a terminal. With no flag and no
# terminal (an agent, CI, a pipe) it is local, so an unattended install never
# stops on a prompt and never needs Docker.
#
# The chosen path is written as the workspace's runtime configuration (step
# 7 below). --switch-path rewrites only that configuration, so a user can move
# between paths later without reinstalling.
RUNTIME_CONFIG_DIR="$OMNIBASE_PATH/config/onex/runtime"
RUNTIME_CONFIG_FILE="$RUNTIME_CONFIG_DIR/runtime_config.yaml"
RUNTIME_CONFIG_MARKER="# generated-by: omnibase install.sh"

usage() {
    cat <<'EOF'
Usage: ./install.sh [--path local|docker]
       ./install.sh --switch-path local|docker

  --path local        fully local runtime, no Docker (the default)
  --path docker       self-hosted Docker stack (PostgreSQL, Redpanda, Valkey)
  --switch-path PATH  rewrite this install's runtime configuration for PATH,
                      without cloning or building anything

The cloud path is coming later and is not selectable yet.
With no --path, the installer asks when run in a terminal and uses local
otherwise.
EOF
}

install_path=""
switch_only=0
while [ $# -gt 0 ]; do
    case "$1" in
        --path|--switch-path)
            [ "$1" = "--switch-path" ] && switch_only=1
            if [ $# -lt 2 ]; then
                error "$1 needs a value: local or docker."
                usage >&2
                exit 2
            fi
            install_path="$2"
            shift 2
            ;;
        --path=*) install_path="${1#--path=}"; shift ;;
        --switch-path=*) install_path="${1#--switch-path=}"; switch_only=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *)
            error "Unknown argument: $1"
            usage >&2
            exit 2
            ;;
    esac
done

if [ -z "$install_path" ]; then
    if [ -t 0 ] && [ -t 1 ]; then
        echo ""
        echo "Choose an install path:"
        echo "  1) local   fully local runtime, no Docker (default)"
        echo "  2) docker  self-hosted Docker stack (PostgreSQL, Redpanda, Valkey)"
        echo "     cloud   coming later, not selectable yet"
        read -r -p "Install path [local]: " answer
        case "$answer" in
            ""|1|local) install_path="local" ;;
            2|docker) install_path="docker" ;;
            *) install_path="$answer" ;;
        esac
    else
        install_path="local"
        info "No --path given and no terminal to ask in: using the local install path."
    fi
fi

case "$install_path" in
    local|docker) ;;
    cloud)
        error "The cloud install path is not available yet. Choose local or docker."
        exit 2
        ;;
    *)
        error "Unknown install path '$install_path'. Choose local or docker."
        usage >&2
        exit 2
        ;;
esac
info "Install path: $install_path"

# Writes the workspace's runtime configuration for the chosen path. This is
# the tier-1 (self-hosted) runtime config the platform already reads, not a
# file of this installer's invention: `onex delegate` reads it from
# $OMNIBASE_PATH/config/onex/runtime/runtime_config.yaml whenever
# OMNIBASE_PATH is set (and refuses to run without it once OMNIBASE_PATH is
# set), and the runtime kernel reads it when ONEX_CONTRACTS_DIR points at
# $OMNIBASE_PATH/config/onex. It declares the transport only; the broker
# address of the docker path comes from the stack's own .env settings.
#
# A file this installer did not write is never overwritten: the first line
# marks the installer's own copies, and anything else is refused by name.
write_runtime_config() {
    local path_choice="$1"
    if [ -f "$RUNTIME_CONFIG_FILE" ] && [ "$(head -n 1 "$RUNTIME_CONFIG_FILE")" != "$RUNTIME_CONFIG_MARKER" ]; then
        error "$RUNTIME_CONFIG_FILE exists and was not written by this installer."
        error "It is left untouched. Move it aside to let the installer write the $path_choice configuration."
        return 1
    fi
    local bus_type description
    case "$path_choice" in
        local)
            bus_type="inmemory"
            description="omnibase install path local: fully local runtime, in-memory event bus, no Docker"
            ;;
        docker)
            bus_type="kafka"
            description="omnibase install path docker: self-hosted Docker stack, Kafka-compatible event bus"
            ;;
    esac
    mkdir -p "$RUNTIME_CONFIG_DIR"
    local tmp
    tmp="$(mktemp "$RUNTIME_CONFIG_DIR/.runtime_config.XXXXXX")"
    cat > "$tmp" <<EOF
$RUNTIME_CONFIG_MARKER
# install-path: $path_choice
#
# This workspace's runtime configuration, written for the install path above.
# Rewrite it for another path with:  make switch-path INSTALL_PATH=<local|docker>
# (or ./install.sh --switch-path <local|docker>). Hand edits are kept only
# if you delete the first line, after which the installer never touches it.
name: "omnibase-$path_choice"
description: "$description"
input_topic: "requests"
output_topic: "responses"
group_id: "onex-runtime"
event_bus:
  type: "$bus_type"
  profile: "local"
  environment: "local"
  max_history: 1000
  circuit_breaker_threshold: 5
EOF
    mv "$tmp" "$RUNTIME_CONFIG_FILE"
    info "Wrote the $path_choice runtime configuration to $RUNTIME_CONFIG_FILE"
}

# ------------------------------------------------------------------
# 1. Check prerequisites
# ------------------------------------------------------------------
info "Checking prerequisites..."

missing=()

if ! command -v git &>/dev/null; then
    missing+=("git")
fi

# Docker is a prerequisite of the docker path only. The local path never
# starts a container, so a host without Docker installs it fully.
if [ "$install_path" = "docker" ]; then
    if ! command -v docker &>/dev/null; then
        missing+=("docker (the docker install path runs the self-hosted stack in Docker; use --path local to install without it)")
    elif ! docker compose version &>/dev/null; then
        missing+=("docker compose plugin (needed by the docker install path)")
    fi
fi

if ! command -v uv &>/dev/null; then
    missing+=("uv (install: curl -LsSf https://astral.sh/uv/install.sh | sh)")
fi

# Check Python 3.12+
if command -v python3 &>/dev/null; then
    py_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    py_major=$(echo "$py_version" | cut -d. -f1)
    py_minor=$(echo "$py_version" | cut -d. -f2)
    if [ "$py_major" -lt 3 ] || { [ "$py_major" -eq 3 ] && [ "$py_minor" -lt 12 ]; }; then
        missing+=("python3.12+ (found $py_version)")
    fi
else
    missing+=("python3.12+")
fi

# Check Node 20+
if command -v node &>/dev/null; then
    node_major=$(node -v | sed 's/v//' | cut -d. -f1)
    if [ "$node_major" -lt 20 ]; then
        missing+=("node20+ (found v$node_major)")
    fi
else
    missing+=("node20+")
fi

if [ ${#missing[@]} -gt 0 ]; then
    error "Missing prerequisites:"
    for dep in "${missing[@]}"; do
        echo "  - $dep"
    done
    exit 1
fi

info "All prerequisites satisfied."

if [ "$switch_only" -eq 1 ]; then
    if [ ! -d "$OMNIBASE_PATH" ]; then
        error "No install at $OMNIBASE_PATH to switch. Run ./install.sh --path $install_path first."
        exit 1
    fi
    write_runtime_config "$install_path"
    info "Switched this install to the $install_path path. Nothing was cloned or rebuilt."
    if [ "$install_path" = "docker" ]; then
        echo "Start the self-hosted stack with:"
        echo "  cd $OMNIBASE_PATH/omnibase_infra && source scripts/onex-cli.sh && infra-up"
    fi
    exit 0
fi

# ------------------------------------------------------------------
# 2. Clone repositories
# ------------------------------------------------------------------
info "Cloning repositories into $REPOS_DIR..."
mkdir -p "$REPOS_DIR"

# Parse repos.yaml (simple line-based parsing, no yq dependency)
while IFS= read -r line; do
    # Extract repo field values
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*name:[[:space:]]*(.+) ]]; then
        current_name="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^[[:space:]]*repo:[[:space:]]*(.+) ]]; then
        current_repo="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^[[:space:]]*type:[[:space:]]*(.+) ]]; then
        current_type="${BASH_REMATCH[1]}"

        # We have all three fields — process this repo
        target="$REPOS_DIR/$current_name"
        if [ -d "$target" ]; then
            warn "$current_name already cloned, skipping."
        else
            info "Cloning $current_repo -> $current_name"
            # Some repos (e.g. private org repos) may not be accessible to
            # every caller. Don't let one inaccessible repo abort the whole
            # install under `set -e` — warn and continue.
            git clone "https://github.com/$current_repo.git" "$target" ||
                warn "Failed to clone $current_repo (private repo or no access?), skipping."
        fi
    fi
done < "$SCRIPT_DIR/repos.yaml"

# ------------------------------------------------------------------
# 3. Build Python environments
# ------------------------------------------------------------------
info "Building Python environments..."

for dir in "$REPOS_DIR"/*/; do
    repo=$(basename "$dir")
    if [ -f "$dir/pyproject.toml" ]; then
        info "Installing $repo (Python)..."
        (cd "$dir" && uv sync 2>&1 | tail -3) || warn "Failed to sync $repo (non-fatal)"
    fi
done

# ------------------------------------------------------------------
# 4. Install Node.js dependencies
# ------------------------------------------------------------------
if [ -d "$REPOS_DIR/omnidash" ] && [ -f "$REPOS_DIR/omnidash/package.json" ]; then
    info "Installing omnidash (Node.js)..."
    (cd "$REPOS_DIR/omnidash" && npm install 2>&1 | tail -3) || warn "Failed to install omnidash deps (non-fatal)"
fi

# ------------------------------------------------------------------
# 5. Install the Market skill package (Market nodes for `onex skill`)
# ------------------------------------------------------------------
# `onex skill` resolves nodes from omnimarket via a co-install into the
# omnibase_infra venv (the canonical mechanism omnibase_infra itself ships
# at scripts/install-node-skill-package.sh — never re-implemented here).
# Both repos and the infra venv must exist for this to be possible; skip
# (non-fatal, matching the rest of this script's degrade-gracefully
# posture) if either prerequisite didn't clone/build successfully above.
skill_installer="$REPOS_DIR/omnibase_infra/scripts/install-node-skill-package.sh"
infra_python="$REPOS_DIR/omnibase_infra/.venv/bin/python"
if [ -d "$REPOS_DIR/omnimarket" ] && [ -x "$skill_installer" ] && [ -x "$infra_python" ]; then
    info "Installing Market skill package (omnimarket) into the omnibase_infra venv..."
    bash "$skill_installer" --execute "$infra_python" ||
        warn "Failed to install the Market skill package (non-fatal) — re-run manually: bash $skill_installer --execute $infra_python"
else
    warn "Skipping Market skill package install: omnimarket and/or the omnibase_infra venv are not present."
    warn "Market skill nodes will show as \"Unknown node\" under 'onex skill' until you run:"
    warn "  bash $skill_installer --execute $infra_python"
fi

# ------------------------------------------------------------------
# 6. Set up environment file
# ------------------------------------------------------------------
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    info "Created .env from template. Edit it with your configuration."
else
    info ".env already exists, skipping."
fi

if ! grep -q '^OMNIBASE_PATH=' "$SCRIPT_DIR/.env" 2>/dev/null; then
    { echo ""; echo "# Canonical workspace root (installer-derived) — required by the"; \
      echo "# omnimarket drift guard and the workspace-root node refusals."; \
      echo "OMNIBASE_PATH=$OMNIBASE_PATH"; \
      echo "# Temporary bridge for tools still on the older spelling; removed"; \
      echo "# by OMN-16856. Same directory, not a second parameter."; \
      echo "OMNI_HOME=$OMNIBASE_PATH"; } >> "$SCRIPT_DIR/.env"
fi

# ------------------------------------------------------------------
# 7. Write the runtime configuration for the chosen install path
# ------------------------------------------------------------------
write_runtime_config "$install_path"

# ------------------------------------------------------------------
# Done
# ------------------------------------------------------------------
echo ""
info "Installation complete!"
echo ""
echo "Install path: $install_path (runtime configuration: $RUNTIME_CONFIG_FILE)"
echo ""
echo "Next steps:"
echo "  1. Export OMNIBASE_PATH in your shell (required — see docs/GETTING_STARTED.md):"
echo "       export OMNIBASE_PATH=\"$OMNIBASE_PATH\""
if [ "$install_path" = "docker" ]; then
    echo "  2. Edit .env with your configuration (passwords, endpoints)"
    echo "  3. Start the self-hosted stack (PostgreSQL, Redpanda, Valkey):"
    echo "       cd $OMNIBASE_PATH/omnibase_infra && source scripts/onex-cli.sh && infra-up"
    echo "  4. Run 'make dev' to start development servers"
    echo "  5. Run 'make status' to check everything is running"
else
    echo "  2. Run 'make dev' to start development servers"
    echo "  3. Run 'make status' to check everything is running"
    echo ""
    echo "The local path needs no Docker. Docker is used only by the docker install path"
    echo "(the self-hosted stack); switch to it later with: make switch-path INSTALL_PATH=docker"
fi
echo ""
