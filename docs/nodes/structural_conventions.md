<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: structural_conventions.md
version: 1.0.0
uuid: 8fb940be-2f54-4594-b687-fb3e97152e76
author: OmniNode Team
created_at: 2025-05-27T07:49:32.621584
last_modified_at: 2025-05-27T17:26:51.923906
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: cc966e86fc949003ebcf4b2cf776435c90e8afcea941f918a7d421debe294078
entrypoint: python@structural_conventions.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.structural_conventions
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Architecture: Structural Conventions

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Define canonical directory structure, file layout, discovery mechanisms, and module typing conventions for ONEX nodes  
> **Audience:** Node developers, system architects, contributors  
> **Series:** Node Architecture  

---

## Overview

This document defines the canonical directory structure, file layout, discovery mechanisms, and module typing conventions for ONEX nodes. It builds on the [nodes as functions](./index.md) model to define a consistent, discoverable, and maintainable structure for node implementations.

---

## Protocol Placement Guidance

> **See Also:** For comprehensive guidance on protocol and model placement decisions, import patterns, and governance, see [Core Protocols](../reference-protocols-core.md) and [Registry Protocols](../reference-protocols-registry.md).

ONEX protocols and models must be placed according to their intended scope and usage to ensure clear architectural boundaries and appropriate code reuse.

### Quick Decision Matrix

| Criteria | Shared (`src/omnibase/protocol/`, `src/omnibase/model/`) | Node-Specific (`nodes/{node}/v{version}/protocol/`, `models/`) |
|----------|--------|---------------|
| **Usage Scope** | Used by 2+ nodes, CLI tools, or external plugins | Used only within a single node |
| **Interface Type** | Plugin boundaries, tool contracts, cross-node APIs | Internal node logic, state management |
| **Evolution Rate** | Stable, versioned, backward-compatible changes | Rapid iteration, node-specific requirements |

### Examples

**✅ Shared Components:**
- `ProtocolEventBus` - Event communication across nodes
- `ProtocolFileTypeHandler` - Plugin boundary for file processing  
- `OnexEvent` - Standard event model system-wide
- `OnexResultModel` - Common result format

**✅ Node-Specific Components:**
- `ProtocolOnextreeValidator` - Tree generator validation logic
- `StamperInputState` - Internal stamper node state
- Node-specific constants and error enums

### Import Patterns

**✅ Correct:**
```python
# Shared components - from any location
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.model.model_onex_event import OnexEvent

# Node-specific - only within same node
from .protocol.protocol_onextree_validator import ProtocolOnextreeValidator
from .models.state import StamperInputState
```

**❌ Forbidden:**
```python
# Cross-node imports of node-specific components
from omnibase.nodes.node_tree_generator.protocols.protocol_onextree_validator import ProtocolOnextreeValidator
```

---

## Directory and Module Structure

ONEX nodes follow a standardized directory structure that makes them easily discoverable and ensures proper isolation and dependency management.

### Standard Node Structure

```
node_name/                      # Root directory for the node
├── node.onex.yaml              # Node metadata and contract definition
├── src/                        # Source code for the node implementation
│   ├── __init__.py             # Package initialization
│   ├── main.py                 # Main implementation (often the entrypoint)
│   └── helpers/                # Internal helpers specific to this node
├── tests/                      # Tests for this specific node
│   ├── __init__.py
│   ├── test_main.py            # Tests for the main implementation
│   └── fixtures/               # Test fixtures and helpers
└── README.md                   # Node-specific documentation
```

### Node Discovery via `.tree`

ONEX nodes are discovered through a centralized `.tree` file at the root of a repository or project, which catalogs all available nodes.

```yaml
# Example .tree file
nodes:
  - name: validator.schema
    path: nodes/validator.schema/node.onex.yaml
  - name: transform.summarize
    path: nodes/transform.summarize/node.onex.yaml
  # Additional nodes...
```

This centralized discovery mechanism enables tools, runtimes, and CI systems to find and validate all nodes without traversing the entire directory structure.

---

## File Layouts and Naming

ONEX follows specific conventions for file naming and structure to ensure consistency and predictability.

### File Naming Conventions

| File Type        | Naming Pattern              | Example                       |
|------------------|-----------------------------|------------------------------ |
| Node Metadata    | `node.onex.yaml`            | `node.onex.yaml`              |
| Entrypoint       | Referenced in metadata      | `src/main.py`                 |
| Tests            | `test_*.py`                 | `tests/test_main.py`          |
| Internal Helpers | `*_helper.py`, `*_util.py`  | `src/helpers/parsing_util.py` |

### Core Files

