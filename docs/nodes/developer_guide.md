<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: developer_guide.md
version: 1.0.0
uuid: 6241b093-5915-4c59-9792-2cca50f9fdff
author: OmniNode Team
created_at: 2025-05-22T14:03:21.845800
last_modified_at: 2025-05-22T21:19:13.437045
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 2fa97f36ac7a463ecf82192ceb1d9ed3ce2e23c346310ec8b1cecf848d9e5a69
entrypoint: python@developer_guide.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.developer_guide
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Developer Guide: Development Conventions & Best Practices

> **Status:** Canonical Draft
> **Last Updated:** 2025-05-18
> **Purpose:** Define standard testing philosophy, process guidelines, and contribution best practices for OmniBase/ONEX.
> **Audience:** All ONEX contributors
> **Series:** Node Architecture
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting documentation.

---

## 📄 Canonical Testing Philosophy

> This section provides canonical guidance on test structure, dependency handling, and test philosophy within the `tests/` directory.

### Test Structure & Organization

OmniBase/ONEX follows a specific approach to testing that emphasizes:

1. **Directory Structure Mirroring:** The `tests/` directory structure mirrors `src/omnibase/` modules.
2. **No Test Markers:** Tests are organized by directory structure, not by markers.
3. **Registry Swapping:** Tests use registry fixtures that can swap between mock and real implementations.
4. **Contract Testing:** Tests focus on verifying that implementations fulfill their protocol contracts.

### Registry Swapping in Tests

```python
import pytest
from omnibase.core.registry import SchemaRegistry # Import the concrete registry stub

@pytest.fixture(params=["mock", "real"])
def registry(request):
    """
    Pytest fixture to swap between mock and real registry implementations.
    In M0, this uses the minimal SchemaRegistry stub and its load_mock/load_from_disk stubs.
    In M1+, this will use the fully implemented SchemaRegistry.
    """
    if request.param == "mock":
        # In M0, this calls the SchemaRegistry.load_mock() stub
        return SchemaRegistry.load_mock()
    # In M0, this calls the SchemaRegistry.load_from_disk() stub
    return SchemaRegistry.load_from_disk()

# Example test using the fixture:
def test_node_lookup_behavior(registry):
    # Test logic here works with either mock or real registry
    # In M0, this test will hit the SchemaRegistry.get_node() stub
    node_stub = registry.get_node("example_node_id")
    assert node_stub.get("stub") is True # Verify stub behavior
```

---

## 🧭 Tool vs Utility Definitions (Explanation)

A clear distinction is made between modules intended as CLI entrypoints (Tools) and modules providing reusable internal logic (Utilities). Adhering to these conventions is crucial for code organization and discoverability.

| Type    | Directory               | Naming Convention | Purpose                                       |
|---------|------------------------|-------------------|-----------------------------------------------|
| Tool    | `src/omnibase/tools/`  | `cli_*.py`        | Exposed CLI interfaces (e.g., `onex validate`)|
| Utility | `src/omnibase/utils/`  | `utils_*.py`      | Shared internal logic, not exposed via CLI    |

CLI entry points (`cli_main.py`) in `src/omnibase/tools/` route commands to specific tool modules (`cli_validate.py`, `cli_stamp.py`). Utility modules in `src/omnibase/utils/` should be importable and contain functions or classes for shared tasks like URI parsing, hashing, error handling helpers, etc.

---

## 🔧 CLI Naming Rules (Explanation)

Consistent naming for CLI-facing components ensures discoverability and predictability within the `onex` command space.

- All CLI-facing scripts must use `cli_` prefix (e.g., `cli_validate.py`, `cli_stamp.py`) in the `src/omnibase/tools/` directory.
- `cli_main.py` must serve as the primary entry point, routing subcommands under the main `onex` executable defined in `pyproject.toml`.
- Help text (managed via `typer`) should be clear, consistent, and reference canonical documentation and URI conventions where relevant.

---

