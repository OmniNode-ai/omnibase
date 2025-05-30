<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: entry_points.md
version: 1.0.0
uuid: 63a916f9-9211-4eb2-8edd-e368f732faa7
author: OmniNode Team
created_at: '2025-05-28T12:40:26.863311'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://entry_points
namespace: markdown://entry_points
meta_type: tool

<!-- === /OmniNode:Metadata === -->
# Plugin Discovery Entry Points

> **Status:** Canonical
> **Last Updated:** 2025-05-25
> **Purpose:** Developer guide for plugin discovery patterns and entry point configuration in the ONEX ecosystem

## Overview

This guide explains how to create and configure plugins for the ONEX system using entry points, configuration files, and environment variables. The ONEX plugin system supports multiple discovery mechanisms to accommodate different deployment scenarios and development workflows.

## Discovery Mechanisms

The ONEX system supports three plugin discovery mechanisms, loaded in this order:

1. **Entry Points** - Standard Python packaging mechanism (recommended)
2. **Configuration Files** - YAML-based plugin registry
3. **Environment Variables** - Runtime plugin specification

## Entry Points (Recommended)

Entry points are the preferred mechanism for distributing ONEX plugins as they integrate with Python's packaging ecosystem and provide automatic discovery.

### Configuration

#### Using `pyproject.toml` (Recommended)

```toml
[project]
name = "my-onex-plugin"
version = "1.0.0"
description = "Custom ONEX handlers for my organization"

[project.entry-points."omnibase.handlers"]
csv_processor = "my_onex_plugin.handlers:CSVHandler"
xml_processor = "my_onex_plugin.handlers:XMLHandler"
custom_format = "my_onex_plugin.handlers:CustomFormatHandler"
```

#### Using `setup.cfg` (Legacy)

```ini
[metadata]
name = my-onex-plugin
version = 1.0.0
description = Custom ONEX handlers for my organization

[options.entry_points]
omnibase.handlers =
    csv_processor = my_onex_plugin.handlers:CSVHandler
    xml_processor = my_onex_plugin.handlers:XMLHandler
    custom_format = my_onex_plugin.handlers:CustomFormatHandler
```

#### Using `setup.py` (Legacy)

```python
from setuptools import setup, find_packages

setup(
    name="my-onex-plugin",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "omnibase.handlers": [
            "csv_processor = my_onex_plugin.handlers:CSVHandler",
            "xml_processor = my_onex_plugin.handlers:XMLHandler",
            "custom_format = my_onex_plugin.handlers:CustomFormatHandler",
        ]
    },
)
```

### Plugin Package Structure

```
my-onex-plugin/
├── pyproject.toml              # Entry point configuration
├── README.md                   # Installation and usage guide
├── my_onex_plugin/
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── csv_handler.py      # CSVHandler implementation
│   │   ├── xml_handler.py      # XMLHandler implementation
│   │   └── custom_handler.py   # CustomFormatHandler implementation
│   └── tests/
│       ├── __init__.py
│       └── test_handlers.py
└── tests/
    └── integration/
        └── test_plugin_integration.py
```

### Handler Implementation Example

```python
# my_onex_plugin/handlers/csv_handler.py
from pathlib import Path
from typing import Any, List, Optional, Tuple

from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler


class CSVHandler(ProtocolFileTypeHandler):
    """Handler for CSV files with custom metadata support."""

    # Required metadata properties
    @property
    def handler_name(self) -> str:
        return "csv_processor"

    @property
    def handler_version(self) -> str:
        return "1.0.0"

    @property
    def handler_author(self) -> str:
        return "My Organization"

    @property
    def handler_description(self) -> str:
        return "Processes CSV files with custom metadata extraction"

    @property
    def supported_extensions(self) -> List[str]:
        return [".csv", ".tsv"]

    @property
    def supported_filenames(self) -> List[str]:
        return []

    @property
    def handler_priority(self) -> int:
        return 0  # Plugin priority

    @property
    def requires_content_analysis(self) -> bool:
        return True

    def can_handle(self, path: Path, content: str) -> bool:
        """Check if this handler can process the given file."""
        return path.suffix.lower() in [".csv", ".tsv"]

    def extract_block(self, path: Path, content: str) -> Tuple[Optional[Any], str]:
        """Extract metadata from CSV file."""
        # Implementation for extracting CSV metadata
        # Return (metadata_dict, remaining_content)
        pass

    def serialize_block(self, meta: Any) -> str:
        """Serialize metadata back to CSV format."""
        # Implementation for serializing metadata
        pass

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """Stamp CSV file with metadata."""
        # Implementation for stamping CSV files
        pass

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """Validate CSV file metadata."""
        # Implementation for validating CSV files
        pass

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        """Pre-validation hook."""
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        """Post-validation hook."""
        return None
```

### Installation and Usage

