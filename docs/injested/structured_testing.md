# OmniBase Structured Testing, Tags, and Test Case Design

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

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

---

## Tags and Execution Filtering

Tags provide execution scope:

- `pre-commit`, `ci`, `regression`, `canary`
- Filters: `--tags`, `--exclude-tags`, `--lifecycle`

Lifecycle gates (`canary`, `stable`, `deprecated`) block or allow based on orchestrator stage.

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

> If you don’t test what you automate, you’re not automating—you’re gambling.