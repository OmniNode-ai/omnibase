<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: canonical_file_types.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 76c2e59e-304c-4c22-88f7-dcc06b905435 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.162207 -->
<!-- last_modified_at: 2025-05-21T16:42:46.103565 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 961fe1b8a502dee0f707cce7321e5e3312a351c5b9d5af01d3850e1a0b418a5f -->
<!-- entrypoint: {'type': 'python', 'target': 'canonical_file_types.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.canonical_file_types -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: canonical_file_types.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 5f0b0fdc-2b6c-4877-a08c-2cff97c07348 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.664801 -->
<!-- last_modified_at: 2025-05-21T16:39:56.651557 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 44eee9fc164cedb4374e34e7487757edccdbc5b495d4fd47fa840f5d6dcdcd76 -->
<!-- entrypoint: {'type': 'python', 'target': 'canonical_file_types.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.canonical_file_types -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: canonical_file_types.md -->
<!-- version: 1.0.0 -->
<!-- uuid: a8712588-5b2d-4d60-adb1-5f5ff48a2d44 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.664801 -->
<!-- last_modified_at: 2025-05-21T16:24:00.300023 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 78b4713244d17724564ccca7cc7b5e64ecab592e4da66751657cf573dea9ed85 -->
<!-- entrypoint: {'type': 'python', 'target': 'canonical_file_types.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.canonical_file_types -->
<!-- meta_type: tool -->
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
