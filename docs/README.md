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
- [ONEX Protocol Primer](onex/index.md) - Core protocol concepts
- [Node Architecture](nodes/index.md) - Node development and patterns
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