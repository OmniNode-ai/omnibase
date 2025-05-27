<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: node_testing_guidelines.md
version: 1.0.0
uuid: 9c2cbdc9-55f7-4615-9544-cf4b99fcd599
author: OmniNode Team
created_at: 2025-05-27T08:16:50.976436
last_modified_at: 2025-05-27T17:26:51.849267
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 78645b6c6b476b5b509aec2e6fbc9d164c9e382337919f92b960a95360539d0e
entrypoint: python@node_testing_guidelines.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.node_testing_guidelines
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Testing Guidelines

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Define structure, conventions, and best practices for testing ONEX nodes  
> **Audience:** Node developers, QA engineers, contributors  
> **Related:** [Testing Framework](./README.md), [Fixtures Guidelines](./fixtures_guidelines.md)  

---

## Overview

This document defines the structure, conventions, and best practices for testing nodes in the ONEX architecture. It establishes patterns that ensure nodes are reliable, maintainable, and properly integrated with the ONEX ecosystem.

---

## Canonical Directory Structure

Each node should include its own test directory colocated alongside the node implementation:

```
src/
  omnibase/
    nodes/
      stamper_node/
        v1_0_0/
          node.py
          state_contract.yaml
          node.onex.yaml
          tests/
            __init__.py
            test_main.py
            test_integration.py
            test_contract_compliance.py
            fixtures/
              __init__.py
              sample_input.yaml
              sample_output.yaml
              error_cases.yaml
            mocks/
              __init__.py
              mock_dependencies.py
```

### Directory Structure Rules

* **Colocated Tests**: Tests live alongside the node implementation, not in a separate top-level `tests/` directory
* **Version-Specific**: Tests are version-specific and live within the node's version directory
* **Module Structure**: Include `__init__.py` in all test and fixture directories to enforce proper module structure
* **Separation of Concerns**: Separate unit tests, integration tests, and contract compliance tests

---

## Test Conventions

### Import Standards

```python
# Use absolute imports for clarity and pytest compatibility
from omnibase.nodes.stamper_node.v1_0_0.node import run_stamper_node
from omnibase.core.protocol_execution_context import ProtocolExecutionContext
from omnibase.testing.fixtures import load_test_fixture
from omnibase.testing.test_helpers import assert_contract_compliance

# Avoid relative imports in tests
# from .node import run_stamper_node  # ❌ Don't do this
```

### Test Marking and Organization

```python
import pytest
from typing import Dict, Any

@pytest.mark.node
class TestStamperNode:
    """Test suite for stamper node functionality."""
    
    @pytest.mark.unit
    def test_basic_functionality(self):
        """Test basic node functionality with valid input."""
        pass
    
    @pytest.mark.integration
    def test_cli_integration(self):
        """Test node execution via CLI."""
        pass
    
    @pytest.mark.contract
    def test_contract_compliance(self):
        """Test compliance with declared state contract."""
        pass
    
    @pytest.mark.error_handling
    def test_error_scenarios(self):
        """Test error handling and edge cases."""
        pass
```

### Test Categories

* **`@pytest.mark.node`**: Mark all node-specific tests
* **`@pytest.mark.unit`**: Pure unit tests with no external dependencies
* **`@pytest.mark.integration`**: Tests that involve CLI, file system, or external services
* **`@pytest.mark.contract`**: Tests that validate state contract compliance
* **`@pytest.mark.error_handling`**: Tests focused on error scenarios and edge cases

---

## Core Test Requirements

### 1. CLI Execution Validation

Every node must be testable via the ONEX CLI:

```python
import subprocess
import json
import pytest

@pytest.mark.integration
def test_cli_execution():
    """Test node execution via onex CLI."""
    # Test basic execution
    result = subprocess.run([
        "poetry", "run", "onex", "run", "stamper_node",
        "--args", '{"file_path": "test_file.py"}'
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    assert "NODE_SUCCESS" in result.stdout
    
    # Parse and validate output
    output = json.loads(result.stdout)
    assert output["status"] == "success"
    assert "metadata" in output

@pytest.mark.integration
def test_cli_introspection():
    """Test node introspection via CLI."""
    result = subprocess.run([
        "poetry", "run", "onex", "run", "stamper_node", "--introspect"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    introspection = json.loads(result.stdout)
    assert "input_contract" in introspection
    assert "output_contract" in introspection
    assert "metadata" in introspection
```

