<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:27.176822'
description: Stamped by ONEX
entrypoint: python://testing.md
hash: e6e9e50be70be82aa0c9b56412b6277551c881440d8575b8bf58c9528e900c5b
last_modified_at: '2025-05-29T11:50:15.362575+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: testing.md
namespace: omnibase.testing
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: 210b3bc3-48dc-41f4-9e19-3877161b5e70
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# OmniBase/ONEX Testing Philosophy and Practices

> **Status:** Canonical  
> **Last Updated:** 2025-05-21  
> **Purpose:** Define the mandatory, canonical approach to testing within ONEX/Milestone 0, emphasizing a markerless, registry-driven, fixture-injected, protocol-first testing system that enforces strict automation and discipline.

> **Node Testing Standard:**
> For all node-local tests, fixtures, and scaffolds, see the canonical [Node Testing Guidelines](./testing/node_testing_guidelines.md). This document defines required structure, conventions, and CI integration for ONEX nodes.

---

# Table of Contents

1. Core Philosophy: Markerless, Registry-Driven, Fixture-Injected, Protocol-First Testing
2. Automation and Registry Discipline
3. CI Tiers and Contexts
4. Canonical Patterns: Registry and Fixture Injection
5. Test Output and Reporting
6. Minimal Negative Test Policy (Stub)
7. Future Milestones (M1+): Stub Section
8. Cross-References
9. Testing Roadmap: Future Milestones and Advanced Features
10. Quick Start for New Contributors
11. Glossary
12. Amendment and Feedback Process
13. Canonical Signature
14. Pull Request Template Enforcement

---

## 🚫 No Excuses: Mandatory Compliance

All contributors **must** adhere strictly to this document. Any pull request that deviates from these guidelines without explicit, justified exception comments will be rejected. This is non-negotiable.

---

## 1. Core Philosophy: Markerless, Registry-Driven, Fixture-Injected, Protocol-First Testing

### 1.1 No Unit/Integration Markers or Directory Categorization

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

### 1.2 Registry-Driven Test Data and Test Case Discovery

- All test cases, fixtures, and data must be registered in central registries.
- Registration **must** be automated via decorators or import hooks whenever possible.
- Manual registry entry is permitted only as a temporary exception and must be documented explicitly with a `# TODO` comment referencing this policy.
- Registries must support introspection, filtering, and enumeration of test cases.
- This enables scalable, composable, and extensible test suites.
- **Stub nodes must always include all required fields as defined by the canonical Enum (`NodeMetadataField`), even at Milestone 0.**
- This prevents drift, ensures negative testing and schema validation are robust, and future-proofs the test suite.
- Optional fields may be omitted or set to None/empty unless required by downstream code or validation. Never let a missing optional field cause a failure for a consumer that expects "optional means optional."
- All project-specific errors must be defined in `core/errors.py` and used in stubs and negative tests. Do not use generic exceptions.
- See the code example below for a compliant stub node and error raising pattern.

### 1.3 Fixture Injection Is Mandatory

- All test dependencies (e.g., registries, data providers) must be injected via pytest fixtures.
- Test functions **must not** instantiate or hardcode dependencies internally.
- Fixtures must be parameterized to provide different dependency contexts (e.g., mock, integration).
- Fixture parameters must be marked with the appropriate CI tier markers (`pytest.mark.mock`, `pytest.mark.integration`, `pytest.mark.external` (stubbed for future)).

### 1.4 Protocol-First Testing

- Tests must validate *public protocol contracts* only.
- Protocols include JSON schemas, CLI argument/response formats, public API behaviors, and error types.
- Tests **must not** rely on or inspect internal implementation details or state.
- This ensures robustness and maintainability as implementations evolve.

### 1.5 Protocol-Driven, Fixture-Injectable Test Engines (e.g., Stamper)

