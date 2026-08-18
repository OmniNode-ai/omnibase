.PHONY: install setup dev test update status clean help

REPOS_DIR := $(CURDIR)/repos
SHELL := /bin/bash

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Clone all repos, build Python envs, install Node deps
	@echo "==> Installing ONEX platform..."
	@bash install.sh
	@echo "==> Installation complete. Run 'make setup' to configure environment."

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
	@for repo in omnibase_core omnibase_infra omnibase_spi omnibase_compat omniclaude omniintelligence omnimemory onex_change_control; do \
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
	@echo "==> To check infrastructure status, run: infra-status"

clean: ## Remove all cloned repos (destructive!)
	@echo "WARNING: This will delete all cloned repositories in repos/."
	@read -p "Are you sure? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		rm -rf $(REPOS_DIR); \
		echo "==> Cleaned."; \
	else \
		echo "==> Cancelled."; \
	fi
