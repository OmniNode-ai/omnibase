<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: handlers_registry_api.md
version: 1.0.0
uuid: 13e2a80c-a545-46c1-82db-79b0ea46455d
author: OmniNode Team
created_at: 2025-05-25T11:19:39.093725
last_modified_at: 2025-05-25T15:20:36.123394
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: f6823626cbdc4118bb4d4b1705cce095d0f976c3d2ba1b757eb41c7fd58f2434
entrypoint: python@handlers_registry_api.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.handlers_registry_api
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Handler & Registry API Documentation

> **Status:** Canonical  
> **Version:** 1.0.0  
> **Last Updated:** 2025-05-25  
> **Purpose:** Complete API documentation for ONEX Handler and Registry system

## Overview

The ONEX Handler & Registry system provides a flexible, extensible architecture for processing different file types within the ONEX ecosystem. This system supports plugin-based extensions, priority-based conflict resolution, and comprehensive metadata introspection.

## Architecture

### Core Components

1. **ProtocolFileTypeHandler** - Interface defining handler contract
2. **FileTypeHandlerRegistry** - Central registry for handler management
3. **Handler Implementations** - Concrete handlers for specific file types
4. **Plugin System** - Runtime handler registration and override capabilities

### Handler Hierarchy

```
Core Handlers (Priority: 100)
├── IgnoreFileHandler (.gitignore, .onexignore)
└── [Future core handlers]

Runtime Handlers (Priority: 50)
├── PythonHandler (.py files)
├── MarkdownHandler (.md files)
├── MetadataYAMLHandler (.yaml, .yml metadata)
└── [Future runtime handlers]

Node-Local Handlers (Priority: 10)
├── [Node-specific implementations]
└── [Custom business logic handlers]

Plugin Handlers (Priority: 0)
├── [Third-party plugins]
└── [User-defined extensions]
```

## Handler Interface

### ProtocolFileTypeHandler

All handlers must implement the `ProtocolFileTypeHandler` interface:

```python
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler

class MyCustomHandler(ProtocolFileTypeHandler):
    # Required metadata properties
    @property
    def handler_name(self) -> str:
        return "my_custom_handler"
    
    @property
    def handler_version(self) -> str:
        return "1.0.0"
    
    @property
    def handler_author(self) -> str:
        return "Your Name"
    
    @property
    def handler_description(self) -> str:
        return "Description of what this handler does"
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".custom", ".ext"]
    
    @property
    def supported_filenames(self) -> List[str]:
        return ["special_file.txt"]
    
    @property
    def handler_priority(self) -> int:
        return 10  # Node-local priority
    
    @property
    def requires_content_analysis(self) -> bool:
        return True  # If handler needs to read file content
    
    # Required methods
    def can_handle(self, file_path: Path) -> OnexResultModel:
        """Determine if this handler can process the given file."""
        pass
    
    def extract_block(self, file_path: Path) -> OnexResultModel:
        """Extract metadata block from file."""
        pass
    
    def serialize_block(self, metadata: dict, file_path: Path) -> OnexResultModel:
        """Serialize metadata block for insertion into file."""
        pass
    
    def pre_validate(self, file_path: Path) -> OnexResultModel:
        """Validate file before processing."""
        pass
    
    def post_validate(self, file_path: Path) -> OnexResultModel:
        """Validate file after processing."""
        pass
```

### Required Metadata Properties

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `handler_name` | `str` | Unique identifier for the handler | `"python_handler"` |
| `handler_version` | `str` | Semantic version of the handler | `"1.2.3"` |
| `handler_author` | `str` | Author or team responsible | `"OmniNode Team"` |
| `handler_description` | `str` | Brief description of functionality | `"Handles Python source files"` |
| `supported_extensions` | `List[str]` | File extensions this handler supports | `[".py", ".pyx"]` |
| `supported_filenames` | `List[str]` | Specific filenames this handler supports | `["setup.py"]` |
| `handler_priority` | `int` | Priority for conflict resolution | `50` |
| `requires_content_analysis` | `bool` | Whether handler needs file content | `True` |

## Registry API

### FileTypeHandlerRegistry

The central registry manages all handlers and provides discovery, registration, and conflict resolution.

#### Basic Usage

```python
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry

# Create registry instance
registry = FileTypeHandlerRegistry()

# Register a handler by extension
registry.register_handler(".custom", MyCustomHandler)

# Register a handler by filename
registry.register_handler("special_file.txt", MyCustomHandler, registration_type="filename")

# Register with custom priority and override
registry.register_handler(
    ".py", 
    MyCustomPythonHandler, 
    priority=75,
    override=True,
    source="plugin"
)

# Get handler for a file
result = registry.get_handler_for_file(Path("example.py"))
if result.status == OnexStatus.SUCCESS:
    handler = result.data["handler"]
    # Use handler...
```

