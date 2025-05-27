# ONEX Structured Testing Framework

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the structured testing framework and test case design patterns in ONEX  
> **Audience:** Test developers, node authors, QA engineers  
> **Companion:** [Testing Philosophy](./testing.md), [Registry Specification](./registry.md)

---

## Overview

ONEX treats tests as first-class registry components. All test cases are declarative, taggable, and executable via orchestrators. They support fixture injection, result validation, and dependency resolution, following the protocol-first architecture principles of the ONEX ecosystem.

---

## Test Case Types

| Type | Description | Use Cases |
|------|-------------|-----------|
| `unit` | Component-level input/output test | Individual node validation, protocol compliance |
| `integration` | Multi-step or pipeline-based checks | Node interaction, workflow validation |
| `e2e` | Full artifact lifecycle simulations | Complete system workflows, user scenarios |
| `canary` | High-frequency validators/tests | Continuous monitoring, health checks |
| `regression` | Linked to known issues or failures | Bug prevention, stability validation |

---

## Test Case Metadata Block

All test cases must include comprehensive metadata following the ONEX metadata specification:

```yaml
uuid: "test-uuid-12345"
name: "test_fix_header_output"
type: "test"
tags: ["unit", "tool", "canary"]
entrypoint: "tests/test_fix_header.yaml"
version: "0.1.0"
expected_result: "pass"
test_type: "unit"
lifecycle: "active"
dependencies:
  - id: "tool-fix_header"
    type: "tool"
    version_spec: ">=0.1.0"
  - id: "artifact-headerless"
    type: "data_artifact"
```

### Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `uuid` | string | ✅ | Unique test identifier |
| `name` | string | ✅ | Human-readable test name |
| `type` | string | ✅ | Must be "test" |
| `tags` | array | ✅ | Test categorization tags |
| `entrypoint` | string | ✅ | Test execution entry point |
| `version` | string | ✅ | Test version (semantic versioning) |
| `expected_result` | string | ✅ | Expected outcome (pass/fail/skip) |
| `test_type` | string | ✅ | Test category (unit/integration/e2e/canary/regression) |
| `lifecycle` | string | ✅ | Lifecycle state (draft/active/deprecated/archived) |
| `dependencies` | array | ⬜ | Test dependencies and requirements |

---

## Protocol-Driven Test Design

### Test Protocol Definition

All tests must implement the `TestProtocol` for consistency and interoperability:

```python
from typing import Protocol, Any, Dict, List
from dataclasses import dataclass

@dataclass
class TestResult:
    """Standardized test result."""
    status: Literal["pass", "fail", "skip"]
    message: str
    duration_ms: int
    diff: Optional[str] = None
    reason: Optional[str] = None
    artifact_refs: List[str] = None
    metadata: Dict[str, Any] = None

class TestProtocol(Protocol):
    """Protocol for ONEX test cases."""
    
    def execute(self, context: TestContext) -> TestResult:
        """Execute the test case."""
        ...
    
    def validate_prerequisites(self, context: TestContext) -> bool:
        """Validate test prerequisites are met."""
        ...
    
    def get_dependencies(self) -> List[str]:
        """Get list of test dependencies."""
        ...
```

### Fixture-Injectable Test Example

Protocol-driven tools like the ONEX Metadata Stamper require test cases that are context-agnostic and registry-driven:

```python
from omnibase.protocols import StamperProtocol

def test_stamp_valid_files(stamper_engine: StamperProtocol):
    """Test stamping valid files with protocol-based engine."""
    files = ["valid1.yaml", "valid2.yaml"]
    result = stamper_engine.stamp(files, dry_run=True)
    
    assert all(r["status"] in ("success", "warning") for r in result)
    assert len(result) == 2
    
    for file_result in result:
        assert "metadata" in file_result
        assert "hash" in file_result["metadata"]

def test_stamp_invalid_files(stamper_engine: StamperProtocol):
    """Test stamping invalid files handles errors gracefully."""
    files = ["nonexistent.yaml", "invalid-syntax.yaml"]
    result = stamper_engine.stamp(files, dry_run=True)
    
    assert all(r["status"] == "error" for r in result)
    assert all("error_message" in r for r in result)
```

