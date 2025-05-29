<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode Team
created_at: '2025-05-28T12:40:26.887931'
description: Stamped by ONEX
entrypoint: python://plugin_discovery.md
hash: d59dfc0002d9c4d7038cf584a23134d15016a94a61c504aff3138a3c3e36aad4
last_modified_at: '2025-05-29T11:50:15.219765+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: plugin_discovery.md
namespace: omnibase.plugin_discovery
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: e6d21375-b318-4ee3-970c-e82b3b27b009
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# ONEX Plugin Discovery System

> **Status:** Canonical  
> **Last Updated:** 2025-01-01  
> **Purpose:** Complete guide to plugin discovery and loading in the ONEX system

## Overview

The ONEX plugin discovery system provides a unified way to discover and load plugins from multiple sources. It supports five plugin types and three discovery mechanisms, enabling flexible plugin management for different deployment scenarios.

## Plugin Types

The system supports the following plugin types:

| Type | Description | Entry Point Group | Environment Prefix |
|------|-------------|-------------------|-------------------|
| `handler` | File type handlers for metadata processing | `omnibase.handlers` | `ONEX_PLUGIN_HANDLER_` |
| `validator` | Validation plugins for custom checks | `omnibase.validators` | `ONEX_PLUGIN_VALIDATOR_` |
| `tool` | Tool plugins for extended functionality | `omnibase.tools` | `ONEX_PLUGIN_TOOL_` |
| `fixture` | Test fixture providers | `omnibase.fixtures` | `ONEX_PLUGIN_FIXTURE_` |
| `node` | Node plugins (for future M2 development) | `omnibase.nodes` | `ONEX_PLUGIN_NODE_` |

## Discovery Mechanisms

### 1. Entry Points (pyproject.toml/setup.cfg)

Entry points provide the most standard and portable way to register plugins. They are automatically discovered when packages are installed.

#### Configuration in pyproject.toml

```toml
[tool.poetry.plugins."omnibase.handlers"]
csv_handler = "my_package.handlers:CSVHandler"
xml_handler = "my_package.handlers:XMLHandler"

[tool.poetry.plugins."omnibase.validators"]
security_validator = "my_package.validators:SecurityValidator"

[tool.poetry.plugins."omnibase.tools"]
code_generator = "my_package.tools:CodeGenerator"
```

#### Configuration in setup.cfg

```ini
[options.entry_points]
omnibase.handlers =
    csv_handler = my_package.handlers:CSVHandler
    xml_handler = my_package.handlers:XMLHandler

omnibase.validators =
    security_validator = my_package.validators:SecurityValidator
```

**Priority:** 0 (lowest)  
**Use Case:** Standard plugin distribution via PyPI or internal package repositories

### 2. Configuration Files (plugin_registry.yaml)

Configuration files provide centralized plugin management with detailed metadata and priority control.

#### Default Configuration Locations

The system searches for configuration files in this order:
1. `plugin_registry.yaml` (current directory)
2. `~/.onex/plugin_registry.yaml` (user home)
3. `/etc/onex/plugin_registry.yaml` (system-wide)

#### Configuration Format

```yaml
# Plugin registry configuration
handlers:
  csv_processor:
    module: "omnibase.plugins.handlers.csv_handler"
    class: "CSVHandler"
    priority: 5
    description: "CSV file processor with metadata extraction"
    version: "1.0.0"
  
  xml_processor:
    module: "omnibase.plugins.handlers.xml_handler"
    class: "XMLHandler"
    priority: 5
    description: "XML file processor with schema validation"
    version: "1.0.0"

validators:
  security_validator:
    module: "omnibase.plugins.validators.security_validator"
    class: "SecurityValidator"
    priority: 8
    description: "Security validation for sensitive data detection"
    version: "1.0.0"

tools:
  code_generator:
    module: "omnibase.plugins.tools.code_generator"
    class: "CodeGenerator"
    priority: 5
    description: "Automated code generation tool"
    version: "1.0.0"

# Global plugin configuration
config:
  enabled_types:
    - handlers
    - validators
    - tools
    - fixtures
    - nodes
  
  loading:
    fail_fast: false
    timeout: 30
    validate_plugins: true
    verbose_logging: false
  
  security:
    allow_arbitrary_paths: false
    require_signatures: false
    trusted_sources:
      - "omnibase.plugins"
      - "omnibase.core"
```