### 2. Event Emission Validation

Nodes must emit proper lifecycle events:

```python
from omnibase.testing.event_capture import EventCapture

@pytest.mark.unit
def test_event_emission():
    """Test that node emits required lifecycle events."""
    event_capture = EventCapture()
    
    # Execute node with event capture
    with event_capture:
        result = run_stamper_node({
            "file_path": "test_file.py"
        })
    
    # Validate events
    events = event_capture.get_events()
    event_types = [e["type"] for e in events]
    
    assert "NODE_START" in event_types
    assert "NODE_SUCCESS" in event_types or "NODE_FAILURE" in event_types
    
    # Validate event structure
    start_event = next(e for e in events if e["type"] == "NODE_START")
    assert "timestamp" in start_event
    assert "node_uri" in start_event
    assert "input_state" in start_event
```

### 3. State Contract Compliance

Validate input/output against declared contracts:

```python
import yaml
from jsonschema import validate, ValidationError

@pytest.mark.contract
def test_input_contract_compliance():
    """Test that node validates input against its contract."""
    # Load the node's state contract
    with open("state_contract.yaml", "r") as f:
        contract = yaml.safe_load(f)
    
    input_schema = contract["input_schema"]
    
    # Test valid input
    valid_input = {"file_path": "test.py"}
    validate(instance=valid_input, schema=input_schema)  # Should not raise
    
    # Test invalid input
    invalid_input = {"wrong_field": "value"}
    with pytest.raises(ValidationError):
        validate(instance=invalid_input, schema=input_schema)

@pytest.mark.contract
def test_output_contract_compliance():
    """Test that node output conforms to its contract."""
    with open("state_contract.yaml", "r") as f:
        contract = yaml.safe_load(f)
    
    output_schema = contract["output_schema"]
    
    # Execute node and validate output
    result = run_stamper_node({"file_path": "test.py"})
    
    # Validate output structure
    validate(instance=result, schema=output_schema)
    
    # Validate required fields
    assert "status" in result
    assert "metadata" in result
    assert result["status"] in ["success", "failure"]
```

### 4. Metadata Structure Validation

Validate `.onex` metadata structure:

```python
@pytest.mark.contract
def test_onex_metadata_structure():
    """Test that node produces valid .onex metadata."""
    result = run_stamper_node({"file_path": "test.py"})
    
    # Check for required metadata fields
    metadata = result.get("metadata", {})
    
    required_fields = [
        "execution_time_ms",
        "node_version",
        "trust_score",
        "timestamp"
    ]
    
    for field in required_fields:
        assert field in metadata, f"Missing required metadata field: {field}"
    
    # Validate field types
    assert isinstance(metadata["execution_time_ms"], (int, float))
    assert isinstance(metadata["trust_score"], (int, float))
    assert 0.0 <= metadata["trust_score"] <= 1.0
```

---

## Advanced Testing Patterns

### Fixture-Based Testing

```python
import pytest
from omnibase.testing.fixtures import load_test_fixture

@pytest.fixture
def sample_input():
    """Load sample input from fixtures."""
    return load_test_fixture("stamper_node/sample_input.yaml")

@pytest.fixture
def expected_output():
    """Load expected output from fixtures."""
    return load_test_fixture("stamper_node/sample_output.yaml")

@pytest.mark.unit
def test_with_fixtures(sample_input, expected_output):
    """Test using predefined fixtures."""
    result = run_stamper_node(sample_input)
    
    # Compare key fields (allowing for dynamic fields like timestamps)
    assert result["status"] == expected_output["status"]
    assert result["file_hash"] == expected_output["file_hash"]
```

### Mock-Based Testing