```bash
# Install the plugin
pip install my-onex-plugin

# The plugin is automatically discovered when ONEX loads
# No additional configuration required
```

## Configuration Files

Configuration files provide a way to register plugins without modifying Python packages, useful for deployment scenarios where entry points are not practical.

### Configuration Format

```yaml
# plugin_registry.yaml
handlers:
  csv_processor:
    module: "my_onex_plugin.handlers.csv_handler"
    class: "CSVHandler"
    priority: 5
    description: "CSV file processor with custom metadata"
    
  xml_processor:
    module: "my_onex_plugin.handlers.xml_handler"
    class: "XMLHandler"
    priority: 3
    description: "XML file processor"
    
  legacy_format:
    module: "legacy_handlers.old_format"
    class: "LegacyFormatHandler"
    priority: 1
    description: "Legacy format handler for backward compatibility"
```

### Configuration File Locations

The system searches for configuration files in this order:

1. `./plugin_registry.yaml` (current directory)
2. `~/.onex/plugin_registry.yaml` (user home directory)
3. `/etc/onex/plugin_registry.yaml` (system-wide)

### Manual Configuration Loading

```python
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry

registry = FileTypeHandlerRegistry()
registry.register_all_handlers()

# Load additional plugins from specific config file
registry.register_plugin_handlers_from_config("/path/to/custom/config.yaml")
```

## Environment Variables

Environment variables provide runtime plugin specification, useful for containerized deployments and testing.

### Format

```bash
ONEX_PLUGIN_HANDLER_<NAME>=module.path:ClassName
```

### Examples

```bash
# Register a CSV handler
export ONEX_PLUGIN_HANDLER_CSV="my_onex_plugin.handlers.csv_handler:CSVHandler"

# Register an XML handler
export ONEX_PLUGIN_HANDLER_XML="my_onex_plugin.handlers.xml_handler:XMLHandler"

# Register a custom format handler
export ONEX_PLUGIN_HANDLER_CUSTOM="custom_handlers.special:SpecialFormatHandler"
```

### Docker Example

```dockerfile
FROM python:3.11

# Install your plugin package
COPY my-onex-plugin /app/my-onex-plugin
RUN pip install /app/my-onex-plugin

# Set environment variables for additional handlers
ENV ONEX_PLUGIN_HANDLER_CSV="my_onex_plugin.handlers.csv_handler:CSVHandler"
ENV ONEX_PLUGIN_HANDLER_XML="my_onex_plugin.handlers.xml_handler:XMLHandler"

# Your application code
COPY . /app
WORKDIR /app
```

## Discovery Order and Priority

### Loading Order

1. **Core Handlers** (Priority 100) - Built-in system handlers
2. **Runtime Handlers** (Priority 50) - Standard ONEX ecosystem handlers
3. **Node-Local Handlers** (Priority 10) - Node-specific handlers
4. **Plugin Handlers** (Priority 0) - Discovered plugins

### Within Plugin Handlers

1. **Entry Points** - Loaded first, priority 0 by default
2. **Configuration Files** - Loaded second, priority from config
3. **Environment Variables** - Loaded last, priority 0

### Conflict Resolution

When multiple handlers can handle the same file type:

1. **Higher priority wins** (100 > 50 > 10 > 0)
2. **Within same priority, last registered wins**
3. **Use `override=True` to force replacement**

## Best Practices

### Plugin Development

1. **Follow Protocol Contract**
   - Implement all required methods and properties
   - Use proper type annotations
   - Handle errors gracefully

2. **Naming Conventions**
   - Use descriptive entry point names
   - Follow `snake_case` for handler names
   - Include organization/purpose in names

3. **Testing**
   - Test handler in isolation
   - Test integration with ONEX registry
   - Test conflict resolution scenarios

4. **Documentation**
   - Provide clear installation instructions
   - Document supported file types and patterns
   - Include usage examples

### Entry Point Naming

```toml
# Good: Descriptive and specific
[project.entry-points."omnibase.handlers"]
acme_csv_processor = "acme_plugin.handlers:CSVHandler"
acme_xml_validator = "acme_plugin.handlers:XMLHandler"

# Avoid: Generic or conflicting names
[project.entry-points."omnibase.handlers"]
csv = "acme_plugin.handlers:CSVHandler"  # Too generic
handler = "acme_plugin.handlers:XMLHandler"  # Too vague
```

### Error Handling

```python
class MyHandler(ProtocolFileTypeHandler):
    def can_handle(self, path: Path, content: str) -> bool:
        try:
            # Your logic here
            return path.suffix.lower() == ".myformat"
        except Exception as e:
            # Log error but don't crash
            logger.error(f"Error in can_handle for {path}: {e}")
            return False

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        try:
            # Your stamping logic
            return OnexResultModel(status=OnexStatus.SUCCESS, ...)
        except Exception as e:
            # Return error result instead of raising
            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=str(path),
                messages=[OnexMessageModel(
                    summary=f"Stamping failed: {e}",
                    level=LogLevelEnum.ERROR
                )]
            )
```