## 🔍 Code Review Standards

This section defines the standards for code review and pull requests to maintain quality and consistency.

### Pull Request Template

All pull requests should include:

1. **Summary:** Brief description of the change
2. **Issue Link:** Reference to the issue being addressed
3. **Type of Change:** 
   - Bug fix
   - New feature
   - Documentation update
   - Refactoring
   - Performance improvement
4. **Testing:** How the changes were tested
5. **Documentation:** What documentation was updated

### Code Review Checklist

Reviewers should verify:

- [  ] Code follows naming conventions
- [  ] New code has appropriate test coverage
- [  ] Documentation is updated to reflect changes
- [  ] Changes align with architectural principles
- [  ] Performance implications are considered
- [  ] Security implications are addressed

---

## 🚀 Contribution Workflow

This section outlines the recommended workflow for contributing to the OmniBase/ONEX project.

### Development Setup

1. **Environment Setup:**
   ```bash
   # Clone repository
   git clone https://github.com/omnibase/omnibase.git
   cd omnibase
   
   # Set up virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies (in development mode)
   pip install -e ".[dev]"
   
   # Set up pre-commit hooks
   pre-commit install
   ```

2. **Before Making Changes:**
   - Ensure all tests pass: `pytest`
   - Create a new branch for your changes: `git checkout -b feature/your-feature-name`

3. **After Making Changes:**
   - Run linters and formatters: `pre-commit run --all-files`
   - Run tests: `pytest`
   - Update documentation as needed
   - Commit your changes with descriptive commit messages

4. **Submitting Changes:**
   - Push your branch to GitHub
   - Create a pull request with complete information using the PR template
   - Address review comments promptly

---

## 📊 Performance and Testing Guidelines

Guidelines for ensuring code performance and effective testing.

### Performance Considerations

- Minimize external API calls
- Use caching where appropriate
- Profile performance-critical code paths
- Consider memory usage for large operations
- Document performance characteristics in comments
- Apply `memoization_tier: deep` in `.onex` metadata for composite nodes that encapsulate reusable workflows. This enables subgraph-level caching and reduces redundant execution.
- When implementing model-backed or transformer nodes, declare `execution_profile` fields (speed, accuracy, efficiency) and `model_profiles` with cost metrics to support cost-aware planning.
- For stateful or reducer-based nodes, implement reducer snapshotting to avoid replay overhead in long-running or frequently restarted sessions.
- If a node exhibits performance instability, mark it with appropriate trust metadata (`trust_score_stub`) to allow the planner to deprioritize it during execution graph construction.

### Testing Expectations

- Aim for 90%+ test coverage for new code
- Include unit tests for individual components
- Add integration tests for component interactions
- Test both happy paths and error conditions
- Use parametrized tests for testing multiple scenarios
- Mock external dependencies to ensure test isolation

---

## Protocol Placement Guidance

When adding or refactoring a Python Protocol (interface/ABC), always determine its intended scope:
- **Runtime Protocol:** Used only by the ONEX runtime system (execution, eventing, I/O, orchestration). Place in `runtime/protocol/`.
- **Core/Cross-Cutting Protocol:** Used by models, CLI, nodes, or plugins. Place in `protocol/` (core/global).
- **Node-Local Protocol:** Used only within a single node. Keep in the node's directory.

See `structural_conventions.md` for the full decision table and canonical questions to ask.

**Contributor Checklist:**
- [ ] Before adding or moving a protocol, check where it is used.
- [ ] If only used by runtime, move to `runtime/protocol/`.
- [ ] If used by models, CLI, or multiple nodes, keep in `protocol/`.
- [ ] If node-local, keep in the node directory.
- [ ] Document rationale in PRs and code comments if unsure.

Protocol placement is enforced in code review and CI.

---

**Status:** This document defines the canonical development practices for contributing to OmniBase/ONEX. All contributors should follow these practices to ensure code quality, maintainability, and consistency.

---
