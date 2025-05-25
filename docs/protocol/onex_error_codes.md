<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: onex_error_codes.md
version: 1.0.0
uuid: a357f4b2-d6ef-4ab8-a566-fb50528dc833
author: OmniNode Team
created_at: 2025-05-25T14:11:03.037069
last_modified_at: 2025-05-25T18:17:32.537293
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 1dd344f226a62fc48eb2662f054cdfc4f2b6b356023307582a57a7c0b68d3d8e
entrypoint: python@onex_error_codes.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.onex_error_codes
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Error Code Taxonomy

> **Version:** 1.0.0  
> **Status:** Draft  
> **Last Updated:** 2025-05-25  
> **Purpose:** Define standardized error codes for automated error classification and alerting

## Overview

This document defines a hierarchical error code system for the ONEX ecosystem. Standardized error codes enable automated error classification, alerting, and debugging across all ONEX components.

## Error Code Format

### Structure

Error codes follow the format: `ONEX_<COMPONENT>_<NUMBER>_<DESCRIPTION>`

- **ONEX**: System prefix
- **COMPONENT**: 3-4 letter component identifier
- **NUMBER**: 3-digit sequential number (001-999)
- **DESCRIPTION**: Snake_case description (optional for human readability)

### Examples

```
ONEX_STAMP_001_FILE_NOT_FOUND
ONEX_VALIDATE_002_SCHEMA_MISMATCH
ONEX_REGISTRY_003_DUPLICATE_ENTRY
ONEX_CLI_004_INVALID_ARGUMENT
```

### Short Form

For metadata storage and APIs, use the short form: `ONEX_STAMP_001`

## Component Categories

### Core Components

| Component | Code | Description | Number Range |
|-----------|------|-------------|--------------|
| STAMP | STAMP | File stamping operations | 001-099 |
| VALIDATE | VALID | Validation operations | 100-199 |
| REGISTRY | REG | Registry operations | 200-299 |
| CLI | CLI | Command-line interface | 300-399 |
| RUNTIME | RT | Runtime operations | 400-499 |
| TELEMETRY | TELEM | Telemetry and monitoring | 500-599 |

### Infrastructure Components

| Component | Code | Description | Number Range |
|-----------|------|-------------|--------------|
| EVENT | EVENT | Event system | 600-699 |
| SCHEMA | SCHEMA | Schema operations | 700-799 |
| FIXTURE | FIX | Test fixtures | 800-899 |
| SYSTEM | SYS | System-level errors | 900-999 |

## Error Code Registry

### Stamper Node Errors (001-099)

| Code | Short Code | Description | Severity | Recoverable |
|------|------------|-------------|----------|-------------|
| ONEX_STAMP_001_FILE_NOT_FOUND | ONEX_STAMP_001 | Target file does not exist | ERROR | No |
| ONEX_STAMP_002_FILE_READ_ERROR | ONEX_STAMP_002 | Cannot read target file | ERROR | Retry |
| ONEX_STAMP_003_FILE_WRITE_ERROR | ONEX_STAMP_003 | Cannot write to target file | ERROR | Retry |
| ONEX_STAMP_004_PERMISSION_DENIED | ONEX_STAMP_004 | Insufficient file permissions | ERROR | No |
| ONEX_STAMP_005_INVALID_FILE_TYPE | ONEX_STAMP_005 | Unsupported file type | ERROR | No |
| ONEX_STAMP_006_METADATA_PARSE_ERROR | ONEX_STAMP_006 | Cannot parse existing metadata | ERROR | No |
| ONEX_STAMP_007_METADATA_VALIDATION_ERROR | ONEX_STAMP_007 | Metadata validation failed | ERROR | No |
| ONEX_STAMP_008_HANDLER_NOT_FOUND | ONEX_STAMP_008 | No handler for file type | ERROR | No |
| ONEX_STAMP_009_BACKUP_FAILED | ONEX_STAMP_009 | Cannot create backup file | WARNING | Yes |
| ONEX_STAMP_010_IDEMPOTENCY_CHECK_FAILED | ONEX_STAMP_010 | Idempotency verification failed | ERROR | No |

