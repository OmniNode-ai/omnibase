# OmniBase/ONEX Testing Philosophy and Practices

> **Status:** Canonical
> **Last Updated:** 2025-05-17
> **Purpose:** Define and document the project's approach to testing, emphasizing registry-driven, markerless test structure for maximum flexibility, maintainability, and clarity.

---

## 🧪 Testing Philosophy

OmniBase/ONEX does **not** distinguish between "unit" and "integration" tests using markers or directories. Instead, all tests are written to be agnostic to the type of dependencies (mock or real) they use. This approach:
- Encourages DRY, flexible, and maintainable test code
- Avoids marker drift and ambiguous test categorization
- Allows any test to run with any registry or dependency context

### Protocol-First Testing Principle

The guiding principle of testing in this project is "protocol-first" testing. Tests focus on validating the contracts and behaviors exposed by components rather than mocking or inspecting internal implementations. This ensures that tests remain robust and meaningful regardless of underlying changes, emphasizing conformance to expected protocols and schema contracts.

### What We Mean by "Protocol"

"Protocol," in this context, refers to any formalized interface contract including JSON schema structures, CLI argument/response formats, expected behaviors of public APIs, and defined error types. Tests should validate that these interfaces behave correctly, rather than relying on internal implementation details.

**Supersedes:** The previous checklist item for test marker structure (unit/integration) is replaced by this canonical approach.

---

## 🔄 Registry Swapping in Tests

All tests should receive their dependencies (e.g., registries) via fixtures or parametrization. This enables the same test logic to be exercised with different dependency types.

### Example: Fixture-Based Registry Injection
```python
import pytest

@pytest.fixture(params=["mock", "real"])
def registry(request):
    if request.param == "mock":
        return MockRegistry()
    elif request.param == "real":
        return RealRegistry()
    else:
        raise ValueError(f"Unknown registry type: {request.param}")

def test_node_behavior(registry):
    # Test logic here works with either mock or real registry
    ...
```

> Note: The registry fixture can be extended to load registries dynamically from `.tree` or `.onex` metadata files to support additional registry contexts.

### Adding New Registry Types
- Extend the fixture to support new registry implementations as needed.
- Avoid hardcoding registry logic in test bodies; centralize in fixtures/factories.

### Fixture Scalability

As the number of injectable dependencies grows (e.g., schema loader, lifecycle manager), prefer centralized fixture factories (e.g., `get_registry(name)`) or composition-based fixture utilities. Keep tests readable by isolating fixture complexity from test logic and centralizing registry construction in `conftest.py`.

---

## 🗂️ Test Structure

- All tests reside under the `tests/` directory, organized by module or feature (e.g., `tests/core/`, `tests/schema/`).
- Tests should be written to accept injected dependencies, not to construct them directly.
- No subdirectories or markers for "unit" or "integration".

### Canonical Pattern: Class-Based, Protocol-Aware Registry-Driven Tests

For all protocol-driven components (such as registries), tests **must** use a class-based structure named after the protocol/component under test (e.g., `class TestSchemaRegistry:`). Each test should be a method, and the registry fixture should be typed to the canonical test protocol (e.g., `ProtocolTestableRegistry`).

This pattern:
- Groups related tests for maintainability and discoverability
- Supports future extension (e.g., more protocols, shared setup)
- Keeps each test method atomic and focused
- Avoids stateful test classes and meta-programming
- Is compatible with pytest and ONEX/OmniBase registry-driven philosophy

#### Example: Canonical Registry-Driven Test
```python
import pytest
from omnibase.protocol.protocol_testable_registry import ProtocolTestableRegistry

class TestSchemaRegistry:
    def test_fixture_returns_testable_registry(self, registry: ProtocolTestableRegistry):
        assert isinstance(registry, ProtocolTestableRegistry)

    def test_get_node_returns_canonical_stub(self, registry: ProtocolTestableRegistry):
        node_id = "example_node_id"
        node_stub = registry.get_node(node_id)
        # ... field checks as required ...
```

> This is the required pattern for all new and existing registry-driven tests.

### Test Naming and Scope

While markers like `unit` and `integration` are not used, contributors may still name test files to suggest scope if helpful. For example:
- `test_registry_logic.py` for focused validation of internal logic
- `test_registry_system.py` for broad interaction flows

This is optional and not enforced by the test runner.

---

## ▶️ Running Tests

To run all tests:
```
pytest
```

To run tests with a specific registry type (if parametrized):
```
pytest -k mock
pytest -k real
```
Or use pytest's `-m` or `-k` options as appropriate for your fixture/parametrization setup.

---

## 🤖 CI Integration

- CI is configured to run all tests in all supported registry contexts (mock and real).
- Failures in any context are surfaced and must be addressed.
- No test selection is based on markers; all tests are run in all contexts.

---

## ⚠️ Edge Cases

- If a test requires only a specific registry type, use `pytest.skip` or fixture logic to skip as appropriate.
- Document such cases clearly in the test code.

---

## 🔮 Extensibility

- To add a new registry type, update the registry fixture and document the change here.
- If new test contexts (e.g., performance, fuzz) are added, extend this document and the fixture structure accordingly.

---

## 🧱 Registry Validation and Schema Contract Testing

Tests should be written to verify that components registered in the registry conform to ONEX schema contracts. This includes validating the structure, required fields, and constraints defined by schemas against live registry data. Such schema contract testing ensures that registry contents remain consistent and valid as the system evolves.

### Example: Schema Conformance Test

```python
from omnibase.schema import load_schema
from jsonschema import validate

class TestSchemaRegistry:
    def test_registry_node_conforms_to_schema(self, registry):
        node = registry.get_node("sample-node-id")
        schema = load_schema("onex_node.yaml")
        validate(instance=node.to_dict(), schema=schema)
```

---

## ❓ FAQ / Troubleshooting

**Q: Why aren't there unit/integration markers?**
A: The project philosophy is to maximize test flexibility and minimize categorization overhead. All tests should be able to run in any dependency context.

**Q: How do I add a new registry type?**
A: Update the registry fixture in your test suite and document the new type here.

**Q: How do I run only tests with real dependencies?**
A: Use pytest's `-k` option or adjust the fixture to select only the desired registry type.

**Q: How do I test schema conformance of a registry item?**
A: Use the schema validator against the live registry output or import the schema and run programmatic validation in your test.

**Q: What exactly qualifies as a "protocol" in protocol-first testing?**
A: Protocols include anything with a defined interface or contract, such as schemas, CLI argument formats, expected return structures, and error conventions.

---

## 🔗 Cross-References

- See [README.md](../README.md) for development and testing instructions.
- See [docs/milestones/milestone_0_bootstrap.md](milestones/milestone_0_bootstrap.md) for milestone context.

---

> This document is canonical. All contributors must follow these practices for all new and existing tests.