#### Advanced Registration

```python
# Bulk registration
handlers = {
    ".custom1": MyHandler1,
    ".custom2": MyHandler2,
    "special.txt": MyHandler3
}
registry.register_handlers(handlers, source="plugin", priority=20)

# Register handler class (auto-instantiation)
registry.register_handler(".ext", MyHandlerClass, instantiate=True)

# Register with metadata
registry.register_handler(
    ".special",
    handler_instance,
    priority=30,
    source="node-local",
    metadata={"plugin_version": "2.1.0", "author": "Plugin Team"}
)
```

#### Registry Introspection

```python
# List all registered handlers
handlers_info = registry.list_handlers()
for key, info in handlers_info.items():
    print(f"Handler: {info['handler_name']}")
    print(f"  Type: {info['type']}")
    print(f"  Priority: {info['priority']}")
    print(f"  Source: {info['source']}")
    print(f"  Version: {info.get('handler_version', 'unknown')}")

# Get handler statistics
stats = registry.get_handler_stats()
print(f"Total handlers: {stats['total_handlers']}")
print(f"Extension handlers: {stats['extension_handlers']}")
print(f"Filename handlers: {stats['filename_handlers']}")

# Check for conflicts
conflicts = registry.get_conflicts()
for conflict in conflicts:
    print(f"Conflict for {conflict['key']}: {conflict['handlers']}")
```

## Node Integration

### Adding Handler Support to Nodes

All ONEX nodes support the `handler_registry` parameter for custom handler registration:

```python
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry

def run_my_node(
    input_state: MyNodeInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> MyNodeOutputState:
    """
    Main node entrypoint with handler registry support.
    
    Args:
        input_state: Node input configuration
        event_bus: Optional event bus for notifications
        handler_registry: Optional custom handler registry for file processing
    """
    # Create engine with handler registry
    engine = MyNodeEngine(handler_registry=handler_registry)
    
    # Process files using custom handlers
    result = engine.process_files(input_state.file_paths)
    
    return MyNodeOutputState(result=result)
```

### Engine Implementation

```python
class MyNodeEngine:
    def __init__(self, handler_registry: Optional[FileTypeHandlerRegistry] = None):
        self.handler_registry = handler_registry or FileTypeHandlerRegistry()
        
        # Register node-local handlers if needed
        self.handler_registry.register_handler(
            ".special", 
            MyNodeSpecialHandler,
            source="node-local",
            priority=10
        )
    
    def process_files(self, file_paths: List[Path]) -> List[ProcessResult]:
        results = []
        for file_path in file_paths:
            # Get appropriate handler
            handler_result = self.handler_registry.get_handler_for_file(file_path)
            if handler_result.status == OnexStatus.SUCCESS:
                handler = handler_result.data["handler"]
                # Process with handler
                result = handler.extract_block(file_path)
                results.append(result)
        return results
```

## Plugin Development

### Creating a Plugin Handler

1. **Implement the Protocol**

```python
from pathlib import Path
from typing import List
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.model.enum_onex_status import OnexStatus

class MyPluginHandler(ProtocolFileTypeHandler):
    """Custom plugin handler for .myext files."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    # Metadata properties
    @property
    def handler_name(self) -> str:
        return "my_plugin_handler"
    
    @property
    def handler_version(self) -> str:
        return "1.0.0"
    
    @property
    def handler_author(self) -> str:
        return "Plugin Developer"
    
    @property
    def handler_description(self) -> str:
        return "Handles .myext files with custom processing"
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".myext"]
    
    @property
    def supported_filenames(self) -> List[str]:
        return []
    
    @property
    def handler_priority(self) -> int:
        return 0  # Plugin priority
    
    @property
    def requires_content_analysis(self) -> bool:
        return True
    
    # Implementation methods
    def can_handle(self, file_path: Path) -> OnexResultModel:
        """Check if we can handle this file."""
        if file_path.suffix.lower() == ".myext":
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                data={"can_handle": True}
            )
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            data={"can_handle": False}
        )
    
    def extract_block(self, file_path: Path) -> OnexResultModel:
        """Extract metadata from .myext file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Custom extraction logic
            metadata = self._parse_myext_metadata(content)
            
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                data={"metadata": metadata}
            )
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.ERROR,
                messages=[f"Failed to extract metadata: {e}"]
            )
    
    def serialize_block(self, metadata: dict, file_path: Path) -> OnexResultModel:
        """Serialize metadata for .myext file."""
        try:
            serialized = self._serialize_myext_metadata(metadata)
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                data={"serialized_block": serialized}
            )
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.ERROR,
                messages=[f"Failed to serialize metadata: {e}"]
            )
    
    def pre_validate(self, file_path: Path) -> OnexResultModel:
        """Validate file before processing."""
        if not file_path.exists():
            return OnexResultModel(
                status=OnexStatus.ERROR,
                messages=["File does not exist"]
            )
        return OnexResultModel(status=OnexStatus.SUCCESS)
    
    def post_validate(self, file_path: Path) -> OnexResultModel:
        """Validate file after processing."""
        # Custom validation logic
        return OnexResultModel(status=OnexStatus.SUCCESS)
    
    def _parse_myext_metadata(self, content: str) -> dict:
        """Custom parsing logic for .myext files."""
        # Implementation specific to .myext format
        pass
    
    def _serialize_myext_metadata(self, metadata: dict) -> str:
        """Custom serialization logic for .myext files."""
        # Implementation specific to .myext format
        pass
```

