<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: node_testing_guidelines.md
version: 1.0.0
uuid: 384849dd-2c3a-4343-afd7-d961cc8cdad8
author: OmniNode Team
created_at: 2025-05-28T12:40:27.205575
last_modified_at: 2025-05-28T17:20:05.993281
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: cc013cd78d4db44b67451e60e5c13534f7dd5208673dcca7afce5d0c2a9d7e99
entrypoint: python@node_testing_guidelines.md
runtime_language_hint: python>=3.11
namespace: omnibase.stamped.node_testing_guidelines
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Node Testing Guidelines

This document defines the structure, conventions, and best practices for testing nodes in the OmniNode architecture.

## Canonical Directory Structure

Each node should include its own test directory colocated alongside the node implementation:

```
src/
  omnibase/
    nodes/
      stamper_node/
        node.py
        state_contract.yaml
        node.onex.yaml
        tests/
          __init__.py
          test_main.py
          fixtures/
            __init__.py
            sample_input.yaml
```

## Test Conventions
- Use **absolute imports** to ensure compatibility with pytest and avoid import ambiguity.
- Include `__init__.py` in all test and fixture directories to enforce module structure.
- Use the `@pytest.mark.node` decorator to clearly mark node-specific tests.
- Keep tests local to the node. Shared test utilities should be placed in `src/omnibase/testing/`.

## CLI and Contract Validation
Node tests should validate the following:
- Execution via `onex run <node>`
- Emission of `NODE_START`, `NODE_SUCCESS`, and `NODE_FAILURE` events
- Compliance with the declared `state_contract.yaml`
- Correct output `.onex` structure
- Validate that the node is executable via the `onex` CLI entrypoint (e.g., `onex run stamper_node`)

## Recommended Enhancements
- Add a `tests/node_runner.py` harness to programmatically execute any node for test validation.
- Use `.onextree` files to enforce test and fixture layout across all nodes. All node-local tests and fixtures must be explicitly listed in the node's `.onextree` file. CI will fail if unlisted test files are discovered.

## CI Integration
Example GitHub Actions step:
```yaml
- name: Run node tests
  run: pytest src/omnibase/nodes --tb=short -m node
```

## Documentation and Scaffold
- A test scaffold should be included with new node generation.
- All node test scaffolds must include:
  - `tests/test_main.py` with a working `@pytest.mark.node` stub
  - `tests/fixtures/sample_input.yaml` stamped with `.onex` metadata
  - Optional: `README.md` at the node root linking to test and coverage expectations

---

This structure supports long-term scalability and traceability across all ONEX-based nodes.

## Shared Utilities

Common fixtures or test utilities shared across nodes should live in:

```
src/
  omnibase/
    testing/
      __init__.py
      fixtures.py
      test_helpers.py
```

These modules must not import node-specific logic and should remain stable across major ONEX releases.