- Protocol-driven tools like the ONEX Metadata Stamper must expose all core logic via Python Protocols, enabling test engines to be swapped via fixture injection.
- Test suites must validate only the public protocol contract, not internal implementation details.
- All test dependencies (e.g., file discovery, I/O, ignore pattern sources) must be injected via fixtures, supporting both real and in-memory/mock contexts.
- The protocol registry enables dynamic discovery and selection of test engines for different CI tiers or test scenarios.
- Example fixture for protocol-driven stamper with updated engine types:

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

- Tests must be context-agnostic and registry-driven:

```python
def test_stamp_valid_files(stamper_engine):
    files = ["valid1.yaml", "valid2.yaml"]
    result = stamper_engine.stamp(files, dry_run=True)
    assert all(r.status in (OnexStatus.SUCCESS, OnexStatus.WARNING) for r in result)
```

### 1.6 Testing Handler-Based Architectures (e.g., Stamper)

- Handler-based architectures like the ONEX Metadata Stamper use a `FileTypeHandlerRegistry` to delegate stamping operations to appropriate handlers.
- Tests must validate both the public protocol contract of each handler and the proper registration/delegation by the registry.
- Tests for handlers must verify that:
  - The handler correctly processes files of its supported type
  - The handler respects the protocol contract of its parent interface
  - The handler integrates correctly with its registry
  - The handler properly uses shared components (e.g., mixins)
- Example test for handler registration:

```python
def test_handler_registration(handler_registry):
    # Test that the registry contains handlers for all supported file types
    assert handler_registry.get_handler(Path("test.md")) is not None
    assert handler_registry.get_handler(Path("test.yaml")) is not None
    assert handler_registry.get_handler(Path("test.py")) is not None
    assert handler_registry.get_handler(Path("test.unsupported")) is None
```

### 1.7 Testing Idempotency

- Idempotent operations like the ONEX Metadata Stamper's file stamping must be tested for idempotency.
- Tests must verify that repeated application of the operation produces identical results.
- For stamping, this means verifying that:
  - Stamping an unstamped file adds metadata and computes hash correctly
  - Stamping an already-stamped file with no changes results in no modifications
  - Stamping an already-stamped file with content changes updates metadata appropriately
  - Hash and last_modified_at fields are only updated when necessary
- Example test for stamper idempotency:

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
    
    # Now modify the file content outside the metadata block
    current_content = test_file.read_text()
    modified_content = current_content.replace("content: value", "content: new_value")
    test_file.write_text(modified_content)
    
    # Third stamp - should update metadata
    result3 = stamper_engine.stamp_file(test_file, write=True)
    assert result3.status == OnexStatus.SUCCESS
    content3 = test_file.read_text()
    
    # Contents should be different from content2
    assert content3 != content2
```

### 1.8 Testing Dry Run vs. Write Mode

- Tools like the ONEX Metadata Stamper support both dry-run (default) and write modes.
- Tests must verify that:
  - Dry-run mode (default) shows what would change but does not modify files
  - Write mode actually modifies files as expected
  - Both modes return accurate results about what was or would be changed
- Example test for dry-run vs. write modes:

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

- See [docs/protocols.md](./protocols.md) and [docs/structured_testing.md](./structured_testing.md) for canonical registry and protocol patterns.

## Quick Start for New Contributors

> **New to ONEX Testing? Start Here:**
> - All stub nodes must include all required fields as defined by the canonical Enum (`NodeMetadataField`), even at Milestone 0.
> - All project-specific errors must be defined in `core/errors.py` and used in stubs and negative tests.
> - Use only fixture parameter markers for CI context selection—never mark test functions or directories.
> - Register all test cases and fixtures using decorators/import hooks where possible. If you must register manually, add a `# TODO` and open an issue.
> - See Section 4 for canonical code patterns.
> - If in doubt, ask for help or propose a clarification (see Amendment Process below).
> - **A pre-push hook will automatically run the full test suite (`pytest`) before every `git push`. This ensures that no untested code is pushed to the repository. You can skip this check with `git push --no-verify` (not recommended).**

---

## 2. Automation and Registry Discipline