**Priority:** 5 (medium)  
**Use Case:** Centralized plugin management, organizational plugin policies

### 3. Environment Variables

Environment variables provide the highest priority plugin registration, useful for runtime overrides and deployment-specific configurations.

#### Environment Variable Format

```bash
# Format: ONEX_PLUGIN_<TYPE>_<NAME>=module.path:ClassName
export ONEX_PLUGIN_HANDLER_CSV="my_package.handlers:CSVHandler"
export ONEX_PLUGIN_VALIDATOR_SECURITY="my_package.validators:SecurityValidator"
export ONEX_PLUGIN_TOOL_GENERATOR="my_package.tools:CodeGenerator"
```

**Priority:** 10 (highest)  
**Use Case:** Runtime overrides, deployment-specific configurations, testing

## Plugin Priority System

When multiple plugins are registered with the same name and type, the system uses priority to determine which plugin to load:

1. **Environment Variables:** Priority 10 (highest)
2. **Configuration Files:** Priority 5 (configurable)
3. **Entry Points:** Priority 0 (lowest)

Higher priority plugins replace lower priority ones. If priorities are equal, the first registered plugin is kept.

## Plugin Protocol

All plugins must implement the `PluginProtocol`:

```python
from typing import Protocol, Any

class PluginProtocol(Protocol):
    def bootstrap(self, registry: Any) -> None:
        """Bootstrap the plugin with the given registry."""
        ...
```

### Example Plugin Implementation

```python
from omnibase.core.core_plugin_loader import PluginProtocol

class MyCustomHandler(PluginProtocol):
    def __init__(self):
        self.name = "MyCustomHandler"
        self.version = "1.0.0"
    
    def bootstrap(self, registry: Any) -> None:
        """Bootstrap the plugin with the handler registry."""
        # Register file extensions this handler supports
        registry.register_handler(".custom", self)
        print(f"Bootstrapped {self.name} v{self.version}")
    
    def process_file(self, file_path: str) -> dict:
        """Process a custom file format."""
        # Implementation specific to this handler
        return {"status": "processed", "file": file_path}
```

## Using the Plugin System

### Basic Usage

```python
from omnibase.core.core_plugin_loader import (
    discover_plugins,
    load_plugin,
    bootstrap_plugins,
    get_plugin_loader,
    PluginType
)

# Discover all plugins from all sources
discover_plugins()

# Load a specific plugin
handler = load_plugin(PluginType.HANDLER, "csv_processor")

# Bootstrap all plugins of a type with a registry
bootstrap_plugins(PluginType.HANDLER, my_handler_registry)

# Get discovery report
loader = get_plugin_loader()
report = loader.get_discovery_report()
print(f"Found {report['total_plugins']} plugins")
```

### Advanced Usage

```python
from omnibase.core.core_plugin_loader import PluginLoader, PluginType

# Create a custom plugin loader
loader = PluginLoader()

# Discover from specific config file
loader.discover_config_file_plugins("/path/to/custom/config.yaml")

# Load all plugins of a specific type
handlers = loader.load_plugins_by_type(PluginType.HANDLER)

# Get detailed discovery report
report = loader.get_discovery_report()
for plugin_key, details in report["plugins"].items():
    print(f"{plugin_key}: {details['description']} (v{details['version']})")
```

## CLI Integration

The plugin system integrates with the ONEX CLI for plugin management:

```bash
# Discover and list all plugins
onex plugins list

# Get detailed information about a plugin
onex plugins info handler csv_processor

# Bootstrap plugins for a specific type
onex plugins bootstrap handlers

# Get plugin discovery report
onex plugins report
```

## Error Handling

The plugin system uses the centralized ONEX error handling:

```python
from omnibase.core.core_plugin_loader import PluginValidationError
from omnibase.core.error_codes import CoreErrorCode

try:
    plugin = load_plugin(PluginType.HANDLER, "nonexistent")
except PluginValidationError as e:
    print(f"Plugin error: {e}")
    print(f"Error code: {e.error_code}")
    exit_code = e.get_exit_code()
```

## Security Considerations

### Plugin Validation

- All plugins are validated to implement the required `bootstrap()` method
- Plugin loading can be configured to fail fast on validation errors
- Timeout protection prevents hanging during plugin loading

