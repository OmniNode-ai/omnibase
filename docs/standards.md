<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:53:59.075873'
description: Stamped by ONEX
entrypoint: python://standards.md
hash: 54293bb32d501a4600bf431fba36f7c4c890aa2777b13774b4636603a322ba8c
last_modified_at: '2025-05-29T11:50:15.338535+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: standards.md
namespace: omnibase.standards
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: 47d66794-00af-40f3-a132-ba1e415ed35a
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# OmniBase/ONEX Standards and Conventions

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define and enforce comprehensive standards for all files, directories, code artifacts, and architectural patterns in the OmniBase/ONEX project. All contributors must follow these rules for consistency, maintainability, and discoverability.

---

## Table of Contents

1. [File and Directory Naming](#file-and-directory-naming)
2. [Versioned Architecture](#versioned-architecture)
3. [Reserved Naming Prefixes](#reserved-naming-prefixes)
4. [Protocol and Model Organization](#protocol-and-model-organization)
5. [Node Structure Standards](#node-structure-standards)
6. [CLI Tools and Commands](#cli-tools-and-commands)
7. [Handler Organization](#handler-organization)
8. [Testing Standards](#testing-standards)
9. [Documentation Standards](#documentation-standards)
10. [Code Quality Standards](#code-quality-standards)
11. [Enforcement and Compliance](#enforcement-and-compliance)

---

## File and Directory Naming

### General Principles

- **Use lowercase with underscores** for all Python files and directories
- **Prefix files with their functional scope** to avoid naming conflicts and improve clarity
- **Use semantic versioning** for all versioned components (`v1_0_0/`, `v2_1_0/`)
- **Avoid camelCase or PascalCase** in filenames (except for legacy compatibility)
- **Use hyphen-separated names** for YAML/JSON schema files

### Directory Structure

```
src/omnibase/
├── core/                      # Core system components
├── protocol/                  # Shared protocol definitions
├── model/                     # Shared data models
├── utils/                     # Utility functions and helpers
├── handlers/                  # Shared file type handlers
├── nodes/                     # ONEX nodes (versioned)
├── runtimes/                  # Runtime implementations (versioned)
├── cli_tools/                 # CLI tools and commands (versioned)
├── schemas/                   # JSON/YAML schemas
├── templates/                 # Code and file templates
├── fixtures/                  # Test fixtures and data
├── enums/                     # Shared enumerations
├── mixin/                     # Shared mixins
└── metadata/                  # Metadata utilities
```

### File Naming Patterns

| Component Type | Naming Pattern | Example |
|----------------|----------------|---------|
| Core modules | `core_<name>.py` | `core_registry.py` |
| Protocol definitions | `protocol_<name>.py` | `protocol_event_bus.py` |
| Data models | `model_<name>.py` | `model_onex_event.py` |
| Utilities | `utils_<name>.py` | `utils_uri_parser.py` |
| Handlers | `handler_<name>.py` | `handler_python.py` |
| CLI tools | `cli_<name>.py` | `cli_main.py` |
| Test files | `test_<name>.py` | `test_registry.py` |
| Templates | `template_<name>.<ext>` | `template_node.py` |

---

## Versioned Architecture

### Version Directory Structure

All major components use semantic versioning with underscore-separated directories:

```
component_name/
├── v1_0_0/                    # Version 1.0.0
├── v1_1_0/                    # Version 1.1.0
├── v2_0_0/                    # Version 2.0.0 (breaking changes)
└── v2_1_0/                    # Version 2.1.0 (latest)
```

### Versioned Components

- **Nodes**: `src/omnibase/nodes/{node_name}/v{major}_{minor}_{patch}/`
- **Runtimes**: `src/omnibase/runtimes/{runtime_name}/v{major}_{minor}_{patch}/`
- **CLI Tools**: `src/omnibase/cli_tools/{tool_name}/v{major}_{minor}_{patch}/`

### Version Metadata

Each versioned component must include:
- **Metadata file**: `node.onex.yaml`, `runtime.yaml`, or `cli_tool.yaml`
- **Contract file**: `contract.yaml` (for nodes)
- **README**: Version-specific documentation

---

## Reserved Naming Prefixes

### Mandatory Prefixes

| Prefix | Usage | Location | Example |
|--------|-------|----------|---------|
| `core_` | Core system logic | `src/omnibase/core/` | `core_registry.py` |
| `protocol_` | Protocol definitions | `src/omnibase/protocol/` | `protocol_event_bus.py` |
| `model_` | Data models | `src/omnibase/model/` | `model_onex_event.py` |
| `utils_` | Utility functions | `src/omnibase/utils/` | `utils_uri_parser.py` |
| `handler_` | File type handlers | `*/handlers/` | `handler_python.py` |
| `cli_` | CLI tools/commands | `*/cli_tools/` | `cli_main.py` |
| `test_` | Test files | `tests/` | `test_registry.py` |
| `template_` | Template files | `src/omnibase/templates/` | `template_node.py` |

### Legacy and Migration

- **No `legacy_` prefix** unless explicitly staging for migration
- Files should be renamed to match standards during refactoring
- Migration must be documented in changelog

---

## Protocol and Model Organization

### Shared vs Node-Specific

#### Shared Components (`src/omnibase/protocol/`, `src/omnibase/model/`)

**Use for:**
- Cross-node interfaces and contracts
- Plugin boundaries and APIs
- System-wide event models
- Common result formats
- Stable, versioned interfaces

**Examples:**
- `ProtocolEventBus` - Event communication across nodes
- `ProtocolFileTypeHandler` - Plugin boundary for file processing
- `OnexEvent` - Standard event model system-wide
- `OnexResultModel` - Common result format

#### Node-Specific Components (`nodes/{node}/v{version}/protocol/`, `models/`)

**Use for:**
- Internal node logic and state
- Node-specific validation
- Rapid iteration requirements
- No reuse potential outside node

**Examples:**
- `ProtocolOnextreeValidator` - Tree generator validation logic
- `StamperInputState` - Internal stamper node state
- Node-specific constants and error enums

### Import Patterns

#### ✅ Correct Patterns

```python
# Shared components - from any location
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.model.model_onex_event import OnexEvent

# Node-specific - only within same node
from .protocol.protocol_onextree_validator import ProtocolOnextreeValidator
from .models.state import StamperInputState

# TYPE_CHECKING pattern for circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock

class ProtocolCanonicalSerializer(Protocol):
    def canonicalize_metadata_block(self, block: "NodeMetadataBlock") -> str:
        ...
```

#### ❌ Forbidden Patterns

```python
# Cross-node imports of node-specific components
from omnibase.nodes.tree_generator_node.v1_0_0.protocol.protocol_onextree_validator import ProtocolOnextreeValidator

# Direct circular imports
from omnibase.model.model_node_metadata import NodeMetadataBlock  # In protocol file
```

---

## Node Structure Standards

### Canonical Node Layout

```
src/omnibase/nodes/<node_name>/v<major>_<minor>_<patch>/
├── node.py                    # Main node entrypoint
├── node.onex.yaml             # Node metadata and configuration
├── contract.yaml              # Input/output state contract
├── introspection.py           # Node introspection implementation
├── error_codes.py             # Node-specific error definitions
├── README.md                  # Node documentation
├── __init__.py                # Package initialization
├── .onexignore               # Files to ignore in processing
├── pytest.ini               # Node-specific test configuration
├── models/                    # Node-specific data models
│   ├── __init__.py
│   ├── state.py              # Input/output state models
│   └── constants.py          # Node-specific constants
├── helpers/                   # Node implementation logic
│   ├── __init__.py
│   ├── helpers_<function>.py # Prefixed helper modules
│   └── ...
├── node_tests/                # Node-specific tests
│   ├── __init__.py
│   ├── test_<node_name>.py
│   └── fixtures/             # Test data and fixtures
├── examples/                  # Usage examples (optional)
└── protocol/                  # Node-specific protocols (optional)
    ├── __init__.py
    └── protocol_<specific>.py
```

### Required Files

Every node version must contain:
1. **`node.py`** - Main entrypoint with canonical function signature
2. **`node.onex.yaml`** - Node metadata following canonical schema
3. **`contract.yaml`** - Input/output state contract definition
4. **`introspection.py`** - Node introspection implementation
5. **`error_codes.py`** - Node-specific error code definitions

### Node Metadata Format

```yaml
# node.onex.yaml
node_id: "example_node"
name: "Example Node"
version: "1.0.0"
entrypoint:
  module: "nodes.example_node.v1_0_0.node"
  function: "run_example_node"
contract: "contract.yaml"
runtime_requirements:
  python_version: ">=3.11"
  dependencies: []
```

---

## CLI Tools and Commands

### CLI Structure

```
src/omnibase/cli_tools/onex/v1_0_0/
├── cli_main.py                # Main CLI entrypoint
├── cli_tool.yaml             # CLI tool metadata
├── cli_version_resolver.py   # Version resolution logic
├── .onexignore              # Files to ignore
├── commands/                 # Individual command implementations
│   ├── run_node.py          # Node execution commands
│   ├── list_handlers.py     # Handler management
│   └── fix_node_health.py   # Maintenance commands
└── cli_tests/               # CLI-specific tests
```

### CLI Naming Rules

- **Main entrypoint**: `cli_main.py`
- **Command modules**: Descriptive names in `commands/` directory
- **CLI metadata**: `cli_tool.yaml` for tool configuration
- **Framework**: Use Typer for all CLI implementations
- **Help text**: Clear, consistent, reference canonical documentation

### Command Implementation Pattern

```python
import typer
from typing import Optional

app = typer.Typer()

@app.command()
def example_command(
    input_file: str = typer.Argument(..., help="Input file path"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
) -> None:
    """Example command with proper Typer patterns."""
    # Implementation here
```

---

## Handler Organization

### Handler Hierarchy

#### Core Handlers (Priority: 100)
- **Location**: `src/omnibase/core/`
- **Purpose**: Essential system functionality
- **Examples**: Registry, error handling, plugin loading

#### Runtime Handlers (Priority: 50)
- **Location**: `src/omnibase/runtimes/onex_runtime/v1_0_0/handlers/`
- **Purpose**: Standard file type support
- **Examples**: `handler_python.py`, `handler_markdown.py`, `handler_metadata_yaml.py`

#### Node-Local Handlers (Priority: 10)
- **Location**: `src/omnibase/nodes/{node}/v{version}/helpers/`
- **Purpose**: Node-specific functionality
- **Examples**: Node-specific file processors, validation logic

#### Plugin Handlers (Priority: 0)
- **Location**: External packages with entry points
- **Purpose**: Third-party or experimental functionality

### Handler Naming and Structure

```python
# handler_python.py
from typing import Protocol, TYPE_CHECKING
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock

class PythonHandler(ProtocolFileTypeHandler):
    """Handler for Python source files."""
    
    def get_supported_extensions(self) -> list[str]:
        return [".py"]
    
    def process_file(self, file_path: str, metadata: "NodeMetadataBlock") -> str:
        # Implementation
        pass
```

---

## Testing Standards

### Test Organization

```
tests/
├── core/                     # Core component tests
├── protocol/                 # Protocol compliance tests
├── model/                    # Model validation tests
├── handlers/                 # Handler tests
├── fixtures/                 # Shared test fixtures
├── integration/              # Integration tests
└── e2e/                     # End-to-end tests
```

### Test Naming Conventions

- **Test files**: `test_<component>.py`
- **Test classes**: `Test<Component>`
- **Test methods**: `test_<functionality>`
- **Parametrized tests**: `test_<functionality>_parametrized.py`

### Test Implementation Standards

```python
import pytest
from typing import Any
from omnibase.protocol.protocol_registry import ProtocolRegistry

class TestRegistry:
    """Test suite for registry functionality."""
    
    def test_basic_functionality(self) -> None:
        """Test basic registry operations."""
        # Implementation
        pass
    
    @pytest.mark.parametrize("input_data,expected", [
        ("test_input", "expected_output"),
        # More test cases
    ])
    def test_parametrized_functionality(self, input_data: str, expected: str) -> None:
        """Test functionality with multiple inputs."""
        # Implementation
        pass
```

### Test Requirements

- **Coverage**: Minimum 80% for all new code
- **Protocol-driven**: Use registry-injected test cases
- **No hardcoded data**: Use fixtures and factories
- **Model-based assertions**: Avoid string-based assertions for domain fields
- **Separation**: Unit, integration, and e2e tests clearly separated

---

## Documentation Standards

### Documentation Structure

```
docs/
├── standards/               # Standards and conventions
├── architecture/           # Architectural documentation
├── nodes/                  # Node-specific documentation
├── testing/                # Testing guidelines
├── guides/                 # User and developer guides
├── examples/               # Usage examples
├── changelogs/             # Version changelogs
└── milestones/             # Project milestones
```

### Documentation Requirements

- **Markdown format**: All documentation in Markdown
- **Metadata blocks**: Include ONEX metadata in all documentation files
- **Naming**: Use lowercase, hyphen-separated names
- **Structure**: Clear headings, table of contents for long documents
- **Examples**: Include code examples and usage patterns
- **Links**: Use relative links, keep all links current

### Documentation Metadata

```markdown
# Document Title

Content here...
```

---

## Code Quality Standards

### Python Code Standards

#### Type Annotations
- **Required**: All public functions and methods must have type annotations
- **Return types**: Always specify return types
- **Complex types**: Use `typing` module for complex types
- **Forward references**: Use string annotations for forward references

```python
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock

def process_metadata(
    metadata: "NodeMetadataBlock",
    options: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Process metadata with proper type annotations."""
    # Implementation
    return []
```

#### Error Handling
- **Use enums**: Define error codes as enums
- **Structured exceptions**: Use custom exception classes
- **Logging**: Include correlation IDs in all log messages
- **Recovery**: Implement graceful error recovery where possible

```python
from enum import Enum
from omnibase.model.model_base_error import BaseError

class ProcessingErrorCode(Enum):
    INVALID_INPUT = "INVALID_INPUT"
    PROCESSING_FAILED = "PROCESSING_FAILED"

class ProcessingError(BaseError):
    """Custom exception for processing errors."""
    pass
```

#### Dependency Injection
- **No singletons**: Avoid global state and singletons
- **Constructor injection**: Inject dependencies via constructors
- **Protocol interfaces**: Use protocols for dependency contracts
- **Testability**: Ensure all dependencies can be mocked

```python
from omnibase.protocol.protocol_event_bus import ProtocolEventBus

class ExampleService:
    def __init__(self, event_bus: ProtocolEventBus) -> None:
        self._event_bus = event_bus
    
    def process(self) -> None:
        # Use injected dependency
        self._event_bus.emit_event(...)
```

### Code Formatting

- **Black**: Use Black for code formatting
- **Line length**: 88 characters maximum
- **Imports**: Use isort for import organization
- **Docstrings**: Use Google-style docstrings

### Linting and Type Checking

- **Ruff**: Use Ruff for linting
- **MyPy**: Use MyPy for type checking
- **Pre-commit**: All checks must pass in pre-commit hooks

---

## Enforcement and Compliance

### Automated Enforcement

#### Pre-commit Hooks
- Metadata stamping
- Code formatting (Black, isort)
- Linting (Ruff)
- Type checking (MyPy)
- Test execution
- Documentation validation

#### CI/CD Pipeline
- Full test suite execution
- Standards compliance validation
- Parity validation across nodes
- Documentation build verification
- Security scanning

### Manual Review Requirements

#### Code Review Checklist
- [ ] Naming conventions followed
- [ ] Type annotations present
- [ ] Error handling implemented
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No singleton patterns
- [ ] Protocol interfaces used correctly

#### Standards Review Process
1. **Automated checks**: All CI checks must pass
2. **Peer review**: At least one maintainer review required
3. **Standards validation**: Compliance with this document verified
4. **Documentation review**: All documentation updated appropriately

### Compliance Validation

#### Parity Validator
Run the parity validator to ensure ecosystem compliance:

```bash
poetry run onex run parity_validator_node --args='["--verbose"]'
```

#### Standards Audit
Regular audits must verify:
- File naming compliance
- Directory structure adherence
- Protocol placement correctness
- Documentation completeness
- Test coverage requirements

### Exceptions and Waivers

- **Justification required**: All deviations must be documented
- **Maintainer approval**: Exceptions require maintainer review
- **Time-bound**: Temporary exceptions must have resolution timeline
- **Documentation**: All exceptions documented in ADRs

---

## Migration and Legacy

### Legacy Code Handling

- **Gradual migration**: Refactor legacy code incrementally
- **Standards alignment**: Bring legacy code up to current standards
- **Documentation**: Document migration decisions and timelines
- **Testing**: Ensure legacy code has adequate test coverage

### Breaking Changes

- **Version bumps**: Breaking changes require major version increments
- **Migration guides**: Provide clear migration documentation
- **Deprecation notices**: Give advance warning of breaking changes
- **Backward compatibility**: Maintain compatibility for at least 2 major versions

---

## References

- [Canonical File Types](standards/canonical_file_types.md)
- [Node Structural Conventions](nodes/structural_conventions.md)
- [Protocol and Model Organization](protocols_and_models.md)
- [Testing Guidelines](testing.md)
- [CLI Interface Documentation](cli_interface.md)

---

> **This document is canonical.** All contributors must follow these standards for all new and existing code. Deviations must be justified, documented, and reviewed by maintainers. For questions or clarifications, refer to the project maintainers or create an issue for discussion.
