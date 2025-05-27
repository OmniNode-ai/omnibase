# ONEX Node Architecture: Templates and Scaffolding

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the role and structure of canonical templates used for scaffolding new nodes and components  
> **Audience:** Node developers, system architects, contributors  
> **Series:** Node Architecture  

---

## Overview

This document outlines the role and structure of canonical templates used for scaffolding new nodes and components in the ONEX system. Templates provide a consistent starting point for creating new node functions, ensuring they adhere to architectural standards, follow best practices, and can integrate seamlessly into the broader ecosystem.

The standardization emerged from recognizing that nodes as functions need consistent interfaces, boilerplate, and scaffolding to maintain quality and interoperability as the ecosystem grows.

---

## Template Types and Locations

ONEX provides several categories of templates, each serving different creation needs.

### Template Categories

| Category | Purpose | Location |
|----------|---------|----------|
| Node Templates | Base templates for different node types | `src/omnibase/templates/node/` |
| Validator Templates | Templates for validation-focused nodes | `src/omnibase/templates/validator/` |
| Tool Templates | Templates for CLI tools and utilities | `src/omnibase/templates/tool/` |
| Test Templates | Templates for test suites | `src/omnibase/templates/test/` |

### Template Discovery

Templates are organized hierarchically in the templates directory and are automatically discovered by the scaffolding system:

```
src/omnibase/templates/
├── node/                    # Node function templates
│   ├── basic/               # Basic node template
│   ├── agent/               # Agent node template
│   ├── transformer/         # Transformer node template
│   └── validator/           # Validator node template
├── test/                    # Test templates
│   ├── unit/                # Unit test templates
│   └── integration/         # Integration test templates
├── tool/                    # Tool templates
│   └── cli/                 # CLI tool templates
└── protocol/                # Protocol implementation templates
```

---

## Template Components

Each template includes a complete set of files needed to implement a functional node or component.

### Standard Node Template Components

A typical node template includes:

* **node.onex.yaml.tmpl**: Template for the node metadata file
* **\_\_init\_\_.py.tmpl**: Template for the module initialization
* **main.py.tmpl**: Template for the main implementation
* **test_main.py.tmpl**: Template for the test suite
* **README.md.tmpl**: Template for the documentation

### Template Variables

Templates use a set of standard variables that are replaced during scaffolding:

```
{{node_name}}             # The name of the node (e.g., "validator.schema")
{{node_description}}      # A brief description of the node
{{author}}                # The author's name
{{version}}               # The initial version (usually "0.1.0")
{{created_date}}          # The creation date
{{uuid}}                  # A generated UUID for the node
{{entrypoint_path}}       # The path to the entrypoint file
{{namespace}}             # The node's namespace
{{meta_type}}             # The node's meta type (tool, agent, utility)
```

---

## Scaffolding Commands

The `onex` CLI provides commands for scaffolding new nodes and components using templates.

### Basic Scaffolding

```bash
# Create a new node
onex scaffold node validator.schema \
  --description "Validates schema files" \
  --author "ONEX Team" \
  --template basic

# Create a new CLI tool
onex scaffold tool cli_schema_validator \
  --description "CLI tool for schema validation" \
  --author "ONEX Team"

# Create a new test suite
onex scaffold test validator.schema \
  --template unit \
  --description "Unit tests for schema validator"
```

### Template Selection

The scaffolding system selects templates based on the specified node type and template name:

```bash
# Create a transformer node using the transformer template
onex scaffold node transformer.text.summarizer \
  --template transformer \
  --description "Summarizes text using an LLM"

# Create an agent node with reducer support
onex scaffold node agent.conversation.manager \
  --template agent \
  --description "Manages conversation state and context"
```

### Advanced Scaffolding Options

```bash
# Create node with custom metadata
onex scaffold node validator.custom \
  --template validator \
  --description "Custom validation logic" \
  --author "Custom Team" \
  --version "1.0.0" \
  --meta-type "tool" \
  --namespace "custom.validators"

# Create node with dependencies
onex scaffold node processor.data \
  --template basic \
  --dependencies "tool://utils.parser@>=1.0.0,validator://schema.json@^2.0.0"
```

---

## Template Standards

Templates adhere to specific standards to ensure quality and consistency.

### Template File Format

Template files use a `.tmpl` extension and incorporate Jinja2-style variables:

```python
# {{entrypoint_path}}
"""
{{node_description}}

Created by {{author}} on {{created_date}}
"""
from typing import Optional
from pydantic import BaseModel
from omnibase.protocol.protocol_event_bus import ProtocolEventBus

class {{node_name|title}}Input(BaseModel):
    """Input state contract for {{node_name}}."""
    field1: str
    field2: int
    options: Optional[dict] = None

class {{node_name|title}}Output(BaseModel):
    """Output state contract for {{node_name}}."""
    status: str
    result: str
    metadata: Optional[dict] = None

def run_{{node_name|lower|replace('.', '_')}}(
    input_state: {{node_name|title}}Input,
    event_bus: Optional[ProtocolEventBus] = None
) -> {{node_name|title}}Output:
    """
    {{node_description}}

    Args:
        input_state: The input state conforming to the state contract
        event_bus: Optional event bus for emitting execution events

    Returns:
        The output state conforming to the state contract
    """
    # Emit start event
    if event_bus:
        event_bus.emit("{{node_name}}.start", {"input": input_state.model_dump()})
    
    try:
        # TODO: Implement node logic here
        result = "Not implemented yet"
        
        output = {{node_name|title}}Output(
            status="success",
            result=result,
            metadata={
                "node_name": "{{node_name}}",
                "version": "{{version}}"
            }
        )
        
        # Emit success event
        if event_bus:
            event_bus.emit("{{node_name}}.success", {"output": output.model_dump()})
        
        return output
        
    except Exception as e:
        # Emit error event
        if event_bus:
            event_bus.emit("{{node_name}}.error", {"error": str(e)})
        
        return {{node_name|title}}Output(
            status="error",
            result="",
            metadata={"error": str(e)}
        )
```

### Metadata Template

```yaml
# node.onex.yaml.tmpl
schema_version: "0.1.0"
name: "{{node_name}}"
version: "{{version}}"
uuid: "{{uuid}}"
author: "{{author}}"
created_at: "{{created_date}}"
last_modified_at: "{{created_date}}"
description: "{{node_description}}"
state_contract: "state_contract://{{node_name|replace('.', '_')}}_schema.json"
lifecycle: "draft"
entrypoint:
  type: python
  target: "{{entrypoint_path}}"
namespace: "{{namespace}}"
meta_type: "{{meta_type}}"
runtime_language_hint: "python>=3.11"
tags: []
trust_score_stub:
  runs: 0
  failures: 0
  trust_score: 1.0
protocols_supported: []
dependencies: []
environment: []
license: "Apache-2.0"
```

### Documentation Templates

Documentation templates include standard sections:

```markdown
# {{node_name}}

> {{node_description}}  
> Created by {{author}} on {{created_date}}

## Overview

Brief overview of what this node does and its purpose in the ONEX ecosystem.

## Usage

### Basic Usage

```python
from {{namespace}}.{{node_name|replace('.', '_')}} import run_{{node_name|lower|replace('.', '_')}}
from {{namespace}}.models import {{node_name|title}}Input

# Create input state
input_state = {{node_name|title}}Input(
    field1="example",
    field2=42
)

# Execute node
result = run_{{node_name|lower|replace('.', '_')}}(input_state)
print(result.result)
```

### CLI Usage

```bash
# Run via ONEX CLI
poetry run onex run {{node_name}} --args='{"field1": "example", "field2": 42}'
```

## Input Contract

The node accepts input conforming to the `{{node_name|title}}Input` model:

- `field1` (str): Description of field1
- `field2` (int): Description of field2
- `options` (dict, optional): Additional options

## Output Contract

The node returns output conforming to the `{{node_name|title}}Output` model:

- `status` (str): Execution status ("success" or "error")
- `result` (str): The main result of the operation
- `metadata` (dict, optional): Additional metadata about the execution

## Configuration

List any environment variables or configuration options:

- `EXAMPLE_CONFIG`: Description of configuration option

## Testing

```bash
# Run tests
poetry run pytest tests/test_{{node_name|replace('.', '_')}}.py

# Run with coverage
poetry run pytest tests/test_{{node_name|replace('.', '_')}}.py --cov
```

## Dependencies

- List any external dependencies
- Reference any other ONEX nodes this depends on

## License

Apache-2.0
```

### Test Template

