<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: onex_node_spec.md
version: 1.0.0
uuid: cd078337-320b-4776-b365-e3045d7bcd28
author: OmniNode Team
created_at: 2025-05-22T17:18:16.691458
last_modified_at: 2025-05-22T21:19:13.583123
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 8998a01ab67a641079a3d3c24a2b77899eb23af0aed688b7eb9a8a90b57fdcdf
entrypoint: python@onex_node_spec.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.onex_node_spec
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Specification and Linking Model

> **Status:** Canonical Draft  
> **Last Updated:** 2025-05-18  
> **Purpose:** Define the complete `.onex` node schema, linking model, URI format, trust and validation metadata, and the structure and behavior required for ONEX node discoverability, execution, and interconnectivity.  
> **Audience:** Node authors, tool builders, runtime developers, CI engineers

---

## 🧱 What is an ONEX Node?

An ONEX node is a self-contained, declarative, executable unit defined by a `.onex` metadata file. Nodes are:
- Discoverable via `.tree` or registry
- Executable via a defined `entrypoint`
- Validated against schemas and CI rules
- Composable via `dependencies`, `protocols_supported`, and `base_class`
- Rated via a trust score stub
- Interoperable with ONEX runtimes and agents

---

## 📄 Canonical `.onex` Metadata Schema

Each node has a `node.onex.yaml` file located in its top-level directory.

```yaml
# node.onex.yaml (example)
schema_version: "0.1.0"
name: "extract_summary_block"
version: "1.0.0"
uuid: "65dfc205-96f3-4f86-8497-cf6d8a1c4b95"
author: "foundation"
created_at: 2025-05-17T10:05:00Z
last_modified_at: 2025-05-17T10:15:00Z
description: "Parses a metadata block and extracts summary and status fields for display."
state_contract: "state_contract://summary_block_schema.json"
lifecycle: "active"
hash: "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
entrypoint:
  type: python
  target: src/omnibase/tools/cli_extract_summary_block.py
namespace: "omninode.tools.extract_summary_block"
meta_type: "tool"
runtime_language_hint: "python>=3.11"
tags: ["metadata", "docs", "summary"]
trust_score_stub:
  runs: 12
  failures: 0
  trust_score: 1.0
x-extensions: {}
protocols_supported: []
base_class:
  - validator://core.schema_validator@1.0.0
dependencies:
  - tool://tools.tree_generator@>=0.2.0
environment: []
license: "Apache-2.0"
# Optional field not shown: signature_block
```

## Protocol-Driven Stamping and Metadata Validation

- The ONEX Metadata Stamper is implemented as a protocol-driven, fixture-injectable engine. It injects and validates metadata blocks in `.onex` files according to the canonical schema above.
- All stamping and validation logic is defined by Python Protocols, enabling extensibility, testability, and context-agnostic execution.
- The stamper engine ensures that all required fields, formats, and schema constraints are enforced for every node.
- All dependencies (file I/O, ignore pattern sources, etc.) are injected via constructor or fixture, never hardcoded.
- The protocol-driven design enables registry-driven, context-agnostic validation and stamping in CI, pre-commit, and developer workflows.
- See [docs/protocols.md](../protocols.md), [docs/tools/stamper.md](../tools/stamper.md), and [docs/testing.md](../testing.md) for details on protocol-driven stamping and validation.

---

## 🔗 Canonical Linking Fields

### M1 Fields (Current)

| Field             | Type     | Description                                            |
|------------------|----------|--------------------------------------------------------|
| `dependencies`    | list     | Other nodes this node requires at runtime             |
| `base_class`      | list     | Interface or abstract class this node adheres to      |
| `protocols_supported` | list | Protocols or standards this node conforms to          |

These fields **must use a standardized URI format** (see below).

---

## 🌐 URI Format for Linking Fields

### Canonical Format

```
<type>://<namespace>@<version_spec>
```

- `<type>`: `tool`, `validator`, `agent`, `model`, `schema`, `plugin`
- `<namespace>`: Dot-delimited identifier (e.g. `core.schema_validator`)
- `<version_spec>`: Semver or constraint (e.g. `1.0.0`, `>=0.2.0`)

### Examples

```yaml
dependencies:
  - tool://tools.tree_generator@>=0.2.0
  - validator://core.schema_validator@1.0.0
base_class:
  - validator://core.base@^1.0
```

---

## 📦 File Layout (Recommended)

Each node should be self-contained in its own directory, named to match the `name` in the `.onex`.

```
extract_summary_block/
├── node.onex.yaml
├── src/
│   └── omnibase/
│       └── tools/
│           └── cli_extract_summary_block.py
├── tests/
│   └── test_extract_summary_block.py
├── README.md
```

This layout:
- Ensures tooling and CI can discover node boundaries
- Matches `.tree` generation
- Keeps implementation, metadata, and tests co-located

---

## 📜 State Contract (Input/Output Interface)

