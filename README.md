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

# Common commands
poetry run onex list-nodes                    # List all available nodes
poetry run onex run stamper_node --introspect # Get node information
poetry run onex validate src/omnibase/        # Validate files
poetry run onex stamp file **/*.py            # Stamp Python files
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

## Architecture Overview

ONEX provides a contract-first, metadata-driven execution model for composable, trust-aware nodes. Key architectural components include:

- **Node-as-Function Model**: Nodes are self-contained, executable units with formal interfaces
- **Protocol-Driven Design**: All components follow standardized protocol interfaces
- **Registry System**: Automatic node discovery and version resolution
- **Trust & Validation**: Built-in integrity checking and compliance enforcement
- **CLI Integration**: Comprehensive command-line interface for all operations

## Getting Started

For complete setup instructions, see the **[Getting Started Guide](docs/guides/getting_started.md)** which covers:
- Environment setup and installation
- Basic CLI usage and workflows
- Development environment configuration
- Testing and validation procedures

## Pre-commit Hooks
To ensure code quality and consistency, this project uses [pre-commit](https://pre-commit.com/) with hooks for black, ruff, and isort. To set up:

```bash
pre-commit install
pre-commit run --all-files
```

> **Note:** A pre-push hook will automatically run the full test suite (`pytest`) before every `git push`. This ensures that no untested code is pushed to the repository. You can skip this check with `git push --no-verify` (not recommended).

See [docs/guides/getting_started.md](docs/guides/getting_started.md#5-confirm-pre-commit-hooks) for more details.

## Documentation

### 📚 Core Documentation
- **[Documentation Overview](docs/README.md)** - Complete documentation index and navigation
- **[Getting Started Guide](docs/guides/getting_started.md)** - Installation, setup, and first steps
- **[CLI Quick Reference](docs/cli_examples.md)** - Essential CLI commands and usage patterns

### 🏗️ Architecture & Design
- **[Node Architecture Series](docs/nodes/index.md)** - Comprehensive guide to ONEX node architecture
- **[Core Protocols](docs/reference-protocols-core.md)** - Core protocol definitions and execution
- **[Registry Protocols](docs/reference-protocols-registry.md)** - Registry, validation, handler protocols
- **[Data Models](docs/reference-data-models.md)** - Data models, composition, testing
- **[Registry Architecture](docs/registry_architecture.md)** - Node discovery and version resolution system
- **[Error Handling](docs/error_handling.md)** - Error taxonomy, retry patterns, and observability
- **[Monadic Node Core](docs/architecture-node-monadic-core.md)** - Core monadic principles and interfaces
- **[Node Composition](docs/architecture-node-composition.md)** - Composition patterns and execution models

### 🔧 Development
- **[Developer Guide](docs/developer_guide.md)** - Development conventions and best practices
- **[Contributing Guidelines](docs/contributing.md)** - How to contribute to the project
- **[Testing Framework](docs/testing.md)** - Testing philosophy and guidelines
- **[Standards](docs/standards.md)** - Naming conventions and code standards

### 🛠️ Tools & CLI
- **[CLI Interface](docs/cli_interface.md)** - Complete CLI specification and commands
- **[Stamper Tool](docs/tools/stamper.md)** - File metadata stamping and validation
- **[Handler Protocols](docs/reference-handlers-protocol.md)** - Handler protocols and interfaces
- **[Handler Registry](docs/reference-handlers-registry.md)** - Registry API and management
- **[Handler Implementation](docs/guide-handlers-implementation.md)** - Implementation examples and testing

### 🔒 Operations & Security
- **[Security Overview](docs/reference-security-overview.md)** - Architecture and authentication
- **[Security Implementation](docs/guide-security-implementation.md)** - Authorization, secrets, secure execution
- **[Security Design](docs/architecture-security-design.md)** - Network security architecture
- **[Security Monitoring](docs/guide-security-monitoring.md)** - Security monitoring and vulnerability management
- **[Incident Response](docs/guide-incident-response.md)** - Incident response and compliance
- **[Infrastructure](docs/infrastructure.md)** - Deployment and infrastructure requirements
- **[Monitoring](docs/monitoring.md)** - Observability and metrics collection

### 📋 Reference
- **[Metadata Specification](docs/metadata.md)** - Canonical metadata block format
- **[Configuration](docs/configuration.md)** - System configuration and settings
- **[Lifecycle Policy](docs/lifecycle_policy.md)** - Node lifecycle management
- **[Changelog](docs/changelog.md)** - Version history and release notes

## Contribution Policy

> **Status:** Project is in foundational refactor. **No outside PRs until node infra is finalized.**  
> Please open an issue to discuss or use [this issue](link-to-notify-issue) to be notified when contributions open.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

---

For comprehensive documentation, see the **[Documentation Overview](docs/README.md)** which provides complete navigation to all available resources.

## Testing

This project follows a comprehensive testing philosophy with protocol-driven test design. See the **[Testing Framework](docs/testing.md)** for:
- Canonical testing philosophy and principles
- Test structure and organization guidelines
- Node testing patterns and best practices
- Fixture management and test data guidelines

All test-related questions and practices are governed by the testing documentation.

## License

This project is licensed under the terms of the [MIT License](LICENSE).
