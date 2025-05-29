<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:26.848974'
description: Stamped by ONEX
entrypoint: python://conflict_resolution.md
hash: 24132d9578032ba5adfc1f4e32ae173f4f10fbb1f0212c7c700f88b5aba3cdd0
last_modified_at: '2025-05-29T11:50:15.200341+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: conflict_resolution.md
namespace: omnibase.conflict_resolution
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: d8bba054-1263-4bee-810d-5be3f05c4715
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# Plugin Priority and Conflict Resolution

> **Status:** Canonical
> **Last Updated:** 2025-05-25
> **Purpose:** Define priority rules and conflict resolution behavior for handlers and plugins in the ONEX ecosystem

## Overview

The ONEX handler registry implements a priority-based conflict resolution system to manage situations where multiple handlers can process the same file type or pattern. This document defines the rules, priorities, and behaviors for resolving conflicts between handlers from different sources.

## Priority Hierarchy

### Priority Levels

The system uses a four-tier priority hierarchy:

| Priority | Source | Description | Use Cases |
|----------|--------|-------------|-----------|
| **100** | Core | Essential system functionality | `.onexignore`, `.gitignore`, security handlers |
| **50** | Runtime | Standard ONEX ecosystem handlers | `.py`, `.md`, `.yaml`, `.json` |
| **10** | Node-Local | Node-specific functionality | Custom validation, specialized formats |
| **0** | Plugin | Third-party or experimental | Organization-specific, community extensions |

### Priority Assignment

```python
# Core handlers (Priority 100)
registry.register_special(".onexignore", IgnoreFileHandler(), source="core", priority=100)
registry.register_special(".gitignore", IgnoreFileHandler(), source="core", priority=100)

# Runtime handlers (Priority 50)
registry.register_handler(".py", PythonHandler(), source="runtime", priority=50)
registry.register_handler(".yaml", MetadataYAMLHandler(), source="runtime", priority=50)
registry.register_handler(".md", MarkdownHandler(), source="runtime", priority=50)

# Node-local handlers (Priority 10)
registry.register_handler(".custom", CustomHandler(), source="node-local", priority=10)

# Plugin handlers (Priority 0)
registry.register_handler("csv_processor", CSVHandler(), source="plugin", priority=0)
```

## Conflict Resolution Rules

### Basic Resolution

1. **Higher priority always wins**: A handler with priority 50 will override a handler with priority 10
2. **Equal priority, last registered wins**: Among handlers with the same priority, the most recently registered takes precedence
3. **Override flag bypasses priority**: Using `override=True` forces replacement regardless of priority

### Resolution Algorithm

```python
def resolve_conflict(existing_handler, new_handler):
    """
    Conflict resolution algorithm for handler registration.
    
    Returns True if new_handler should replace existing_handler.
    """
    # Override flag always wins
    if new_handler.override:
        return True
    
    # Higher priority wins
    if new_handler.priority > existing_handler.priority:
        return True
    
    # Equal priority, reject (with warning)
    if new_handler.priority == existing_handler.priority:
        log_warning("Handler conflict detected, keeping existing handler")
        return False
    
    # Lower priority loses
    return False
```

### Conflict Detection

The registry automatically detects conflicts when:

- Multiple handlers register for the same file extension (e.g., `.yaml`)
- Multiple handlers register for the same special filename (e.g., `.onexignore`)
- Multiple handlers register with the same name

## Load Order and Registration

### Standard Load Order

1. **Core handlers** - Registered first with highest priority
2. **Runtime handlers** - Registered second with medium priority
3. **Node-local handlers** - Registered when nodes are initialized
4. **Plugin handlers** - Discovered and registered last

### Registration Methods

```python
# Automatic registration (recommended)
registry.register_all_handlers()  # Loads core, runtime, and discovers plugins

# Manual registration
registry.register_handler(".ext", Handler(), source="runtime", priority=50)
registry.register_special("filename", Handler(), source="core", priority=100)
registry.register_node_local_handlers({".custom": CustomHandler()})
```

## Override Behavior

### When to Use Override