The `state_contract` field links to a JSON Schema file that defines the node's expected input/output shape. Example:

```json
{
  "title": "SummaryBlockState",
  "type": "object",
  "properties": {
    "summary": { "type": "string" },
    "status": { "type": "string" }
  },
  "required": ["summary", "status"]
}
```

- File is referenced via `state_contract: "state_contract://summary_block_schema.json"`
- Schema lives under `src/omnibase/schema/schemas/`
- Used for both runtime validation and CI enforcement

---

## ✅ Validation Rules

Milestone 1 CI must enforce:

- All `.onex` files must pass schema validation (`onex_node.yaml`)
- `uuid` must be a valid v4 UUID
- `hash` must match file hash of `node.onex.yaml`
- `lifecycle` must be one of: `draft`, `active`, `deprecated`, `archived`
- `.tree` file must reference this node correctly
- `entrypoint.target` must exist and be executable

Optional (Stretch):
- Signature block validation
- Trust score consistency across executions
- URI parsing and dereferencing for dependency validation

---

## 🔐 Trust and Signature Fields

Optional, planned for M3/M4:

- `trust_score_stub` records execution history
- `signature_block` enables cryptographic verification of the node metadata

---

## 🔧 Templates and Node Scaffolding

ONEX will support generation of nodes via reusable templates:

- Templates reside in `src/omnibase/templates/`
- Scaffold nodes (coming in Milestone 2) will generate compliant `.onex`, source, and test files

---

## 📁 .tree Discovery Format

Each project or container should have a top-level `.tree` file that enumerates valid nodes. Example:

```yaml
nodes:
  - name: extract_summary_block
    path: extract_summary_block/node.onex.yaml
  - name: validate_tree_file
    path: tree_validator/node.onex.yaml
```

---

## 📚 Cross-References

- [onex_node.yaml](../schema/schemas/onex_node.yaml)
- [execution_result.json](../schema/schemas/execution_result.json)
- [state_contract.json](../schema/schemas/state_contract.json)
- [Milestone 1 Checklist](../milestones/milestone_1_protocol_and_schema.md)
- [ONEX Bootstrap / Milestone 0](../milestones/milestone_0_bootstrap.md)

---

## 🧭 Future Work

| Proposed Field     | Purpose                                                             |
|--------------------|---------------------------------------------------------------------|
| `consumes`         | Declares what formats or data types this node reads                |
| `produces`         | Declares what formats or data types this node emits                |
| `compatible_with`  | Links nodes that can be safely chained (based on state_contract)   |
| `fork_of`          | Declares this node as a fork/derivative of another node            |
| `generated_by`     | Links the tool or node that scaffolded/generated this node         |

- These fields are optional in the current schema but may be added as extensions or in a schema upgrade (v0.2+).
- Validation rules and CI enforcement for them will be introduced in Milestone 3 or later.

---

## 🔁 Schema Extension Strategy

- All schemas must include `schema_version`
- Additive fields allowed in minor versions
- Breaking changes require new schema version
- x-prefixed fields (`x-extensions`) are always ignored by validators and can be used for node-local metadata

---

## Future Enhancements

The following enhancements are proposed for future versions of the ONEX Node Specification. Each item includes a summary, rationale, and suggested milestone for implementation. This section is non-normative and subject to change as the project evolves.

| # | Enhancement Title                | One-line Summary                        | Suggested Milestone |
|---|----------------------------------|-----------------------------------------|---------------------|
| 1 | Node Schema Versioning           | Add explicit version fields and policies | M2                  |
| 2 | Trust/Signature Metadata         | Support for cryptographic attestations   | M2/M3               |
| 3 | Node Health/Status               | Standardize health and lifecycle fields  | M3                  |
| 4 | Node Tagging and Discovery       | Add tags and search metadata             | M3                  |
| 5 | Inter-Node Linking               | Model relationships between nodes        | M3                  |
| 6 | Extension Mechanisms             | Support for custom node types/extensions | M3                  |
| 7 | Security and Access Control      | Add access control and security metadata | M3                  |
| 8 | Provenance and Audit Trails      | Track node origin and change history     | M3                  |
| 9 | Multi-Format Serialization       | Support YAML, JSON, TOML, etc.           | M3                  |
|10 | Compatibility Policies           | Define backward/forward compatibility    | M3                  |

### 1. Node Schema Versioning
**Overview:**  
Introduce explicit version fields and schema evolution policies to the ONEX node specification.

**Motivation/Rationale:**  
Enables backward/forward compatibility, clear upgrade paths, and robust validation as the node model evolves.

**Implementation Considerations:**  
- Define `version` and `schema_version` fields in the `.onex` schema.
- Document migration and deprecation policies.
- Update validation logic to enforce version compatibility.

**Suggested Milestone:**  
M2

**Dependencies:**  
- Agreement on versioning policy
- Schema loader updates

