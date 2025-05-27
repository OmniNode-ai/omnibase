<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: metadata.md
version: 1.0.0
uuid: 8cf58a86-2b89-47ec-b68b-97f9a79501da
author: OmniNode Team
created_at: 2025-05-27T05:30:10.683697
last_modified_at: 2025-05-27T17:26:51.827134
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: be9d3e1eef1dcd926a88acc3b594f2c8a960e59c747ed13a25e1ae36d70bda47
entrypoint: python@metadata.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.metadata
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# OmniBase Metadata Specification

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Define the canonical metadata format, field semantics, dependency schema, and validation mechanisms

---

## Overview

Every OmniBase component—validators, tools, test cases, data artifacts—must include a canonical metadata block. Metadata enables registry indexing, dependency resolution, version enforcement, and lineage tracking via UUID-based graphs. This document defines the canonical format, field semantics, dependency schema, lineage/federation, and validation mechanisms.

---

## Canonical Metadata Block & Field Semantics

### Canonical Metadata Block (YAML)

```yaml
# === OmniNode:Metadata ===
metadata_version: "0.1.0"
protocol_version: "1.0.0"
schema_version: "1.1.0"
uuid: "123e4567-e89b-12d3-a456-426614174000"
name: "example_validator"
namespace: "foundation.script.validate"
version: "0.1.0"
author: "OmniNode Team"
owner: "foundation-team"
copyright: "Copyright OmniNode"
created_at: "2025-05-12T12:00:00Z"
last_modified_at: "2025-05-13T10:00:00Z"
description: "A canonical example of a validator metadata block."
state_contract: "state_contract://default"
lifecycle: "active"
hash: "0000000000000000000000000000000000000000000000000000000000000000"
entrypoint:
  type: "python"
  target: "python_validate_example.py"
runtime_language_hint: "python>=3.11"
meta_type: "tool"
tags: ["canary", "pre-commit", "schema-validation"]
capabilities: []
protocols_supported: ["O.N.E. Core v0.1"]
base_class: []
dependencies: []
inputs: []
outputs: []
environment: []
license: "MIT"
signature_block: null
x_extensions: {}
testing: null
os_requirements: []
architectures: []
container_image_reference: null
compliance_profiles: []
data_handling_declaration: null
logging_config: null
source_repository: null
# === /OmniNode:Metadata ===
```

### Field Semantics

| Field                    | Type         | Description                                                      |
|--------------------------|--------------|------------------------------------------------------------------|
| metadata_version         | str          | Metadata schema version (SemVer)                                 |
| protocol_version         | str          | Protocol version (SemVer)                                        |
| schema_version           | str          | Node schema version (SemVer)                                     |
| uuid                     | str (UUID)   | Globally unique identifier (UUIDv4)                              |
| name                     | str          | Human-readable label                                             |
| namespace                | str          | Hierarchical scope (e.g. `foundation.script.validate`)           |
| version                  | str          | Component version (SemVer)                                       |
| author                   | str          | Author of the component                                          |
| owner                    | str          | Owning team or org                                               |
| copyright                | str          | Copyright statement                                              |
| created_at               | str (ISO8601)| RFC 3339 timestamp                                              |
| last_modified_at         | str (ISO8601)| RFC 3339 timestamp                                              |
| description              | str          | Optional freeform description                                    |
| state_contract           | str          | State contract URI                                               |
| lifecycle                | Enum         | One of: active, draft, deprecated, etc.                         |
| hash                     | str          | Canonical content hash (SHA-256, 64 hex chars)                   |
| entrypoint               | object       | Entrypoint block: `{type: str, target: str}`                     |
| runtime_language_hint    | str          | Language/version hint (e.g. `python>=3.11`)                      |
| meta_type                | Enum         | One of: tool, validator, plugin, etc.                            |
| tags                     | list[str]    | Filterable tags                                                  |
| capabilities             | list[str]    | Capabilities provided                                            |
| protocols_supported      | list[str]    | Supported protocol versions                                      |
| base_class               | list[str]    | Base classes (if any)                                            |
| dependencies             | list         | Dependency blocks                                                |
| inputs                   | list         | Input blocks                                                     |
| outputs                  | list         | Output blocks                                                    |
| environment              | list[str]    | Environment requirements                                         |
| license                  | str          | License string                                                   |
| signature_block          | object/null  | Signature block (optional)                                       |
| x_extensions             | dict         | Arbitrary extensions                                             |
| testing                  | object/null  | Testing block (optional)                                         |
| os_requirements          | list[str]    | OS requirements                                                  |
| architectures            | list[str]    | Supported architectures                                          |
| container_image_reference| str/null     | Container image reference (optional)                             |
| compliance_profiles      | list[str]    | Compliance profiles                                              |
| data_handling_declaration| object/null  | Data handling declaration (optional)                             |
| logging_config           | object/null  | Logging config (optional)                                        |
| source_repository        | object/null  | Source repository info (optional)                                |

- **Enums**: `lifecycle`, `meta_type`, and some nested fields are enums. See the canonical model for allowed values.
- **Entrypoint**: Always a structured block, not a string.

### Blank Line Rule After Metadata Block

All stamped files must have exactly one blank line between the closing delimiter of the metadata block and the first non-whitespace content. This is enforced by the ONEX Metadata Stamper and required for standards compliance.

**Canonical Example:**

```markdown
<!-- === /OmniNode:Metadata === -->

# First heading or content starts here
```

---

## Canonical Block Delimiters

All metadata blocks **must** be wrapped in the following comment delimiters (file-type-specific):

- **Python**: `# === OmniNode:Metadata ===` ... `# === /OmniNode:Metadata ===`
- **YAML**: `# === OmniNode:Metadata ===` ... `# === /OmniNode:Metadata ===`
- **JSON/Markdown**: `