**Key Principles:**
- The `stamper_engine` fixture is parameterized to provide both real and in-memory/mock engines
- Test cases are registered in the test registry and discovered dynamically
- All test logic validates only the public protocol contract
- All dependencies (e.g., file I/O, ignore patterns) are injected via fixtures

---

## Declarative Test Structure

Tests can be defined declaratively using YAML for simple validation scenarios:

```yaml
# test_fix_header.yaml
test_name: "Header fixer adds missing license"
test_type: "unit"
input_artifact: "artifact-headerless"
tool_under_test: "tool-fix_header"
expected_output: "artifact-with-header"
expected_diff: true
assertions:
  - field: content
    contains: "Licensed under Apache"
  - field: metadata.license
    equals: "Apache-2.0"
  - field: status
    equals: "success"
validation:
  schema: "test_result_schema_v1.json"
  strict_mode: true
```

### Declarative Test Fields

| Field | Type | Description |
|-------|------|-------------|
| `test_name` | string | Human-readable test description |
| `test_type` | string | Test category |
| `input_artifact` | string | Input artifact identifier |
| `tool_under_test` | string | Tool/node being tested |
| `expected_output` | string | Expected output artifact |
| `expected_diff` | boolean | Whether output should differ from input |
| `assertions` | array | List of validation assertions |
| `validation` | object | Validation configuration |

---

## Test Registry Protocol

### Test File Location

All node tests must be placed in standardized locations:

```text
src/omnibase/nodes/{node_id}/test.py          # Primary test file
src/omnibase/nodes/{node_id}/test_case_*.py   # Extended test scenarios
src/omnibase/nodes/{node_id}/test_scenario_*.py # Scenario tests
src/omnibase/nodes/{node_id}/test_variant_*.py  # Variant tests
```

Extended test files must be declared in `metadata.yaml`:

```yaml
auxiliary:
  test_cases:
    - test_case_fail_on_bad_input.py
    - test_variant_edge_case.py
    - test_scenario_complex_workflow.py
```

### Registration Protocol

Every valid test module must contain a `register()` function that populates the test registry:

```python
from omnibase.core.registry import TestRegistry

def register(registry: TestRegistry) -> None:
    """Register test cases with the test registry."""
    registry.add_test(
        test_id="validator.check.namegen",
        test_function=validate_namegen_behavior,
        metadata={
            "category": "validation",
            "protocol": "ONEX-Test-v0.1",
            "tags": ["unit", "validation", "namegen"]
        }
    )
    
    registry.add_test(
        test_id="validator.check.metadata",
        test_function=validate_metadata_structure,
        metadata={
            "category": "validation", 
            "protocol": "ONEX-Test-v0.1",
            "tags": ["unit", "validation", "metadata"]
        }
    )

def validate_namegen_behavior(context: TestContext) -> TestResult:
    """Test name generation behavior."""
    # Test implementation
    pass

def validate_metadata_structure(context: TestContext) -> TestResult:
    """Test metadata structure validation."""
    # Test implementation
    pass
```

### Metadata Requirements

Each test file must contain metadata matching the ONEX test schema:

```yaml
# In test file frontmatter or separate metadata.yaml
metadata_version: 0.1
id: validator.check.namegen
category: validation
protocol: ONEX-Test-v0.1
tags: ["unit", "validation"]
dependencies:
  - "core.registry"
  - "protocols.validation"
```

---

## Test Discovery and Execution

### Discovery Mechanisms

Tests are discovered through multiple channels:

1. **File System Scanning**: Scan node directories for test files
2. **Registry Lookup**: Query registry for objects with `type: test`
3. **Metadata Analysis**: Parse `.onextree` entries under `nodes:`
4. **Entry Point Discovery**: Use setuptools entry points for plugins

```python
class TestDiscovery:
    """Test discovery engine."""
    
    def discover_tests(self, criteria: DiscoveryCriteria) -> List[TestMetadata]:
        """Discover tests matching criteria."""
        discovered_tests = []
        
        # File system discovery
        fs_tests = self._discover_from_filesystem()
        discovered_tests.extend(fs_tests)
        
        # Registry discovery
        registry_tests = self._discover_from_registry(criteria)
        discovered_tests.extend(registry_tests)
        
        # Plugin discovery
        plugin_tests = self._discover_from_plugins()
        discovered_tests.extend(plugin_tests)
        
        return self._deduplicate_tests(discovered_tests)
```

### Execution Engine

