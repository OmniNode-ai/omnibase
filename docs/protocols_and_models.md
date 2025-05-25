<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: protocols_and_models.md
version: 1.0.0
uuid: ebc3a78c-08ff-427c-9e0e-c03198b28fc3
author: OmniNode Team
created_at: 2025-05-25T08:01:29.435398
last_modified_at: 2025-05-25T12:21:50.085718
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 2261502cb4358cee0efa205a08fe4094869272528343780dab5730cb333969f2
entrypoint: python@protocols_and_models.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.protocols_and_models
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Protocols and Models: Placement Guidelines and Governance

> **Status:** Canonical  
> **Last Updated:** 2025-05-25  
> **Purpose:** Comprehensive guide for protocol and model placement decisions, import patterns, and governance in the ONEX system.

## Overview

The ONEX system uses a carefully designed architecture that distinguishes between **shared protocols/models** (cross-cutting concerns) and **node-specific protocols/models** (local implementation details). This document provides definitive guidance on when components should be shared vs node-local, along with governance policies for maintaining this architecture.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Decision Matrix](#decision-matrix)
3. [Placement Guidelines](#placement-guidelines)
4. [Import Patterns](#import-patterns)
5. [Examples](#examples)
6. [Governance and Evolution](#governance-and-evolution)
7. [Migration Guidelines](#migration-guidelines)
8. [Enforcement](#enforcement)

## Core Principles

### 1. **Cross-Cutting vs Node-Specific**
- **Shared components** address concerns that span multiple nodes, tools, or external integrations
- **Node-specific components** address implementation details unique to a single node's functionality

### 2. **Protocol-First Design**
- All interfaces use `Protocol` for external contracts and plugin boundaries
- Use `ABC` only for internal inheritance patterns within shared components
- Protocols define contracts; implementations provide behavior

### 3. **Minimal Duplication**
- Eliminate actual code duplication (e.g., multiple `DummySchemaLoader` implementations)
- Allow conceptual duplication when components serve different purposes
- Consolidate only when there's genuine reuse potential

### 4. **Clear Ownership**
- Shared components have system-wide ownership and governance
- Node-specific components are owned by their respective node teams
- Clear boundaries prevent accidental coupling

## Decision Matrix

Use this matrix to determine whether a protocol or model should be shared or node-specific:

| Criteria | Shared | Node-Specific |
|----------|--------|---------------|
| **Usage Scope** | Used by 2+ nodes, CLI tools, or external plugins | Used only within a single node |
| **Interface Type** | Plugin boundaries, tool contracts, cross-node APIs | Internal node logic, state management |
| **Evolution Rate** | Stable, versioned, backward-compatible changes | Rapid iteration, node-specific requirements |
| **Testing Strategy** | Contract compliance, protocol conformance | Implementation details, business logic |
| **Dependencies** | Minimal, stable dependencies | Node-specific dependencies allowed |
| **Documentation** | Comprehensive, public API docs | Node-local documentation |

### Decision Examples

**✅ Should be Shared:**
- `ProtocolEventBus` - Used by multiple nodes for event communication
- `ProtocolFileTypeHandler` - Plugin boundary for file processing
- `OnexEvent` - Standard event model across the system
- `OnexResultModel` - Common result format for all operations

**✅ Should be Node-Specific:**
- `ProtocolOnextreeValidator` - Specific to tree generator node validation logic
- `StamperInputState` - Internal state model for stamper node
- `TreeGeneratorConstants` - Node-specific configuration and constants
- Node-specific error enums and status codes

## Placement Guidelines

### Shared Components

**Protocols:**
```
src/omnibase/protocol/
├── protocol_event_bus.py          # Event system contracts
├── protocol_file_type_handler.py  # File processing contracts
├── protocol_schema_loader.py      # Schema loading contracts
└── ...
```

**Models:**
```
src/omnibase/model/
├── model_onex_event.py            # Standard event model
├── model_onex_message_result.py   # Common result models
├── model_node_metadata.py         # Node metadata structures
└── ...
```

**Tests:**
```
tests/protocol/                    # Protocol compliance tests
tests/model/                       # Model validation tests
```

### Node-Specific Components

**Protocols:**
```
src/omnibase/nodes/{node_name}/v{version}/protocol/
├── protocol_specific_validator.py  # Node-specific validation
└── ...
```

**Models:**
```
src/omnibase/nodes/{node_name}/v{version}/models/
├── state.py                       # Node state models
├── constants.py                   # Node-specific constants
└── ...
```

**Tests:**
```
src/omnibase/nodes/{node_name}/v{version}/node_tests/
├── test_node_logic.py             # Node implementation tests
└── ...
```

## Import Patterns

### Canonical Import Patterns

**✅ Correct Shared Protocol Imports:**
```python
# From any location
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
```

**✅ Correct Node-Specific Imports:**
```python
# Only within the same node
from .protocol.protocol_onextree_validator import ProtocolOnextreeValidator
from .models.state import TreeGeneratorInputState
```

**✅ Correct Cross-Node Shared Usage:**
```python
# Node A using shared components
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.model.model_onex_message_result import OnexResultModel

# Node B using the same shared components
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.model.model_onex_message_result import OnexResultModel
```

### Anti-Patterns

**❌ Incorrect Cross-Node Imports:**
```python
# Node A importing Node B's specific protocols - FORBIDDEN
from omnibase.nodes.tree_generator_node.v1_0_0.protocol.protocol_onextree_validator import ProtocolOnextreeValidator

# CLI tool importing node-specific models - FORBIDDEN  
from omnibase.nodes.stamper_node.v1_0_0.models.state import StamperInputState
```

**❌ Incorrect Shared Component Duplication:**
```python
# Multiple implementations of the same concept - FORBIDDEN
# File 1: nodes/node_a/utils/dummy_loader.py
class DummySchemaLoader: ...

# File 2: nodes/node_b/mocks/dummy_loader.py  
class DummySchemaLoader: ...

# Should be: Single shared implementation in fixtures/mocks/
```

## Examples

### Example 1: Event Bus Protocol (Shared)

**Why Shared:**
- Used by multiple nodes for event communication
- Plugin boundary for event subscribers
- Standard contract across the system

**Location:** `src/omnibase/protocol/protocol_event_bus.py`

```python
from typing import Protocol
from omnibase.model.model_onex_event import OnexEvent

class ProtocolEventBus(Protocol):
    """Cross-cutting event communication contract."""
    
    def publish(self, event: OnexEvent) -> None:
        """Publish event to all subscribers."""
        ...
    
    def subscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        """Subscribe to events."""
        ...
```

### Example 2: Tree Validator Protocol (Node-Specific)

**Why Node-Specific:**
- Only used within tree generator node
- Highly specific to .onextree validation logic
- No reuse potential in other nodes

**Location:** `src/omnibase/nodes/tree_generator_node/v1_0_0/protocol/protocol_onextree_validator.py`

```python
from typing import Protocol
from pathlib import Path

class ProtocolOnextreeValidator(Protocol):
    """Tree generator specific validation contract."""
    
    def validate_onextree_structure(self, tree_data: dict) -> bool:
        """Validate .onextree file structure."""
        ...
    
    def check_path_consistency(self, root: Path, tree_data: dict) -> bool:
        """Check paths in tree match filesystem."""
        ...
```

### Example 3: Model Consolidation (Shared)

**Before (Duplicated):**
```python
# File 1: utils/utils_tests/dummy_schema_loader.py
class DummySchemaLoader:
    def load_schema(self, path: Path) -> dict:
        return {"dummy": "schema"}

# File 2: nodes/stamper_node/v1_0_0/node_tests/mocks/dummy_loader.py
class DummySchemaLoader:
    def load_schema(self, path: Path) -> dict:
        return {"dummy": "schema"}
```

**After (Consolidated):**
```python
# Single location: src/omnibase/fixtures/mocks/dummy_schema_loader.py
class DummySchemaLoader:
    """Canonical mock schema loader for testing."""
    
    def load_schema(self, path: Path) -> dict:
        return {"dummy": "schema"}

# Usage everywhere:
from omnibase.fixtures.mocks.dummy_schema_loader import DummySchemaLoader
```

## Governance and Evolution

### Shared Component Governance

**Ownership:**
- System architects own shared protocols and models
- Changes require architectural review
- Backward compatibility is mandatory

**Versioning:**
- Semantic versioning for all shared components
- Deprecation policy: 2 major versions minimum
- Migration guides for breaking changes

**Documentation:**
- Comprehensive API documentation required
- Usage examples and integration patterns
- Change logs with rationale

### Node-Specific Component Governance

**Ownership:**
- Node teams own their specific protocols and models
- Changes can be made independently
- No backward compatibility requirements

**Evolution:**
- Rapid iteration allowed
- Node-specific versioning
- Local documentation standards

### Promotion Process

**Node-Specific → Shared:**
1. Identify reuse potential across 2+ nodes
2. Architectural review and approval
3. Refactor to shared location with proper versioning
4. Update all imports and dependencies
5. Add comprehensive tests and documentation

**Shared → Node-Specific (Rare):**
1. Demonstrate lack of cross-cutting usage
2. Architectural review and deprecation plan
3. Move to appropriate node with version bump
4. Update imports and remove shared version

## Migration Guidelines

### Moving Components to Shared

1. **Assessment:**
   - Verify usage across multiple nodes
   - Ensure stable interface design
   - Check for conflicting implementations

2. **Implementation:**
   - Create shared version with proper metadata
   - Add comprehensive protocol compliance tests
   - Update all import statements
   - Remove duplicate implementations

3. **Validation:**
   - Run full test suite
   - Verify no functionality changes
   - Check import consistency

### Consolidating Duplicates

1. **Identification:**
   - Audit for identical or near-identical implementations
   - Check for naming conflicts
   - Assess merge feasibility

2. **Consolidation:**
   - Choose canonical implementation
   - Move to appropriate shared location
   - Update all references
   - Remove duplicates

3. **Testing:**
   - Ensure all previous functionality works
   - Add missing test coverage
   - Validate protocol compliance

## Enforcement

### Automated Checks

**Linting Rules:**
- Prevent cross-node protocol/model imports
- Enforce shared component import patterns
- Flag duplicate implementations

**CI Validation:**
- Protocol compliance testing
- Import pattern validation
- Shared component duplication detection

**Pre-commit Hooks:**
- Import pattern validation
- Protocol placement verification
- Documentation completeness checks

### Manual Review

**Code Review Checklist:**
- [ ] Appropriate placement (shared vs node-specific)
- [ ] Correct import patterns
- [ ] No inappropriate cross-node dependencies
- [ ] Proper documentation and tests
- [ ] Follows naming conventions

**Architectural Review:**
- Required for new shared protocols/models
- Required for promotion from node-specific to shared
- Required for breaking changes to shared components

### Violation Remediation

**Common Violations:**
1. Cross-node imports of node-specific components
2. Duplicate implementations of shared concepts
3. Inappropriate placement of protocols/models
4. Missing documentation or tests

**Remediation Process:**
1. Identify violation through automated checks or review
2. Assess impact and create remediation plan
3. Implement fixes following migration guidelines
4. Validate fixes through testing and review
5. Update documentation and governance as needed

---

## Summary

This governance model ensures that the ONEX system maintains clear architectural boundaries while enabling appropriate code reuse. By following these guidelines, we can:

- **Minimize duplication** without forcing inappropriate consolidation
- **Maintain clear ownership** and responsibility boundaries
- **Enable rapid iteration** where appropriate while ensuring stability where needed
- **Provide clear guidance** for developers on placement decisions
- **Enforce consistency** through automated tooling and review processes

The key is to balance the benefits of shared components (reuse, consistency, maintenance) with the benefits of node-specific components (flexibility, independence, rapid iteration) based on actual usage patterns and architectural needs.