```python
# test_{{node_name|replace('.', '_')}}.py.tmpl
"""
Tests for {{node_name}} node.

Created by {{author}} on {{created_date}}
"""
import pytest
from {{namespace}}.{{node_name|replace('.', '_')}} import run_{{node_name|lower|replace('.', '_')}}
from {{namespace}}.models import {{node_name|title}}Input, {{node_name|title}}Output

class Test{{node_name|title|replace('.', '')}}:
    """Test suite for {{node_name}} node."""
    
    def test_basic_functionality(self):
        """Test basic node functionality."""
        input_state = {{node_name|title}}Input(
            field1="test",
            field2=123
        )
        
        result = run_{{node_name|lower|replace('.', '_')}}(input_state)
        
        assert isinstance(result, {{node_name|title}}Output)
        assert result.status == "success"
        assert result.metadata is not None
    
    def test_error_handling(self):
        """Test error handling."""
        # TODO: Implement error case testing
        pass
    
    def test_input_validation(self):
        """Test input validation."""
        # Test invalid input
        with pytest.raises(ValueError):
            {{node_name|title}}Input(field1="", field2="invalid")
    
    def test_output_contract(self):
        """Test output contract compliance."""
        input_state = {{node_name|title}}Input(
            field1="test",
            field2=123
        )
        
        result = run_{{node_name|lower|replace('.', '_')}}(input_state)
        
        # Verify output structure
        assert hasattr(result, 'status')
        assert hasattr(result, 'result')
        assert hasattr(result, 'metadata')
        
        # Verify types
        assert isinstance(result.status, str)
        assert isinstance(result.result, str)
```

---

## Custom Templates

Organizations can create custom templates to extend the standard templates with specific requirements.

### Custom Template Location

Custom templates can be placed in a project-specific templates directory:

```
project_root/
├── .onex/
│   └── templates/         # Project-specific templates
│       └── custom_node/   # Custom node template
│           ├── node.onex.yaml.tmpl
│           ├── main.py.tmpl
│           ├── test_main.py.tmpl
│           └── README.md.tmpl
├── nodes/                 # Node implementations
└── .tree                  # Node discovery file
```

### Custom Template Usage

```bash
# Use a custom template
onex scaffold node custom.node \
  --template-dir ./.onex/templates \
  --template custom_node \
  --description "Custom node implementation"

# List available custom templates
onex scaffold list-templates --template-dir ./.onex/templates
```

### Custom Template Creation

```bash
# Create a new custom template
onex template create my_custom_template \
  --template-dir ./.onex/templates \
  --description "My custom node template"

# This creates the template directory structure
# .onex/templates/my_custom_template/
```

---

## Template Versioning

Templates are versioned to ensure compatibility with different ONEX versions.

### Template Version Compatibility

Each template includes a metadata section indicating its compatibility:

```yaml
# template_metadata.yaml
template_name: "basic_node"
template_version: "1.0.0"
compatible_with:
  onex_min_version: "0.1.0"
  onex_max_version: "1.0.0"
author: "ONEX Team"
description: "Basic node template for general-purpose nodes"
variables:
  - name: "node_name"
    description: "The name of the node"
    required: true
  - name: "node_description"
    description: "A brief description of the node"
    required: true
  - name: "author"
    description: "The author's name"
    default: "ONEX Team"
```

### Template Validation

```bash
# Validate a template
onex template validate basic_node

# Validate all templates
onex template validate --all

# Check template compatibility
onex template check-compatibility basic_node --onex-version 1.0.0
```

---

## Best Practices

### Template Design

1. **Keep templates minimal**: Include only essential boilerplate
2. **Use clear variable names**: Make template variables self-explanatory
3. **Include comprehensive documentation**: Provide clear usage examples
4. **Follow naming conventions**: Adhere to ONEX naming standards
5. **Include proper error handling**: Template generated code should handle errors gracefully

### Template Usage

1. **Choose appropriate templates**: Select templates that match your node's purpose
2. **Customize after scaffolding**: Templates provide starting points, not final implementations
3. **Update metadata**: Ensure all metadata fields are accurate
4. **Add proper tests**: Extend template tests to cover your specific functionality
5. **Document customizations**: Document any deviations from template patterns

### Template Maintenance

1. **Version templates**: Keep templates versioned and compatible
2. **Update regularly**: Keep templates current with ONEX standards
3. **Test templates**: Ensure scaffolded code works correctly
4. **Document changes**: Maintain changelog for template updates
5. **Validate compatibility**: Ensure templates work with target ONEX versions

---

## References

- [Node Architecture Index](./index.md) - Overview of node architecture series
- [Structural Conventions](./structural_conventions.md) - Directory structure and file layout
- [Node Contracts](./node_contracts.md) - Contract-first node design
- [Developer Guide](./developer_guide.md) - Development conventions and best practices
- [Standards](../standards.md) - Naming conventions and code standards
- [CLI Examples](../cli_examples.md) - CLI usage examples and patterns

---

**Note:** This document defines the canonical templates and scaffolding system for creating new ONEX components. Templates provide a consistent starting point for node development, ensure architectural standards are followed, and improve developer productivity. 