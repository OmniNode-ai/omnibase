.PHONY: install switch-path setup dev test update status clean help

# Derived from this Makefile's own location (MAKEFILE_LIST), not $(CURDIR):
# $(CURDIR) is the invoking shell's cwd, which only matches the checkout
# when make is run from inside it. `make -f /path/to/omnibase/Makefile
# install` from elsewhere would otherwise silently point REPOS_DIR and the
# workspace root at the caller's cwd instead of the checkout.
MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
REPOS_DIR := $(MAKEFILE_DIR)repos
SHELL := /bin/bash

# Canonical workspace root every sibling repo clone hangs off of
# ($OMNIBASE_PATH/<repo>). Exported so every recipe below (and anything it
# invokes, e.g. the onex CLI or the omnimarket drift guard) inherits it.
# Derived from this Makefile's own location, never hardcoded and never
# silently defaulted to the wrong directory.
export OMNIBASE_PATH := $(REPOS_DIR)

# TEMPORARY BRIDGE — remove with OMN-16856. The omnimarket sweep and
# orchestration nodes, and the Market skill co-install script, still read
# the older OMNI_HOME spelling of this same root. Setting both to one
# derived directory keeps them working while OMN-16856's scope question is
# open. This is one directory with two labels, not two parameters.
export OMNI_HOME := $(REPOS_DIR)

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# The install path (OMN-20123): local (fully local runtime, no Docker; the
# default) or docker (self-hosted Docker stack). Empty means install.sh asks
# when run in a terminal and uses local otherwise. Cloud is not selectable yet.
INSTALL_PATH ?=

install: ## Clone all repos, build Python envs, install Node deps (INSTALL_PATH=local|docker)
	@echo "==> Installing ONEX platform..."
	@bash install.sh $(if $(INSTALL_PATH),--path $(INSTALL_PATH))
	@echo "==> Installation complete. Run 'make setup' to configure environment."

switch-path: ## Rewrite the runtime configuration for another install path (INSTALL_PATH=local|docker)
	@if [ -z "$(INSTALL_PATH)" ]; then \
		echo "ERROR: name the path to switch to: make switch-path INSTALL_PATH=local or INSTALL_PATH=docker" >&2; \
		exit 2; \
	fi
	@bash install.sh --switch-path $(INSTALL_PATH)

setup: ## Create .env from template
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "==> Created .env from template. Edit it with your configuration."; \
	else \
		echo "==> .env already exists, skipping."; \
	fi
	@echo "==> Optional: to run the full self-hosted stack (Docker), see docs/GETTING_STARTED.md"

dev: ## Start omnidash dev server and show onex CLI help
	@echo "==> Starting development environment..."
	@if [ -d $(REPOS_DIR)/omnidash ]; then \
		echo "Starting omnidash dev server on port 3000..."; \
		cd $(REPOS_DIR)/omnidash && PORT=3000 npm run dev & \
	fi
	@if [ -d $(REPOS_DIR)/omnibase_core ]; then \
		echo ""; \
		echo "==> onex CLI:"; \
		cd $(REPOS_DIR)/omnibase_core && uv run onex --help 2>/dev/null || echo "(onex CLI not available — run 'make install' first)"; \
	fi

test: ## Run tests across all Python repos
	@echo "==> Running tests..."
	@for repo in omnibase_core omnibase_infra omnibase_spi omnibase_compat omniclaude omniintelligence omnimemory omnimarket onex_change_control; do \
		if [ -d $(REPOS_DIR)/$$repo ]; then \
			echo ""; \
			echo "--- Testing $$repo ---"; \
			cd $(REPOS_DIR)/$$repo && uv run pytest tests/ -x -q 2>&1 | tail -5 || true; \
		fi; \
	done
	@echo ""
	@echo "==> Tests complete."

update: ## Pull latest main across all repos
	@echo "==> Updating all repositories..."
	@for dir in $(REPOS_DIR)/*/; do \
		repo=$$(basename $$dir); \
		echo "--- $$repo ---"; \
		cd $$dir && git pull --ff-only 2>&1 | tail -1 || true; \
	done
	@echo ""
	@echo "==> Update complete."

status: ## Show repo versions and infrastructure health
	@echo "==> Repository status:"
	@for dir in $(REPOS_DIR)/*/; do \
		repo=$$(basename $$dir); \
		branch=$$(cd $$dir && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?"); \
		commit=$$(cd $$dir && git log -1 --format='%h %s' 2>/dev/null || echo "?"); \
		printf "  %-25s %-10s %s\n" "$$repo" "[$$branch]" "$$commit"; \
	done
	@echo ""
	@path=$$(sed -n 's/^# install-path: //p' $(REPOS_DIR)/config/onex/runtime/runtime_config.yaml 2>/dev/null); \
	if [ -z "$$path" ]; then \
		echo "==> Install path: unknown (no installer-written runtime configuration; run 'make install')"; \
	elif [ "$$path" = "docker" ]; then \
		echo "==> Install path: docker. To check the self-hosted stack, run infra-status from repos/omnibase_infra (after 'source scripts/onex-cli.sh')"; \
	else \
		echo "==> Install path: $$path (fully local runtime, no Docker)"; \
	fi

clean: ## Remove all cloned repos (destructive!)
	@echo "WARNING: This will delete all cloned repositories in repos/."
	@read -p "Are you sure? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		rm -rf $(REPOS_DIR); \
		echo "==> Cleaned."; \
	else \
		echo "==> Cancelled."; \
	fi
