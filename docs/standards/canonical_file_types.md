<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: canonical_file_types.md
version: 1.0.0
uuid: 7c9aa5e9-82c3-47dc-8345-2a5dc100ca9c
author: OmniNode Team
created_at: 2025-05-28T12:40:27.149158
last_modified_at: 2025-05-28T17:20:04.292793
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 67236f0867f9e068e348e27b65baf1657de63d14ee2e1dcf157d86a996784c5d
entrypoint: python@canonical_file_types.md
runtime_language_hint: python>=3.11
namespace: omnibase.stamped.canonical_file_types
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Canonical File Types Index

> **Status:** Canonical
> **Last Updated:** 2024-06-14
> **Purpose:** This document enumerates all canonical file types, templates, and reference examples for ONEX/OmniBase. It is the authoritative source for standards review, onboarding, and CI enforcement. All new file types/templates must be added here and kept up to date.

## How to Use
- Use this index during standards review, onboarding, and when creating new files.
- Each entry links to the canonical template, a real example (if available), the schema (if applicable), and the reference documentation.
- All files listed here must conform to [docs/standards.md](../standards.md) and all Cursor rules.

| File Type         | Description                                      | Canonical Template                                      | Real Example                                         | Schema/Model                                         | Reference Doc                                      |
|------------------|--------------------------------------------------|---------------------------------------------------------|------------------------------------------------------|------------------------------------------------------|----------------------------------------------------|
| Node Metadata    | ONEX node metadata block (`node.onex.yaml`)      | [node_metadata.yaml.tmpl](../../src/omnibase/templates/node_metadata.yaml.tmpl) | [onex_node.yaml](../../src/omnibase/schemas/onex_node.yaml) | [onex_node.yaml](../../src/omnibase/schemas/onex_node.yaml) | [node_contracts.md](../nodes/node_contracts.md)    |
| Directory Tree   | Directory structure file (`.tree`, `.tree.json`) | [tree_format.yaml](../../src/omnibase/schemas/tree_format.yaml) | [valid_basic.tree](../../tests/validate/directory_tree/test_case/valid/valid_basic.tree) | [tree_format.yaml](../../src/omnibase/schemas/tree_format.yaml) | [registry.md](../registry.md)                      |
| State Contract   | Node state contract schema                       | [state_contract.yaml](../../src/omnibase/schemas/state_contract.yaml) | [valid_state_contract.yaml](../../tests/schema/testdata/valid_state_contract.yaml) | [state_contract.yaml](../../src/omnibase/schemas/state_contract.yaml) | [node_contracts.md](../nodes/node_contracts.md)    |
| Execution Result | Node execution result schema                     | [execution_result.yaml](../../src/omnibase/schemas/execution_result.yaml) | [valid_execution_result.yaml](../../tests/schema/testdata/valid_execution_result.yaml) | [execution_result.yaml](../../src/omnibase/schemas/execution_result.yaml) | [registry.md](../registry.md)                      |
| Test File        | Canonical test file (Python)                     | [test_sample.py.tmpl](../../src/omnibase/templates/test_sample.py.tmpl) | [core_test_registry_cases.py](../../tests/core/core_test_registry_cases.py) | N/A                                                  | [testing.md](../testing.md)                        |
| Protocol File    | Canonical protocol definition (Python)           | [protocol.py.tmpl](../../src/omnibase/templates/protocol.py.tmpl) | [protocol_registry.py](../../src/omnibase/protocol/protocol_registry.py) | N/A                                                  | [protocols.md](../protocols.md)                    |
| CLI Tool         | Canonical CLI tool (Typer-based)                 | [cli_tool.py.tmpl](../../src/omnibase/templates/cli_tool.py.tmpl) | [cli_stamp.py](../../src/omnibase/tools/cli_stamp.py) | N/A                                                  | [cli_interface.md](../cli_interface.md)             |
| Utility Module   | Canonical utility module (Python)                | [utils.py.tmpl](../../src/omnibase/templates/utils.py.tmpl) | N/A                                                 | N/A                                                  | [nodes/templates_scaffolding.md](../nodes/templates_scaffolding.md) |

---

**Maintenance Policy:**
- This document must be updated whenever a new canonical file type or template is introduced.
- All links must be kept current. Broken or outdated links are a standards violation.
- Standards reviewers must reference this document during every review.
- All files stamped with a metadata block (Markdown, Python, YAML, etc.) must have exactly one blank line between the closing delimiter of the metadata block and the first non-whitespace content. This is enforced by the ONEX Metadata Stamper and required for standards compliance.

# Canonical File Types and Protocol Interface Standards

## Protocol Interface Import Pattern: Avoiding Circular Imports

All protocol interfaces that need to reference model types (e.g., NodeMetadataBlock) **must** use the following canonical pattern to avoid circular imports while maintaining strong typing:

- Use `from typing import TYPE_CHECKING` and import the model only inside an `if TYPE_CHECKING:` block.
- Use forward references (string type annotations) for model types in protocol method signatures.
- Always use package-absolute imports (never relative imports).

**Rationale:**
- This pattern prevents runtime circular imports while allowing static type checkers (mypy, Pyright, etc.) to enforce type safety.
- It is compatible with all major Python type checkers and is widely used in large-scale, type-safe Python projects.

**Example:**
```python
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock

class ProtocolCanonicalSerializer(Protocol):
    def canonicalize_metadata_block(self, block: "NodeMetadataBlock", ...) -> str:
        ...
```

**This is the required pattern for all ONEX protocol interfaces.**

## 2025-06 Update: Versioned Node Directories and File Naming

- **Node Versioning:** Each node must reside in a versioned subdirectory (e.g., `v1_0_0/`).
- **Canonical Metadata:** Each version must have exactly one `node.onex.yaml` file as the canonical metadata block.
- **Contract Naming:** The state contract file must be named `contract.yaml` for consistency and CI/tooling compatibility.
- **Adapters:** All adapters (CLI, web, etc.) must be placed in an `adapters/` directory under each version. Adapters must be referenced in `node.onex.yaml` by explicit module/class.
- **Empty Version Stubs:** Loader ignores version directories unless `node.onex.yaml` is present or a `WIP` marker is set.
- **Rationale and Examples:** See [structural_conventions.md](../nodes/structural_conventions.md) for full rationale and canonical examples.

## 2025-06 Update: Registry-Centric, Versioned Artifact Layout

- All nodes, adapters, contracts, runtimes, CLI tools, and packages are versioned in their own subdirectories.
- Each artifact version must include a corresponding metadata file (e.g., node.onex.yaml, cli_adapter.yaml, contract.yaml, etc.).
- The loader and CI enforce this structure using a `.onextree` manifest and registry metadata files.
- See [structural_conventions.md](../nodes/structural_conventions.md) and [registry_architecture.md](../registry_architecture.md) for full rationale and canonical examples.

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

- All references are explicit in metadata and resolved via the registry.
- No symlinks or direct imports—everything is loaded dynamically by the registry.
- Compatibility is managed via semantic version ranges in metadata.
- CLI tools, nodes, adapters, contracts, runtimes, and packages can all evolve independently, with the registry enforcing compatibility and discoverability.

### .onextree Manifest and Loader

- The `.onextree` file is a declarative manifest describing the expected structure of ONEX project directories and artifact packages.
- Loader only recognizes a version if `node.onex.yaml` is present or a `.wip` marker file is set in the version directory.
- Adapters and contracts must be referenced in `node.onex.yaml` with explicit module/class and filename.
