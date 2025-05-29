<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:26.876570'
description: Stamped by ONEX
entrypoint: python://logger_node_plugin_example.md
hash: a8b2a90ef1a86df95f9f2bde241540307ca3eb973e6bde7305f446142f5304b9
last_modified_at: '2025-05-29T11:50:15.213419+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: logger_node_plugin_example.md
namespace: omnibase.logger_node_plugin_example
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: b47d1373-bd22-4cc0-b29f-cbe36299e017
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# Logger Node Plugin Development Guide

> **Status:** Documentation  
> **Last Updated:** 2025-05-26  
> **Purpose:** Guide for developing external plugins for the ONEX Logger Node

## Overview

The ONEX Logger Node supports pluggable output format handlers through a well-defined protocol interface. This allows developers to create custom output formats without modifying the core logger node code.

## Plugin Architecture

### Core Components

1. **ProtocolLogFormatHandler**: The interface all handlers must implement
2. **LogFormatHandlerRegistry**: Manages handler discovery and registration
3. **Entry Points**: Python packaging mechanism for plugin discovery
4. **Priority System**: Handles conflicts between multiple handlers for the same format

### Handler Discovery Methods

The logger node discovers handlers through multiple mechanisms:

1. **Core Handlers**: Built-in handlers (JSON, YAML, Markdown, Text, CSV)
2. **Entry Points**: Plugins registered via `pyproject.toml` or `setup.py`
3. **Runtime Registration**: Handlers registered programmatically
4. **Node-Local Handlers**: Handlers specific to a node instance

## Creating a Custom Format Handler

### Step 1: Implement the Protocol

```python
# my_plugin/xml_format_handler.py
from typing import Dict, Any, List
from omnibase.nodes.logger_node.v1_0_0.protocol.protocol_log_format_handler import ProtocolLogFormatHandler
from omnibase.nodes.logger_node.v1_0_0.models.state import LoggerInputState
from omnibase.core.error_codes import OnexError, CoreErrorCode

class XmlFormatHandler(ProtocolLogFormatHandler):
    """XML format handler for log entries."""

    @property
    def handler_name(self) -> str:
        return "xml_format_handler"

    @property
    def handler_version(self) -> str:
        return "1.0.0"

    @property
    def handler_author(self) -> str:
        return "Your Name"

    @property
    def handler_description(self) -> str:
        return "Formats log entries as XML documents"

    @property
    def supported_formats(self) -> List[str]:
        return ["xml"]

    @property
    def handler_priority(self) -> int:
        return 0  # Plugin priority

    @property
    def requires_dependencies(self) -> List[str]:
        return ["xml.etree.ElementTree"]  # Built into Python

    def can_handle(self, format_name: str) -> bool:
        return format_name.lower() in [f.lower() for f in self.supported_formats]

    def format_log_entry(self, input_state: LoggerInputState, log_entry: Dict[str, Any]) -> str:
        """Format a log entry as XML."""
        try:
            import xml.etree.ElementTree as ET
            
            # Create root element
            root = ET.Element("log_entry")
            
            # Add basic fields
            for key, value in log_entry.items():
                if isinstance(value, dict):
                    # Handle nested objects (like context)
                    sub_element = ET.SubElement(root, key)
                    for sub_key, sub_value in value.items():
                        sub_sub_element = ET.SubElement(sub_element, sub_key)
                        sub_sub_element.text = str(sub_value)
                elif isinstance(value, list):
                    # Handle arrays (like tags)
                    sub_element = ET.SubElement(root, key)
                    for item in value:
                        item_element = ET.SubElement(sub_element, "item")
                        item_element.text = str(item)
                else:
                    # Handle simple values
                    element = ET.SubElement(root, key)
                    element.text = str(value)
            
            # Convert to string with pretty formatting
            ET.indent(root, space="  ", level=0)
            return ET.tostring(root, encoding='unicode')
            
        except Exception as exc:
            raise OnexError(
                f"Failed to serialize log entry to XML: {str(exc)}",
                CoreErrorCode.INVALID_PARAMETER
            )

    def validate_dependencies(self) -> bool:
        """Validate that XML module is available."""
        try:
            import xml.etree.ElementTree
            return True
        except ImportError:
            return False

    def get_format_metadata(self) -> Dict[str, Any]:
        """Get metadata about XML format."""
        return {
            "format_name": "xml",
            "file_extensions": [".xml"],
            "mime_types": ["application/xml", "text/xml"],
            "description": "Extensible Markup Language - structured document format",
            "features": [
                "structured_data",
                "unicode_support",
                "nested_elements",
                "attributes",
                "namespaces"
            ],
            "use_cases": [
                "structured_logging",
                "document_storage",
                "configuration_files",
                "data_exchange"
            ],
            "output_characteristics": {
                "human_readable": True,
                "machine_parseable": True,
                "compact": False,
                "preserves_types": False
            }
        }
```

### Step 2: Package Configuration

Create a `pyproject.toml` for your plugin:

```toml
[tool.poetry]
name = "omnibase-logger-xml-plugin"
version = "1.0.0"
description = "XML format handler plugin for ONEX Logger Node"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = ">=3.11"
omnibase = ">=0.1.0"

[tool.poetry.plugins."omnibase.logger_format_handlers"]
xml_format = "my_plugin.xml_format_handler:XmlFormatHandler"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Step 3: Installation and Usage

1. **Install your plugin**:
   ```bash
   pip install omnibase-logger-xml-plugin
   ```

2. **Use the new format**:
   ```bash
   poetry run onex run logger_node --args='["--log-level", "info", "--message", "Hello World", "--output-format", "xml"]'
   ```

3. **Verify plugin discovery**:
   ```python
   from omnibase.nodes.logger_node.v1_0_0.registry.log_format_handler_registry import LogFormatHandlerRegistry
   
   registry = LogFormatHandlerRegistry()
   registry.register_all_handlers()
   
   print("Available formats:", list(registry.handled_formats()))
   # Should include 'xml' if plugin is installed
   ```

## Advanced Plugin Features

### Custom Dependencies

If your plugin requires external dependencies:

```python
@property
def requires_dependencies(self) -> List[str]:
    return ["lxml", "beautifulsoup4"]

def validate_dependencies(self) -> bool:
    try:
        import lxml
        import bs4
        return True
    except ImportError:
        return False
```

### Multiple Format Support

A single handler can support multiple formats:

```python
@property
def supported_formats(self) -> List[str]:
    return ["xml", "xhtml", "svg"]

def can_handle(self, format_name: str) -> bool:
    return format_name.lower() in ["xml", "xhtml", "svg"]
```

### Priority and Conflict Resolution

Set higher priority to override existing handlers:

```python
@property
def handler_priority(self) -> int:
    return 50  # Higher than default plugin priority (0)
```

## Testing Your Plugin

Create tests for your plugin:

```python
# test_xml_handler.py
import pytest
from my_plugin.xml_format_handler import XmlFormatHandler
from omnibase.nodes.logger_node.v1_0_0.models.state import LoggerInputState, LogLevel, OutputFormat

def test_xml_handler_basic_formatting():
    handler = XmlFormatHandler()
    
    input_state = LoggerInputState(
        version="1.0.0",
        log_level=LogLevel.INFO,
        message="Test message",
        output_format=OutputFormat.JSON  # Doesn't matter for handler
    )
    
    log_entry = {
        "timestamp": "2025-05-26T12:00:00Z",
        "level": "INFO",
        "message": "Test message",
        "logger": "test"
    }
    
    result = handler.format_log_entry(input_state, log_entry)
    
    # Verify XML structure
    assert "<log_entry>" in result
    assert "<message>Test message</message>" in result
    assert "<level>INFO</level>" in result

def test_xml_handler_metadata():
    handler = XmlFormatHandler()
    
    assert handler.handler_name == "xml_format_handler"
    assert handler.can_handle("xml")
    assert not handler.can_handle("json")
    assert handler.validate_dependencies()
    
    metadata = handler.get_format_metadata()
    assert metadata["format_name"] == "xml"
    assert "xml" in metadata["file_extensions"][0]
```

## Plugin Distribution

### PyPI Distribution

1. **Build your package**:
   ```bash
   poetry build
   ```

2. **Publish to PyPI**:
   ```bash
   poetry publish
   ```

3. **Install from PyPI**:
   ```bash
   pip install omnibase-logger-xml-plugin
   ```

### Local Development

For local development and testing:

```bash
# Install in development mode
pip install -e .

# Or with poetry
poetry install
```

## Best Practices

### 1. Error Handling
- Always use `OnexError` with appropriate error codes
- Validate inputs and dependencies
- Provide meaningful error messages

### 2. Performance
- Keep handlers stateless and thread-safe
- Minimize dependencies and import overhead
- Cache expensive operations when possible

### 3. Documentation
- Provide clear format metadata
- Document supported features and limitations
- Include usage examples

### 4. Testing
- Test with various input combinations
- Test dependency validation
- Test error conditions
- Include integration tests

### 5. Versioning
- Follow semantic versioning
- Document breaking changes
- Maintain backward compatibility when possible

## Plugin Registry

The logger node maintains a registry of all discovered plugins. You can inspect this at runtime:

```python
from omnibase.nodes.logger_node.v1_0_0.helpers.logger_engine import LoggerEngine

engine = LoggerEngine()
formats = engine.list_available_formats()

for format_name, info in formats.items():
    print(f"Format: {format_name}")
    print(f"  Handler: {info['handler_name']}")
    print(f"  Source: {info['source']}")
    print(f"  Priority: {info['priority']}")
    print(f"  Dependencies OK: {info['dependencies_available']}")
```

## Troubleshooting

### Plugin Not Discovered
1. Check entry point configuration in `pyproject.toml`
2. Verify plugin is installed in the same environment
3. Check for import errors in the handler class
4. Ensure handler implements all required protocol methods

### Handler Conflicts
1. Check handler priorities
2. Use `override=True` when registering
3. Verify format name uniqueness
4. Check registration source and order

### Dependency Issues
1. Implement proper dependency validation
2. Handle missing dependencies gracefully
3. Document required dependencies clearly
4. Consider optional dependencies for enhanced features

## Example Plugins

The ONEX ecosystem includes several example plugins:

- **XML Handler**: Formats logs as XML documents
- **HTML Handler**: Creates HTML log reports
- **SQLite Handler**: Stores logs in SQLite database
- **Elasticsearch Handler**: Sends logs to Elasticsearch

See the [ONEX Plugin Registry](https://github.com/omnibase/plugins) for more examples and community contributions.
