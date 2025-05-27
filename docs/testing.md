<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: testing.md
version: 1.0.0
uuid: 9db83ecd-00c6-440e-80f1-73929af13937
author: OmniNode Team
created_at: 2025-05-27T05:25:47.609104
last_modified_at: 2025-05-27T17:26:52.005710
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 977844217998295b602b57d43bc33b86d0ba51feb71bbc2d8585aca344ee18f9
entrypoint: python@testing.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.testing
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# OmniBase/ONEX Testing Philosophy and Practices

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the mandatory, canonical approach to testing within ONEX, emphasizing a markerless, registry-driven, fixture-injected, protocol-first testing system that enforces strict automation and discipline.

> **Node Testing Standard:**
> For all node-local tests, fixtures, and scaffolds, see the canonical [Node Testing Guidelines](./testing/node_testing_guidelines.md). This document defines required structure, conventions, and CI integration for ONEX nodes.

---

## Table of Contents

1. [Core Philosophy](#1-core-philosophy)
2. [Automation and Registry Discipline](#2-automation-and-registry-discipline)
3. [CI Tiers and Contexts](#3-ci-tiers-and-contexts)
4. [Canonical Patterns](#4-canonical-patterns)
5. [Test Output and Reporting](#5-test-output-and-reporting)
6. [Quick Start for New Contributors](#6-quick-start-for-new-contributors)

---

## 🚫 Mandatory Compliance

All contributors **must** adhere strictly to this document. Any pull request that deviates from these guidelines without explicit, justified exception comments will be rejected. This is non-negotiable.

---

## 1. Core Philosophy

### 1.1 Markerless, Registry-Driven, Fixture-Injected, Protocol-First Testing

#### No Unit/Integration Markers or Directory Categorization

- Tests **must never** be categorized as "unit" or "integration" by markers, decorators, or directory structure.
- **Markers are strictly reserved for fixture parameters to control CI context, and must never be used on test functions, classes, or directories for categorization.**
- The **only** distinction between test types is the *dependency context* provided by injected fixtures.
- Test code must be agnostic to dependency type; it must run identically regardless of whether dependencies are mock, integration, or future types.
- CI tiers and test selection are controlled exclusively by fixture parameter markers, never by test function or file markers.

> **Do/Don't Table: Marker Usage**
>
> | Allowed (Do)                                   | Forbidden (Don't)                                 |
> |------------------------------------------------|--------------------------------------------------|
> | Use `pytest.mark.mock` on fixture parameters   | Use `pytest.mark.mock` on test functions/classes  |
> | Use `pytest.mark.integration` on fixture params| Use any marker for test categorization in files   |
> | Use marker IDs for fixture parameter selection | Use directory names to indicate test type         |
> |                                               | Use markers for anything except fixture params    |

#### Registry-Driven Test Data and Test Case Discovery

- All test cases, fixtures, and data must be registered in central registries.
- Registration **must** be automated via decorators or import hooks whenever possible.
- Manual registry entry is permitted only as a temporary exception and must be documented explicitly with a `# TODO` comment referencing this policy.
- Registries must support introspection, filtering, and enumeration of test cases.
- This enables scalable, composable, and extensible test suites.

#### Fixture Injection Is Mandatory

- All test dependencies (e.g., registries, data providers) must be injected via pytest fixtures.
- Test functions **must not** instantiate or hardcode dependencies internally.
- Fixtures must be parameterized to provide different dependency contexts (e.g., mock, integration).
- Fixture parameters must be marked with the appropriate CI tier markers (`pytest.mark.mock`, `pytest.mark.integration`).

#### Protocol-First Testing

- Tests must validate *public protocol contracts* only.
- Protocols include JSON schemas, CLI argument/response formats, public API behaviors, and error types.
- Tests **must not** rely on or inspect internal implementation details or state.
- This ensures robustness and maintainability as implementations evolve.

### 1.2 Protocol-Driven, Fixture-Injectable Test Engines

Protocol-driven tools like the ONEX Metadata Stamper must expose all core logic via Python Protocols, enabling test engines to be swapped via fixture injection.

Example fixture for protocol-driven stamper:

```python
@pytest.fixture(params=[
    pytest.param("real", id="real", marks=pytest.mark.integration),
    pytest.param("in_memory", id="mock", marks=pytest.mark.mock),
    pytest.param("hybrid", id="hybrid", marks=pytest.mark.mock),
])
def stamper_engine(request):
    if request.param == "real":
        return RealStamperEngine()
    elif request.param == "in_memory":
        return InMemoryStamperEngine()
    elif request.param == "hybrid":
        return HybridStamperEngine()
    else:
        raise OnexError(f"Unknown engine: {request.param}", CoreErrorCode.INVALID_PARAMETER)
```

Tests must be context-agnostic and registry-driven:

```python
def test_stamp_valid_files(stamper_engine):
    files = ["valid1.yaml", "valid2.yaml"]
    result = stamper_engine.stamp(files, dry_run=True)
    assert all(r.status in (OnexStatus.SUCCESS, OnexStatus.WARNING) for r in result)
```

### 1.3 Testing Handler-Based Architectures

Handler-based architectures like the ONEX Metadata Stamper use a `FileTypeHandlerRegistry` to delegate stamping operations to appropriate handlers.

Tests must validate both the public protocol contract of each handler and the proper registration/delegation by the registry.

Example test for handler registration:

```python
def test_handler_registration(handler_registry):
    # Test that the registry contains handlers for all supported file types
    assert handler_registry.get_handler(Path("test.md")) is not None
    assert handler_registry.get_handler(Path("test.yaml")) is not None
    assert handler_registry.get_handler(Path("test.py")) is not None
    assert handler_registry.get_handler(Path("test.unsupported")) is None
```

### 1.4 Testing Idempotency

Idempotent operations like the ONEX Metadata Stamper's file stamping must be tested for idempotency.

Example test for stamper idempotency:

```python
def test_stamper_idempotency(stamper_engine, tmp_path):
    # Create a test file
    test_file = tmp_path / "test.yaml"
    test_file.write_text("content: value")
    
    # First stamp - should add metadata
    result1 = stamper_engine.stamp_file(test_file, write=True)
    assert result1.status == OnexStatus.SUCCESS
    content1 = test_file.read_text()
    
    # Second stamp - should not modify the file
    result2 = stamper_engine.stamp_file(test_file, write=True)
    assert result2.status == OnexStatus.SUCCESS
    content2 = test_file.read_text()
    
    # Contents should be identical - no microsecond-level churn
    assert content1 == content2
```

### 1.5 Testing Dry Run vs. Write Mode

Tools like the ONEX Metadata Stamper support both dry-run (default) and write modes.

Example test for dry-run vs. write modes:

```python
def test_dry_run_vs_write_mode(stamper_engine, tmp_path):
    # Create a test file
    test_file = tmp_path / "test.yaml"
    test_file.write_text("content: value")
    original_content = test_file.read_text()
    
    # Dry run mode (default) - should not modify the file
    result1 = stamper_engine.stamp_file(test_file)
    assert result1.status == OnexStatus.SUCCESS
    assert test_file.read_text() == original_content
    
    # Write mode - should modify the file
    result2 = stamper_engine.stamp_file(test_file, write=True)
    assert result2.status == OnexStatus.SUCCESS
    modified_content = test_file.read_text()
    assert modified_content != original_content
    assert "metadata_version" in modified_content
```

---

## 2. Automation and Registry Discipline

- Registries **must** be populated automatically via decorators or import hooks **wherever technically feasible**.
- Any manual registry population is a temporary exception and must be clearly documented with a `# TODO` comment referencing this policy.
- Test discovery, parametrization, and execution rely on these registries.
- Contributors must document any deviation or manual intervention with `# TODO` comments referencing this policy.

### 2.1 Temporary Exception Policy

- Manual registry entries are allowed for a maximum of one milestone unless a technical blocker is documented and reviewed.
- All exceptions must be listed in the issue tracker and referenced in code with a `# TODO` comment.
- The team must review and close exceptions as automation becomes feasible.

---

## 3. CI Tiers and Contexts

| Tier         | Context Type                   | Pytest Marker         | CI Trigger                        |
|--------------|-------------------------------|-----------------------|----------------------------------|
| mock         | In-memory, isolated            | `@pytest.mark.mock`   | Every PR, every commit            |
| integration  | Local service/container usage | `@pytest.mark.integration` | PRs + main branch merge        |
| external     | Deployed/live system APIs     | `@pytest.mark.external` | Scheduled/manual only (Future) |

Test runs **must** use CLI marker expressions to select contexts:

```bash
# Run all tests in all contexts
pytest

# Run only mock-tier tests (fast)
pytest -m "mock or (not integration and not external)"

# Run only integration-tier tests
pytest -m "integration"

# Run only external-tier tests (future)
pytest -m "external"
```

### 3.1 Dependency Injection via Fixtures

All tests must receive their dependencies via fixtures or parametrization. The canonical pattern:

```python
UNIT_CONTEXT = 1
INTEGRATION_CONTEXT = 2

@pytest.fixture(params=[
    pytest.param(UNIT_CONTEXT, id="unit", marks=pytest.mark.mock),
    pytest.param(INTEGRATION_CONTEXT, id="integration", marks=pytest.mark.integration),
])
def registry(request) -> ProtocolRegistry:
    """
    Canonical registry-swapping fixture for ONEX registry-driven tests.
    Context mapping:
      UNIT_CONTEXT = 1 (unit/mock context; in-memory, isolated)
      INTEGRATION_CONTEXT = 2 (integration/real context; real registry, disk-backed)
    """
    if request.param == UNIT_CONTEXT:
        return SchemaRegistry.load_mock()
    elif request.param == INTEGRATION_CONTEXT:
        return SchemaRegistry.load_from_disk()
    else:
        raise OnexError(f"Unknown registry context: {request.param}", CoreErrorCode.INVALID_PARAMETER)
```

---

## 4. Canonical Patterns

### 4.1 Test Case Registry Pattern

- All test case definitions for a given module must reside in a dedicated file (e.g., `core_test_registry_cases.py`).
- Use classes for test cases to allow for future setup/teardown, state, and extensibility.
- Each test case must be registered with a unique ID via a decorator.
- The registry is the single source of truth for all positive and negative test cases for that module.

### 4.2 Dependency Injection Fixture Pattern

```python
# tests/conftest.py

import pytest
from omnibase.protocol.protocol_testable_registry import ProtocolTestableRegistry
from omnibase.registry import MockRegistry, IntegrationRegistry

@pytest.fixture(params=[
    pytest.param("mock", id="mock_context", marks=pytest.mark.mock),
    pytest.param("integration", id="integration_context", marks=pytest.mark.integration),
])
def registry(request) -> ProtocolTestableRegistry:
    if request.param == "mock":
        return MockRegistry()
    elif request.param == "integration":
        return IntegrationRegistry()
    else:
        pytest.skip("Unsupported registry context")
```

---

## 5. Test Output and Reporting

- All test results must include clear status indicators (SUCCESS, WARNING, ERROR, FAILURE).
- Test IDs must be surfaced in pytest output and CI reporting for coverage and review.
- Failed tests must provide actionable error messages with context.

---

## 6. Quick Start for New Contributors

> **New to ONEX Testing? Start Here:**
> - Use only fixture parameter markers for CI context selection—never mark test functions or directories.
> - Register all test cases and fixtures using decorators/import hooks where possible. If you must register manually, add a `# TODO` and open an issue.
> - All test dependencies must be injected via pytest fixtures.
> - Tests must validate public protocol contracts only, not internal implementation details.
> - **A pre-push hook will automatically run the full test suite (`pytest`) before every `git push`. This ensures that no untested code is pushed to the repository. You can skip this check with `git push --no-verify` (not recommended).**

### Example Test Structure

```python
def test_example_functionality(registry, test_case):
    """Test example functionality using injected dependencies."""
    # Test logic here - context-agnostic
    result = registry.process(test_case.input)
    assert result.status == test_case.expected_status
    assert result.output == test_case.expected_output
```

---

## Contributing to Testing Documentation

1. Follow the patterns outlined in this document
2. Document any deviations with `# TODO` comments
3. Keep tests focused on public protocol contracts
4. Ensure all fixtures are properly parameterized for different contexts
5. Run `pre-commit run --all-files` before pushing

For more information, see the [Node Testing Guidelines](./testing/node_testing_guidelines.md).