2. **Register the Plugin**

```python
# In your plugin initialization code
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry

def register_plugin(registry: FileTypeHandlerRegistry):
    """Register the plugin handler with the registry."""
    handler = MyPluginHandler()
    registry.register_handler(
        ".myext",
        handler,
        source="plugin",
        priority=0,
        metadata={
            "plugin_name": "MyExt Plugin",
            "plugin_version": "1.0.0",
            "author": "Plugin Developer"
        }
    )
```

3. **Use in Node Context**

```python
# When calling a node with custom handlers
from omnibase.nodes.stamper_node.v1_0_0.node import run_stamper_node
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry

# Create custom registry
custom_registry = FileTypeHandlerRegistry()
register_plugin(custom_registry)

# Use with node
result = run_stamper_node(
    input_state=stamper_input,
    handler_registry=custom_registry
)
```

## Versioning Strategy

### Handler Versioning

Handlers follow semantic versioning (semver) principles:

- **Major version** (X.0.0): Breaking changes to handler interface
- **Minor version** (0.X.0): New features, backward compatible
- **Patch version** (0.0.X): Bug fixes, backward compatible

### Registry Versioning

The registry system itself follows the ONEX runtime versioning:

- Current version: `v1_0_0` (located in `src/omnibase/runtimes/onex_runtime/v1_0_0/`)
- Future versions will be parallel implementations: `v1_1_0`, `v2_0_0`, etc.

### Compatibility Matrix

| Registry Version | Handler Interface Version | Compatibility |
|------------------|---------------------------|---------------|
| v1_0_0 | 1.0.x | ✅ Full compatibility |
| v1_0_0 | 1.1.x | ✅ Backward compatible |
| v1_0_0 | 2.0.x | ❌ Breaking changes |

## Migration Guide

### Upgrading from Legacy Handlers

If you have existing handlers that don't implement the metadata properties:

1. **Add Required Metadata Properties**

```python
# Before (legacy)
class OldHandler:
    def can_handle(self, file_path):
        # implementation
        pass

# After (current)
class NewHandler(ProtocolFileTypeHandler):
    @property
    def handler_name(self) -> str:
        return "old_handler_updated"
    
    @property
    def handler_version(self) -> str:
        return "2.0.0"  # Increment for metadata addition
    
    # ... other required properties
    
    def can_handle(self, file_path: Path) -> OnexResultModel:
        # Updated implementation with proper return type
        pass
```

2. **Update Return Types**

```python
# Before
def extract_block(self, file_path):
    return {"metadata": data}

# After  
def extract_block(self, file_path: Path) -> OnexResultModel:
    return OnexResultModel(
        status=OnexStatus.SUCCESS,
        data={"metadata": data}
    )
```

3. **Update Registration**

```python
# Before
registry.handlers[".ext"] = OldHandler()

# After
registry.register_handler(".ext", NewHandler(), source="migration")
```

### Breaking Changes in v1.0.0

- **Required metadata properties**: All handlers must implement the 8 required metadata properties
- **Typed return values**: All methods must return `OnexResultModel` instances
- **Path parameters**: File paths must be `pathlib.Path` objects, not strings

### Migration Checklist

- [ ] Add all required metadata properties to custom handlers
- [ ] Update method signatures to use `Path` and `OnexResultModel`
- [ ] Update handler registration to use new `register_handler()` API
- [ ] Test handler functionality with new registry system
- [ ] Update documentation and examples
- [ ] Increment handler version numbers appropriately

