<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: README.md
version: 1.0.0
uuid: 97d6edb7-6d01-4783-8446-8b6bbf2f3074
author: OmniNode Team
created_at: 2025-05-27T05:24:25.600769
last_modified_at: 2025-05-27T17:26:51.993942
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: f473dae78a59f4175c125ac7f244af4cf7310d157cb9c5d2c38a2a9378e5a48c
entrypoint: python@README.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.README
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# OmniBase / ONEX Documentation

Welcome to the OmniBase (ONEX) documentation. This is the canonical source for architecture, onboarding, and reference materials for the ONEX node execution protocol.

---

## Overview

OmniBase provides a contract-first, metadata-driven execution model for composable, trust-aware nodes. This documentation covers:

- **Architecture:** Core protocols, registry design, and execution patterns
- **Node Development:** How to create, test, and deploy ONEX nodes
- **CLI Tools:** Command-line interface for node management and validation
- **Standards:** Coding conventions, testing guidelines, and best practices

---

## Directory Structure

```
docs/
├── README.md                # This file - documentation overview
├── index.md                 # Main documentation hub
├── architecture/            # Architecture deep dives and design decisions
├── error_handling/          # Error handling specifications and patterns
├── guides/                  # Getting started, CLI, and how-to guides
├── metadata/                # Metadata specifications and validation
├── nodes/                   # Node architecture and development guides
├── onex/                    # ONEX protocol primer and specifications
├── plugins/                 # Plugin system documentation
├── protocol/                # Core protocol specifications
├── rfcs/                    # Request for Comments and proposals
├── security/                # Security specifications and threat models
├── standards/               # Coding and naming standards
├── templates/               # Documentation templates
├── testing/                 # Testing guidelines and best practices
└── tools/                   # Tool documentation and usage guides
```

---

## Quick Start

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Run the ONEX CLI:**
   ```bash
   poetry run onex --help
   ```

3. **Validate nodes:**
   ```bash
   poetry run onex run parity_validator_node
   ```

4. **Run tests:**
   ```bash
   poetry run pytest
   ```

---

## Key Documentation

- [Documentation Hub](index.md) - Main entry point with all specifications
- [Getting Started Guide](guides/getting_started.md) - Environment setup and first steps
- [Core Protocols](reference-protocols-core.md) - Core protocol definitions and execution
- [Registry Protocols](reference-protocols-registry.md) - Registry, validation, handler protocols
- [Data Models](reference-data-models.md) - Data models, composition, testing
- [Node Architecture](nodes/index.md) - Node development and patterns
- [Monadic Node Core](architecture-node-monadic-core.md) - Core monadic principles and interfaces
- [Node Composition](architecture-node-composition.md) - Composition patterns and execution models
- [Handler Protocols](reference-handlers-protocol.md) - Handler protocols and interfaces
- [Handler Registry](reference-handlers-registry.md) - Registry API and management
- [Handler Implementation](guide-handlers-implementation.md) - Implementation examples and testing
- [CLI Interface](cli_interface.md) - Command-line tool reference
- [Testing Guidelines](testing.md) - Testing philosophy and practices

---

## Registry-Centric Architecture

OmniBase/ONEX uses a fully registry-driven, versioned artifact structure. All nodes, adapters, contracts, runtimes, CLI tools, and packages are versioned in their own subdirectories, with explicit metadata and registry references.

### Example Directory Layout

```
src/omnibase/
  nodes/
    stamper_node/
      v1_0_0/
        node.py
        node.onex.yaml
        contract.yaml
        adapters/
          cli_adapter.py
        tests/
          test_node.py
          fixtures/
            sample_input.yaml
  runtimes/
    onex_runtime/
      v1_0_0/
        runtime.py
        runtime.yaml
  cli_tools/
    onex/
      v1_0_0/
        cli_main.py
        cli_tool.yaml
  registry/
    registry.yaml
    adapters.yaml
    contracts.yaml
    runtimes.yaml
    packages.yaml
    cli_tools.yaml
```

### Key Principles

- **Versioned Artifacts:** All artifacts are versioned in their own subdirectories
- **Explicit References:** All references are explicit in metadata and resolved via the registry
- **Dynamic Loading:** No symlinks or direct imports—everything is loaded dynamically by the registry
- **Compatibility Management:** Managed via semantic version ranges in metadata
- **Independent Evolution:** CLI tools, nodes, adapters, contracts, runtimes, and packages can all evolve independently

### Loader and .onextree Manifest

- The `.onextree` file is a declarative manifest describing the directory structure for ONEX projects
- Used by the registry for validation, discovery, and enforcement of standards
- Loader only recognizes a version if `node.onex.yaml` is present or a `.wip` marker file is set
- Adapters and contracts must be referenced in `node.onex.yaml` with explicit module/class and filename

---

## Contributing to Documentation

1. Follow the directory conventions outlined above
2. Every substantial document should include a metadata block (`Status`, `Last Updated`, etc.)
3. Name files with lowercase snake_case
4. Keep line length ≤ 100 chars when practical
5. Run `pre-commit run --all-files` before pushing

For more information, see the main [project README](../README.md).

This documentation is automatically validated in CI to ensure consistency and accuracy.

## Quick Navigation
