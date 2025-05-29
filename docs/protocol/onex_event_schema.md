<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:26.960974'
description: Stamped by ONEX
entrypoint: python://onex_event_schema.md
hash: 3d45dcab0419292a5da43b7bae893701a84e63d18e79fbfec9b441d963d2016c
last_modified_at: '2025-05-29T11:50:15.263996+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: onex_event_schema.md
namespace: omnibase.onex_event_schema
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: 6a33274a-a955-4c16-a949-1e90fbd1de1d
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# ONEX Event Schema Specification

> **Version:** 1.0.0  
> **Status:** Canonical  
> **Last Updated:** 2025-05-25  
> **Purpose:** Define the canonical event schema for all ONEX event emitters

## Overview

The ONEX Event Schema defines the standardized structure for all events emitted within the ONEX ecosystem. This schema ensures consistency across all nodes, telemetry systems, and event consumers, enabling reliable observability, debugging, and system integration.

## Core Event Model

All ONEX events MUST conform to the `OnexEvent` model defined in `src/omnibase/model/model_onex_event.py`.

### Schema Definition

```python
class OnexEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    node_id: Union[str, UUID] = Field(...)
    event_type: OnexEventTypeEnum = Field(...)
    correlation_id: Optional[str] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)
```

### Required Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `event_id` | `UUID` | Unique identifier for this event | Auto-generated if not provided |
| `timestamp` | `datetime` | When the event occurred (UTC) | Auto-generated if not provided |
| `node_id` | `str \| UUID` | Identifier of the emitting node | Must be non-empty |
| `event_type` | `OnexEventTypeEnum` | Type of event | Must be valid enum value |

### Optional Fields

| Field | Type | Description | Usage |
|-------|------|-------------|-------|
| `correlation_id` | `str` | Request/operation tracking ID | For tracing related events |
| `metadata` | `Dict[str, Any]` | Event-specific payload | Context and additional data |

## Event Types

The canonical event types are defined in `OnexEventTypeEnum`:

### Node Lifecycle Events

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `NODE_START` | Node operation begins | Start of node execution |
| `NODE_SUCCESS` | Node operation completed successfully | End of successful execution |
| `NODE_FAILURE` | Node operation failed | When node execution fails |

#### Required Metadata Fields

| Event Type | Metadata Field | Type | Description |
|------------|----------------|------|-------------|
| `NODE_START` | `input_state` | `dict` | Serialized input state (JSON-serializable) |
| `NODE_SUCCESS` | `input_state` | `dict` | Serialized input state (JSON-serializable) |
| `NODE_SUCCESS` | `output_state` | `dict` | Serialized output state (JSON-serializable) |
| `NODE_FAILURE` | `input_state` | `dict` | Serialized input state (JSON-serializable) |
| `NODE_FAILURE` | `error` | `str` | Error message |

#### Optional Metadata Fields

| Event Type | Metadata Field | Type | Description |
|------------|----------------|------|-------------|
| `NODE_START` | `node_version` | `str` | Version of the node implementation |
| `NODE_START` | `operation_type` | `str` | Type of operation being performed |
| `NODE_SUCCESS` | `execution_time_ms` | `float` | Total execution time in milliseconds |
| `NODE_SUCCESS` | `result_summary` | `str` | Human-readable result summary |
| `NODE_FAILURE` | `error_type` | `str` | Exception class name |
| `NODE_FAILURE` | `error_code` | `str` | Standardized error code for automated processing |
| `NODE_FAILURE` | `execution_time_ms` | `float` | Time until failure in milliseconds |
| `NODE_FAILURE` | `stack_trace` | `str` | Full stack trace (optional, for debugging) |

### Telemetry Events

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `TELEMETRY_OPERATION_START` | Function/operation begins | Start of decorated function |
| `TELEMETRY_OPERATION_SUCCESS` | Function/operation succeeds | End of successful function |
| `TELEMETRY_OPERATION_ERROR` | Function/operation fails | When decorated function fails |

#### Required Metadata Fields

| Event Type | Metadata Field | Type | Description |
|------------|----------------|------|-------------|
| `TELEMETRY_OPERATION_START` | `operation` | `str` | High-level operation name |
| `TELEMETRY_OPERATION_START` | `function` | `str` | Specific function name |
| `TELEMETRY_OPERATION_SUCCESS` | `operation` | `str` | High-level operation name |
| `TELEMETRY_OPERATION_SUCCESS` | `function` | `str` | Specific function name |
| `TELEMETRY_OPERATION_SUCCESS` | `execution_time_ms` | `float` | Execution time in milliseconds |
| `TELEMETRY_OPERATION_ERROR` | `operation` | `str` | High-level operation name |
| `TELEMETRY_OPERATION_ERROR` | `function` | `str` | Specific function name |
| `TELEMETRY_OPERATION_ERROR` | `execution_time_ms` | `float` | Time until error in milliseconds |
| `TELEMETRY_OPERATION_ERROR` | `error_type` | `str` | Exception class name |
| `TELEMETRY_OPERATION_ERROR` | `error_message` | `str` | Exception message |