```python
from unittest.mock import patch, MagicMock
import pytest

@pytest.mark.unit
@patch('omnibase.nodes.stamper_node.v1_0_0.node.calculate_file_hash')
def test_with_mocks(mock_hash):
    """Test node behavior with mocked dependencies."""
    # Setup mock
    mock_hash.return_value = "abc123"
    
    # Execute node
    result = run_stamper_node({"file_path": "test.py"})
    
    # Verify mock was called
    mock_hash.assert_called_once_with("test.py")
    
    # Verify result
    assert result["file_hash"] == "abc123"

@pytest.mark.unit
def test_error_handling_with_mocks():
    """Test error handling with mocked failures."""
    with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
        result = run_stamper_node({"file_path": "nonexistent.py"})
        
        assert result["status"] == "failure"
        assert "error" in result
        assert "File not found" in result["error"]["message"]
```

### Performance Testing

```python
import time
import pytest

@pytest.mark.performance
def test_execution_performance():
    """Test node execution performance."""
    start_time = time.time()
    
    result = run_stamper_node({"file_path": "large_file.py"})
    
    execution_time = time.time() - start_time
    
    # Verify performance requirements
    assert execution_time < 5.0, f"Node took too long: {execution_time}s"
    assert result["status"] == "success"
    
    # Verify reported execution time is accurate
    reported_time_ms = result["metadata"]["execution_time_ms"]
    assert abs(execution_time * 1000 - reported_time_ms) < 100  # Within 100ms
```

---

## Test Harness and Utilities

### Node Test Runner

Create a reusable test harness for programmatic node execution:

```python
# tests/node_runner.py
from typing import Dict, Any, Optional
from omnibase.core.protocol_execution_context import ProtocolExecutionContext
from omnibase.testing.event_capture import EventCapture

class NodeTestRunner:
    """Test harness for executing nodes in test environments."""
    
    def __init__(self, node_function):
        self.node_function = node_function
        self.event_capture = EventCapture()
    
    def run(self, input_state: Dict[str, Any], 
            context: Optional[ProtocolExecutionContext] = None) -> Dict[str, Any]:
        """Execute node with test instrumentation."""
        
        if context is None:
            context = ProtocolExecutionContext.create_test_context()
        
        with self.event_capture:
            result = self.node_function(input_state, context)
        
        return {
            "result": result,
            "events": self.event_capture.get_events(),
            "execution_time": self.event_capture.get_execution_time(),
            "context": context
        }
    
    def assert_success(self, execution_result: Dict[str, Any]):
        """Assert that execution was successful."""
        assert execution_result["result"]["status"] == "success"
        
        events = execution_result["events"]
        event_types = [e["type"] for e in events]
        assert "NODE_START" in event_types
        assert "NODE_SUCCESS" in event_types
    
    def assert_failure(self, execution_result: Dict[str, Any], expected_error: str = None):
        """Assert that execution failed as expected."""
        assert execution_result["result"]["status"] == "failure"
        
        if expected_error:
            error_message = execution_result["result"]["error"]["message"]
            assert expected_error in error_message

# Usage in tests
@pytest.mark.unit
def test_with_harness():
    """Test using the node test harness."""
    runner = NodeTestRunner(run_stamper_node)
    
    execution = runner.run({"file_path": "test.py"})
    runner.assert_success(execution)
    
    assert execution["execution_time"] < 1000  # Less than 1 second
```

---

## CI Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/node-tests.yml
name: Node Tests

on: [push, pull_request]

jobs:
  test-nodes:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install poetry
        poetry install
    
    - name: Run node unit tests
      run: |
        poetry run pytest src/omnibase/nodes --tb=short -m "node and unit" -v
    
    - name: Run node integration tests
      run: |
        poetry run pytest src/omnibase/nodes --tb=short -m "node and integration" -v
    
    - name: Run contract compliance tests
      run: |
        poetry run pytest src/omnibase/nodes --tb=short -m "node and contract" -v
    
    - name: Generate coverage report
      run: |
        poetry run pytest src/omnibase/nodes --cov=src/omnibase/nodes --cov-report=xml -m node
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: node-tests
        name: Run node tests
        entry: poetry run pytest src/omnibase/nodes -m "node and unit" --tb=short
        language: system
        pass_filenames: false
        always_run: true
```

---

## Test Scaffolding

### Automatic Test Generation

When creating new nodes, include test scaffolding:

```python
# Template: tests/test_main.py
import pytest
from omnibase.nodes.{{node_name}}.v1_0_0.node import run_{{node_name}}
from omnibase.testing.fixtures import load_test_fixture