```python
class TestExecutor:
    """Test execution engine with parallel support."""
    
    def execute_tests(
        self, 
        tests: List[TestMetadata],
        execution_config: ExecutionConfig
    ) -> TestExecutionResult:
        """Execute tests with specified configuration."""
        
        results = []
        
        if execution_config.parallel:
            results = self._execute_parallel(tests, execution_config)
        else:
            results = self._execute_sequential(tests, execution_config)
        
        return TestExecutionResult(
            total_tests=len(tests),
            passed=len([r for r in results if r.status == "pass"]),
            failed=len([r for r in results if r.status == "fail"]),
            skipped=len([r for r in results if r.status == "skip"]),
            results=results,
            duration_ms=sum(r.duration_ms for r in results)
        )
```

---

## Tags and Execution Filtering

### Standard Tags

| Tag | Purpose | Usage |
|-----|---------|-------|
| `pre-commit` | Pre-commit hook tests | Fast, essential validations |
| `ci` | Continuous integration tests | Automated pipeline tests |
| `regression` | Regression prevention tests | Known issue prevention |
| `canary` | Health check tests | Continuous monitoring |
| `unit` | Unit tests | Component-level testing |
| `integration` | Integration tests | Multi-component testing |
| `e2e` | End-to-end tests | Full workflow testing |
| `performance` | Performance tests | Benchmarking and profiling |
| `security` | Security tests | Vulnerability and compliance |

### Filtering Examples

```bash
# Run unit tests only
onex test --tags unit

# Run all tests except performance tests
onex test --exclude-tags performance

# Run tests for specific lifecycle stage
onex test --lifecycle active

# Run tests matching multiple criteria
onex test --tags "unit,integration" --lifecycle active

# Run specific test by UUID
onex test --uuid test-uuid-12345

# Run tests with custom filter expression
onex test --filter "tags.contains('canary') and lifecycle=='active'"
```

### Lifecycle Gates

Lifecycle states control test execution in different environments:

| Lifecycle | Description | Execution Context |
|-----------|-------------|-------------------|
| `draft` | Development tests | Local development only |
| `active` | Production tests | All environments |
| `deprecated` | Legacy tests | Limited execution, warnings |
| `archived` | Retired tests | No execution, historical reference |

---

## CLI Integration

### Basic Commands

```bash
# Run all tests
onex test

# Run specific test by ID
onex test --id validator.check.namegen

# Run tests with tags
onex test --tags unit,validation

# Run tests from batch file
onex test --batch test_registry.yaml

# Lint test definitions
onex test --lint

# Run tests with detailed output
onex test --verbose --diff

# Run tests in parallel
onex test --parallel --workers 4

# Run tests with coverage
onex test --coverage --coverage-report html
```

### Advanced Usage

```bash
# Run tests with custom configuration
onex test --config test_config.yaml

# Run tests with specific timeout
onex test --timeout 300

# Run tests with retry on failure
onex test --retry 3

# Run tests with custom output format
onex test --format json --output results.json

# Run tests with environment variables
onex test --env TEST_MODE=integration

# Run tests with fixture overrides
onex test --fixtures test_fixtures.yaml
```

---

## Result Models

### TestResult Schema

```python
@dataclass
class TestResult:
    """Comprehensive test result model."""
    status: Literal["pass", "fail", "skip"]
    message: str
    duration_ms: int
    test_id: str
    test_name: str
    diff: Optional[str] = None
    reason: Optional[str] = None
    artifact_refs: List[str] = None
    metadata: Dict[str, Any] = None
    error_details: Optional[ErrorDetails] = None
    performance_metrics: Optional[PerformanceMetrics] = None

@dataclass
class ErrorDetails:
    """Detailed error information."""
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None

@dataclass
class PerformanceMetrics:
    """Performance measurement data."""
    execution_time_ms: int
    memory_usage_mb: float
    cpu_usage_percent: float
    io_operations: int
```

### Unified Result Model

All validators and test components must return a `UnifiedResultModel`:

```python
from typing import Protocol, List, Any
from dataclasses import dataclass

@dataclass
class OnexMessageModel:
    """Structured message model."""
    summary: str
    level: str  # error, warning, info, debug
    type: Optional[str] = None  # error, note, fixed, skipped
    file: Optional[str] = None
    line: Optional[int] = None
    details: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@dataclass
class UnifiedResultModel:
    """Unified result model for all ONEX operations."""
    status: str  # success, error, warning, info
    messages: List[OnexMessageModel]
    metadata: Optional[Dict[str, Any]] = None

class ValidatorProtocol(Protocol):
    """Protocol for ONEX validators."""
    
    def validate(self, data: Any) -> UnifiedResultModel:
        """Validate data and return unified result."""
        ...
```

### Example Usage

```python
def validate_metadata_block(metadata: Dict[str, Any]) -> UnifiedResultModel:
    """Validate metadata block structure."""
    messages = []
    
    # Check required fields
    required_fields = ["uuid", "name", "version", "author"]
    for field in required_fields:
        if field not in metadata:
            messages.append(OnexMessageModel(
                summary=f"Missing required metadata field: {field}",
                level="error",
                type="error",
                details=f"The '{field}' field is required in all metadata blocks.",
                context={"validator": "MetadataBlockValidator", "field": field}
            ))
    
    # Determine overall status
    has_errors = any(msg.level == "error" for msg in messages)
    status = "error" if has_errors else "success"
    
    return UnifiedResultModel(
        status=status,
        messages=messages,
        metadata={"validator": "MetadataBlockValidator", "fields_checked": len(required_fields)}
    )
```

---

## Test Enforcement Rules

### Required Patterns

1. **Individual Executability**: All test files must be individually executable
2. **No Global State**: Tests must not rely on global state or shared configuration
3. **Protocol Compliance**: All tests must implement the `TestProtocol`
4. **Result Format**: All tests must return `UnifiedResultModel` or `TestResult`
5. **Dependency Injection**: All dependencies must be injected, no global instantiation

### Forbidden Patterns

- ❌ Ad hoc string errors
- ❌ Unstructured JSON or free-form result objects  
- ❌ Mixing ABCs and Protocols for the same contract
- ❌ Global instantiation without dependency injection
- ❌ Direct print statements for test output
- ❌ Hardcoded file paths or environment assumptions

### Best Practices

- ✅ Use Protocol classes for all interfaces
- ✅ Implement comprehensive fixture injection
- ✅ Follow structured result models
- ✅ Include performance metrics where relevant
- ✅ Provide detailed error context
- ✅ Use semantic versioning for test versions
- ✅ Tag tests appropriately for filtering
- ✅ Document test dependencies clearly

---

## Integration with ONEX Ecosystem

### Registry Integration

Tests are first-class citizens in the ONEX registry:

```python
# Register test in the main registry
registry.register_test(
    test_metadata=TestMetadata(
        uuid="test-metadata-validator-001",
        name="Metadata Block Validator Test",
        version="1.0.0",
        test_type="unit",
        tags=["validation", "metadata", "unit"],
        dependencies=["core.metadata", "protocols.validation"]
    ),
    test_implementation=MetadataValidatorTest()
)
```

### CLI Integration

```bash
# Discover and run tests through registry
onex run test_runner_node --args='["--tags", "unit"]'

# Validate test definitions
onex validate --target tests/ --validator test_metadata

# List available tests
onex list-nodes --type test

# Get test information
onex node-info test-metadata-validator-001
```

### Orchestration Integration

Tests can be orchestrated as part of larger workflows:

```yaml
# workflow.yaml
workflow:
  name: "Validation Pipeline"
  steps:
    - name: "Unit Tests"
      node: "test_runner_node"
      args: ["--tags", "unit", "--format", "json"]
    - name: "Integration Tests"  
      node: "test_runner_node"
      args: ["--tags", "integration"]
      depends_on: ["Unit Tests"]
    - name: "Generate Report"
      node: "test_report_generator"
      depends_on: ["Unit Tests", "Integration Tests"]
```

---

## References

- [Testing Philosophy](./testing.md)
- [Registry Specification](./registry.md)
- [Orchestration Specification](./orchestration.md)
- [Error Handling](./error_handling.md)
- [Core Protocols](./reference-protocols-core.md)
- [Registry Protocols](./reference-protocols-registry.md)
- [Data Models](./reference-data-models.md)

---

**Note:** The ONEX Structured Testing Framework provides a comprehensive foundation for building reliable, maintainable test suites that integrate seamlessly with the broader ONEX ecosystem. All testing components should follow these patterns to ensure consistency and interoperability. 