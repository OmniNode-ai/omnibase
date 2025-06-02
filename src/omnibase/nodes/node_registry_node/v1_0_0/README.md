<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: README.md
version: 1.0.0
uuid: 0a18f676-b84a-4b2b-9d03-2fc297904673
author: OmniNode Team
created_at: '2025-05-28T12:40:27.515911'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://README
namespace: markdown://README
meta_type: tool

<!-- === /OmniNode:Metadata === -->
# Node Registry Node

> Event-driven ONEX node registry for dynamic node discovery and query.

## Overview

The Node Registry Node maintains a live, event-driven registry of all ONEX nodes in the ecosystem. It subscribes to `NODE_ANNOUNCE` events, tracks node metadata and status, and exposes a protocol for querying the registry or individual node info.

## Usage

### CLI Usage

```bash
python -m omnibase.nodes.node_registry_node.v1_0_0.node get_active_nodes
python -m omnibase.nodes.node_registry_node.v1_0_0.node get_node --node-id "<node_id>"
```

### Programmatic Usage

```python
from omnibase.nodes.node_registry_node.v1_0_0.node import run_node_registry_node
from omnibase.nodes.node_registry_node.v1_0_0.models.state import NodeRegistryInputState

input_state = NodeRegistryInputState(
    version="1.0.0",
    action="get_active_nodes"
)
result = run_node_registry_node(input_state)
print(result.model_dump_json(indent=2))
```

## Input State

| Field     | Type   | Required | Description                                 |
|-----------|--------|----------|---------------------------------------------|
| version   | str    | Yes      | Schema version for input state              |
| action    | str    | Yes      | Action to perform: 'get_active_nodes', 'get_node' |
| node_id   | str    | No       | Node ID for node-specific queries           |

## Output State

| Field         | Type   | Description                                   |
|---------------|--------|-----------------------------------------------|
| version       | str    | Schema version (matches input)                |
| status        | str    | Execution status ('success', 'failure', 'warning') |
| message       | str    | Human-readable result message                 |
| registry_json | str    | JSON-serialized registry state or node info   |

## Events

This node emits the following ONEX events:

- `NODE_ANNOUNCE_ACCEPTED`: When a node announce is accepted
- `NODE_ANNOUNCE_REJECTED`: When a node announce is rejected
- `NODE_START`, `NODE_SUCCESS`, `NODE_FAILURE`: Standard node lifecycle events

## Development

### File Structure

```
node_registry_node/v1_0_0/
├── node.onex.yaml          # Node metadata
├── contract.yaml           # State contract
├── node.py                 # Main node implementation
├── models/
│   └── state.py           # State models
├── node_tests/            # Node tests
└── README.md              # This file
```

### Testing

```bash
pytest src/omnibase/nodes/node_registry_node/v1_0_0/node_tests/
```

## Customization Instructions

To extend or adapt the node registry:
1. Update the state models in `models/state.py` for new fields or actions.
2. Update the contract and metadata as needed.
3. Add new protocol actions or event handlers in `node.py`.
4. Expand tests in `node_tests/` to cover new scenarios.

## License

Apache-2.0
