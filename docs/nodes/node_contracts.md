<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: node_contracts.md
version: 1.0.0
uuid: 3f0f945d-6fe6-4cef-a9bc-8b383efbf0c2
author: OmniNode Team
created_at: 2025-05-27T07:54:38.534280
last_modified_at: 2025-05-27T17:26:51.897197
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: b37e39ed7f00059c0bf5f90f73d162b65dd7dfd623bbd4cb316b5317f5dea06c
entrypoint: python@node_contracts.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.node_contracts
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Architecture: Node Contracts and Metadata Structure

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the complete `.onex` node schema, linking model, URI format, trust and validation metadata, and schema extension strategy  
> **Audience:** Node authors, tool builders, runtime developers, CI engineers  
> **Series:** Node Architecture  

---

## Overview

This document defines the contract-first, metadata-driven node design philosophy and structure for ONEX. It formalizes the complete `.onex` node schema, linking model, URI format, trust and validation metadata, and schema extension strategy. The core principle is that metadata and contracts are the true execution foundation of ONEX.

---

## Canonical `.onex` Metadata Schema

Each node must include a `node.onex.yaml` metadata file located in its top-level directory. This file must conform to the canonical schema defined in the ONEX node schema specification.

### Example Node Metadata

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
# Optional field for advanced nodes: reducer: "path/to/reducer.py"
```

### Memoization Tier (Optional)

Composite nodes may include an optional `memoization_tier` field in their `cache` block to indicate whether caching should be applied only at the outermost node level (`shallow`) or recursively within the subgraph (`deep`).

```yaml
cache:
  enabled: true
  strategy: memoize
  scope: composite
  memoization_tier: deep  # 'deep' enables caching of all internal subgraph node executions
```

When set to `deep`, the runtime stores `trace_hash`-indexed execution traces for subgraph nodes, enabling reuse of identical subgraph computations across different workflows.

---

## Canonical Linking Fields

Nodes are linkable via metadata fields that describe relationships, composition, and origin. These links enable execution graphs, provenance chains, UI visualization, and dependency resolution.

### Core Linking Fields

| Field             | Type     | Description                                            |
|------------------|----------|--------------------------------------------------------|
| `dependencies`    | list     | Other nodes this node requires at runtime             |
| `base_class`      | list     | Interface or abstract class this node adheres to      |
| `protocols_supported` | list | Protocols or standards this node conforms to          |

These fields **must use a standardized URI format** (see below).

---

## URI Format for Linking Fields

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

## State Contract (Input/Output Interface)

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

## Validation Rules

CI must enforce:

- All `.onex` files must pass schema validation
- `uuid` must be a valid v4 UUID
- `hash` must match file hash of `node.onex.yaml`
- `lifecycle` must be one of: `draft`, `active`, `deprecated`, `archived`
- `.tree` file must reference this node correctly
- `entrypoint.target` must exist and be executable

Advanced validation features:
- Signature block validation
- Trust score consistency across executions
- URI parsing and dereferencing for dependency validation

---

## Trust and Signature Fields

Advanced trust and verification features:

- `trust_score_stub` records execution history
- `signature_block` enables cryptographic verification of the node metadata

### Trust Score Structure

```yaml
trust_score_stub:
  runs: 152
  failures: 5
  trust_score: 0.967
  last_updated: 2025-01-27T10:15:00Z
  verification_status: "verified"
```

---

## Schema Extension Strategy

- All schemas must include `schema_version`
- Additive fields allowed in minor versions
- Breaking changes require new schema version
- x-prefixed fields (`x-extensions`) are always ignored by validators and can be used for node-local metadata

### Extension Example

```yaml
x-extensions:
  custom_metrics:
    performance_tier: "high"
    cost_category: "compute_intensive"
  experimental_features:
    async_execution: true
```

---

## Node Contracts and Metadata Architecture

### Key Principles

#### Every Node is Metadata-First

* A node is defined entirely by its metadata:
  * What it does
  * What it needs
  * What it outputs
  * What it affects
* Logic is *secondary* to declared contracts and performance history

#### Contracts Define Executability

```yaml
input_contract:
  metadata.name: str
  config.enabled: bool