Use `override=True` in these scenarios:

1. **Replacing legacy handlers** during migration
2. **Testing scenarios** where you need specific handler behavior
3. **Emergency fixes** where a core handler needs replacement
4. **Development environments** for debugging purposes

### Override Examples

```python
# Replace a core handler (use with caution)
registry.register_handler(
    ".onexignore", 
    CustomIgnoreHandler(), 
    source="plugin", 
    priority=0, 
    override=True  # Forces replacement despite lower priority
)

# Replace runtime handler with node-local version
registry.register_handler(
    ".yaml", 
    CustomYAMLHandler(), 
    source="node-local", 
    priority=10, 
    override=True  # Replaces runtime handler
)
```

### Override Warnings

The system logs warnings when overrides occur:

```
WARNING: Overriding core handler for .onexignore with plugin handler (priority 0 -> 100)
WARNING: Overriding runtime handler for .yaml with node-local handler (priority 50 -> 10)
```

## Conflict Scenarios and Resolutions

### Scenario 1: Extension Conflict

**Situation**: Two handlers want to process `.csv` files

```python
# First registration
registry.register_handler(".csv", BasicCSVHandler(), source="runtime", priority=50)

# Second registration (conflict)
registry.register_handler(".csv", AdvancedCSVHandler(), source="plugin", priority=0)
```

**Resolution**: BasicCSVHandler wins (higher priority)
**Log**: `WARNING: Handler for extension .csv already registered with higher priority (50 >= 0)`

### Scenario 2: Same Priority Conflict

**Situation**: Two plugin handlers for the same extension

```python
# First registration
registry.register_handler(".xml", XMLHandler1(), source="plugin", priority=0)

# Second registration (same priority)
registry.register_handler(".xml", XMLHandler2(), source="plugin", priority=0)
```

**Resolution**: XMLHandler1 wins (first registered)
**Log**: `WARNING: Handler for extension .xml already registered with equal priority (0 >= 0)`

### Scenario 3: Override Scenario

**Situation**: Need to replace a runtime handler

```python
# Existing runtime handler
registry.register_handler(".json", StandardJSONHandler(), source="runtime", priority=50)

# Override with custom handler
registry.register_handler(
    ".json", 
    CustomJSONHandler(), 
    source="node-local", 
    priority=10, 
    override=True
)
```

**Resolution**: CustomJSONHandler wins (override=True)
**Log**: `INFO: Overriding runtime handler for .json with node-local handler`

### Scenario 4: Special Filename Conflict

**Situation**: Multiple handlers for `.gitignore`

```python
# Core handler (already registered)
registry.register_special(".gitignore", IgnoreFileHandler(), source="core", priority=100)

# Plugin attempts to override
registry.register_special(".gitignore", CustomGitHandler(), source="plugin", priority=0)
```

**Resolution**: IgnoreFileHandler wins (much higher priority)
**Log**: `WARNING: Special handler for .gitignore already registered with higher priority (100 >= 0)`

## Best Practices

### For Plugin Developers

1. **Use appropriate priorities**: Don't set artificially high priorities
2. **Avoid core conflicts**: Don't override core handlers unless absolutely necessary
3. **Document conflicts**: Clearly document any intentional overrides
4. **Test thoroughly**: Verify your handler works in conflict scenarios

```python
# Good: Appropriate priority for plugin
registry.register_handler(".myformat", MyFormatHandler(), source="plugin", priority=0)

# Avoid: Artificially high priority
registry.register_handler(".myformat", MyFormatHandler(), source="plugin", priority=99)
```

### For Node Developers

1. **Register conditionally**: Only register if handler_registry is provided
2. **Use node-local priority**: Stick to priority 10 for node-local handlers
3. **Handle gracefully**: Don't fail if registration is rejected
4. **Document handlers**: List custom handlers in node documentation

```python
def run_my_node(input_state, event_bus=None, handler_registry=None):
    if handler_registry:
        # Good: Conditional registration with appropriate priority
        handler_registry.register_handler(
            ".nodeformat", 
            NodeSpecificHandler(), 
            source="node-local", 
            priority=10
        )
    # Continue with node logic...
```

