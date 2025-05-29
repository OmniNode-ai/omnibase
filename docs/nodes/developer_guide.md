<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:26.626015'
description: Stamped by ONEX
entrypoint: python://developer_guide.md
hash: a932d04c3b922e484c21e6cae7cc7d5a3308ea77c727b3f515b95b656a489d6a
last_modified_at: '2025-05-29T11:50:15.076061+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: developer_guide.md
namespace: omnibase.developer_guide
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: aa8df5f9-a12b-4c86-a5c8-cfc9cb5b8024
version: 1.0.0

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

## 🔧 Structured Logging Guidelines

ONEX uses a comprehensive structured logging system that routes all output through the Logger Node as side effects.

### Usage Guidelines

**Replace all print() and logging calls:**
```python
# ❌ Don't use print() or logging
print("Processing file:", filename)
logging.info("Operation completed")

# ✅ Use structured logging
from omnibase.core.structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum

emit_log_event(LogLevelEnum.INFO, "Processing file", {"filename": filename})
emit_log_event("info", "Operation completed", {"duration_ms": 150})
```

### Configuration

Configure structured logging via environment variables:
```bash
export ONEX_LOG_FORMAT=json          # Output format
export ONEX_LOG_LEVEL=info           # Minimum log level
export ONEX_ENABLE_CORRELATION_IDS=true  # Enable correlation tracking
export ONEX_LOG_TARGETS=stdout       # Output targets
```

### Benefits

- **Architectural Purity:** All output flows through Logger Node
- **Better Observability:** Correlation IDs and structured context
- **Single Configuration:** Centralized output formatting
- **Consistent Patterns:** One way to emit logs across entire codebase

---

## 🔌 Plugin Development Guidelines

ONEX supports flexible plugin discovery through multiple mechanisms.

### Plugin Types

| Type | Purpose | Entry Point Group |
|------|---------|-------------------|
| `handler` | File type processors | `omnibase.handlers` |
| `validator` | Custom validation | `omnibase.validators` |
| `tool` | Extended functionality | `omnibase.tools` |
| `fixture` | Test fixture providers | `omnibase.fixtures` |
| `node` | Node plugins (M2) | `omnibase.nodes` |

### Plugin Registration

**1. Entry Points (pyproject.toml):**
```toml
[tool.poetry.plugins."omnibase.handlers"]
csv_handler = "my_package.handlers:CSVHandler"
```

**2. Configuration File (plugin_registry.yaml):**
```yaml
handlers:
  csv_processor:
    module: "my_package.handlers.csv_handler"
    class: "CSVHandler"
    priority: 5
```

**3. Environment Variables:**
```bash
export ONEX_PLUGIN_HANDLER_CSV="my_package.handlers:CSVHandler"
```

### Plugin Protocol

All plugins must implement the `PluginProtocol`:
```python
from omnibase.core.core_plugin_loader import PluginProtocol

class MyPlugin(PluginProtocol):
    def bootstrap(self, registry: Any) -> None:
        """Bootstrap the plugin with the given registry."""
        pass
```

---

## 🛡️ Error Handling Guidelines

All error handling must use centralized error codes for consistency.

### Usage

```python
from omnibase.core.error_codes import OnexError, CoreErrorCode

# ❌ Don't use generic exceptions
raise ValueError("Invalid input")

# ✅ Use centralized error codes
raise OnexError("Invalid input provided", CoreErrorCode.INVALID_PARAMETER)
```

### Benefits

- Consistent error reporting across all components
- CI enforcement of error code compliance
- Structured error handling for better debugging
- Standardized error responses for APIs

### Error Code Categories

- **INVALID_PARAMETER:** Invalid input parameters
- **FILE_NOT_FOUND:** Missing required files
- **DEPENDENCY_UNAVAILABLE:** Missing dependencies
- **OPERATION_FAILED:** General operation failures
- **PERMISSION_DENIED:** Access control violations

---

## 🔒 Sensitive Data Guidelines

ONEX provides automatic redaction of sensitive fields to prevent credential leakage.

### Marking Sensitive Fields

```python
from pydantic import BaseModel, Field
from omnibase.core.sensitive_field_redaction import SensitiveFieldRedactionMixin

class MyState(SensitiveFieldRedactionMixin, BaseModel):
    api_key: Optional[str] = Field(default=None, metadata={"sensitive": True})
    password: Optional[str] = Field(default=None, metadata={"sensitive": True})
    public_data: str = "safe to log"
```

### Automatic Redaction

- Sensitive fields are automatically redacted during `.model_dump()`
- Redaction applied in logs and events
- Protocol-first testing validates redaction behavior
- Prevents accidental credential exposure

### Best Practices

- Mark all credentials, tokens, and PII as sensitive
- Use descriptive field names that indicate sensitivity
- Test redaction behavior in your test suites
- Review logs to ensure no sensitive data leakage

---

## 📊 Telemetry and Observability

ONEX provides comprehensive telemetry and event infrastructure for observability.

### Telemetry Decorators

All node entrypoints should use telemetry decorators:
```python
from omnibase.core.telemetry import telemetry

@telemetry("my_node")
def run_my_node(input_state, event_bus):
    # Node implementation
    return output_state
```

### Correlation ID Propagation

- Correlation IDs are automatically generated and propagated
- All events and logs include correlation context
- Enables distributed tracing across complex workflows
- Supports debugging and monitoring in production

### Event Emission

The system automatically emits standardized events:
- `NODE_START`: When node execution begins
- `NODE_SUCCESS`: When node completes successfully
- `NODE_FAILURE`: When node encounters errors

### Performance Metrics

- Automatic timing capture for all operations
- Performance metrics included in telemetry
- Resource usage tracking where applicable
- Supports performance optimization and monitoring

---

## 🔧 Function Metadata Extension

ONEX supports language-agnostic function-as-tool stamping across multiple languages.

### Supported Languages

- **Python:** AST-based parsing with type hints and docstrings
- **JavaScript/TypeScript:** AST-based parsing with JSDoc and TypeScript types
- **Bash/Shell:** Pattern-based parsing with comment metadata
- **YAML/JSON:** Schema-based function definitions

### Function Tool Metadata

Functions are treated as tools within the unified metadata schema:
```yaml
# === OmniNode:Metadata ===
# ... standard file metadata ...
# tools:
#   validate_schema:
#     type: function
#     language: python
#     line: 45
#     description: "Validates JSON schema format"
#     inputs: ["schema: Dict[str, Any]"]
#     outputs: ["ValidationResult"]
#     error_codes: ["SCHEMA_INVALID"]
#     side_effects: ["logs validation events"]
# === /OmniNode:Metadata ===
```

### Benefits

- 56% reduction in metadata overhead vs separate blocks
- Natural tool discovery across all languages
- Seamless integration with existing ONEX infrastructure
- Foundation for M2 dynamic tool composition

### CLI Integration

```bash
# Discover and stamp functions in files
poetry run onex stamp file <file> --discover-functions

# List all tools including functions
poetry run onex list-tools <file>

# Get detailed function information
poetry run onex tool-info <file>:<function_name>
```

---

**Status:** This document defines the canonical development practices for contributing to OmniBase/ONEX. All contributors should follow these practices to ensure code quality, maintainability, and consistency.

---