#### Optional Metadata Fields

| Event Type | Metadata Field | Type | Description |
|------------|----------------|------|-------------|
| `TELEMETRY_OPERATION_START` | `args_count` | `int` | Number of positional arguments |
| `TELEMETRY_OPERATION_START` | `kwargs_keys` | `List[str]` | Names of keyword arguments |
| `TELEMETRY_OPERATION_START` | `context` | `dict` | Additional context information |
| `TELEMETRY_OPERATION_SUCCESS` | `result_type` | `str` | Type of returned value |
| `TELEMETRY_OPERATION_SUCCESS` | `success` | `bool` | Always True for success events |
| `TELEMETRY_OPERATION_SUCCESS` | `performance_metrics` | `dict` | Additional performance metrics |
| `TELEMETRY_OPERATION_ERROR` | `success` | `bool` | Always False for error events |
| `TELEMETRY_OPERATION_ERROR` | `error_code` | `str` | Standardized error code for automated processing |
| `TELEMETRY_OPERATION_ERROR` | `recoverable` | `bool` | Whether error is recoverable |

## Metadata Schema Standards

The `metadata` field MUST follow these conventions for consistency:

### Common Metadata Fields

| Field | Type | Description | Used By |
|-------|------|-------------|---------|
| `operation` | `str` | High-level operation name | All telemetry events |
| `function` | `str` | Specific function name | All telemetry events |
| `execution_time_ms` | `float` | Execution time in milliseconds | Success/error events |
| `correlation_id` | `str` | Request tracking ID | All events (also top-level) |

### Node Lifecycle Metadata

#### NODE_START Events
```python
metadata = {
    "input_state": dict,  # Serialized input state
    "node_version": str,  # Node version
    "operation_type": str,  # Type of operation
}
```

#### NODE_SUCCESS Events
```python
metadata = {
    "input_state": dict,   # Serialized input state
    "output_state": dict,  # Serialized output state
    "execution_time_ms": float,  # Total execution time
    "result_summary": str,  # Human-readable result
}
```

#### NODE_FAILURE Events
```python
metadata = {
    "input_state": dict,  # Serialized input state
    "error": str,         # Error message
    "error_type": str,    # Exception class name
    "execution_time_ms": float,  # Time until failure
    "stack_trace": str,   # Optional: full stack trace
}
```

### Telemetry Metadata

#### TELEMETRY_OPERATION_START Events
```python
metadata = {
    "operation": str,      # High-level operation (e.g., "process_file")
    "function": str,       # Function name (e.g., "run_stamper_node")
    "args_count": int,     # Number of positional arguments
    "kwargs_keys": List[str],  # Names of keyword arguments
    "context": dict,       # Optional: additional context
}
```

#### TELEMETRY_OPERATION_SUCCESS Events
```python
metadata = {
    "operation": str,         # High-level operation
    "function": str,          # Function name
    "execution_time_ms": float,  # Execution time
    "result_type": str,       # Type of returned value
    "success": bool,          # Always True for success events
    "performance_metrics": dict,  # Optional: additional metrics
}
```

#### TELEMETRY_OPERATION_ERROR Events
```python
metadata = {
    "operation": str,         # High-level operation
    "function": str,          # Function name
    "execution_time_ms": float,  # Time until error
    "error_type": str,        # Exception class name
    "error_message": str,     # Exception message
    "success": bool,          # Always False for error events
    "recoverable": bool,      # Optional: whether error is recoverable
}
```

## Event Emission Standards

### Serialization Standards

1. **Format**: All `input_state` and `output_state` fields MUST be JSON-serializable Python dictionaries
2. **Size Limits**: State objects should not exceed 100KB when serialized to avoid event bus performance issues
3. **Depth Limits**: Nested objects should not exceed 10 levels of depth
4. **Sensitive Data**: Sensitive fields MUST be redacted before serialization (see Sensitive Field Redaction section)
5. **Large Objects**: For large state objects, consider storing only essential fields and reference external storage

### Correlation ID Propagation