- Registries **must** be populated automatically via decorators or import hooks **wherever technically feasible**.
- Any manual registry population is a temporary exception and must be clearly documented with a `# TODO` comment referencing this policy.
- If automation is not yet possible for a given test or fixture, contributors **must** document the limitation and may proceed with manual registration, but must also open an issue or note the limitation for future automation.
- Test discovery, parametrization, and execution rely on these registries.
- Contributors must document any deviation or manual intervention with `# TODO` comments referencing this policy.
- **Exception Process:** If a contributor encounters a scenario where automation is not possible, they must document the reason in the code and notify the team via the issue tracker or PR description. Reviewers must confirm the limitation is legitimate and temporary.

---

### 2.1 Registry Automation Roadmap

- **Milestone 0:** Manual registry population is permitted only with explicit `# TODO` and issue tracker entry. All manual entries must be tracked and reviewed in each milestone retro.
- **Milestone 1:** All registries must be automated via decorators/import hooks unless a technical blocker is documented and approved by the team.
- **Milestone 2+:** CI must fail if any manual registry entry remains without an open, approved exception.

---

### 2.2 Temporary Exception Policy

- Manual registry entries are allowed for a maximum of one milestone unless a technical blocker is documented and reviewed.
- All exceptions must be listed in the issue tracker and referenced in code with a `# TODO` comment.
- The team must review and close exceptions as automation becomes feasible.

---

## 3. CI Tiers and Contexts

| Tier         | Context Type                   | Pytest Marker         | CI Trigger                        |
|--------------|-------------------------------|-----------------------|----------------------------------|
| mock         | In-memory, isolated            | `@pytest.mark.mock`   | Every PR, every commit            |
| integration  | Local service/container usage | `@pytest.mark.integration` | PRs + main branch merge        |
| external     | Deployed/live system APIs     | `@pytest.mark.external` (stub) | Scheduled/manual only (Future) |

- Fixtures must parametrize over these contexts with the appropriate markers.
- Test runs **must** use CLI marker expressions to select contexts:

```bash
# Run all tests in all contexts
pytest

# Run only mock-tier tests (fast)
pytest -m "mock or (not integration and not external)"

# Run only integration-tier tests
pytest -m "integration"

# Run only external-tier tests (stub; no current tests)
pytest -m "external"
```

---

## 🔄 Dependency Injection via Fixtures (Refined)

All tests must receive their dependencies (e.g., registries) via fixtures or parametrization. The canonical pattern for context-driven, markerless testing is:

- Use integer context IDs for all fixture parameterization (e.g., `UNIT_CONTEXT = 1`, `INTEGRATION_CONTEXT = 2`).
- Use `pytest.param(..., id="unit", marks=pytest.mark.mock)` and `pytest.param(..., id="integration", marks=pytest.mark.integration)` for each context.
- "unit" is synonymous with "mock context" (in-memory, isolated); "integration" is synonymous with "real context" (disk-backed, service-backed, or real registry).
- IDs are for human-readable test output; markers are for CI tier filtering.
- The fixture must raise an `OnexError` if an unknown context is requested (future-proofing).

