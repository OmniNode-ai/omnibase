# Git Utilities for OmniNode

## Orchestration Script: `orchestrate_git.py`

A minimal orchestrator for batch git and project board actions.

### Usage

```sh
python utils/git/orchestrate_git.py add commit push add-ticket \
  --path . --message "My commit" \
  --org OmniNode-ai --project 1 --url https://github.com/OmniNode-ai/ai-dev/issues/144 \
  --dry-run
```

- `add`, `commit`, `push`, `add-ticket` are actions performed in order.
- `--dry-run` prints actions instead of executing them.

## Add Ticket Utility: `add_ticket_to_project.py`

Adds a GitHub issue to an org-level project board using the GitHub CLI.

### Usage

```sh
python utils/git/add_ticket_to_project.py \
  --org OmniNode-ai --project 1 --url https://github.com/OmniNode-ai/ai-dev/issues/144 \
  --dry-run
```

- Requires the GitHub CLI (`gh`) to be installed and authenticated.
- `--dry-run` prints the command instead of executing it.

## Unit Tests

Tests for the add-ticket utility are in `utils/git/tests/test_add_ticket_to_project.py`.

### Run tests:

```sh
pytest utils/git/tests/test_add_ticket_to_project.py
```

---

**Note:** These tools are designed for dry-run safety and can be extended for more advanced workflows.
