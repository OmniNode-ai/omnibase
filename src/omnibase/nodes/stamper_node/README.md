# Stamper Node

## Canonical Directory Structure

```
src/omnibase/nodes/stamper_node/
├── node.onex.yaml
├── src/
│   ├── main.py
│   └── helpers/
├── tests/
│   ├── test_main.py
│   ├── fixtures/
│   │   ├── stamper_node_fixture_basic.py
│   │   ├── stamper_node_fixture_error_cases.py
│   │   └── data/
│   │       ├── stamper_node_data_valid.yaml
│   │       ├── stamper_node_data_invalid_01.yaml
│   │       └── stamper_node_data_edgecase_largefile.yaml
│   └── ...
└── README.md
```

## File Naming Table (snake_case)

| Type         | Location                                      | Pattern                                      | Example                                      |
|--------------|-----------------------------------------------|----------------------------------------------|----------------------------------------------|
| Node Py      | `tests/fixtures/`                             | `stamper_node_fixture_<purpose>.py`          | `stamper_node_fixture_basic.py`              |
| Node Data    | `tests/fixtures/data/`                        | `stamper_node_data_<purpose>[_<variant>].yaml` | `stamper_node_data_invalid_01.yaml`          |

- Use snake_case for all `<purpose>` and `<variant>` fields.
- Number or describe variants as needed for multiple related files.

## Example: Stamped Fixture/Data File

```yaml
# stamper_node_data_valid.yaml
---
# === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
schema_version: 0.1.0
name: stamper_node_data_valid.yaml
version: 1.0.0
uuid: 123e4567-e89b-12d3-a456-426614174000
created_at: 2025-06-10T12:00:00Z
last_modified_at: 2025-06-10T12:00:00Z
description: Example valid input for stamper node test
state_contract: state_contract://stamper_node_contract.yaml
lifecycle: active
hash: <TO_BE_COMPUTED>
entrypoint:
  type: testdata
  target: stamper_node_data_valid.yaml
namespace: omnibase.nodes.stamper_node.tests.fixtures.data
meta_type: testdata
# === /OmniNode:Metadata ===

file_path: "mock/path.yaml"
author: "TestUser"
expected_status: "success"
```

## Hybrid Fixture Structure

- **Central/shared fixtures:** `tests/fixtures/`, `tests/conftest.py` for protocol/model/common fixtures.
- **Node-local fixtures:** `src/omnibase/nodes/stamper_node/tests/fixtures/` for node-specific or custom cases.
- **Rationale:** Supports both encapsulation and reusability across nodes while enabling scalable test design.

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

## Further Reading

- See `docs/testing/fixtures_guidelines.md` for full fixture strategy, naming conventions, and examples.
- See `docs/nodes/structural_conventions.md` for node directory and file structure standards. 