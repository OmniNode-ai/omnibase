<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: templates_scaffolding.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 137307b7-0dfd-4d7e-9e55-c5120ee4e230 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.160990 -->
<!-- last_modified_at: 2025-05-21T16:42:46.074130 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 021c56d3dc142b15f8dafeaf7089b6dc7a4a7a6be9407d468768774fc2906549 -->
<!-- entrypoint: {'type': 'python', 'target': 'templates_scaffolding.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.templates_scaffolding -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: templates_scaffolding.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 1979fc5f-031a-4a0a-a3b7-a51d709363e5 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.436482 -->
<!-- last_modified_at: 2025-05-21T16:39:56.512385 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 8eed4d18a23e0b980bc812742a0451f76d932f837e64daac1f31bd22a9b5780f -->
<!-- entrypoint: {'type': 'python', 'target': 'templates_scaffolding.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.templates_scaffolding -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: templates_scaffolding.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 4e329daf-6a6f-4af4-a1e5-6bc39516ce83 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.663970 -->
<!-- last_modified_at: 2025-05-21T16:24:00.324388 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 174d8712d93f20756da6217cc8abe0a6780a3e4e81a59c38dba090b859d75afc -->
<!-- entrypoint: {'type': 'python', 'target': 'templates_scaffolding.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.templates_scaffolding -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

# ONEX Node Architecture: Templates and Scaffolding

> **Status:** Canonical  
> **Series:** Node Architecture  
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting documentation. 

## 11 - Templates and Scaffolding

### Context & Origin

This document outlines the role and structure of canonical templates used for scaffolding new nodes and components in the ONEX system. Templates provide a consistent starting point for creating new node functions, ensuring they adhere to architectural standards, follow best practices, and can integrate seamlessly into the broader ecosystem. This standardization emerged from recognizing:

> "Nodes as functions need consistent interfaces, boilerplate, and scaffolding to maintain quality and interoperability as the ecosystem grows."

---

### Template Types and Locations

ONEX provides several categories of templates, each serving different creation needs.

#### ✅ Template Categories

| Category | Purpose | Location |
|----------|---------|----------|
| Node Templates | Base templates for different node types | `src/omnibase/templates/node/` |
| Validator Templates | Templates for validation-focused nodes | `src/omnibase/templates/validator/` |
| Tool Templates | Templates for CLI tools and utilities | `src/omnibase/templates/tool/` |
| Test Templates | Templates for test suites | `src/omnibase/templates/test/` |

#### ✅ Template Discovery

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

### Template Components

Each template includes a complete set of files needed to implement a functional node or component.

#### ✅ Standard Node Template Components

A typical node template includes:

* **node.onex.yaml.tmpl**: Template for the node metadata file
* **\_\_init\_\_.py.tmpl**: Template for the module initialization
* **main.py.tmpl**: Template for the main implementation
* **test_main.py.tmpl**: Template for the test suite
* **README.md.tmpl**: Template for the documentation

#### ✅ Template Variables

Templates use a set of standard variables that are replaced during scaffolding:

```
{{node_name}}             # The name of the node (e.g., "validator.schema")
{{node_description}}      # A brief description of the node
{{author}}                # The author's name
{{version}}               # The initial version (usually "0.1.0")
{{created_date}}          # The creation date
{{uuid}}                  # A generated UUID for the node
{{entrypoint_path}}       # The path to the entrypoint file
```

---

### Scaffolding Commands

The `onex` CLI provides commands for scaffolding new nodes and components using templates.

#### ✅ Basic Scaffolding

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
```

#### ✅ Template Selection

The scaffolding system selects templates based on the specified node type and template name:

```bash
# Create a transformer node using the transformer template
onex scaffold node transformer.text.summarizer \
  --template transformer \
  --description "Summarizes text using an LLM"
```

---

### Template Standards

Templates adhere to specific standards to ensure quality and consistency.

#### ✅ Template File Format

Template files use a `.tmpl` extension and incorporate Jinja2-style variables:

```python
# {{entrypoint_path}}
"""
{{node_description}}

Created by {{author}} on {{created_date}}
"""
from pydantic import BaseModel

class InputState(BaseModel):
    field1: str
    field2: int

class OutputState(BaseModel):
    result: str

def process_input(input_state: InputState) -> OutputState:
    """
    Process the input state and return the output state.

    Args:
        input_state: The input state conforming to the state contract

    Returns:
        The output state conforming to the state contract
    """
    return OutputState(result="Not implemented yet")
```

#### ✅ Documentation Templates

Documentation templates include standard sections:

```markdown
# {{node_name}}

> {{node_description}}
> Created by {{author}} on {{created_date}}

## Usage

```python
# Example usage code
```

## Input Contract

Describe the expected input state contract here.

## Output Contract

Describe the output state contract here.

## Configuration

List configuration options if applicable.
```

---

### Custom Templates

Organizations can create custom templates to extend the standard templates with specific requirements.

#### ✅ Custom Template Location

Custom templates can be placed in a project-specific templates directory:

```
project_root/
├── .onex/
│   └── templates/         # Project-specific templates
│       └── custom_node/   # Custom node template
├── nodes/                 # Node implementations
└── .tree                  # Node discovery file
```

#### ✅ Custom Template Usage

```bash
# Use a custom template
onex scaffold node custom.node \
  --template-dir ./.onex/templates \
  --template custom_node
```

---

### Template Versioning

Templates are versioned to ensure compatibility with different ONEX versions.

#### ✅ Template Version Compatibility

Each template includes a metadata section indicating its compatibility:

```yaml
# Template metadata (stored in a separate YAML file)
template_name: "basic_node"
template_version: "1.0.0"
compatible_with:
  onex_min_version: "0.1.0"
  onex_max_version: "1.0.0"
author: "ONEX Team"
description: "Basic node template for general-purpose nodes"
```

---

**Status:** This document defines the canonical templates and scaffolding system for creating new ONEX components. Templates provide a consistent starting point for node development, ensure architectural standards are followed, and improve developer productivity.

---

> **Note:** The URI parser utility is protocol-ready for M1+ and uses canonical Enum and Pydantic model types. See src/omnibase/utils/utils_uri_parser.py, model/model_uri.py, and model/model_enum_metadata.py for details.