* **node.onex.yaml**: The canonical metadata file that defines the node's interface, dependencies, and execution properties. Contains fields like `state_contract`, `dependencies`, `entrypoint`, etc. as defined in [Node Contracts and Metadata](./node_contracts.md).
* **Entrypoint File**: The main implementation file specified by the `entrypoint.target` field in the metadata. This file contains the core function that implements the node's primary behavior and adheres to the specified `state_contract`.
* **README.md**: Documents the node's purpose, usage, examples, and any special considerations. Should be kept in sync with metadata properties.

---

## Type Hinting and State Contracts

ONEX nodes use explicit type definitions to represent their input and output contracts.

### State Contracts as Types

```python
# Example state contract implementation in Python
from pydantic import BaseModel
from typing import List, Optional

class SummaryInputState(BaseModel):
    """Input state contract for the summarizer node."""
    text: str
    max_length: Optional[int] = 100
    preserve_keywords: List[str] = []

class SummaryOutputState(BaseModel):
    """Output state contract for the summarizer node."""
    summary: str
    original_length: int
    summary_length: int
    preserved_keywords_count: int
```

These types enforce the structure of input and output states, providing both runtime validation and development-time type checking.

Nodes that support reducer-based internal state or `memoization_tier: deep` caching should also ensure their state types and execution outputs are schema-bound. Reducers may implement snapshot-compatible state models using `BaseModel`, while composite nodes should document the types of all subgraph input and output contracts to support trace hashing and planner compatibility.

---

## Module Typing and Categorization

ONEX modules are categorized based on their primary role and behavior to aid in discovery and composition.

### Node Type Categories

| Type          | Purpose                                            | Examples                           |
|---------------|----------------------------------------------------|------------------------------------|
| `tool`        | General-purpose transformation or utility function | `validator`, `parser`, `formatter` |

---

## Canonical Versioned Node Structure

ONEX nodes use a versioned directory structure to support multiple versions, robust adapter management, and extensibility. Each node version is isolated, and all adapters, contracts, and helpers are versioned per node.

```
nodes/
  stamper_node/
    v1_0_0/
      node.py                # Main implementation (entrypoint)
      node.onex.yaml         # Canonical metadata (references entrypoint, adapter, contract)
      contract.yaml          # State contract (normalized name for CI/tooling)
      models/                # State/input/output models
      helpers/               # Node-local helpers
      adapters/              # All adapters (e.g., cli_adapter.py, web_adapter.py)
      tests/                 # Node-local tests
      fixtures/              # Node-local test fixtures
    v2_0_0/                  # (Optional, empty or WIP)
      WIP                    # Loader ignores unless node.onex.yaml or WIP flag present
  another_node/
    v1_0_0/
      ...
```

### Rationale
- **Adapters**: Always versioned and node-local to prevent global conflicts. Place all adapters in `adapters/`.
- **Contracts**: Use `contract.yaml` for consistency and glob-friendly tooling.
- **Metadata**: `node.onex.yaml` is the only canonical metadata file; it references the entrypoint, adapter, and contract.
- **Empty Version Stubs**: Loader ignores empty versions unless a `node.onex.yaml` or `WIP` marker is present.

### Canonical `.onextree` Example

```yaml
type: directory
name: nodes
children:
  - type: directory
    name: stamper_node
    children:
      - type: directory
        name: v1_0_0
        children:
          - type: file
            name: node.py
            metadata: node.onex.yaml
          - type: file
            name: node.onex.yaml
          - type: file
            name: contract.yaml
          - type: directory
            name: models
            children: []
          - type: directory
            name: helpers
            children: []
          - type: directory
            name: adapters
            children:
              - type: file
                name: cli_adapter.py
              - type: file
                name: web_adapter.py
          - type: directory
            name: tests
            children: []
          - type: directory
            name: fixtures
            children: []
```

### Loader Behavior
- Loader only recognizes a version if `node.onex.yaml` is present or a `WIP` marker is set.
- Adapters and contracts must be referenced in `node.onex.yaml` with explicit module/class and filename.
- All metadata, contract, and adapter references are validated at load time.

---

## Registry-Centric, Versioned Artifact Layout

ONEX enforces a fully registry-driven, versioned artifact structure. All nodes, adapters, contracts, runtimes, CLI tools, and packages are versioned in their own subdirectories, with explicit metadata and registry references.

### Canonical Example Directory Layout

```
src/omnibase/
  nodes/
    stamper_node/
      v1_0_0/
        node.py
        node.onex.yaml
        contract.yaml
        adapters/
          cli_adapter.py
        tests/
          test_node.py
          fixtures/
            sample_input.yaml
  runtimes/
    onex_runtime/
      v1_0_0/
        runtime.py
        runtime.yaml
  cli_tools/
    onex/
      v1_0_0/
        cli_main.py
        cli_tool.yaml
  registry/
    registry.yaml
    adapters.yaml
    contracts.yaml
    runtimes.yaml
    packages.yaml
    cli_tools.yaml
```

