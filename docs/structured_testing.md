# OmniBase Structured Testing, Tags, and Test Case Design

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

> **Note:** This document is a technical reference for structured testing and test case design. It is closely related to the [Registry Spec](./registry.md), [Orchestration Spec](./orchestration.md), and [Error Handling Spec](./error_handling.md).

---

## Overview

OmniBase treats tests as first-class registry components. All test cases are declarative, taggable, and executable via orchestrators. They support fixture injection, result validation, and dependency resolution.

---

## Test Case Types

| Type         | Description                          |
|--------------|--------------------------------------|
| `unit`       | Component-level input/output test    |
| `integration`| Multi-step or pipeline-based checks  |
| `e2e`        | Full artifact lifecycle simulations  |
| `canary`     | High-frequency validators/tests      |
| `regression` | Linked to known issues or failures   |

---

## Test Case Metadata Block

See also: [Registry Spec](./registry.md) for canonical metadata fields.

```yaml
uuid: "test-uuid"
name: "test_fix_header_output"
type: "test"
tags: ["unit", "tool", "canary"]
entrypoint: "tests/test_fix_header.yaml"
version: "0.1.0"
expected_result: "pass"
test_type: "unit"
lifecycle: "canary"
dependencies:
  - id: "tool-fix_header"
    type: "tool"
    version_spec: ">=0.1.0"
  - id: "artifact-headerless"
    type: "data_artifact"
```

## Protocol-Driven, Fixture-Injectable Test Case Example (Stamper)

Protocol-driven tools like the ONEX Metadata Stamper require test cases that are context-agnostic and registry-driven. All test logic must validate only the public protocol contract, and all dependencies (e.g., file I/O, ignore patterns) must be injected via fixtures.

### Example: Registry-Driven Test Case for Stamper

```python
from omnibase.protocols import ProtocolStamperEngine

def test_stamp_valid_files(stamper_engine: ProtocolStamperEngine):
    files = ["valid1.yaml", "valid2.yaml"]
    result = stamper_engine.stamp(files, dry_run=True)
    assert all(r["status"] in ("success", "warning") for r in result)
```

- The `stamper_engine` fixture is parameterized to provide both real and in-memory/mock engines.
- Test cases are registered in the test registry and discovered dynamically.
- See [docs/testing.md](./testing.md) and [docs/protocols.md](./protocols.md) for registry and fixture-injection patterns.

---

## Declarative Test Structure (YAML)

```yaml
# test_fix_header.yaml
test_name: "Header fixer adds missing license"
input_artifact: "artifact-headerless"
tool_under_test: "tool-fix_header"
expected_output: "artifact-with-header"
expected_diff: true
assertions:
  - field: content
    contains: "Licensed under Apache"
```

---

## CLI Usage

```bash
omnibase test --tags unit --type test
omnibase test --uuid test-uuid
omnibase test --filter "lifecycle=canary,type=test"
```

Results conform to `TestResult` schema and include:

- Pass/fail
- Traceable UUIDs
- Messages
- Output diffs (if `--diff` enabled)

See also: [Error Handling Spec](./error_handling.md) for result and error models.

---

## Tags and Execution Filtering

Tags provide execution scope:

- `pre-commit`, `ci`, `regression`, `canary`
- Filters: `--tags`, `--exclude-tags`, `--lifecycle`

Lifecycle gates (`canary`, `stable`, `deprecated`) block or allow based on orchestrator stage. See [Orchestration Spec](./orchestration.md) for details.

---

## Result Model

```python
class TestResult(Result):
    status: Literal["pass", "fail", "skip"]
    diff: Optional[str]
    reason: Optional[str]
    artifact_refs: list[str]
```

---

## Planned Enhancements

- [ ] Test case lineage graphs
- [ ] Fixture generator DSL
- [ ] Visual test explorer UI
- [ ] Delta-only reexecution engine
- [ ] Test case mutation + robustness check mode

---

> If you don't test what you automate, you're not automating—you're gambling.

# ONEX v0.1 Canonical Test Registry Protocol

> **ONEX v0.1 Canonical Section**
> This section is canonical and supersedes any conflicting details below.

## ONEX Test Registry Protocol (v0.1)