## Best Practices

### Handler Development

1. **Single Responsibility**: Each handler should focus on one file type or format
2. **Error Handling**: Always return proper `OnexResultModel` with appropriate status
3. **Performance**: Minimize file I/O in `can_handle()` method
4. **Validation**: Implement thorough pre and post validation
5. **Documentation**: Provide clear docstrings and examples

### Registry Usage

1. **Lazy Loading**: Register handlers only when needed
2. **Priority Management**: Use appropriate priorities for conflict resolution
3. **Source Attribution**: Always specify source when registering handlers
4. **Metadata**: Include relevant metadata for debugging and introspection

### Plugin Development

1. **Namespace**: Use unique handler names to avoid conflicts
2. **Configuration**: Support configuration through constructor parameters
3. **Testing**: Provide comprehensive tests for all handler methods
4. **Documentation**: Include usage examples and API documentation

## Examples

### Complete Handler Example

See the [PythonHandler implementation](../src/omnibase/runtimes/onex_runtime/v1_0_0/handlers/handler_python.py) for a complete example of a production handler.

### Plugin Package Structure

```
my_onex_plugin/
├── __init__.py
├── handlers/
│   ├── __init__.py
│   ├── my_handler.py
│   └── another_handler.py
├── tests/
│   ├── test_my_handler.py
│   └── test_another_handler.py
├── setup.py
└── README.md
```

### Entry Points Configuration

```python
# setup.py
setup(
    name="my-onex-plugin",
    entry_points={
        "onex.handlers": [
            "myext = my_onex_plugin.handlers.my_handler:MyPluginHandler",
        ]
    }
)
```

## Troubleshooting

### Common Issues

1. **Handler Not Found**
   - Check file extension matches registered extension
   - Verify handler is properly registered
   - Check priority conflicts

2. **Metadata Validation Errors**
   - Ensure all required metadata properties are implemented
   - Verify property types match requirements
   - Check for empty or None values

3. **Registration Conflicts**
   - Use `get_conflicts()` to identify conflicts
   - Adjust priorities or use override flag
   - Check source attribution

### Debugging

```python
# Enable debug logging
import logging
logging.getLogger("omnibase.core.core_file_type_handler_registry").setLevel(logging.DEBUG)

# Check registry state
registry = FileTypeHandlerRegistry()
print(registry.list_handlers())
print(registry.get_handler_stats())
print(registry.get_conflicts())

# Test handler directly
handler = MyHandler()
result = handler.can_handle(Path("test.ext"))
print(f"Can handle: {result.status}, {result.data}")
```

## API Reference

### FileTypeHandlerRegistry Methods

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `register_handler()` | Register a handler | `key`, `handler`, `priority`, `source`, etc. | `OnexResultModel` |
| `get_handler_for_file()` | Get handler for file | `file_path: Path` | `OnexResultModel` |
| `list_handlers()` | List all handlers | None | `dict` |
| `get_handler_stats()` | Get registry statistics | None | `dict` |
| `get_conflicts()` | Get priority conflicts | None | `List[dict]` |
| `register_handlers()` | Bulk register handlers | `handlers: dict`, `source`, `priority` | `OnexResultModel` |

### ProtocolFileTypeHandler Methods

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `can_handle()` | Check if handler supports file | `file_path: Path` | `OnexResultModel` |
| `extract_block()` | Extract metadata from file | `file_path: Path` | `OnexResultModel` |
| `serialize_block()` | Serialize metadata block | `metadata: dict`, `file_path: Path` | `OnexResultModel` |
| `pre_validate()` | Validate before processing | `file_path: Path` | `OnexResultModel` |
| `post_validate()` | Validate after processing | `file_path: Path` | `OnexResultModel` |

## Changelog

### v1.0.0 (2025-05-25)

**Added:**
- Complete Handler & Registry API documentation
- Metadata property requirements for all handlers
- Plugin development guide and examples
- Migration guide from legacy handlers
- Comprehensive API reference
- Troubleshooting and debugging guide

**Breaking Changes:**
- Required metadata properties for all handlers
- Typed return values (`OnexResultModel`)
- Path parameters must be `pathlib.Path` objects

**Migration Required:**
- Update existing handlers to implement metadata properties
- Update method signatures and return types
- Update registration calls to use new API

---

> **Next Steps:** See [CHANGELOG.md](../CHANGELOG.md) for system-wide changes and [Plugin Development Guide](./plugins/plugin_development.md) for advanced plugin topics.
