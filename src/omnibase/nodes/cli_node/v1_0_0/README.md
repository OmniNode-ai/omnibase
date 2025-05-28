<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: README.md
version: 1.0.0
uuid: df426f5e-4b74-4c42-a486-c7a073b57a87
author: OmniNode Team
created_at: 2025-05-28T12:40:27.245113
last_modified_at: 2025-05-28T17:20:04.976879
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 251de8f9a5d2b9dd4c14cec00d8190946617d037b4939c020ed08c373aede6cd
entrypoint: python@README.md
runtime_language_hint: python>=3.11
namespace: omnibase.stamped.README
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# CLI Node

> **Version:** 1.0.0  
> **Status:** Active  
> **Type:** Orchestrator Node  

## Overview

The CLI Node is an orchestrator node that handles command routing and node management via event-driven architecture. It serves as the central command interface for the ONEX ecosystem, providing a unified way to discover, execute, and manage other nodes.

## Key Features

- **Command Routing**: Routes CLI commands to appropriate target nodes
- **Node Discovery**: Automatically discovers and registers available nodes
- **Event-Driven Architecture**: Uses event bus for node registration and communication
- **Introspection Support**: Provides detailed information about registered nodes
- **Version Management**: Handles node version resolution and execution

## Supported Commands

### `run`
Execute a target node with specified arguments.

```bash
# Basic execution
poetry run onex run stamper_node --args='["file.py"]'

# With introspection
poetry run onex run stamper_node --introspect

# With specific version
poetry run onex run stamper_node --version v1_0_0 --args='["--dry-run", "file.py"]'
```

### `list-nodes`
List all registered nodes in the system.

```bash
poetry run onex list-nodes
```

### `node-info`
Get detailed information about a specific node.

```bash
poetry run onex node-info stamper_node
poetry run onex node-info template_node --version v1_0_0
```

### `version`
Display CLI node version information.

```bash
poetry run onex version
```

### `info`
Display system information and CLI node status.

```bash
poetry run onex info
```

### `handlers`
List all registered file type handlers.

```bash
poetry run onex handlers
```

## Architecture

### Event-Driven Design

The CLI Node uses an event bus architecture for:

- **Node Registration**: Nodes can register themselves via `NODE_REGISTER` events
- **Command Execution**: Publishes `NODE_START`, `NODE_SUCCESS`, and `NODE_FAILURE` events
- **Dynamic Discovery**: Automatically discovers existing nodes using the version resolver

### Node Discovery

The CLI Node discovers nodes through two mechanisms:

1. **Static Discovery**: Uses the existing CLI version resolver to find nodes
2. **Event-Driven Registration**: Accepts node registrations via event bus

### Command Execution

When executing target nodes, the CLI Node:

1. Validates the target node exists and is registered
2. Imports the target node's module
3. Temporarily modifies `sys.argv` to pass arguments
4. Calls the target node's `main()` function
5. Handles different return types (None, int, objects with status)

## State Models

### CLIInputState

```python
{
    "version": "1.0.0",
    "command": "run",
    "target_node": "stamper_node",
    "node_version": "v1_0_0",  # optional
    "args": ["--dry-run", "file.py"],
    "introspect": false,
    "list_versions": false,
    "correlation_id": "optional-id"
}
```

### CLIOutputState

```python
{
    "version": "1.0.0",
    "status": "success",
    "message": "Node stamper_node executed successfully",
    "command": "run",
    "target_node": "stamper_node",
    "result_data": {"return_value": "0"},
    "execution_time_ms": 150.5,
    "correlation_id": "optional-id"
}
```

### NodeRegistrationState

```python
{
    "node_name": "stamper_node",
    "node_version": "v1_0_0",
    "module_path": "omnibase.nodes.stamper_node.v1_0_0.node",
    "capabilities": ["cli_execution", "file_processing"],
    "cli_entrypoint": "main",
    "introspection_available": true,
    "metadata": {}
}
```

## Integration

### Using as a Library

```python
from omnibase.nodes.cli_node.v1_0_0.node import run_cli_node
from omnibase.nodes.cli_node.v1_0_0.models.state import create_cli_input_state

# Create input state
input_state = create_cli_input_state(
    command="run",
    target_node="stamper_node",
    args=["--dry-run", "file.py"]
)

# Execute CLI node
output_state = run_cli_node(input_state)
print(f"Status: {output_state.status}")
print(f"Message: {output_state.message}")
```

### Event Bus Integration

```python
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.nodes.cli_node.v1_0_0.node import CLINode

# Create event bus
event_bus = InMemoryEventBus()

# Create CLI node with custom event bus
cli_node = CLINode(event_bus)

# Register a custom node via event
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
registration_event = OnexEvent(
    event_type=OnexEventTypeEnum.NODE_REGISTER,
    node_id="custom_node",
    metadata={
        "node_name": "custom_node",
        "node_version": "v1_0_0",
        "module_path": "my.custom.node",
        "capabilities": ["custom_processing"]
    }
)
event_bus.publish(registration_event)
```

## Error Handling

The CLI Node handles various error scenarios:

- **Unknown Commands**: Returns error status with helpful message
- **Missing Target Node**: Suggests using `list-nodes` to see available nodes
- **Import Errors**: Provides specific error messages for module import failures
- **Execution Errors**: Captures and reports node execution failures
- **Validation Errors**: Validates input state and provides clear error messages

## Performance

- **Fast Discovery**: Node discovery is cached after initial load
- **Event-Driven**: Minimal overhead for event bus operations
- **Execution Tracking**: Provides execution time metrics for performance monitoring

## Testing

The CLI Node includes comprehensive tests for:

- Command routing and validation
- Node discovery and registration
- Event bus integration
- Error handling scenarios
- State model validation

Run tests with:

```bash
poetry run pytest src/omnibase/nodes/cli_node/v1_0_0/node_tests/
```

## Future Enhancements

- **Plugin System**: Support for dynamically loaded CLI plugins
- **Command Aliases**: Support for custom command aliases
- **Batch Execution**: Execute multiple nodes in sequence or parallel
- **Configuration Management**: Support for CLI configuration files
- **Advanced Filtering**: Filter nodes by capabilities, tags, or other metadata