output_contract:
  patch.valid: bool
  patch.modified_files: [str]
```

* Contracts are strict, versioned, and testable
* Every node must register a contract to be eligible for execution

#### Contracts Enable Validation, Composition, Replacement

* Contracts enable:
  * Pre-flight checks
  * Composition across nodes
  * Trust score comparisons
  * Dynamic replacement and substitution

---

## Metadata Block Structure

### Complete Metadata Example

```yaml
id: scaffold.validator
version: 0.3.1
hash: sha256:abcd1234
input_contract: {...}
output_contract: {...}
performance:
  total_runs: 152
  success_rate: 96.7%
  avg_latency_ms: 108
  cost_profile_usd: 0.0012
trust:
  verified: true
  signer: omninode.registry
  score: 0.92
cache:
  strategy: memoize
  memoization_tier: deep
```

### Performance Memory

* Nodes self-report execution results
* Registry aggregates and updates over time
* Failed nodes can be replaced, promoted, or demoted automatically

### Trace Hashing

* `trace_hash` = deterministic representation of:
  * Node ID + version
  * Input + config
  * Output + exit state

This enables:
* Cache key creation
* Node equivalence comparisons
* Hash-based override or fallback selection

---

## Node Lifecycles

Nodes are:
* Defined via contract
* Executed under constraint
* Tracked via metadata
* Benchmarked over time
* Swappable via hash or contract match

### Evolutionary Optimization

* Nodes can be tournament-tested or judged
* If a node fails or degrades, the system can:
  * Generate a new variant
  * Compare hash and score
  * Promote the best-fit node

---

## Node Identity and Mutation Policy

| Field            | Mutable? | Notes                         |
| ---------------- | -------- | ----------------------------- |
| `id`             | ❌        | Immutable                     |
| `version`        | ✅        | Version bump required         |
| `trace_hash`     | ✅        | Changes per execution context |
| `trust.score`    | ✅        | Dynamic                       |
| `input_contract` | ✅        | Must be versioned             |
| `performance.*`  | ✅        | Aggregated continuously       |

---

## Prompt + Model Integration

Prompts and models are treated as:
* Input blocks with contracts
* Nodes with execution metadata

### Prompt Block Example

```yaml
id: prompt.codegen.uuid
text: "Write a Python function to validate a UUID."
tags: ["codegen", "validator"]
contracts:
  expected_output: code.text
```

---

## Contract Validation and Testing

### Contract Testing Patterns

```python
def test_node_contract_compliance(node_metadata, test_input):
    """Test that a node adheres to its declared contract."""
    # Validate input against input_contract
    validate_input_contract(test_input, node_metadata.input_contract)
    
    # Execute node
    result = execute_node(node_metadata, test_input)
    
    # Validate output against output_contract
    validate_output_contract(result, node_metadata.output_contract)
    
    # Verify no undeclared side effects
    assert_no_undeclared_side_effects(result)
```

### Contract Evolution

```yaml
# Version 1.0.0
input_contract:
  text: str
  
# Version 1.1.0 (backward compatible)
input_contract:
  text: str
  options: 
    type: object
    default: {}
    
# Version 2.0.0 (breaking change)
input_contract:
  content: str  # renamed from 'text'
  options: object
```

---

## Benefits

* Transparent introspection of any node
* Agent-friendly discovery and routing
* Long-term trust evolution
* Replay and rollback supported
* Contract-driven composition
* Automated validation and testing
* Performance tracking and optimization

---

## References

- [Node Architecture Index](./index.md) - Overview of node architecture series
- [Protocol Definitions](./protocol_definitions.md) - Core protocol interfaces
- [Structural Conventions](./structural_conventions.md) - Directory structure and file layout
- [State Reducers](./state_reducers.md) - State management and reducers
- [Generated Schema Documentation](../generated/onex_node.md) - Complete schema reference
- [Generated State Contract Documentation](../generated/state_contract.md) - State contract schema

---

**Note:** This document defines the canonical structure for contract-first, metadata-driven nodes. Used by all validators, transformers, models, and agent-dispatchable components in ONEX.
