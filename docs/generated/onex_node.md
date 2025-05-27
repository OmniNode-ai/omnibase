<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: onex_node.md
version: 1.0.0
uuid: ed1bba2c-1987-4cc0-b096-f5fbc9bd3e65
author: OmniNode Team
created_at: 2025-05-27T07:27:52.944149
last_modified_at: 2025-05-27T17:26:51.867506
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 8851f429b6705523ab89ce424f59ff044cbf2d5771a33c59d366e51f9b457288
entrypoint: python@onex_node.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.onex_node
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Metadata Schema

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Define the canonical schema for ONEX node metadata  
> **Audience:** Node developers, validators, registry systems  
> **Version:** 1.0.0

---

## Overview

Canonical schema for ONEX node metadata (.onex). All ONEX nodes must conform to this schema. This schema is versioned and will support prerelease/build metadata in future versions. This document defines the complete metadata structure required for ONEX node registration, discovery, and execution.

---

## Schema Fields

| Name | Type | Required | Description | Enum |
|------|------|----------|-------------|------|
| `schema_version` | `string` | Yes | ONEX metadata schema version (semver, e.g., '0.1.0'). Future versions may support prerelease (-beta.1) and build (+build123) metadata. |  |
| `name` | `string` | Yes | Unique node name. |  |
| `version` | `string` | Yes | Node version (semver, e.g., '0.1.0'). Future versions may support prerelease (-rc.1) and build (+build123) tags. |  |
| `uuid` | `string` | Yes | Node UUID (RFC 4122). Must follow standard hyphenation pattern. |  |
| `author` | `string` | Yes | Author or maintainer. |  |
| `created_at` | `string` | Yes | Creation timestamp (ISO 8601). |  |
| `last_modified_at` | `string` | Yes | Last modification timestamp (ISO 8601). |  |
| `description` | `string` | Yes | Human-readable description of the node. |  |
| `state_contract` | `string` | Yes | Canonical URI to the state contract schema (e.g., state_contract://summary_block_schema.json). Must match URI format. |  |
| `lifecycle` | `string` | Yes | Node lifecycle state. | `draft`, `active`, `deprecated`, `archived` |
| `hash` | `string` | Yes | SHA256 hash (64-character hex) of the canonicalized metadata block, excluding this field itself. |  |
| `entrypoint` | `object` | Yes | Entrypoint specification for node execution. |  |
| `runtime_language_hint` | `string` | No | Optional language or interpreter hint (e.g., 'python>=3.10', 'bash', 'node16'). |  |
| `namespace` | `string` | Yes | Node namespace (e.g., 'omninode.tools.<name>'). |  |
| `meta_type` | `string` | Yes | Node type. Must be one of: tool, validator, agent, model, schema, plugin. | `tool`, `validator`, `agent`, `model`, `schema`, `plugin` |
| `tags` | `array` | No | List of tags or categories. (Optional) |  |
| `trust_score_stub` | `object` | No | Stub for trust scoring. (Optional, extensible via x-extensions) |  |
| `x_extensions` | `object` | No | Custom extension fields (optional). |  |
| `protocols_supported` | `array` | No | List of supported protocols (optional). Each must be a canonical URI. |  |
| `base_class` | `array` | No | List of base classes (optional). Each must be a canonical URI. |  |
| `dependencies` | `array` | No | List of dependencies (optional). Each must be a canonical URI. |  |
| `environment` | `array` | No | List of environment requirements (optional). |  |
| `license` | `string` | No | License identifier (optional). |  |
| `signature_block` | `object` | No | Cryptographic signature metadata for integrity and trust. (Optional) |  |

---

## Field Specifications

### Core Identity Fields

#### `uuid`
- Must be a valid RFC 4122 UUID
- Must follow standard hyphenation pattern (8-4-4-4-12)
- Should be generated once and never changed
- Used for unique identification across the ONEX ecosystem

#### `name`
- Must be unique within the namespace
- Should follow naming conventions (lowercase, underscores)
- Used for human-readable identification

#### `version`
- Must follow semantic versioning (semver) format
- Supports prerelease and build metadata in future versions
- Used for version resolution and compatibility checking

### Lifecycle Management

#### `lifecycle`
- **draft**: Under development, not ready for production
- **active**: Production-ready and actively maintained
- **deprecated**: Still functional but discouraged for new use
- **archived**: No longer maintained, kept for historical reference

#### `state_contract`
- URI pointing to the state contract schema
- Defines the expected input/output interface
- Must be resolvable by the ONEX registry

### Execution Configuration

#### `entrypoint`
- Specifies how to execute the node
- Can be a file path, module reference, or execution command
- Must be compatible with the specified runtime

#### `runtime_language_hint`
- Optional hint for execution environment
- Examples: 'python>=3.10', 'bash', 'node16'
- Used by execution engines for environment setup

### Dependency Management

#### `dependencies`
- List of required dependencies with version constraints
- Each dependency must be a canonical URI
- Used for dependency resolution and validation

#### `protocols_supported`
- List of protocols this node implements
- Each protocol must be a canonical URI
- Used for protocol-based discovery and validation

---

## Example Metadata

### Basic Node Example

```yaml
metadata_version: '0.1'
protocol_version: 1.0.0
schema_version: 0.1.0
name: extract_summary_block
version: 1.0.0
uuid: 65dfc205-96f3-4f86-8497-cf6d8a1c4b95
author: foundation
owner: foundation
copyright: 2025 Foundation, All Rights Reserved
created_at: '2025-05-27T10:05:00Z'
last_modified_at: '2025-05-27T10:15:00Z'
description: Parses a metadata block and extracts summary and status fields for display.
state_contract: state_contract://summary_block_schema.json
lifecycle: active
hash: abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
entrypoint: src/omnibase/tools/cli_extract_summary_block.py
namespace: omninode.tools.extract_summary_block
meta_type: tool
runtime_language_hint: python
tags:
  - metadata
  - docs
  - summary
trust_score_stub:
  runs: 12
  failures: 0
  trust_score: 1.0
x_extensions: {}
protocols_supported:
  - validator://core.schema_validator@1.0.0
base_class:
  - validator://core.schema_validator@1.0.0
dependencies:
  - tool://tools.tree_generator@>=0.2.0
environment: []
license: Apache-2.0
```

### Advanced Node with Extensions

```yaml
metadata_version: '0.1'
schema_version: 0.1.0
name: advanced_validator
version: 2.1.0
uuid: 12345678-1234-5678-9abc-123456789012
author: advanced_team
created_at: '2025-05-27T10:00:00Z'
last_modified_at: '2025-05-27T12:00:00Z'
description: Advanced validation node with custom protocols and extensions.
state_contract: state_contract://advanced_validator_schema.json
lifecycle: active
hash: fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321
entrypoint: 
  module: advanced_validator.main
  function: execute
  args: ["--config", "default.yaml"]
namespace: omninode.validators.advanced
meta_type: validator
runtime_language_hint: python>=3.11
tags:
  - validation
  - advanced
  - protocol
protocols_supported:
  - validator://core.advanced_validator@2.0.0
  - protocol://custom.validation@1.5.0
dependencies:
  - tool://core.registry@>=2.0.0
  - validator://base.validator@^1.0.0
environment:
  - PYTHON_PATH=/opt/onex/lib
  - VALIDATION_MODE=strict
license: MIT
signature_block:
  algorithm: RSA-SHA256
  signature: "base64-encoded-signature"
  public_key_id: "key-12345"
x_extensions:
  custom_config:
    validation_rules: strict
    timeout_seconds: 300
  monitoring:
    metrics_enabled: true
    trace_level: debug
```

---

## Validation Rules

### Required Field Validation
- All required fields must be present and non-empty
- UUIDs must be valid RFC 4122 format
- Timestamps must be valid ISO 8601 format
- Versions must follow semantic versioning

### Consistency Validation
- `last_modified_at` must be >= `created_at`
- `lifecycle` must be compatible with `version` (no draft versions in active lifecycle)
- `entrypoint` must be accessible and executable
- All URI references must be valid and resolvable

### Security Validation
- `signature_block` must be valid if present
- Dependencies must be from trusted sources
- No malicious code patterns in entrypoint

---

## Schema Versioning

### Current Version: 1.0.0

### Changelog

#### 1.0.0 (2025-05-27)
- Initial release of canonical node metadata schema
- Support for all core ONEX node types
- Comprehensive dependency and protocol management
- Trust scoring and signature support
- Extensible design with x-extensions

### Deprecation Policy
- All schema deprecations must be documented in this changelog
- Deprecated fields or versions must be marked in the schema and referenced here
- Breaking changes require a major version bump and migration notes
- Backward-compatible changes require a minor version bump
- Patch version increments are for bugfixes or clarifications only

---

## Integration Examples

### CLI Usage

```bash
# Validate node metadata
onex validate --schema node_metadata metadata.yaml

# Generate node template
onex generate node --name my_validator --type validator

# Register node in registry
onex register node metadata.yaml
```

### Programmatic Usage

```python
from omnibase.schemas import NodeMetadataSchema
from omnibase.core.validation import validate_schema

# Load and validate metadata
with open('metadata.yaml', 'r') as f:
    metadata = yaml.safe_load(f)

validation_result = validate_schema(metadata, NodeMetadataSchema)
if validation_result.is_valid:
    print(f"Node {metadata['name']} v{metadata['version']} is valid")
else:
    print(f"Validation errors: {validation_result.errors}")
```

---

## References

- [ONEX Node Specification](../onex_node_spec.md)
- [Registry Architecture](../registry_architecture.md)
- [Metadata Specification](../metadata.md)
- [Lifecycle Policy](../lifecycle_policy.md)

---

**Note:** This schema is the foundation for all ONEX node metadata. All nodes must conform to this schema to be discoverable and executable within the ONEX ecosystem.
