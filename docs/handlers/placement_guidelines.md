<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: placement_guidelines.md
version: 1.0.0
uuid: 4360d7f8-237a-4d8e-9c41-e5434f1794b3
author: OmniNode Team
created_at: 2025-05-27T07:36:21.825913
last_modified_at: 2025-05-27T17:26:51.822188
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 8b4135defddd94cbf897348d6f56e49e48f9717a13ba0c425ef1852b8a0c8a3a
entrypoint: python@placement_guidelines.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.placement_guidelines
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Handler Placement Guidelines

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Provide clear guidelines for determining where handlers should be placed in the ONEX codebase  
> **Audience:** Contributors, maintainers, handler developers  

---

## Overview

This document provides specific guidance for determining the appropriate placement of handlers in the ONEX ecosystem. Use this decision matrix to determine whether a handler belongs in core, runtime, node-local, or plugin locations.

---

## Decision Matrix

### Step 1: Criticality Assessment

**Is this handler critical for ONEX system operation?**

- **YES** → Consider Core Handler (Priority 100)
- **NO** → Continue to Step 2

**Critical handlers include:**
- System configuration processors (`.onexignore`, `.gitignore`)
- Security-related file handlers
- Core metadata processors
- Essential system utilities

### Step 2: Scope Assessment

**Is this handler used across multiple nodes and contexts?**

- **YES** → Consider Runtime Handler (Priority 50)
- **NO** → Continue to Step 3

**Cross-cutting handlers include:**
- Common file type processors (`.py`, `.md`, `.yaml`)
- Standard format handlers
- Widely-used utility processors

### Step 3: Ownership Assessment

**Is this handler specific to a particular node's functionality?**

- **YES** → Consider Node-Local Handler (Priority 10)
- **NO** → Consider Plugin Handler (Priority 0)

**Node-specific handlers include:**
- Custom validation logic for node inputs
- Node-specific file format processors
- Specialized transformation handlers

### Step 4: External Dependencies

**Does this handler have external dependencies or experimental features?**

- **YES** → Plugin Handler (Priority 0)
- **NO** → Review previous steps

---

## Placement Categories

### Core Handlers (`src/omnibase/handlers/`)

**Criteria:**
- ✅ Critical for system operation
- ✅ No external dependencies (standard library only)
- ✅ Stable, well-tested functionality
- ✅ Security or performance critical
- ✅ Used across multiple contexts

**Examples:**
```
src/omnibase/handlers/
├── handler_ignore.py          # .onexignore/.gitignore processing
├── handler_system_config.py   # System configuration files
└── handler_security.py        # Security-related processing
```

**Review Requirements:**
- Architectural review required
- Security review mandatory
- Performance impact assessment
- >95% test coverage
- Comprehensive documentation

### Runtime Handlers (`src/omnibase/runtimes/onex_runtime/v1_0_0/handlers/`)

**Criteria:**
- ✅ Common file types in ONEX ecosystem
- ✅ Broad applicability across nodes
- ✅ Stable, production-ready
- ✅ Minimal external dependencies
- ❌ Not critical for system operation

**Examples:**
```
src/omnibase/runtimes/onex_runtime/v1_0_0/handlers/
├── handler_python.py          # Python file processing
├── handler_markdown.py        # Markdown file processing
├── handler_metadata_yaml.py   # YAML metadata processing
└── handler_json.py            # JSON file processing
```

**Review Requirements:**
- Code review by 2+ maintainers
- >90% test coverage
- Performance benchmarking
- Integration test validation
- Usage examples

### Node-Local Handlers (`src/omnibase/nodes/{node_name}/v{version}/handlers/`)

**Criteria:**
- ✅ Specific to particular node
- ✅ Limited reusability
- ✅ Experimental or specialized
- ❌ Not broadly applicable
- ❌ Not critical for system operation

**Examples:**
```
src/omnibase/nodes/stamper_node/v1_0_0/handlers/
├── handler_custom_format.py   # Node-specific format
└── handler_validation.py      # Custom validation logic

src/omnibase/nodes/tree_generator_node/v1_0_0/handlers/
├── handler_directory_tree.py  # Directory structure processing
└── handler_manifest.py        # Manifest file processing
```

**Review Requirements:**
- Code review by 1+ maintainer
- >80% test coverage
- Node-specific documentation
- No conflicts with existing handlers

### Plugin Handlers (External packages)

**Criteria:**
- ✅ Third-party or experimental
- ✅ External dependencies allowed
- ✅ Optional functionality
- ✅ Community or organization-specific
- ❌ Not part of core ONEX

**Examples:**
```
# External package structure
my_onex_plugin/
├── setup.py                   # Entry point configuration
├── my_plugin/
│   ├── handlers/
│   │   ├── handler_custom.py  # Custom format handler
│   │   └── handler_org.py     # Organization-specific handler
│   └── __init__.py
└── README.md                  # Installation and usage
```

