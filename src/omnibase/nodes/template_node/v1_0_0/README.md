<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: README.md
version: 1.0.0
uuid: 5171e84b-00dd-4b58-8087-bfdd8c4cccf2
author: OmniNode Team
created_at: 2025-05-22T05:34:29.784440
last_modified_at: 2025-05-22T21:19:13.641274
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 1f379ab3bc70a2a41428aef5695d5acaf2c3ef2607641905fb3b32fbfa498d3a
entrypoint: python@README.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.README
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# TEMPLATE Node

> **TEMPLATE**: Replace this with your node's name and description.

## Overview

**TEMPLATE**: Replace this section with a description of your node's purpose and functionality.

This is a template node that demonstrates the canonical structure for ONEX nodes. Use this as a starting point for creating new nodes.

## Usage

### CLI Usage

```bash
# TEMPLATE: Update this example to match your node's CLI interface
python -m omnibase.nodes.template_node.v1_0_0.node "your_required_value" --template-optional-field "optional_value"
```

### Programmatic Usage

```python
# TEMPLATE: Update this example to match your node's API
from omnibase.nodes.template_node.v1_0_0.node import run_template_node
from omnibase.nodes.template_node.v1_0_0.models.state import TemplateInputState

input_state = TemplateInputState(
    version="1.0.0",
    template_required_field="your_value",
    template_optional_field="optional_value"
)

result = run_template_node(input_state)
print(result.model_dump_json(indent=2))
```

## Input State

**TEMPLATE**: Update this section to describe your node's input requirements.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | `str` | Yes | Schema version for input state |
| `template_required_field` | `str` | Yes | TEMPLATE: Replace with your field description |
| `template_optional_field` | `str` | No | TEMPLATE: Replace with your field description |

## Output State

**TEMPLATE**: Update this section to describe your node's output structure.

| Field | Type | Description |
|-------|------|-------------|
| `version` | `str` | Schema version (matches input) |
| `status` | `str` | Execution status (`success`, `failure`, `warning`) |
| `message` | `str` | Human-readable result message |
| `template_output_field` | `str` | TEMPLATE: Replace with your field description |

## Events

This node emits the following ONEX events:

- `NODE_START`: When the node begins execution
- `NODE_SUCCESS`: When the node completes successfully
- `NODE_FAILURE`: When the node encounters an error

## Development

### File Structure

```
template_node/v1_0_0/
├── node.onex.yaml          # Node metadata
├── template_node_contract.yaml  # State contract
├── node.py                 # Main node implementation
├── src/
│   └── main.py            # Entrypoint
├── models/
│   └── state.py           # State models
├── node_tests/            # Node tests
└── README.md              # This file
```

### Testing

**TEMPLATE**: Update this section with your node's testing instructions.

```bash
# Run node tests
pytest src/omnibase/nodes/template_node/v1_0_0/node_tests/

# Run specific test
pytest src/omnibase/nodes/template_node/v1_0_0/node_tests/test_template.py
```

## Customization Instructions

To create a new node from this template:

1. **Copy the template directory**:
   ```bash
   cp -r src/omnibase/nodes/template_node src/omnibase/nodes/your_node_name
   ```

2. **Update metadata files**:
   - Replace all `TEMPLATE_*` placeholders in `node.onex.yaml`
   - Update `template_node_contract.yaml` with your state contract
   - Generate new UUIDs for all metadata blocks

3. **Update source code**:
   - Rename classes in `models/state.py` (e.g., `TemplateInputState` → `YourInputState`)
   - Update the main logic in `node.py`
   - Update imports and function names throughout

4. **Update documentation**:
   - Replace all template content in this README
   - Update examples and usage instructions

5. **Update tests**:
   - Rename and update test files in `node_tests/`
   - Update test cases to match your node's functionality

6. **Validate the new node**:
   ```bash
   # Run tests
   pytest src/omnibase/nodes/your_node_name/
   
   # Validate metadata
   python -m omnibase.tools.validator src/omnibase/nodes/your_node_name/
   ```

## License

**TEMPLATE**: Update this section with your license information.

Apache-2.0