### Validator Errors (100-199)

| Code | Short Code | Description | Severity | Recoverable |
|------|------------|-------------|----------|-------------|
| ONEX_VALID_100_SCHEMA_NOT_FOUND | ONEX_VALID_100 | Schema file not found | ERROR | No |
| ONEX_VALID_101_SCHEMA_PARSE_ERROR | ONEX_VALID_101 | Cannot parse schema file | ERROR | No |
| ONEX_VALID_102_VALIDATION_FAILED | ONEX_VALID_102 | Data validation against schema failed | ERROR | No |
| ONEX_VALID_103_MISSING_REQUIRED_FIELD | ONEX_VALID_103 | Required field missing | ERROR | No |
| ONEX_VALID_104_INVALID_FIELD_TYPE | ONEX_VALID_104 | Field type mismatch | ERROR | No |
| ONEX_VALID_105_CONSTRAINT_VIOLATION | ONEX_VALID_105 | Field constraint violation | ERROR | No |
| ONEX_VALID_106_ENUM_VALUE_INVALID | ONEX_VALID_106 | Invalid enum value | ERROR | No |
| ONEX_VALID_107_SCHEMA_VERSION_MISMATCH | ONEX_VALID_107 | Schema version incompatible | ERROR | No |

### Registry Errors (200-299)

| Code | Short Code | Description | Severity | Recoverable |
|------|------------|-------------|----------|-------------|
| ONEX_REG_200_ENTRY_NOT_FOUND | ONEX_REG_200 | Registry entry not found | ERROR | No |
| ONEX_REG_201_DUPLICATE_ENTRY | ONEX_REG_201 | Entry already exists | ERROR | No |
| ONEX_REG_202_REGISTRY_CORRUPTED | ONEX_REG_202 | Registry data corrupted | CRITICAL | No |
| ONEX_REG_203_REGISTRATION_FAILED | ONEX_REG_203 | Failed to register entry | ERROR | Retry |
| ONEX_REG_204_DEREGISTRATION_FAILED | ONEX_REG_204 | Failed to remove entry | ERROR | Retry |
| ONEX_REG_205_HANDLER_CONFLICT | ONEX_REG_205 | Handler registration conflict | ERROR | No |

### CLI Errors (300-399)

| Code | Short Code | Description | Severity | Recoverable |
|------|------------|-------------|----------|-------------|
| ONEX_CLI_300_INVALID_ARGUMENT | ONEX_CLI_300 | Invalid command argument | ERROR | No |
| ONEX_CLI_301_MISSING_ARGUMENT | ONEX_CLI_301 | Required argument missing | ERROR | No |
| ONEX_CLI_302_COMMAND_NOT_FOUND | ONEX_CLI_302 | Unknown command | ERROR | No |
| ONEX_CLI_303_CONFIG_ERROR | ONEX_CLI_303 | Configuration error | ERROR | No |
| ONEX_CLI_304_OUTPUT_FORMAT_ERROR | ONEX_CLI_304 | Invalid output format | ERROR | No |

### Runtime Errors (400-499)

| Code | Short Code | Description | Severity | Recoverable |
|------|------------|-------------|----------|-------------|
| ONEX_RT_400_NODE_INITIALIZATION_FAILED | ONEX_RT_400 | Node failed to initialize | CRITICAL | No |
| ONEX_RT_401_STATE_SERIALIZATION_ERROR | ONEX_RT_401 | Cannot serialize state | ERROR | No |
| ONEX_RT_402_STATE_DESERIALIZATION_ERROR | ONEX_RT_402 | Cannot deserialize state | ERROR | No |
| ONEX_RT_403_DEPENDENCY_MISSING | ONEX_RT_403 | Required dependency not found | CRITICAL | No |
| ONEX_RT_404_VERSION_MISMATCH | ONEX_RT_404 | Component version incompatible | ERROR | No |

