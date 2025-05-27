<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: execution_result.md
version: 1.0.0
uuid: 2c52155d-16ab-438c-8e02-9f3f96fcbbdb
author: OmniNode Team
created_at: 2025-05-27T07:26:57.648444
last_modified_at: 2025-05-27T17:26:51.803953
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 6775ca502291423495b4b974aa8a064d4b67324d0c7a4eea3157adfb956e0373
entrypoint: python@execution_result.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.execution_result
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Execution Result Schema

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the schema for ONEX node execution results  
> **Audience:** Developers, CI/CD engineers, automation systems  
> **Version:** 1.0.0

---

## Overview

Canonical schema for ONEX node execution results. Used for CI, batch, and runtime reporting. This schema provides a standardized format for capturing the results of node execution operations, enabling consistent reporting and analysis across the ONEX ecosystem.

---

## Schema Fields

| Name | Type | Required | Description | Enum |
|------|------|----------|-------------|------|
| `batch_id` | `string` | Yes | Unique batch identifier |  |
| `status` | `string` | Yes | Batch execution status | `success`, `partial`, `failure` |
| `results` | `array` | Yes | List of node execution results |  |
| `trust_delta` | `number` | No | Trust score delta (optional) |  |
| `started_at` | `string` | Yes | Batch start timestamp (ISO 8601) |  |
| `completed_at` | `string` | Yes | Batch completion timestamp (ISO 8601) |  |

### Result Item Schema

Each item in the `results` array contains:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `node_id` | `string` | Yes | Unique node identifier |
| `success` | `boolean` | Yes | Whether the node execution succeeded |
| `execution_time_ms` | `number` | Yes | Execution time in milliseconds |
| `status` | `string` | Yes | Detailed execution status |
| `errors` | `array` | No | List of error messages (if any) |
| `warnings` | `array` | No | List of warning messages (if any) |
| `metadata` | `object` | No | Additional execution metadata |

---

## Example Usage

### Successful Batch Execution

```yaml
batch_id: validator_patch_v3
status: success
results:
  - node_id: validator.check.format
    success: true
    execution_time_ms: 101
    status: success
  - node_id: validator.check.syntax
    success: true
    execution_time_ms: 87
    status: success
trust_delta: 0.05
started_at: "2025-01-27T08:01:12+00:00"
completed_at: "2025-01-27T08:01:23+00:00"
```

### Partial Failure Batch

```yaml
batch_id: validator_patch_v3
status: partial
results:
  - node_id: validator.check.format
    success: true
    execution_time_ms: 101
    status: success
  - node_id: validator.check.deprecated
    success: false
    status: failure
    execution_time_ms: 45
    errors:
      - "Unexpected global import"
      - "Deprecated function usage detected"
    warnings:
      - "Consider using newer API"
trust_delta: -0.02
started_at: "2025-01-27T08:01:12+00:00"
completed_at: "2025-01-27T08:01:23+00:00"
```

### JSON Format Example

```json
{
  "batch_id": "validator_patch_v3",
  "status": "success",
  "results": [
    {
      "node_id": "validator.check.format",
      "success": true,
      "execution_time_ms": 101,
      "status": "success"
    },
    {
      "node_id": "validator.check.syntax",
      "success": true,
      "execution_time_ms": 87,
      "status": "success"
    }
  ],
  "trust_delta": 0.05,
  "started_at": "2025-01-27T08:01:12+00:00",
  "completed_at": "2025-01-27T08:01:23+00:00"
}
```

---

## Status Values

### Batch Status
- **success**: All nodes executed successfully
- **partial**: Some nodes succeeded, some failed
- **failure**: All nodes failed or batch could not complete

### Node Status
- **success**: Node executed successfully
- **failure**: Node execution failed
- **timeout**: Node execution timed out
- **skipped**: Node execution was skipped
- **cancelled**: Node execution was cancelled

---

## Trust Score Integration

The `trust_delta` field represents the change in trust score for the batch execution:

- **Positive values**: Successful executions that increase trust
- **Negative values**: Failures or issues that decrease trust
- **Zero**: Neutral impact on trust score
- **Null/omitted**: Trust scoring not applicable

Trust scores are calculated based on:
- Execution success rate
- Error frequency and severity
- Performance metrics
- Historical reliability

---

## Validation Rules

### Required Fields
- `batch_id` must be a non-empty string
- `status` must be one of the defined enum values
- `results` must be a non-empty array
- `started_at` and `completed_at` must be valid ISO 8601 timestamps

### Consistency Rules
- `completed_at` must be after `started_at`
- `status` must be consistent with `results` array
- If any result has `success: false`, batch status cannot be `success`
- If all results have `success: false`, batch status should be `failure`

### Performance Constraints
- `execution_time_ms` must be non-negative
- Batch duration should equal sum of individual execution times plus overhead

---

## Schema Versioning

### Current Version: 1.0.0

### Changelog

#### 1.0.0 (2025-01-27)
- Initial release of execution result schema
- Support for batch execution reporting
- Trust score integration
- Dual-format (YAML/JSON) support
- Comprehensive validation rules

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
# Generate execution result
onex run batch_validator --output-format yaml > result.yaml

# Validate result schema
onex validate --schema execution_result result.yaml

# Parse and analyze results
onex analyze execution-result result.yaml
```

### Programmatic Usage

```python
from omnibase.schemas import ExecutionResultSchema
from omnibase.core.validation import validate_schema

# Load and validate result
with open('result.yaml', 'r') as f:
    result_data = yaml.safe_load(f)

validation_result = validate_schema(result_data, ExecutionResultSchema)
if validation_result.is_valid:
    print(f"Batch {result_data['batch_id']} completed with status: {result_data['status']}")
else:
    print(f"Invalid result schema: {validation_result.errors}")
```

---

## References

- [ONEX Node Specification](../onex_node_spec.md)
- [Error Handling](../error_handling.md)
- [Registry Architecture](../registry_architecture.md)
- [Monitoring Specification](../monitoring.md)

---

**Note:** This schema is designed to provide comprehensive execution reporting while maintaining compatibility with existing ONEX tooling and CI/CD systems.