**Entry Point Configuration:**
```toml
[project.entry-points."omnibase.handlers"]
custom_format = "my_plugin.handlers:CustomFormatHandler"
org_specific = "my_plugin.handlers:OrgSpecificHandler"
```

**Review Requirements:**
- Plugin package review
- Entry point validation
- Security review for dependencies
- Installation documentation

---

## Decision Examples

### Example 1: CSV File Handler

**Question:** Where should a CSV file handler be placed?

**Analysis:**
- Critical for system? **NO** (not essential for ONEX operation)
- Used across nodes? **YES** (many nodes might process CSV files)
- External dependencies? **NO** (can use standard library `csv` module)

**Decision:** Runtime Handler (`src/omnibase/runtimes/onex_runtime/v1_0_0/handlers/handler_csv.py`)

### Example 2: Database Connection Handler

**Question:** Where should a database connection handler be placed?

**Analysis:**
- Critical for system? **NO** (not essential for ONEX operation)
- Used across nodes? **MAYBE** (depends on specific use case)
- External dependencies? **YES** (requires database drivers)
- Experimental? **YES** (database integration is not core ONEX functionality)

**Decision:** Plugin Handler (external package with entry points)

### Example 3: Node-Specific Configuration Handler

**Question:** Where should a handler for a node's custom configuration format be placed?

**Analysis:**
- Critical for system? **NO**
- Used across nodes? **NO** (specific to one node)
- Node-specific? **YES**

**Decision:** Node-Local Handler (`src/omnibase/nodes/{node_name}/v{version}/handlers/`)

### Example 4: Security Certificate Handler

**Question:** Where should a handler for processing security certificates be placed?

**Analysis:**
- Critical for system? **YES** (security-critical functionality)
- Used across nodes? **YES** (security is cross-cutting)
- External dependencies? **NO** (can use standard library `ssl`, `cryptography`)
- Stable? **YES** (security requirements are well-established)

**Decision:** Core Handler (`src/omnibase/handlers/handler_security_cert.py`)

---

## Migration Guidelines

### Moving Handlers Between Categories

**From Node-Local to Runtime:**
1. Verify broad applicability
2. Remove node-specific dependencies
3. Add comprehensive tests
4. Update documentation
5. Coordinate with affected nodes

**From Runtime to Core:**
1. Justify criticality for system operation
2. Ensure no external dependencies
3. Security and performance review
4. Architectural review
5. Update priority and placement

**From Core/Runtime to Plugin:**
1. Identify external dependencies
2. Create plugin package structure
3. Configure entry points
4. Provide migration guide
5. Deprecation notice in core/runtime

### Deprecation Process

**Steps:**
1. **Notice:** Add deprecation warnings
2. **Documentation:** Update placement guidelines
3. **Migration:** Provide migration tools/guides
4. **Grace Period:** Minimum 2 release cycles
5. **Removal:** Remove from original location

---

## Best Practices

### Avoiding Conflicts

**Strategies:**
- Use specific file patterns when possible
- Check existing handlers before implementation
- Document known conflicts and resolutions
- Provide clear error messages for conflicts

**Example Conflict Resolution:**
```python
# Good: Specific pattern
class SpecialYamlHandler:
    def can_handle(self, path: Path, content: str) -> bool:
        return path.suffix == '.yaml' and 'special_marker' in content

# Avoid: Overly broad pattern
class GenericYamlHandler:
    def can_handle(self, path: Path, content: str) -> bool:
        return path.suffix == '.yaml'  # Too broad, conflicts likely
```

### Documentation Requirements

**All Handlers Must Document:**
- Purpose and scope
- Supported file types/patterns
- Configuration options
- Usage examples
- Performance characteristics
- Known limitations
- Conflict resolution

### Testing Requirements

**Test Categories:**
- Unit tests for handler logic
- Integration tests with registry
- Performance tests for large files
- Conflict resolution tests
- Error handling tests

---

## Conclusion

These placement guidelines ensure that handlers are organized logically, avoid conflicts, and maintain appropriate separation of concerns. When in doubt, start with a more specific placement (node-local or plugin) and migrate to broader placement (runtime or core) as the handler proves its value and stability.

For questions or clarification on handler placement, consult the [Plugin & Handler Governance](../governance/plugin_handler_governance.md) document or reach out to the maintainer team.

---

## References

- [Plugin & Handler Governance](../governance/plugin_handler_governance.md)
- [Handler Protocols](../reference-handlers-protocol.md)
- [Handler Registry](../reference-handlers-registry.md)
- [Handler Implementation](../guide-handlers-implementation.md)
- [Contributing Guidelines](../contributing.md)
- [Security Overview](../reference-security-overview.md)

---

**Note:** These guidelines help maintain a clean, organized handler ecosystem while providing flexibility for different use cases and development patterns.
