<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:25.901531'
description: Stamped by ONEX
entrypoint: python://README.md
hash: 18af5acd37a67f59cc014e66aa3abb2dee10f6dab37872a31f96a672938db67b
last_modified_at: '2025-05-29T11:50:15.288809+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: README.md
namespace: omnibase.README
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: e4eebccb-2f29-41b5-a94e-d158f74d2390
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# OmniBase / ONEX Documentation

Welcome to the OmniBase (ONEX) documentation. This is the canonical source for architecture, onboarding, and reference materials for the ONEX node execution protocol.

---

## Bootstrap Milestone (M0)
- **Purpose:** Establish the foundational structure, protocols, and CLI for ONEX.
- **Includes:**
  - Canonical directory structure
  - Protocol and registry stubs
  - CLI entrypoint (`onex`)
  - Example templates and schemas
  - Onboarding and architecture docs

---

## Directory Structure

```
/ (repo root)
├── README.md                # Project summary and onboarding
├── docs/                    # Documentation (this folder)
│   ├── guides/              # Getting started, CLI, advanced usage
│   ├── nodes/               # Node Architecture Series
│   ├── milestones/          # Milestone checklists and overviews
│   ├── onex/                # ONEX protocol primer and index
│   └── testing/             # Canonical testing guidance
├── src/omnibase/            # Source code (core, protocol, tools, etc.)
└── tests/                   # Test suite (mirrors src/omnibase/)
```

---

## Running the CLI and Tests

1. **Install dependencies:**
   - With Poetry: `poetry install`
   - Or see [guides/getting_started.md](guides/getting_started.md)
2. **Run the ONEX CLI:**
   ```bash
   poetry run onex --help
   ```
3. **Validate an example node:**
   ```bash
   poetry run onex validate nodes/example_node/node.onex.yaml
   ```
4. **Run tests:**
   ```bash
   poetry run pytest
   ```

---

## Key Documentation
- [ONEX Protocol Primer](onex/index.md)
- [Node Architecture Series](nodes/index.md)
- [Milestone Overview](milestones/overview.md)
- [Developer Guide](nodes/developer_guide.md)

For more, see the [project README](../README.md) or ask in the project chat.

# Canonical Registry-Centric, Versioned Structure (2025-06)

OmniBase/ONEX now uses a fully registry-driven, versioned artifact structure. All nodes, adapters, contracts, runtimes, CLI tools, and packages are versioned in their own subdirectories, with explicit metadata and registry references. The loader and CI enforce this structure using a `.onextree` manifest and registry metadata files.

## Example Directory Layout

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

- All artifacts are versioned in their own subdirectories.
- All references are explicit in metadata and resolved via the registry.
- No symlinks or direct imports—everything is loaded dynamically by the registry.
- Compatibility is managed via semantic version ranges in metadata.
- CLI tools, nodes, adapters, contracts, runtimes, and packages can all evolve independently, with the registry enforcing compatibility and discoverability.

## Loader and .onextree Manifest

- The `.onextree` file is a declarative manifest describing the desired or actual directory structure for ONEX projects and artifact packages. It is used by the registry for validation, discovery, and enforcement of standards.
- Loader only recognizes a version if `node.onex.yaml` is present or a `.wip` marker file is set in the version directory.
- Adapters and contracts must be referenced in `node.onex.yaml` with explicit module/class and filename.

## Roadmap: Document Store Versioning

- Future milestones will introduce versioning for the documentation store itself, enabling historical doc lookup, doc evolution tracking, and registry-driven doc discovery.
