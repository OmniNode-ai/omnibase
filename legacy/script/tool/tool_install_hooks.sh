#!/bin/bash

# Script to install git hooks for the project (hybrid orchestrator approach)

set -e

# Resolve the git repository root
REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_SRC="$REPO_ROOT/containers/foundation/src/foundation/script/hooks"
GIT_HOOKS="$REPO_ROOT/.git/hooks"

cd "$REPO_ROOT"

echo "Installing canonical git hooks (pre-commit, post-merge, post-checkout)..."

# Create hooks directory if it doesn't exist
mkdir -p "$GIT_HOOKS"

# Install pre-commit hook (runs orchestrator on staged files)
cp "$HOOKS_SRC/hooks_pre-commit" "$GIT_HOOKS/pre-commit"
chmod +x "$GIT_HOOKS/pre-commit"

# Install post-merge hook (ensures pre-commit hook is up-to-date after merges)
if [ -f "$HOOKS_SRC/hooks_post-merge" ]; then
  cp "$HOOKS_SRC/hooks_post-merge" "$GIT_HOOKS/post-merge"
  chmod +x "$GIT_HOOKS/post-merge"
fi

# Install post-checkout hook (ensures pre-commit hook is up-to-date after branch switches)
if [ -f "$HOOKS_SRC/hooks_post-checkout" ]; then
  cp "$HOOKS_SRC/hooks_post-checkout" "$GIT_HOOKS/post-checkout"
  chmod +x "$GIT_HOOKS/post-checkout"
fi

echo "Done! Canonical git hooks installed:"
echo "- pre-commit: runs the orchestrator on staged files (standards-compliant tuples only)"
echo "- post-merge: ensures pre-commit hook is up-to-date after merges (if present)"
echo "- post-checkout: ensures pre-commit hook is up-to-date after branch switches (if present)"
echo "You can bypass the hooks with git commit --no-verify if needed."