@pytest.mark.node
class Test{{node_name|title}}:
    """Test suite for {{node_name}} node."""
    
    @pytest.mark.unit
    def test_basic_functionality(self):
        """Test basic node functionality."""
        input_state = {"example_field": "test_value"}
        result = run_{{node_name}}(input_state)
        
        assert result["status"] == "success"
        assert "metadata" in result
    
    @pytest.mark.integration
    def test_cli_execution(self):
        """Test node execution via CLI."""
        # TODO: Implement CLI test
        pass
    
    @pytest.mark.contract
    def test_contract_compliance(self):
        """Test state contract compliance."""
        # TODO: Implement contract validation
        pass
    
    @pytest.mark.error_handling
    def test_error_scenarios(self):
        """Test error handling."""
        # TODO: Implement error case testing
        pass
```

### Fixture Templates

```yaml
# Template: tests/fixtures/sample_input.yaml
example_field: "test_value"
options:
  timeout: 30
  retry_count: 3
```

```yaml
# Template: tests/fixtures/sample_output.yaml
status: "success"
result: "expected_result"
metadata:
  execution_time_ms: 150
  trust_score: 1.0
  node_version: "1.0.0"
```

---

## Shared Testing Utilities

Common fixtures and test utilities should be centralized:

```
src/
  omnibase/
    testing/
      __init__.py
      fixtures.py          # Fixture loading utilities
      test_helpers.py      # Common test helper functions
      event_capture.py     # Event capture for testing
      mock_factories.py    # Mock object factories
      assertions.py        # Custom assertion helpers
```

### Example Shared Utilities

```python
# src/omnibase/testing/test_helpers.py
from typing import Dict, Any
import jsonschema

def assert_contract_compliance(result: Dict[str, Any], schema: Dict[str, Any]):
    """Assert that result complies with the given schema."""
    try:
        jsonschema.validate(instance=result, schema=schema)
    except jsonschema.ValidationError as e:
        pytest.fail(f"Contract compliance failed: {e.message}")

def assert_execution_time_reasonable(result: Dict[str, Any], max_time_ms: int = 5000):
    """Assert that execution time is within reasonable bounds."""
    execution_time = result.get("metadata", {}).get("execution_time_ms", 0)
    assert execution_time <= max_time_ms, f"Execution took too long: {execution_time}ms"

def assert_trust_score_valid(result: Dict[str, Any]):
    """Assert that trust score is valid."""
    trust_score = result.get("metadata", {}).get("trust_score", 0)
    assert 0.0 <= trust_score <= 1.0, f"Invalid trust score: {trust_score}"
```

---

## Best Practices

### Test Organization

1. **Keep tests close to code**: Tests should live alongside the node implementation
2. **Use descriptive test names**: Test names should clearly describe what is being tested
3. **Group related tests**: Use test classes to group related functionality
4. **Separate concerns**: Keep unit, integration, and contract tests separate

### Test Data Management

1. **Use fixtures for test data**: Centralize test data in fixture files
2. **Version test data**: Include test data in version control
3. **Keep test data minimal**: Use the smallest data set that validates the functionality
4. **Document test scenarios**: Include comments explaining complex test scenarios

### Error Testing

1. **Test error paths**: Ensure error scenarios are properly tested
2. **Validate error messages**: Check that error messages are helpful and accurate
3. **Test edge cases**: Include tests for boundary conditions and edge cases
4. **Mock external failures**: Use mocks to simulate external system failures

### Performance Considerations

1. **Set performance expectations**: Define acceptable execution times
2. **Test with realistic data**: Use data sizes similar to production
3. **Monitor test execution time**: Keep test suite execution time reasonable
4. **Use appropriate test levels**: Don't run expensive tests in unit test suites

---

## References

- [Testing Framework](./README.md) - Overall testing philosophy and framework
- [Fixtures Guidelines](./fixtures_guidelines.md) - Detailed fixture management
- [Node Architecture](../nodes/index.md) - Node architecture overview
- [CLI Examples](../cli_examples.md) - CLI usage patterns for testing
- [Standards](../standards.md) - Code and testing standards

---

**Note:** This document establishes the canonical approach to testing ONEX nodes. Following these guidelines ensures that nodes are reliable, maintainable, and properly integrated with the ONEX ecosystem.