- All artifacts are versioned in their own subdirectories
- All references are explicit in metadata and resolved via the registry
- No symlinks or direct imports—everything is loaded dynamically by the registry
- Compatibility is managed via semantic version ranges in metadata
- CLI tools, nodes, adapters, contracts, runtimes, and packages can all evolve independently

---

## Handler Plugin/Override System

ONEX provides a flexible handler plugin system that allows nodes to register custom file type handlers or override existing ones.

### Handler Registration API

#### Basic Registration

```python
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry

# Get registry instance
registry = FileTypeHandlerRegistry()

# Register handler for file extension
registry.register_handler(".custom", MyCustomHandler(), source="node-local", priority=10)

# Register named handler
registry.register_handler("my_processor", MyProcessorHandler(), source="node-local")

# Register special filename handler
registry.register_special("config.yaml", MyConfigHandler(), source="node-local")
```

#### Advanced Registration with Override

```python
# Override existing handler with higher priority
registry.register_handler(
    ".py", 
    MyEnhancedPythonHandler(), 
    source="node-local", 
    priority=60,  # Higher than runtime priority (50)
    override=True
)

# Register handler class (will be instantiated automatically)
registry.register_handler(
    ".xml", 
    XMLHandler,  # Class, not instance
    source="node-local",
    author="MyTeam",  # Passed to constructor
    namespace_prefix="mynode.xml"
)
```

#### Node-Local Handler Registration

```python
# Convenience method for bulk registration
node_handlers = {
    ".custom": MyCustomHandler(),
    ".special": MySpecialHandler(),
    "special:.myconfig": MyConfigHandler(),
    "processor": MyProcessorHandler()
}

registry.register_node_local_handlers(node_handlers)
```

### Handler Priority System

The handler registry uses a priority-based conflict resolution system:

- **Core handlers**: Priority 100 (highest)
- **Runtime handlers**: Priority 50 (medium)
- **Node-local handlers**: Priority 10 (low)
- **Plugin handlers**: Priority 0 (lowest)

Higher priority handlers override lower priority ones. Use `override=True` to force replacement regardless of priority.

### Handler Metadata and Introspection

#### Listing Registered Handlers

```python
# Get all registered handlers with metadata
handlers = registry.list_handlers()

for handler_id, metadata in handlers.items():
    print(f"{handler_id}: {metadata['handler_class']} (source: {metadata['source']}, priority: {metadata['priority']})")
```

#### Getting Handler Information

```python
# Get handler by path
handler = registry.get_handler(Path("myfile.py"))

# Get named handler
processor = registry.get_named_handler("my_processor")

# Check what's handled
extensions = registry.handled_extensions()  # {'.py', '.yaml', '.md', ...}
specials = registry.handled_specials()      # {'.onexignore', '.gitignore', ...}
names = registry.handled_names()            # {'my_processor', ...}
```

### Node Implementation Example

#### In Node Entrypoint (`node.py`)

All ONEX nodes support the `handler_registry` parameter for custom file processing:

```python
from pathlib import Path
from typing import Optional
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from .models.input_state import MyNodeInputState
from .models.output_state import MyNodeOutputState
from .helpers.my_custom_handler import MyCustomHandler

def run_my_node(
    input_state: MyNodeInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> MyNodeOutputState:
    """
    Main node entrypoint with custom handler registration.
    
    Args:
        input_state: Node input configuration
        event_bus: Optional event bus for emitting execution events
        handler_registry: Optional FileTypeHandlerRegistry for custom file processing
        
    Example of node-local handler registration:
        registry = FileTypeHandlerRegistry()
        registry.register_handler(".toml", MyTOMLHandler(), source="node-local")
        output = run_my_node(input_state, handler_registry=registry)
    """
    # Register node-local handlers if registry is provided
    if handler_registry:
        handler_registry.register_handler(
            ".myformat", 
            MyCustomHandler(), 
            source="node-local",
            priority=10
        )
    
    # Node implementation...
    return MyNodeOutputState(...)
```

#### Supported Nodes

The following nodes support the `handler_registry` parameter:

- **Stamper Node** (`run_stamper_node`): For custom metadata stamping and file processing
- **Tree Generator Node** (`run_node_tree_generator`): For custom metadata validation and manifest generation
- **Registry Loader Node** (`run_registry_loader_node`): For custom registry file processing and artifact discovery

