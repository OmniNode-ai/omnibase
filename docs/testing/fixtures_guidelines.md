<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: fixtures_guidelines.md
version: 1.0.0
uuid: 9a944f24-dc19-4cff-997f-c89f4ae47112
author: OmniNode Team
created_at: 2025-05-22T17:18:16.695087
last_modified_at: 2025-05-22T21:19:13.552205
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 67f86a7f953e5b1391204ac88c83af127dbe360aedfc04ddebc35a9961fa1e94
entrypoint: python@fixtures_guidelines.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.fixtures_guidelines
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX/OmniBase Fixture Guidelines

## Rationale: Hybrid Fixture Structure

ONEX/OmniBase uses a hybrid fixture structure to balance encapsulation, reusability, and scalability:
- **Central/shared fixtures:** `tests/fixtures/`, `tests/conftest.py` for protocol/model/common fixtures.
- **Node-local fixtures:** `src/omnibase/nodes/<node>/tests/fixtures/` for node-specific or custom cases.

**Rationale:**
- Central/shared fixtures promote DRY principles and consistency across the project.
- Node-local fixtures enable encapsulation, portability, and independent evolution of nodes.
- This structure supports both core maintainers and plugin/extension authors.

## Canonical Directory Structure and Naming (snake_case)

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

### File Naming Table

| Type         | Location                                      | Pattern                                      | Example                                      |
|--------------|-----------------------------------------------|----------------------------------------------|----------------------------------------------|
| Shared Py    | `tests/fixtures/`                             | `<scope>_fixture_<purpose>.py`               | `shared_fixture_mock_registry.py`            |
| Node Py      | `src/omnibase/nodes/<node>/tests/fixtures/`   | `<node>_fixture_<purpose>.py`                | `stamper_node_fixture_basic.py`              |
| Shared Data  | `tests/fixtures/data/`                        | `<scope>_data_<purpose>[_<variant>].yaml`    | `protocol_data_event_bus_invalid.json`        |
| Node Data    | `src/omnibase/nodes/<node>/tests/fixtures/data/` | `<node>_data_<purpose>[_<variant>].yaml` | `stamper_node_data_invalid_01.yaml`          |

- Use snake_case for all `<scope>`, `<node>`, `<purpose>`, and `<variant>` fields.
- Number or describe variants as needed for multiple related files.

## Example: Stamped Fixture/Data File

```yaml
# <node>_data_valid.yaml
---
# === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
schema_version: 0.1.0
name: <node>_data_valid.yaml
version: 1.0.0
uuid: 123e4567-e89b-12d3-a456-426614174000
created_at: 2025-06-10T12:00:00Z
last_modified_at: 2025-06-10T12:00:00Z
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

## FixtureLoaderProtocol (Minimal Interface)

```python
class FixtureLoaderProtocol(Protocol):
    def discover_fixtures(self) -> list[str]:
        """Return a list of available fixture names."""
    def load_fixture(self, name: str) -> object:
        """Load and return the fixture by name."""
```

## CI Linting for snake_case Compliance

- All fixture and data files must use snake_case naming.
- CI will lint for compliance and fail on violations.

## Versioning/Deprecation of Test Data Files

- When test data evolves, append a version or deprecation suffix (e.g., `_v2`, `_deprecated`).
- Remove or archive deprecated files as appropriate.

## Best Practices

- Always include a `.onex` metadata block in YAML/JSON fixture/data files.
- Keep node-local fixtures/data encapsulated unless sharing is required.
- Use the minimal interface for fixture loaders to support extensibility and plugin scenarios.
- Regularly audit for orphaned or unused fixtures/data (CI task recommended).
- Reference this document and node-specific `README.md` for canonical examples.

## Further Reading

- See node `README.md` for node-specific examples and directory structure.
- See `docs/nodes/structural_conventions.md` for node directory and file structure standards.