### For System Administrators

1. **Monitor conflicts**: Watch logs for conflict warnings
2. **Review overrides**: Audit any override=True usage
3. **Test combinations**: Verify handler combinations work correctly
4. **Document decisions**: Record any intentional priority changes

## Debugging Conflicts

### Listing All Handlers

```python
# Get comprehensive handler information
handlers = registry.list_handlers()

for handler_id, metadata in handlers.items():
    print(f"{handler_id}:")
    print(f"  Class: {metadata['handler_class']}")
    print(f"  Source: {metadata['source']}")
    print(f"  Priority: {metadata['priority']}")
    print(f"  Override: {metadata['override']}")
    print()
```

### Checking Specific Conflicts

```python
# Check what handles a specific file
handler = registry.get_handler(Path("myfile.csv"))
if handler:
    print(f"Handler: {handler.__class__.__name__}")
    print(f"Source: {handler.handler_name}")
else:
    print("No handler found")

# Check handled extensions
extensions = registry.handled_extensions()
print(f"Handled extensions: {extensions}")
```

### Logging Configuration

Enable debug logging to see detailed conflict resolution:

```python
import logging
logging.getLogger("omnibase.FileTypeHandlerRegistry").setLevel(logging.DEBUG)

# Now all registration attempts will be logged
registry.register_handler(".test", TestHandler(), source="plugin", priority=0)
```

## Migration and Compatibility

### Upgrading Handler Priorities

When upgrading the system, handler priorities may change:

```python
# Old system (no priorities)
registry.register_handler(".yaml", YAMLHandler())

# New system (with priorities)
registry.register_handler(".yaml", YAMLHandler(), source="runtime", priority=50)
```

### Backward Compatibility

The system maintains backward compatibility:

- Handlers registered without priority default to priority 0
- Handlers registered without source default to "unknown"
- Old registration methods continue to work

### Migration Script Example

```python
def migrate_handler_registrations(registry):
    """Migrate old handler registrations to new priority system."""
    
    # Get current handlers
    handlers = registry.list_handlers()
    
    # Identify handlers that need priority updates
    for handler_id, metadata in handlers.items():
        if metadata.get('priority', 0) == 0 and metadata.get('source') == 'unknown':
            # This is likely an old registration
            print(f"Consider updating {handler_id} with appropriate priority")
```

## Error Handling

### Registration Failures

The registry handles registration failures gracefully:

```python
try:
    registry.register_handler(".invalid", InvalidHandler(), source="plugin")
except Exception as e:
    # Registration continues, error is logged
    logger.error(f"Failed to register handler: {e}")
```

### Validation Failures

Invalid handlers are rejected during registration:

```python
# This will be rejected if handler doesn't implement required methods
registry.register_handler(".bad", IncompleteHandler(), source="plugin")
# Log: "Plugin handler bad_handler does not implement ProtocolFileTypeHandler. Skipping."
```

## Performance Considerations

### Registration Performance

- Handler registration is O(1) for lookups
- Conflict checking is O(1) per registration
- Plugin discovery is O(n) where n is the number of entry points

### Runtime Performance

- Handler lookup is O(1) for both extensions and special files
- No performance impact from priority system during normal operation
- Conflict resolution only occurs during registration, not during file processing

## Security Considerations

### Handler Validation

All handlers are validated before registration:

- Must implement required protocol methods
- Must provide required metadata properties
- Must pass basic instantiation test

### Override Security

Override functionality should be used carefully:

- Core handlers should rarely be overridden
- Monitor override usage in production
- Consider security implications of handler replacement

## Conclusion

The priority-based conflict resolution system provides a robust and predictable way to manage handler conflicts in the ONEX ecosystem. By following the established priority hierarchy and best practices, developers can create handlers that integrate seamlessly with the existing system while maintaining flexibility for customization and extension.

For questions or clarification on conflict resolution, consult the [Plugin & Handler Governance](../governance/plugin_handler_governance.md) document or reach out to the maintainer team.