---

## Protocol Placement Guidelines

### Shared vs Node-Specific Protocols

**Shared protocols** should be placed in `src/omnibase/protocol/` when they:
- Are used by multiple nodes
- Define cross-cutting concerns (events, file handling, etc.)
- Serve as plugin boundaries
- Provide standard contracts across the system

**Node-specific protocols** should remain in `src/omnibase/nodes/<node>/v*/protocol/` when they:
- Are only used within a single node
- Define node-specific validation or processing logic
- Have no reuse potential in other nodes
- Are highly coupled to node implementation details

### Decision Matrix

| Criteria | Shared | Node-Specific |
|----------|--------|---------------|
| Used by 2+ nodes | ✅ | ❌ |
| Cross-cutting concern | ✅ | ❌ |
| Plugin boundary | ✅ | ❌ |
| Standard contract | ✅ | ❌ |
| Node-specific logic | ❌ | ✅ |
| Implementation coupling | ❌ | ✅ |
| No reuse potential | ❌ | ✅ |

---

## Naming Conventions

### File Naming

- **Node directories**: `<node_name>` (lowercase, underscores)
- **Version directories**: `v<major>_<minor>_<patch>`
- **Python files**: `<prefix>_<name>.py` (lowercase, underscores)
- **Test files**: `test_<name>.py`
- **CLI files**: `cli_<node_name>.py`

### Reserved Prefixes

- `core_`: Core system components
- `protocol_`: Protocol definitions
- `model_`: Data models
- `test_`: Test files
- `cli_`: CLI tools and adapters
- `helper_`: Helper utilities

### Class Naming

- **Nodes**: `<NodeName>Node` (PascalCase)
- **Models**: `<ModelName>Model` or `<ModelName>State`
- **Protocols**: `Protocol<InterfaceName>`
- **Handlers**: `<Type>Handler`

---

## Versioning Strategy

### Version Directory Structure

Each node version gets its own directory following semantic versioning:

```
nodes/my_node/
├── v1_0_0/     # Initial release
├── v1_1_0/     # Minor update
├── v2_0_0/     # Major version
└── v2_1_0/     # Latest version
```

### Version Compatibility

- **Major versions**: Breaking changes allowed
- **Minor versions**: Backward compatible additions
- **Patch versions**: Bug fixes only

### Deprecation Process

1. Mark old version as deprecated in metadata
2. Update documentation with migration guide
3. Maintain for 2 major versions minimum
4. Move to `archive/` directory when removed

---

## Testing Conventions

### Test Organization

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test node entrypoint and workflows
- **Protocol tests**: Test protocol compliance
- **Handler tests**: Test custom handler implementations

### Test Naming

```python
class TestMyNode:
    def test_basic_functionality(self):
        """Test basic node operation."""
        pass
    
    def test_error_handling(self):
        """Test error conditions."""
        pass
    
    def test_custom_handlers(self):
        """Test node-local handler registration."""
        pass
```

### Test Data

- Use protocol-driven test cases
- Avoid hardcoded test data
- Use registry-injected fixtures
- Follow canonical testing patterns

---

## Documentation Requirements

### Required Documentation

1. **Node README**: Purpose, usage, examples
2. **API Documentation**: Input/output models, protocols
3. **Handler Documentation**: Custom handlers and their purpose
4. **Migration Guides**: Version upgrade instructions

### Documentation Standards

- Use canonical Markdown format
- Include code examples
- Document all public interfaces
- Provide troubleshooting guides

---

## Compliance and Validation

### CI Validation

All nodes must pass:
- Metadata schema validation
- Structural convention checks
- Test suite execution
- Documentation completeness

### Pre-commit Hooks

- Metadata stamping
- Code formatting
- Linting and type checking
- Test execution

### Manual Review

- Architecture review for new nodes
- Handler placement validation
- Documentation quality check
- Security and performance review

---

## References

- [Node Architecture Index](./index.md) - Overview of node architecture series
- [Node Contracts](./node_contracts.md) - Contract-first node design
- [Protocol Definitions](./protocol_definitions.md) - Core protocol interfaces
- [Core Protocols](../reference-protocols-core.md) - Core protocol definitions and execution
- [Registry Protocols](../reference-protocols-registry.md) - Registry, validation, handler protocols
- [Data Models](../reference-data-models.md) - Data models, composition, testing
- [Testing Guidelines](../testing.md) - Testing standards and patterns
- [Standards](../standards.md) - Naming conventions and code standards

---

**Note:** These structural conventions ensure consistency, discoverability, and maintainability across all ONEX nodes. All node development should follow these patterns to ensure compatibility with the ONEX runtime and tooling.