1. **Generation**: If no correlation ID is provided, generate one using `str(uuid.uuid4())`
2. **Propagation**: Pass correlation ID through all function calls and event emissions
3. **Consistency**: Use the same correlation ID for all events in a single operation chain

### Timestamp Handling

1. **UTC Only**: All timestamps MUST be in UTC
2. **Precision**: Use microsecond precision when available
3. **Consistency**: Use `datetime.utcnow()` for current timestamps

### Node ID Standards

1. **Format**: Use descriptive names for node types (e.g., "stamper_node", "validator_node")
2. **Instance Uniqueness**: For multiple instances of the same node type, append instance identifier (e.g., "stamper_node-001", "stamper_node-a8f2g")
3. **Consistency**: Use the same node_id across all events from the same node instance
4. **Uniqueness**: Ensure node_id is unique within the system for the specific running instance
5. **Recommendation**: For production deployments, consider using UUIDs or composite IDs for guaranteed uniqueness

### Correlation ID Standards

1. **Type**: Correlation IDs SHOULD be UUIDs for consistency and uniqueness
2. **Generation**: If no correlation ID is provided, generate one using `str(uuid.uuid4())`
3. **Propagation**: Pass correlation ID through all function calls and event emissions
4. **Consistency**: Use the same correlation ID for all events in a single operation chain
5. **External IDs**: Non-UUID correlation IDs are acceptable when integrating with external systems

## Validation Rules

### Required Validations

1. **Event Type**: Must be a valid `OnexEventTypeEnum` value
2. **Timestamp**: Must be a valid UTC datetime
3. **Node ID**: Must be non-empty string or valid UUID
4. **Metadata**: If present, must be JSON-serializable

### Metadata Validations

1. **Required Fields**: Each event type has required metadata fields (see tables above)
2. **Type Safety**: Metadata values must match expected types
3. **Size Limits**: Metadata should not exceed reasonable size limits (recommend < 1MB)

## Implementation Guidelines

### For Event Emitters

```python
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from datetime import datetime
import uuid

# Correct event emission
event = OnexEvent(
    event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
    node_id="my_node",
    correlation_id=str(uuid.uuid4()),
    metadata={
        "operation": "process_data",
        "function": "process_function",
        "args_count": 2,
    }
)
```

### For Event Consumers

```python
def handle_event(event: OnexEvent) -> None:
    # Validate event structure
    assert event.event_type in OnexEventTypeEnum
    assert event.node_id
    assert event.timestamp
    
    # Process based on event type
    if event.event_type == OnexEventTypeEnum.NODE_START:
        handle_node_start(event)
    elif event.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS:
        handle_telemetry_success(event)
```

## Schema Evolution

### Versioning Strategy

1. **Backward Compatibility**: New fields must be optional
2. **Deprecation**: Mark deprecated fields clearly and provide migration path
3. **Version Tracking**: Include schema version in event metadata when needed

### Extension Points

1. **Custom Metadata**: Nodes may add custom metadata fields with clear prefixes
2. **Event Types**: New event types may be added to the enum
3. **Validation**: Additional validation rules may be added

## Compliance Requirements

### All Event Emitters MUST:

1. Use the canonical `OnexEvent` model
2. Include all required fields for each event type
3. Follow metadata schema standards
4. Propagate correlation IDs correctly
5. Use UTC timestamps
6. Validate events before emission

### Event Consumers SHOULD:

1. Handle unknown event types gracefully
2. Validate event structure on receipt
3. Log schema violations for debugging
4. Support schema evolution patterns

## Testing and Validation

### Schema Validation Tests

Event emitters MUST include tests that validate:

1. Event structure conformance
2. Required metadata presence
3. Correlation ID propagation
4. Timestamp accuracy
5. Event type correctness

### Example Test Pattern

```python
def test_event_schema_compliance():
    event = create_test_event()
    
    # Validate required fields
    assert event.event_id
    assert event.timestamp
    assert event.node_id
    assert event.event_type in OnexEventTypeEnum
    
    # Validate metadata schema
    if event.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START:
        assert "operation" in event.metadata
        assert "function" in event.metadata
```

## References

- **Event Model**: `src/omnibase/model/model_onex_event.py`
- **Telemetry Implementation**: `src/omnibase/runtimes/onex_runtime/v1_0_0/telemetry/telemetry.py`
- **Event Bus**: `src/omnibase/runtimes/onex_runtime/v1_0_0/events/event_bus_in_memory.py`
- **Usage Examples**: `examples/telemetry_demo.py`

---

**Note**: This schema is canonical and MUST be followed by all ONEX components. Any deviations require approval and documentation updates.
