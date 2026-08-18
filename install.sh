#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS_DIR="$SCRIPT_DIR/repos"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}==>${NC} $*"; }
warn()  { echo -e "${YELLOW}==>${NC} $*"; }
error() { echo -e "${RED}ERROR:${NC} $*" >&2; }

# ------------------------------------------------------------------
# 1. Check prerequisites
# ------------------------------------------------------------------
info "Checking prerequisites..."

missing=()

if ! command -v git &>/dev/null; then
    missing+=("git")
fi

if ! command -v docker &>/dev/null; then
    missing+=("docker")
fi

if ! command -v docker compose version &>/dev/null 2>&1 && ! docker compose version &>/dev/null 2>&1; then
    # Try the plugin form
    if ! docker compose version &>/dev/null 2>&1; then
        missing+=("docker-compose")
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
# 5. Set up environment file
# ------------------------------------------------------------------
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    info "Created .env from template. Edit it with your configuration."
else
    info ".env already exists, skipping."
fi

# ------------------------------------------------------------------
# Done
# ------------------------------------------------------------------
echo ""
info "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your configuration (passwords, endpoints)"
echo "  2. Run 'make setup' to create your .env file (does NOT start Docker)"
echo "  3. Run 'make dev' to start development servers"
echo "  4. Run 'make status' to check everything is running"
echo ""
