<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: README.md
version: 1.0.0
uuid: 8fdfcb12-f8e9-42a3-8000-a9248b8abdbe
author: OmniNode Team
created_at: '2025-05-28T12:40:27.495112'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://README
namespace: markdown://README
meta_type: tool

<!-- === /OmniNode:Metadata === -->
# Stamper Node

## Canonical Directory Structure

```
src/omnibase/nodes/stamper_node/
├── node.onex.yaml
├── node.py
├── helpers/
├── models/
├── tests/
│   ├── test_main.py
│   ├── fixtures/
│   │   ├── minimal_stamped_fixture.yaml
│   │   └── data/
│   └── ...
├── examples/
│   └── minimal_example.yaml
└── README.md
```

## File Naming Table (snake_case)

| Type         | Location                                      | Pattern                                      | Example                                      |
|--------------|-----------------------------------------------|----------------------------------------------|----------------------------------------------|
| Node Py      | `src/omnibase/nodes/stamper_node/`            | `node.py`                                    | `node.py`                                    |
| Node Data    | `tests/fixtures/`                             | `minimal_stamped_fixture.yaml`               | `minimal_stamped_fixture.yaml`               |
| Example      | `examples/`                                   | `minimal_example.yaml`                       | `minimal_example.yaml`                       |

- Use snake_case for all `<purpose>` and `<variant>` fields.
- Number or describe variants as needed for multiple related files.

## Example: Stamped Fixture/Data File

```yaml
# minimal_stamped_fixture.yaml
---
schema_version: "0.1.0"
name: "fixture_test_node"
version: "1.0.0"
uuid: "f1e2d3c4-5678-4abc-9def-abcdefabcdef"
author: "FixtureBot"
created_at: 2025-06-10T12:00:00Z
last_modified_at: 2025-06-10T12:00:00Z
description: "Test fixture for ONEX node stamping."
state_contract: "state_contract://stamper_node_contract.yaml"
lifecycle: "draft"
hash: "<TO_BE_COMPUTED>"
entrypoint:
  type: python
  target: src/omnibase/nodes/stamper_node/node.py
namespace: "omnibase.nodes.stamper_node.fixture"
meta_type: "tool"
runtime_language_hint: "python>=3.11"
tags: ["fixture", "test", "stamper"]
trust_score_stub:
  runs: 0
  failures: 0
  trust_score: 0.0
x-extensions: {}
protocols_supported: []
base_class: []
dependencies: []
environment: []
license: "Apache-2.0"
```

## Example: Minimal Node Example

```yaml
# minimal_example.yaml
---
schema_version: "0.1.0"
name: "example_node"
version: "1.0.0"
uuid: "e1d2c3b4-5678-4abc-9def-1234567890ef"
author: "ExampleUser"
created_at: 2025-06-10T12:00:00Z
last_modified_at: 2025-06-10T12:00:00Z
description: "Example ONEX node for stamping demonstration."
state_contract: "state_contract://stamper_node_contract.yaml"
lifecycle: "draft"
hash: "<TO_BE_COMPUTED>"
entrypoint:
  type: python
  target: src/omnibase/nodes/stamper_node/node.py
namespace: "omnibase.nodes.stamper_node.example"
meta_type: "tool"
runtime_language_hint: "python>=3.11"
tags: ["example", "stamper"]
trust_score_stub:
  runs: 0
  failures: 0
  trust_score: 0.0
x-extensions: {}
protocols_supported: []
base_class: []
dependencies: []
environment: []
license: "Apache-2.0"
```

## Usage Examples

### CLI

```sh
poetry run python -m omnibase.nodes.stamper_node.node --help
```

### Programmatic

```python
from omnibase.nodes.stamper_node.node import StamperNode
result = StamperNode().run(input_state)
```

## Schema References
- Node metadata: `node.onex.yaml`
- State contract: `stamper_node_contract.yaml`
- Minimal fixture: `tests/fixtures/minimal_stamped_fixture.yaml`
- Example: `examples/minimal_example.yaml`

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