### Telemetry Errors (500-599)

| Code | Short Code | Description | Severity | Recoverable |
|------|------------|-------------|----------|-------------|
| ONEX_TELEM_500_EVENT_EMISSION_FAILED | ONEX_TELEM_500 | Failed to emit telemetry event | WARNING | Yes |
| ONEX_TELEM_501_HANDLER_REGISTRATION_FAILED | ONEX_TELEM_501 | Cannot register event handler | WARNING | Retry |
| ONEX_TELEM_502_CORRELATION_ID_MISSING | ONEX_TELEM_502 | Correlation ID not found | WARNING | Yes |
| ONEX_TELEM_503_EVENT_VALIDATION_FAILED | ONEX_TELEM_503 | Event schema validation failed | WARNING | Yes |

### Event System Errors (600-699)

| Code | Short Code | Description | Severity | Recoverable |
|------|------------|-------------|----------|-------------|
| ONEX_EVENT_600_BUS_UNAVAILABLE | ONEX_EVENT_600 | Event bus not available | ERROR | Retry |
| ONEX_EVENT_601_SUBSCRIPTION_FAILED | ONEX_EVENT_601 | Cannot subscribe to events | ERROR | Retry |
| ONEX_EVENT_602_EVENT_TOO_LARGE | ONEX_EVENT_602 | Event exceeds size limit | ERROR | No |
| ONEX_EVENT_603_SERIALIZATION_FAILED | ONEX_EVENT_603 | Cannot serialize event | ERROR | No |

### Schema Errors (700-799)

| Code | Short Code | Description | Severity | Recoverable |
|------|------------|-------------|----------|-------------|
| ONEX_SCHEMA_700_DEFINITION_INVALID | ONEX_SCHEMA_700 | Schema definition invalid | ERROR | No |
| ONEX_SCHEMA_701_VERSION_INCOMPATIBLE | ONEX_SCHEMA_701 | Schema version incompatible | ERROR | No |
| ONEX_SCHEMA_702_MIGRATION_FAILED | ONEX_SCHEMA_702 | Schema migration failed | ERROR | No |

### System Errors (900-999)

| Code | Short Code | Description | Severity | Recoverable |
|------|------------|-------------|----------|-------------|
| ONEX_SYS_900_OUT_OF_MEMORY | ONEX_SYS_900 | System out of memory | CRITICAL | No |
| ONEX_SYS_901_DISK_FULL | ONEX_SYS_901 | Disk space exhausted | CRITICAL | No |
| ONEX_SYS_902_NETWORK_UNAVAILABLE | ONEX_SYS_902 | Network connection failed | ERROR | Retry |
| ONEX_SYS_903_TIMEOUT | ONEX_SYS_903 | Operation timed out | ERROR | Retry |
| ONEX_SYS_904_RESOURCE_EXHAUSTED | ONEX_SYS_904 | System resource exhausted | ERROR | Retry |

## Error Severity Levels

| Severity | Description | Action Required |
|----------|-------------|-----------------|
| CRITICAL | System-threatening errors | Immediate intervention |
| ERROR | Operation-blocking errors | Investigation required |
| WARNING | Non-blocking issues | Monitoring recommended |
| INFO | Informational messages | No action required |

## Usage Guidelines

### In Code

```python
from omnibase.core.error_codes import OnexErrorCode

# Raise with error code
raise FileNotFoundError(f"[{OnexErrorCode.STAMP_FILE_NOT_FOUND}] File not found: {file_path}")

# In event metadata
metadata = {
    "error": "File not found",
    "error_type": "FileNotFoundError", 
    "error_code": OnexErrorCode.STAMP_FILE_NOT_FOUND,
    "recoverable": False
}
```

