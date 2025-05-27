<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: fixtures_guidelines.md
version: 1.0.0
uuid: 236427a6-29cb-4058-afaa-e7e8866697ca
author: OmniNode Team
created_at: 2025-05-27T07:41:21.581156
last_modified_at: 2025-05-27T17:26:51.925663
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 09e321870b16c734e1dc6383d631354eb2952f9b5bc298d58f202fa167d92141
entrypoint: python@fixtures_guidelines.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.fixtures_guidelines
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Testing Fixtures Guidelines

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Guidelines for organizing and managing test fixtures in the ONEX ecosystem  
> **Audience:** Developers, test engineers, node authors  

---

## Overview

ONEX uses a hybrid fixture structure to balance encapsulation, reusability, and scalability across the testing ecosystem. This document provides canonical guidelines for organizing, naming, and managing test fixtures and data files.

---

## Rationale: Hybrid Fixture Structure

ONEX uses a hybrid fixture structure to balance encapsulation, reusability, and scalability:

- **Central/shared fixtures:** `tests/fixtures/`, `tests/conftest.py` for protocol/model/common fixtures
- **Node-local fixtures:** `src/omnibase/nodes/<node>/tests/fixtures/` for node-specific or custom cases

**Benefits:**
- Central/shared fixtures promote DRY principles and consistency across the project
- Node-local fixtures enable encapsulation, portability, and independent evolution of nodes
- This structure supports both core maintainers and plugin/extension authors

---

## Canonical Directory Structure and Naming

All fixture files and directories must use `snake_case` naming conventions:

```
<repo-root>/
├── tests/
│   ├── fixtures/
│   │   ├── shared_fixture_mock_registry.py
│   │   ├── protocol_fixture_event_bus.py
│   │   └── data/
│   │       ├── shared_data_valid_node.yaml
│   │       └── protocol_data_event_bus_invalid.json
│   └── conftest.py
└── src/omnibase/nodes/<node>/
    ├── node.onex.yaml
    ├── src/
    │   └── ...
    └── tests/
        ├── test_main.py
        ├── fixtures/
        │   ├── <node>_fixture_basic.py
        │   ├── <node>_fixture_error_cases.py
        │   └── data/
        │       ├── <node>_data_valid.yaml
        │       ├── <node>_data_invalid_01.yaml
        │       └── <node>_data_edgecase_largefile.yaml
        └── ...
```

### File Naming Conventions

| Type         | Location                                      | Pattern                                      | Example                                      |
|--------------|-----------------------------------------------|----------------------------------------------|----------------------------------------------|
| Shared Py    | `tests/fixtures/`                             | `<scope>_fixture_<purpose>.py`               | `shared_fixture_mock_registry.py`            |
| Node Py      | `src/omnibase/nodes/<node>/tests/fixtures/`   | `<node>_fixture_<purpose>.py`                | `stamper_node_fixture_basic.py`              |
| Shared Data  | `tests/fixtures/data/`                        | `<scope>_data_<purpose>[_<variant>].yaml`    | `protocol_data_event_bus_invalid.json`        |
| Node Data    | `src/omnibase/nodes/<node>/tests/fixtures/data/` | `<node>_data_<purpose>[_<variant>].yaml` | `stamper_node_data_invalid_01.yaml`          |

**Naming Rules:**
- Use `snake_case` for all `<scope>`, `<node>`, `<purpose>`, and `<variant>` fields
- Number or describe variants as needed for multiple related files
- Be descriptive but concise in naming

---

## Fixture Data File Format

All fixture data files must include proper metadata blocks for consistency and traceability:

```yaml
# <node>_data_valid.yaml
---
# === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: ONEX Team
schema_version: 0.1.0
name: <node>_data_valid.yaml
version: 1.0.0
uuid: 123e4567-e89b-12d3-a456-426614174000
created_at: 2025-05-27T12:00:00Z
last_modified_at: 2025-05-27T12:00:00Z
description: Example valid input for <node> test
state_contract: state_contract://<node>_contract.yaml
lifecycle: active
hash: <TO_BE_COMPUTED>
entrypoint:
  type: testdata
  target: <node>_data_valid.yaml
namespace: omnibase.nodes.<node>.tests.fixtures.data
meta_type: testdata
# === /OmniNode:Metadata ===

file_path: "mock/path.yaml"
author: "TestUser"
expected_status: "success"
```