### Trusted Sources

Configure trusted plugin sources in `plugin_registry.yaml`:

```yaml
config:
  security:
    allow_arbitrary_paths: false
    trusted_sources:
      - "omnibase.plugins"
      - "my_organization.plugins"
```

### Plugin Signatures (Future)

The system is designed to support plugin signatures for enhanced security:

```yaml
config:
  security:
    require_signatures: true
```

## Testing Plugin Discovery

### Unit Tests

```python
import pytest
from omnibase.core.core_plugin_loader import PluginLoader, PluginType

def test_plugin_discovery():
    loader = PluginLoader()
    loader.discover_all_plugins()
    
    plugins = loader.registry.get_plugins_by_type(PluginType.HANDLER)
    assert len(plugins) > 0
    
    # Test specific plugin
    csv_handler = loader.registry.get_plugin(PluginType.HANDLER, "csv_processor")
    assert csv_handler is not None
    assert csv_handler.module_path == "omnibase.plugins.handlers.csv_handler"
```

### Integration Tests

```python
def test_plugin_loading_integration():
    from omnibase.core.core_plugin_loader import discover_plugins, load_plugin
    
    discover_plugins()
    plugin = load_plugin(PluginType.HANDLER, "csv_processor")
    
    assert plugin is not None
    assert hasattr(plugin, "bootstrap")
```

## Troubleshooting

### Common Issues

1. **Plugin Not Found**
   - Check plugin is properly registered in entry points, config file, or environment
   - Verify plugin name matches exactly (case-sensitive)
   - Check plugin type is correct

2. **Import Errors**
   - Ensure plugin module is in Python path
   - Verify module and class names are correct
   - Check for missing dependencies

3. **Bootstrap Failures**
   - Verify plugin implements `bootstrap()` method
   - Check registry parameter is correct type
   - Review plugin-specific error messages

### Debug Mode

Enable verbose logging for plugin discovery:

```python
import logging
logging.getLogger("omnibase.PluginLoader").setLevel(logging.DEBUG)
logging.getLogger("omnibase.PluginRegistry").setLevel(logging.DEBUG)
```

Or via configuration:

```yaml
config:
  loading:
    verbose_logging: true
```

## Best Practices

### Plugin Development

1. **Follow Naming Conventions**
   - Use descriptive plugin names
   - Follow Python package naming conventions
   - Include version information

2. **Implement Proper Error Handling**
   - Use ONEX error codes for consistency
   - Provide meaningful error messages
   - Handle bootstrap failures gracefully

3. **Documentation**
   - Include plugin description and version
   - Document plugin capabilities and requirements
   - Provide usage examples

### Plugin Deployment

1. **Use Entry Points for Distribution**
   - Standard mechanism for PyPI packages
   - Automatic discovery on installation
   - Version management via package manager

2. **Use Config Files for Organization**
   - Centralized plugin management
   - Priority control for plugin conflicts
   - Detailed metadata and descriptions

3. **Use Environment Variables for Overrides**
   - Runtime configuration changes
   - Testing with different plugins
   - Deployment-specific customizations

## Migration Guide

### From Manual Plugin Loading

If you're currently loading plugins manually:

```python
# Old approach
from my_package.handlers import CSVHandler
handler = CSVHandler()

# New approach
from omnibase.core.core_plugin_loader import load_plugin, PluginType
discover_plugins()
handler = load_plugin(PluginType.HANDLER, "csv_handler")
```

### Adding Plugin Discovery to Existing Code

1. **Register your plugins** using one of the three mechanisms
2. **Update imports** to use plugin loader
3. **Add plugin discovery** to your initialization code
4. **Update tests** to use plugin discovery patterns

## Future Enhancements

The plugin system is designed for extensibility:

- **Plugin Dependencies:** Support for plugin dependency resolution
- **Plugin Versioning:** Advanced version compatibility checking
- **Plugin Sandboxing:** Isolated plugin execution environments
- **Plugin Marketplace:** Discovery of community plugins
- **Hot Reloading:** Runtime plugin updates without restart

## References

- [Entry Points Documentation](./entry_points.md)
- [Plugin Conflict Resolution](./conflict_resolution.md)
- [ONEX Error Handling](../error_handling.md)
- [Testing Guidelines](../testing.md)