### In Events

```python
error_event = OnexEvent(
    event_type=OnexEventTypeEnum.NODE_FAILURE,
    node_id="stamper_node",
    correlation_id=correlation_id,
    metadata={
        "input_state": input_state.model_dump(),
        "error": "File not found: test.py",
        "error_type": "FileNotFoundError",
        "error_code": "ONEX_STAMP_001",
        "recoverable": False
    }
)
```

### In Logs

```python
logger.error(
    f"[{OnexErrorCode.STAMP_FILE_NOT_FOUND}] Failed to stamp file",
    extra={
        "error_code": "ONEX_STAMP_001",
        "file_path": file_path,
        "correlation_id": correlation_id
    }
)
```

## Error Code Implementation

### Error Code Enum

```python
from enum import Enum

class OnexErrorCode(str, Enum):
    # Stamper errors
    STAMP_FILE_NOT_FOUND = "ONEX_STAMP_001"
    STAMP_FILE_READ_ERROR = "ONEX_STAMP_002"
    STAMP_FILE_WRITE_ERROR = "ONEX_STAMP_003"
    
    # Validator errors
    VALID_SCHEMA_NOT_FOUND = "ONEX_VALID_100"
    VALID_SCHEMA_PARSE_ERROR = "ONEX_VALID_101"
    
    # Registry errors
    REG_ENTRY_NOT_FOUND = "ONEX_REG_200"
    REG_DUPLICATE_ENTRY = "ONEX_REG_201"
    
    # CLI errors
    CLI_INVALID_ARGUMENT = "ONEX_CLI_300"
    CLI_MISSING_ARGUMENT = "ONEX_CLI_301"
```

### Error Code Metadata

```python
@dataclass
class ErrorCodeInfo:
    code: str
    description: str
    severity: str
    recoverable: bool
    component: str

ERROR_CODE_REGISTRY = {
    OnexErrorCode.STAMP_FILE_NOT_FOUND: ErrorCodeInfo(
        code="ONEX_STAMP_001",
        description="Target file does not exist",
        severity="ERROR",
        recoverable=False,
        component="STAMP"
    ),
    # ... more entries
}
```

## Monitoring and Alerting

### Error Code Metrics

- **Error Rate by Code**: Track frequency of each error code
- **Error Trends**: Monitor error code patterns over time
- **Component Health**: Aggregate errors by component
- **Recovery Success**: Track recovery attempts for recoverable errors

### Alerting Rules

```yaml
# Example alerting configuration
alerts:
  - name: "Critical System Errors"
    condition: "error_code starts_with 'ONEX_SYS_9' AND severity = 'CRITICAL'"
    action: "immediate_page"
    
  - name: "High Error Rate"
    condition: "error_rate > 5% over 5 minutes"
    action: "send_notification"
    
  - name: "New Error Code"
    condition: "error_code not_seen_before"
    action: "log_investigation"
```

## Error Code Evolution

### Adding New Error Codes

1. **Reserve Number**: Check registry for next available number in component range
2. **Define Code**: Add to enum and registry with full metadata
3. **Update Documentation**: Add to this document
4. **Add Tests**: Create test cases for new error scenarios
5. **Update Monitoring**: Add alerting rules if needed

### Deprecating Error Codes

1. **Mark Deprecated**: Add deprecation notice to documentation
2. **Maintain Support**: Keep code functional during transition period
3. **Migration Path**: Provide replacement error code if applicable
4. **Remove**: Remove from enum in next major version

## References

- **Event Schema**: [ONEX Event Schema Specification](onex_event_schema.md)
- **Evolution Strategy**: [ONEX Event Schema Evolution](onex_event_schema_evolution.md)
- **Implementation**: `src/omnibase/core/error_codes.py`

---

**Note**: Error codes are permanent identifiers. Once assigned, an error code should never be reused for a different error type.
