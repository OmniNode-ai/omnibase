<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: README.md
version: 1.0.0
uuid: 35a46723-963b-47b0-b57d-315861920aa4
author: OmniNode Team
created_at: 2025-05-21T13:18:56.541089
last_modified_at: 2025-05-22T21:18:53.686248
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: bc995f8bcbc88ed93eb6d4dae0c6f1f5f19ccd8572139bbb680d69d6a37f084b
entrypoint: python@README.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.README
meta_type: tool
<!-- === /OmniNode:Metadata === -->

# OmniBase / ONEX

[![CI](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/ci.yml?branch=main&label=CI)](https://github.com/OmniNode-ai/omnibase/actions/workflows/ci.yml)
[![Pre-commit](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/ci.yml?branch=main&label=Pre-commit)](https://github.com/OmniNode-ai/omnibase/actions/workflows/ci.yml)
[![MyPy](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/ci.yml?branch=main&label=MyPy)](https://github.com/OmniNode-ai/omnibase/actions/workflows/ci.yml)
[![Tree Validation](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/ci.yml?branch=main&label=Tree%20Validation)](https://github.com/OmniNode-ai/omnibase/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

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

## CI & Quality Metrics

Our CI pipeline enforces strict quality standards across all components:

| Check | Status | Description |
|-------|--------|-------------|
| **Tests** | [![Tests](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/ci.yml?branch=main&label=Tests)](https://github.com/OmniNode-ai/omnibase/actions/workflows/ci.yml) | All unit, integration, and protocol tests must pass |
| **Type Safety** | [![MyPy](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/ci.yml?branch=main&label=MyPy)](https://github.com/OmniNode-ai/omnibase/actions/workflows/ci.yml) | Full MyPy type checking with strict mode |
| **Code Quality** | [![Pre-commit](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/ci.yml?branch=main&label=Pre-commit)](https://github.com/OmniNode-ai/omnibase/actions/workflows/ci.yml) | Black, isort, yamllint, and custom hooks |
| **Structure Validation** | [![Tree Validation](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/ci.yml?branch=main&label=Tree%20Validation)](https://github.com/OmniNode-ai/omnibase/actions/workflows/ci.yml) | `.onextree` manifest must match directory structure |

### Enforcement Standards
- **Schema Validation**: All metadata blocks must pass schema validation
- **Lifecycle Compliance**: All nodes must have valid lifecycle fields (draft/active/deprecated/archived)
- **Hash Integrity**: All metadata must be properly hash-stamped for integrity
- **Protocol Compliance**: All code must follow protocol-driven architecture patterns
- **Zero Tolerance**: CI blocks any non-compliant commits

> **Status:** Milestone 1 Implementation (CI & Enforcement)

OmniBase (ONEX) is the canonical execution, validation, and planning protocol for OmniNode-based systems. This repository provides the foundational scaffolding, protocols, CLI, and documentation for building, validating, and composing ONEX nodes.

## Project Summary
- **Purpose:** Establish a contract-first, metadata-driven execution model for composable, trust-aware nodes.
- **Scope:** This repository contains the ONEX CLI, protocol definitions, canonical templates, and documentation for node authors, tool builders, and runtime developers.

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