## Testing Plugins

### Unit Testing

```python
# tests/test_csv_handler.py
import pytest
from pathlib import Path

from my_onex_plugin.handlers.csv_handler import CSVHandler


class TestCSVHandler:
    def test_can_handle_csv_files(self):
        handler = CSVHandler()
        assert handler.can_handle(Path("test.csv"), "")
        assert handler.can_handle(Path("test.tsv"), "")
        assert not handler.can_handle(Path("test.txt"), "")

    def test_metadata_properties(self):
        handler = CSVHandler()
        assert handler.handler_name == "csv_processor"
        assert handler.handler_version == "1.0.0"
        assert ".csv" in handler.supported_extensions
```

### Integration Testing

```python
# tests/integration/test_plugin_integration.py
import pytest
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry


class TestPluginIntegration:
    def test_plugin_discovery(self):
        registry = FileTypeHandlerRegistry()
        registry.register_all_handlers()
        
        # Check that our plugin was discovered
        handlers = registry.list_handlers()
        assert any("csv_processor" in key for key in handlers.keys())

    def test_handler_priority(self):
        registry = FileTypeHandlerRegistry()
        registry.register_all_handlers()
        
        # Test that plugin handlers have correct priority
        handler = registry.get_named_handler("csv_processor")
        assert handler is not None
```

## Troubleshooting

### Common Issues

1. **Plugin Not Discovered**
   - Check entry point configuration syntax
   - Verify package installation
   - Check import paths and class names

2. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path and module structure
   - Verify class names match entry point configuration

3. **Handler Validation Failures**
   - Implement all required protocol methods
   - Add all required metadata properties
   - Check method signatures and return types

### Debugging

```python
import logging

# Enable debug logging for plugin discovery
logging.getLogger("omnibase.FileTypeHandlerRegistry").setLevel(logging.DEBUG)

# Create registry and check discovered handlers
registry = FileTypeHandlerRegistry()
registry.register_all_handlers()

# List all handlers to see what was discovered
handlers = registry.list_handlers()
for key, info in handlers.items():
    if info["source"] == "plugin":
        print(f"Plugin handler: {key} -> {info}")
```

### Validation Script

```python
#!/usr/bin/env python3
"""Validate plugin handler implementation."""

from my_onex_plugin.handlers.csv_handler import CSVHandler
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler


def validate_handler(handler_class):
    """Validate that a handler implements the required protocol."""
    required_methods = [
        'can_handle', 'extract_block', 'serialize_block',
        'stamp', 'validate', 'pre_validate', 'post_validate'
    ]
    
    required_properties = [
        'handler_name', 'handler_version', 'handler_author',
        'handler_description', 'supported_extensions', 'supported_filenames',
        'handler_priority', 'requires_content_analysis'
    ]
    
    try:
        instance = handler_class()
        
        # Check methods
        for method in required_methods:
            if not hasattr(instance, method):
                print(f"❌ Missing method: {method}")
                return False
            if not callable(getattr(instance, method)):
                print(f"❌ Not callable: {method}")
                return False
        
        # Check properties
        for prop in required_properties:
            if not hasattr(instance, prop):
                print(f"❌ Missing property: {prop}")
                return False
        
        print("✅ Handler validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


if __name__ == "__main__":
    validate_handler(CSVHandler)
```

## Migration Guide

### From Legacy Handlers

If you have existing handlers that don't follow the current protocol:

1. **Add Required Metadata Properties**
   ```python
   @property
   def handler_name(self) -> str:
       return "my_legacy_handler"
   
   # ... add all other required properties
   ```

2. **Update Method Signatures**
   ```python
   # Old
   def stamp(self, path, content):
       pass
   
   # New
   def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
       pass
   ```

3. **Add Entry Point Configuration**
   ```toml
   [project.entry-points."omnibase.handlers"]
   legacy_handler = "my_package.handlers:LegacyHandler"
   ```

### From Manual Registration

If you currently register handlers manually:

```python
# Old way
registry = FileTypeHandlerRegistry()
registry.register_handler(".csv", MyCSVHandler())

# New way - use entry points
# Add to pyproject.toml:
# [project.entry-points."omnibase.handlers"]
# csv_handler = "my_package.handlers:MyCSVHandler"

# Then just:
registry = FileTypeHandlerRegistry()
registry.register_all_handlers()  # Automatically discovers plugins
```

## Conclusion

The ONEX plugin discovery system provides flexible mechanisms for extending handler functionality while maintaining compatibility and performance. Entry points are recommended for most use cases, with configuration files and environment variables available for specialized deployment scenarios.

For questions or support, consult the [Plugin & Handler Governance](../governance/plugin_handler_governance.md) document or reach out to the maintainer team.