**Status:**  
Proposed

---

### 2. Trust/Signature Metadata
**Overview:**  
Support for cryptographic signatures and trust attestations in node metadata.

**Motivation/Rationale:**  
Enables verification of node authenticity, provenance, and trustworthiness.

**Implementation Considerations:**  
- Define `signature_block` and trust fields in the schema.
- Integrate with signing tools and CI.
- Document trust score calculation and signature validation.

**Suggested Milestone:**  
M2/M3

**Dependencies:**  
- Cryptographic library selection
- Trust policy definition

**Status:**  
Proposed

---

### 3. Node Health/Status
**Overview:**  
Standardize health and lifecycle fields for nodes.

**Motivation/Rationale:**  
Allows runtime and CI to track node readiness, deprecation, and operational status.

**Implementation Considerations:**  
- Expand `lifecycle` field and add health/status reporting.
- Define allowed values and transitions.
- Integrate with monitoring tools.

**Suggested Milestone:**  
M3

**Dependencies:**  
- Agreement on lifecycle states
- Runtime/CI integration

**Status:**  
Proposed

---

### 4. Node Tagging and Discovery
**Overview:**  
Add tags and search metadata to improve node discoverability.

**Motivation/Rationale:**  
Facilitates search, filtering, and organization of nodes in registries and UIs.

**Implementation Considerations:**  
- Define `tags` field structure and allowed values.
- Update registry and CLI search logic.

**Suggested Milestone:**  
M3

**Dependencies:**  
- Registry/CLI update

**Status:**  
Proposed

---

### 5. Inter-Node Linking
**Overview:**  
Model relationships and dependencies between nodes beyond current fields.

**Motivation/Rationale:**  
Enables richer composition, chaining, and visualization of node graphs.

**Implementation Considerations:**  
- Define new linking fields (e.g., `compatible_with`, `fork_of`).
- Update schema and validation logic.

| Proposed Link Type  | Description                                                                  |
|---------------------|------------------------------------------------------------------------------|
| `consumes`          | Declares what data types, state_contracts, or formats this node reads       |
| `produces`          | Declares what types of outputs this node emits                              |
| `compatible_with`   | Indicates safe chaining compatibility based on shared state_contracts       |
| `fork_of`           | Marks this node as a fork of another node (version, derivation, reuse)      |
| `generated_by`      | Points to the node or tool that scaffolded or generated this node            |

These link types are reserved in the current schema and will be formalized in Milestone 3 or later.

**Suggested Milestone:**  
M3

**Dependencies:**  
- Schema update
- Registry/visualization tools

**Status:**  
Proposed

---

### 6. Extension Mechanisms
**Overview:**  
Support for custom node types and extension points.

**Motivation/Rationale:**  
Allows organizations and users to define new node behaviors without forking the spec.

**Implementation Considerations:**  
- Define extension points and `x-` fields.
- Document extension registration and validation.

**Suggested Milestone:**  
M3

**Dependencies:**  
- Extension policy

**Status:**  
Proposed

---

### 7. Security and Access Control
**Overview:**  
Add access control and security metadata to nodes.

**Motivation/Rationale:**  
Enables secure execution, sharing, and compliance with organizational policies.

**Implementation Considerations:**  
- Define access control fields (e.g., `access`, `permissions`).
- Integrate with runtime and registry.

**Suggested Milestone:**  
M3

**Dependencies:**  
- Security policy
- Runtime/registry update

**Status:**  
Proposed

---

### 8. Provenance and Audit Trails
**Overview:**  
Track node origin, authorship, and change history.

**Motivation/Rationale:**  
Improves traceability, accountability, and compliance.

**Implementation Considerations:**  
- Define provenance fields (e.g., `generated_by`, `fork_of`).
- Integrate with version control and registry.

**Suggested Milestone:**  
M3

**Dependencies:**  
- Version control integration

**Status:**  
Proposed

---

### 9. Multi-Format Serialization
**Overview:**  
Support for multiple serialization formats (YAML, JSON, TOML, etc.).

**Motivation/Rationale:**  
Increases interoperability and user flexibility.

**Implementation Considerations:**  
- Update schema loader to support multiple formats.
- Document supported formats and conversion tools.

**Suggested Milestone:**  
M3

**Dependencies:**  
- Schema loader update

**Status:**  
Proposed

---

### 10. Compatibility Policies
**Overview:**  
Define backward and forward compatibility policies for node schemas.

**Motivation/Rationale:**  
Ensures smooth upgrades and long-term stability of the node ecosystem.

**Implementation Considerations:**  
- Document compatibility guarantees and migration paths.
- Update validation and CI enforcement.

**Suggested Milestone:**  
M3

**Dependencies:**  
- Policy agreement
- CI update

**Status:**  
Proposed

---

> **This document is required reading for any contributor building ONEX-compliant nodes, scaffolding tools, CI validators, or runtime execution logic.**