---

## Fixture Loader Protocol

For extensibility and consistency, fixture loaders should implement this minimal interface:

```python
from typing import Protocol

class FixtureLoaderProtocol(Protocol):
    def discover_fixtures(self) -> list[str]:
        """Return a list of available fixture names."""
        
    def load_fixture(self, name: str) -> object:
        """Load and return the fixture by name."""
```

This protocol enables:
- Consistent fixture discovery across different contexts
- Plugin and extension support
- Testing framework integration
- Dynamic fixture loading

---

## Versioning and Lifecycle Management

### Versioning Test Data Files

When test data evolves:
- Append a version or deprecation suffix (e.g., `_v2`, `_deprecated`)
- Maintain backward compatibility during transition periods
- Document changes in fixture metadata

### Deprecation Process

1. **Mark as deprecated**: Add `_deprecated` suffix to filename
2. **Update metadata**: Set `lifecycle: deprecated` in metadata block
3. **Grace period**: Maintain deprecated fixtures for at least 2 release cycles
4. **Removal**: Archive or remove deprecated files

### Example Versioning

```
<node>_data_valid.yaml           # Current version
<node>_data_valid_v1.yaml        # Previous version (archived)
<node>_data_invalid_deprecated.yaml  # Deprecated fixture
```

---

## Quality Standards

### CI Compliance

- **Naming compliance**: All fixture and data files must use `snake_case` naming
- **Metadata validation**: All YAML/JSON fixture files must have valid metadata blocks
- **Orphan detection**: CI will identify unused or orphaned fixtures
- **Coverage tracking**: Monitor fixture usage and coverage

### Best Practices

1. **Always include metadata**: Include `.onex` metadata block in YAML/JSON fixture/data files
2. **Encapsulation**: Keep node-local fixtures/data encapsulated unless sharing is required
3. **Minimal interfaces**: Use the minimal interface for fixture loaders to support extensibility
4. **Regular auditing**: Regularly audit for orphaned or unused fixtures/data
5. **Documentation**: Reference this document and node-specific `README.md` for examples

### Testing Standards

- **Isolation**: Fixtures should not depend on external state
- **Determinism**: Fixtures should produce consistent, reproducible results
- **Cleanup**: Fixtures should clean up any resources they create
- **Performance**: Large fixtures should be optimized for test execution speed

---

## Integration with ONEX Testing Framework

### Registry Swapping

Fixtures support registry swapping for isolated testing:

```python
@pytest.fixture
def mock_registry():
    """Provide a mock registry for testing."""
    return MockRegistry()

def test_with_mock_registry(mock_registry):
    # Test uses mock registry instead of real one
    pass
```

### Protocol Testing

Fixtures support protocol compliance testing:

```python
@pytest.fixture
def protocol_validator():
    """Provide protocol validator for testing."""
    return ProtocolValidator()

def test_protocol_compliance(protocol_validator, test_data):
    # Validate that implementation follows protocol
    assert protocol_validator.validate(test_data)
```

---

## Examples

### Shared Fixture Example

```python
# tests/fixtures/shared_fixture_mock_registry.py
import pytest
from omnibase.core.registry import Registry

@pytest.fixture
def mock_registry():
    """Provide a mock registry for testing."""
    registry = Registry()
    # Setup mock data
    return registry
```

### Node-Local Fixture Example

```python
# src/omnibase/nodes/stamper_node/tests/fixtures/stamper_node_fixture_basic.py
import pytest
from pathlib import Path

@pytest.fixture
def stamper_test_files():
    """Provide test files for stamper node testing."""
    return {
        'valid_yaml': Path(__file__).parent / 'data' / 'stamper_node_data_valid.yaml',
        'invalid_yaml': Path(__file__).parent / 'data' / 'stamper_node_data_invalid.yaml'
    }
```

---

## References

- [Testing Guide](../testing.md) - Overall testing philosophy and standards
- [Structured Testing](../structured_testing.md) - Protocol-driven testing framework
- [Node Development Guide](../nodes/developer_guide.md) - Node-specific testing patterns
- [Standards](../standards.md) - Naming conventions and code standards

---

**Note:** This fixture system is designed to scale with the ONEX ecosystem while maintaining consistency and quality across all testing scenarios.
