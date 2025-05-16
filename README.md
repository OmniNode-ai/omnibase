# OmniBase / ONEX

[![Build Status](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/bootstrap.yml?branch=main)](https://github.com/OmniNode-ai/omnibase/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Status:** Bootstrap (Milestone 0)

OmniBase (ONEX) is the canonical execution, validation, and planning protocol for OmniNode-based systems. This repository provides the foundational scaffolding, protocols, CLI, and documentation for building, validating, and composing ONEX nodes.

## Project Summary
- **Purpose:** Establish a contract-first, metadata-driven execution model for composable, trust-aware nodes.
- **Scope:** This repository contains the ONEX CLI, protocol definitions, canonical templates, and documentation for node authors, tool builders, and runtime developers.

## Quickstart

```bash
# Clone the repo
git clone https://github.com/OmniNode-ai/omnibase.git
cd omnibase

# Install dependencies (using Poetry)
poetry install

# Run the CLI
poetry run onex --help
```

## Roadmap

- **Milestone 0:** Bootstrap, protocols, CLI, templates, and canonical test suite.
- **Milestone 1:** Validation engine, registry, and execution runtime.
- **Milestone 2:** Planning, caching, trust, and composite graph support.
- **Milestone 3+:** Federation, P2P, and interop.

See [docs/milestones/overview.md](docs/milestones/overview.md) for details.

## Milestone 0: Bootstrap
- **Goal:** Provide the minimal infrastructure to support node discovery, validation, and CI integration.
- **Includes:**
  - Canonical directory structure
  - Protocol and registry stubs
  - CLI entrypoint (`onex`)
  - Example templates and schemas
  - Documentation for onboarding and architecture

## Getting Started
See [docs/guides/getting_started.md](docs/guides/getting_started.md) for environment setup, installation, and first-run instructions.

## Pre-commit Hooks
To ensure code quality and consistency, this project uses [pre-commit](https://pre-commit.com/) with hooks for black, ruff, and isort. To set up:

```bash
pre-commit install
pre-commit run --all-files
```

> **Note:** A pre-push hook will automatically run the full test suite (`pytest`) before every `git push`. This ensures that no untested code is pushed to the repository. You can skip this check with `git push --no-verify` (not recommended).

See [docs/guides/getting_started.md](docs/guides/getting_started.md#5-confirm-pre-commit-hooks) for more details.

## Documentation
- [ONEX Protocol Primer](docs/onex/index.md)
- [Node Architecture Series](docs/nodes/index.md)
- [Milestone Overview](docs/milestones/overview.md)

## Contribution Policy

> **Status:** Project is in foundational refactor. **No outside PRs until node infra is finalized.**  
> Please open an issue to discuss or use [this issue](link-to-notify-issue) to be notified when contributions open.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

---

For more information, see the [docs/README.md](docs/README.md) or ask in the project chat.

## Testing

See [docs/testing.md](docs/testing.md) for the canonical testing philosophy, structure, and all contributor guidance. All test-related questions and practices are governed by that document.

## License

This project is licensed under the terms of the [MIT License](LICENSE).