#### Example:
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
      INTEGRATION_CONTEXT = 2 (integration/real context; real registry, disk-backed, or service-backed)
    - "unit" is synonymous with "mock context" in this system.
    - "integration" is synonymous with "real context."
    - IDs are for human-readable test output; markers are for CI tier filtering.
    Returns:
        ProtocolRegistry: A SchemaRegistry instance in the appropriate context.
    Raises:
        OnexError: If an unknown context is requested (future-proofing).
    """
    if request.param == UNIT_CONTEXT:
        return SchemaRegistry.load_mock()
    elif request.param == INTEGRATION_CONTEXT:
        return SchemaRegistry.load_from_disk()
    else:
        raise OnexError(f"Unknown registry context: {request.param}", CoreErrorCode.INVALID_PARAMETER)
```

#### Context Mapping Table
| Context Name      | Param Value | ID (pytest output) | Marker (CI)         | Implementation                |
|------------------|-------------|--------------------|---------------------|-------------------------------|
| unit/mock        | 1           | unit               | pytest.mark.mock    | SchemaRegistry.load_mock()     |
| integration/real | 2           | integration        | pytest.mark.integration | SchemaRegistry.load_from_disk() |

---

## 4. Canonical Patterns: Test Case Registry and Dependency Injection Fixtures (Required)

### 4.1 Canonical Test Case Registry Pattern (Refined)

- All test case definitions for a given module (e.g., core registry) must reside in a dedicated, naming-compliant file (e.g., `core_test_registry_cases.py`).
- Use classes for test cases to allow for future setup/teardown, state, and extensibility. For ultra-simple cases, a function may be used, but classes are preferred for uniformity.
- **All field references must use the canonical Enum (e.g., `NodeMetadataField`) for type safety and maintainability. String-based field lists are forbidden.**
- The Enum must be kept in sync with the canonical Pydantic model. A dedicated test must assert Enum/model sync.
- Each test case must be registered with a unique ID via a decorator (e.g., `@register_core_registry_test_case("case_id")`).
- The registry (e.g., `CORE_REGISTRY_TEST_CASES`) is the single source of truth for all positive and negative test cases for that module.
- The test runner file (e.g., `test_registry.py`) must import the registry and parameterize over it, not define test cases directly.
- IDs must be surfaced in pytest output and CI reporting for coverage and review.
- This pattern is ready for plugin-based extension: the registry can be swapped or extended in future milestones without changing test logic.

#### Enum/Model Sync Enforcement
- If an Enum is used for field names, a dedicated test must assert that the Enum and the model fields are always in sync. This prevents drift and enforces type safety at the boundary.
- Example:
  ```python
  from omnibase.model.model_node_metadata import NodeMetadataBlock
  from omnibase.model.model_enum_metadata import NodeMetadataField

  def test_enum_matches_model():
      model_fields = set(NodeMetadataBlock.model_fields.keys())
      enum_fields = set(f.value for f in NodeMetadataField)
      assert model_fields == enum_fields
  ```

#### Example:

```python
# src/omnibase/model/model_enum_metadata.py
from enum import Enum

class NodeMetadataField(Enum):
    NODE_ID = "node_id"
    NODE_TYPE = "node_type"
    # ... all fields ...
    @classmethod
    def required(cls):
        return [cls.NODE_ID, cls.NODE_TYPE, ...]
    @classmethod
    def optional(cls):
        return [cls.DESCRIPTION, ...]

# tests/core/core_test_registry_cases.py
from omnibase.model.model_enum_metadata import NodeMetadataField

for field in NodeMetadataField.required() + NodeMetadataField.optional():
    assert field.value in node
```

### 4.2 Canonical Dependency Injection Fixture Pattern

- All test dependencies (e.g., registries, data providers) must be injected via pytest fixtures.
- Test functions **must not** instantiate or hardcode dependencies internally.
- Fixtures must be parameterized to provide different dependency contexts (e.g., mock, integration).
- Fixture parameters must be marked with the appropriate CI tier markers (`pytest.mark.mock`, `pytest.mark.integration`, `pytest.mark.external` (stubbed for future)).

```python
# tests/conftest.py

import pytest
from omnibase.protocol.protocol_testable_registry import ProtocolTestableRegistry
from omnibase.registry import MockRegistry, IntegrationRegistry

@pytest.fixture(params=[
    pytest.param("mock", id="mock_context", marks=pytest.mark.mock),
    pytest.param("integration", id="integration_context", marks=pytest.mark.integration),
    # pytest.param("external", id="external_context", marks=pytest.mark.external), # Stub for future
])
def registry(request) -> ProtocolTestableRegistry:
    if request.param == "mock":
        return MockRegistry()
    elif request.param == "integration":
        return IntegrationRegistry()
    else:
        pytest.skip("Unsupported registry context")
```

### 4.3 Canonical Test Example Using Injected Fixture and Registry-Driven Test Case

```

```

<!-- Test comment to trigger pre-commit -->