### Overview

The ONEX Test Registry defines how individual test cases, test nodes, and fixtures are discovered, registered, and executed. All testable nodes must comply with this structure to be compatible with the ONEX CI, linting, and trust verification system.

---

### ✅ Test File Location

All node tests must be placed in:

```text
omnibase/src/nodes/{node_id}/test.py
```

For extended test scenarios, additional test files may follow:

```text
test_case_*.py
test_scenario_*.py
test_variant_*.py
```

These must be declared in `metadata.yaml`:

```yaml
auxiliary:
  test_cases:
    - test_case_fail_on_bad_input.py
    - test_variant_edge_case.py
```

---

### 🧠 Registration Protocol

Every valid test module must contain a `register()` function that populates a shared registry object, like so:

```python
def register(registry):
    registry.add("validator.check.namegen", validate_namegen_behavior)
```

This enables dynamic collection and batch execution.

---

### 📜 Metadata Requirements

Each test file must contain a metadata header matching the ONEX test schema. At minimum:

```yaml
metadata_version: 0.1
id: validator.check.namegen
category: validation
protocol: ONEX-Test-v0.1
```

> These values are parsed from the `metadata.yaml` inside the test node folder, or frontmatter if embedded.

---

### 🔎 Discovery and Execution

Tests are discovered via:

* `.tree` file entries under `nodes:`
* Static analysis of node folders with valid test metadata
* Registry lookups for `object_type: test`

---

### 🧪 Enforcement

* All test files must be individually executable
* Must not rely on global state or `conftest.py`-style shared config
* All test cases must assert against:

  * A known result format (e.g., `UnifiedResultModel`)
  * Or a documented schema + validation wrapper

---

### 🧩 CLI Integration

* `onex test --id validator.check.namegen`
* `onex test --all`
* `onex test --batch test_registry.yaml`
* `onex test --lint` (verifies schema + metadata + registration)

---

**Status:** Canonical protocol for test registration and discovery in ONEX.

---

# ONEX v0.1 Canonical Validator Protocol and Result Model

> **This section is canonical and supersedes any conflicting details below.**

## Validator Protocol
- All validators, tools, and fixtures must implement a Python Protocol (not ABC).
- Example:
```python
from typing import Protocol
from foundation.model.model_unified_result import UnifiedResultModel
class ValidatorProtocol(Protocol):
    def validate(self, data: Any) -> UnifiedResultModel:
        ...
```
- ABCs are reserved for infrastructure; business logic/testable components must be DI-compliant via Protocols.

## UnifiedResultModel (Required)
- Validators must return a UnifiedResultModel with structured status and message output.
- Example:
```python
UnifiedResultModel(
  status="error",
  messages=[
    OnexMessageModel(
      summary="Missing required metadata field: owner",
      level="error",
      type="error",
      file="metadata.yaml",
      line=12,
      details="The 'owner' field is required in all metadata blocks.",
      context={"validator": "MetadataBlockValidator"}
    )
  ]
)
```
- Direct string appends, positional messages, or raw print output are disallowed.

## Required Message Fields
| Field     | Type | Required | Description                  |
| --------- | ---- | -------- | ---------------------------- |
| `summary` | str  | ✅        | Short one-line summary       |
| `level`   | str  | ✅        | error, warning, info, etc.   |
| `type`    | str  | ⬜        | error, note, fixed, skipped  |
| `file`    | str  | ⬜        | File path (optional)         |
| `line`    | int  | ⬜        | Line number (optional)       |
| `details` | str  | ⬜        | Extended detail/context      |
| `context` | dict | ⬜        | Arbitrary structured context |

## Forbidden Patterns
- No ad hoc string errors
- No unstructured JSON or free-form result objects
- No mixing ABCs and Protocols for the same contract
- No global instantiation — all dependencies must be injected

## Registry and DI Compliance
- All validators must be registered with metadata, discoverable by ID, instantiable via DI constructor, and accept a logger via constructor.

## CLI Integration
- `onex validate --target metadata.yaml --validator metadata_block`
- `onex lint --include-result-model`

**Status:** This document locks the required interface and result pattern for all ONEX-compatible validators, test harnesses, and registry-registered tooling. 