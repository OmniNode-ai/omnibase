# ONEX State Contract Schema

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the schema for ONEX node state contracts  
> **Audience:** Node developers, contract designers, validation systems  
> **Version:** 1.0.0

---

## Overview

Minimal schema for ONEX node state contracts. State contracts define the expected input/output interface and behavioral guarantees for ONEX nodes. This document provides the foundational schema structure that can be extended for specific node types and use cases.

---

## Schema Fields

| Name | Type | Required | Description | Enum |
|------|------|----------|-------------|------|
| `state` | `object` | Yes | State object definition. Extend with canonical fields for specific contracts. |  |
| `schema_version` | `string` | Yes | State contract schema version (semver) |  |
| `contract_type` | `string` | Yes | Type of state contract | `input`, `output`, `bidirectional`, `stateless` |
| `description` | `string` | No | Human-readable description of the contract |  |
| `validation_rules` | `array` | No | List of validation rules for the state |  |

---

## Contract Types

### Input Contract
Defines the expected input state for a node:
- Specifies required input fields and types
- Defines validation rules for input data
- Used for input validation before node execution

### Output Contract
Defines the expected output state from a node:
- Specifies output fields and types
- Defines success/failure conditions
- Used for output validation after node execution

### Bidirectional Contract
Defines both input and output state:
- Combines input and output specifications
- Defines state transformation rules
- Used for comprehensive node interface definition

### Stateless Contract
For nodes that don't maintain state:
- Defines functional interface only
- No persistent state requirements
- Used for pure function nodes

---

## Basic Schema Structure

### Minimal State Contract

```yaml
schema_version: "1.0.0"
contract_type: "stateless"
description: "Basic stateless contract"
state:
  type: "object"
  properties: {}
```

### Input Contract Example

```yaml
schema_version: "1.0.0"
contract_type: "input"
description: "File validation input contract"
state:
  type: "object"
  properties:
    file_path:
      type: "string"
      description: "Path to file for validation"
      required: true
    validation_rules:
      type: "array"
      description: "List of validation rules to apply"
      items:
        type: "string"
      required: false
  required:
    - file_path
validation_rules:
  - "file_path must be a valid file path"
  - "file must exist and be readable"
```

### Output Contract Example

```yaml
schema_version: "1.0.0"
contract_type: "output"
description: "Validation result output contract"
state:
  type: "object"
  properties:
    status:
      type: "string"
      enum: ["success", "failure", "warning"]
      description: "Validation status"
      required: true
    errors:
      type: "array"
      description: "List of validation errors"
      items:
        type: "object"
        properties:
          code:
            type: "string"
          message:
            type: "string"
          line:
            type: "integer"
      required: false
    warnings:
      type: "array"
      description: "List of validation warnings"
      items:
        type: "object"
        properties:
          code:
            type: "string"
          message:
            type: "string"
          line:
            type: "integer"
      required: false
  required:
    - status
```

---

## Advanced Contract Features

### Bidirectional Contract

```yaml
schema_version: "1.0.0"
contract_type: "bidirectional"
description: "File processor with input and output state"
state:
  input:
    type: "object"
    properties:
      source_file:
        type: "string"
        description: "Source file path"
        required: true
      processing_options:
        type: "object"
        properties:
          format:
            type: "string"
            enum: ["json", "yaml", "xml"]
          validate:
            type: "boolean"
            default: true
        required: false
    required:
      - source_file
  output:
    type: "object"
    properties:
      processed_file:
        type: "string"
        description: "Output file path"
        required: true
      processing_summary:
        type: "object"
        properties:
          lines_processed:
            type: "integer"
          errors_found:
            type: "integer"
          warnings_found:
            type: "integer"
        required: true
      status:
        type: "string"
        enum: ["success", "partial", "failure"]
        required: true
    required:
      - processed_file
      - processing_summary
      - status
validation_rules:
  - "source_file must exist and be readable"
  - "output directory must be writable"
  - "processing_options.format must be supported"
```

---

## Validation Rules

### Rule Types

#### Field Validation
- **Type checking**: Ensure fields match expected types
- **Required fields**: Validate presence of mandatory fields
- **Format validation**: Check string formats, patterns, etc.
- **Range validation**: Validate numeric ranges and constraints

#### Business Logic Validation
- **Cross-field validation**: Rules involving multiple fields
- **Conditional validation**: Rules that apply under certain conditions
- **Custom validation**: Domain-specific validation logic

#### Security Validation
- **Input sanitization**: Prevent injection attacks
- **Path validation**: Ensure safe file system access
- **Permission checks**: Validate access rights

### Rule Definition Format

```yaml
validation_rules:
  - name: "file_exists"
    description: "Validate that the specified file exists"
    type: "field_validation"
    field: "file_path"
    rule: "file_exists"
  - name: "valid_format"
    description: "Ensure format is supported"
    type: "business_logic"
    condition: "processing_options.format is present"
    rule: "format in ['json', 'yaml', 'xml']"
  - name: "safe_path"
    description: "Ensure file path is safe"
    type: "security_validation"
    field: "file_path"
    rule: "no_path_traversal"
```

---

## Schema Extensions

### Custom Properties

State contracts can be extended with custom properties for specific use cases:

```yaml
schema_version: "1.0.0"
contract_type: "bidirectional"
description: "Extended contract with custom properties"
x_extensions:
  performance_requirements:
    max_execution_time_ms: 5000
    max_memory_mb: 512
  monitoring:
    metrics_enabled: true
    trace_level: "info"
  security:
    requires_capability: "file.read"
    sandbox_mode: true
state:
  # ... state definition
```

### Protocol Integration

Contracts can reference ONEX protocols:

```yaml
schema_version: "1.0.0"
contract_type: "input"
description: "Contract implementing validation protocol"
protocols:
  - "protocol://validation.core@1.0.0"
  - "protocol://error_handling.standard@1.0.0"
state:
  # ... state definition following protocol requirements
```

---

## Schema Versioning

### Current Version: 1.0.0

### Changelog

#### 1.0.0 (2025-01-27)
- Initial release of state contract schema
- Support for input, output, bidirectional, and stateless contracts
- Comprehensive validation rule framework
- Extension support for custom properties
- Protocol integration capabilities

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
# Validate state contract
onex validate --schema state_contract contract.yaml

# Generate contract template
onex generate contract --type bidirectional --name file_processor

# Test contract compliance
onex test contract --contract contract.yaml --node my_node
```

### Programmatic Usage

```python
from omnibase.schemas import StateContractSchema
from omnibase.core.validation import validate_contract

# Load and validate contract
with open('contract.yaml', 'r') as f:
    contract = yaml.safe_load(f)

validation_result = validate_contract(contract, StateContractSchema)
if validation_result.is_valid:
    print(f"Contract {contract.get('description', 'unnamed')} is valid")
else:
    print(f"Contract validation errors: {validation_result.errors}")

# Use contract for node validation
from omnibase.core.execution import validate_node_compliance

compliance_result = validate_node_compliance(node, contract)
```

---

## References

- [ONEX Node Specification](../onex_node_spec.md)
- [Core Protocols](../reference-protocols-core.md)
- [Registry Protocols](../reference-protocols-registry.md)
- [Data Models](../reference-data-models.md)
- [Execution Context](../execution_context.md)
- [Error Handling](../error_handling.md)

---

**Note:** State contracts are essential for ensuring reliable node behavior and interface compatibility. All ONEX nodes should define appropriate state contracts to enable proper validation and integration. 