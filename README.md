<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: README.md
version: 1.0.0
uuid: eeb2be00-8df6-4d14-8b00-17755d1496a0
author: OmniNode Team
created_at: '2025-05-28T12:40:25.889454'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://README
namespace: markdown://README
meta_type: tool

<!-- === /OmniNode:Metadata === -->
# OmniBase / ONEX

[![CI](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/ci.yml?branch=main&label=CI)](https://github.com/OmniNode-ai/omnibase/actions/workflows/ci.yml)
[![Pre-commit](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/ci.yml?branch=main&label=Pre-commit)](https://github.com/OmniNode-ai/omnibase/actions/workflows/ci.yml)
[![MyPy](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/ci.yml?branch=main&label=MyPy)](https://github.com/OmniNode-ai/omnibase/actions/workflows/ci.yml)
[![Tree Validation](https://img.shields.io/github/actions/workflow/status/OmniNode-ai/omnibase/ci.yml?branch=main&label=Tree%20Validation)](https://github.com/OmniNode-ai/omnibase/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

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

## Key Features

### 🔧 Structured Logging Infrastructure
ONEX provides a comprehensive structured logging system that routes all internal logging through the Logger Node as side effects, following functional monadic architecture principles.

**Key Benefits:**
- **Architectural Purity:** All output flows through Logger Node as intended side effects
- **Zero Complexity:** No compatibility layers or handlers to maintain
- **Better Observability:** Even CLI output gets correlation IDs and structured context
- **Single Configuration:** All output formatting controlled by Logger Node

**Configuration via Environment Variables:**
```bash
export ONEX_LOG_FORMAT=json          # Output format: json, yaml, markdown, text, csv
export ONEX_LOG_LEVEL=info           # Log level: debug, info, warning, error, critical
export ONEX_ENABLE_CORRELATION_IDS=true  # Enable correlation ID generation
export ONEX_LOG_TARGETS=stdout       # Output targets: stdout, stderr, file
export ONEX_LOG_FILE_PATH=/path/to/log.txt  # File path for file output
```

**Usage in Code:**
```python
from omnibase.core.structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum

# Replace all print() and logging calls with structured events
emit_log_event(LogLevelEnum.INFO, "Processing file", {"filename": "data.json"})
emit_log_event("error", "Operation failed", {"error_code": "ONEX_001"})
```

### 🔌 Plugin Discovery System
ONEX supports flexible plugin discovery through multiple mechanisms with priority-based loading.

**Discovery Methods:**
1. **Entry Points** (pyproject.toml/setup.cfg) - Priority 0
2. **Configuration Files** (plugin_registry.yaml) - Priority 5
3. **Environment Variables** - Priority 10 (highest)

**Supported Plugin Types:**
- **Handlers:** File type processors for metadata extraction
- **Validators:** Custom validation plugins
- **Tools:** Extended functionality plugins
- **Fixtures:** Test fixture providers
- **Nodes:** Node plugins (M2 development)

**Example Configuration:**
```yaml
# plugin_registry.yaml
handlers:
  csv_processor:
    module: "omnibase.plugins.handlers.csv_handler"
    class: "CSVHandler"
    priority: 5
    description: "CSV file processor with metadata extraction"
```

See [docs/plugins/plugin_discovery.md](docs/plugins/plugin_discovery.md) for complete documentation.

### 🛡️ Centralized Error Code System
All error handling uses centralized error codes for consistency and debugging.

**Usage:**
```python
from omnibase.core.error_codes import OnexError, CoreErrorCode

# All errors use defined codes
raise OnexError("Invalid input provided", CoreErrorCode.INVALID_PARAMETER)
```

**Benefits:**
- Consistent error reporting across all components
- CI enforcement of error code compliance
- Structured error handling for better debugging

### 🔒 Sensitive Field Redaction
Automatic redaction of sensitive fields in logs and events to prevent credential leakage.

**Features:**
- Automatic detection and redaction of sensitive fields
- Configurable redaction patterns
- Safe logging of state models with sensitive data
- Protocol-first testing with redaction validation

### 📊 Telemetry & Event Infrastructure
Comprehensive telemetry system with correlation ID propagation and event-driven architecture.

**Features:**
- Correlation/Request ID propagation across all operations
- ONEX Event Schema standardization
- Real-time event processing capabilities
- Telemetry decorators for node entrypoints

### 🔧 Function Metadata Extension
Language-agnostic function-as-tool stamping capability that treats functions as tools within the unified metadata schema.

**Supported Languages:**
- **Python:** AST-based parsing with type hints and docstrings
- **JavaScript/TypeScript:** AST-based parsing with JSDoc and TypeScript types
- **Bash/Shell:** Pattern-based parsing with comment metadata
- **YAML/JSON:** Schema-based function definitions

**Benefits:**
- 56% reduction in metadata overhead vs separate blocks
- Natural tool discovery across all languages
- Seamless integration with existing ONEX infrastructure
- Foundation for M2 dynamic tool composition

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
- [Plugin Discovery Guide](docs/plugins/plugin_discovery.md)
- [Developer Guide](docs/nodes/developer_guide.md)

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
