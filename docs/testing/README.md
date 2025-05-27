# ONEX Testing Guide

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Comprehensive testing guide for the ONEX ecosystem  
> **Audience:** Developers, test engineers, contributors  

---

## Overview

This directory contains canonical testing guidance for ONEX. The ONEX testing framework emphasizes protocol-driven development, registry swapping, and structured test organization to ensure reliability and maintainability across the ecosystem.

---

## Contents

- **[Fixtures Guidelines](./fixtures_guidelines.md)** - Comprehensive guide to organizing and managing test fixtures
- **[Node Testing Guidelines](./node_testing_guidelines.md)** - Specific guidance for testing ONEX nodes

---

## Canonical Testing Philosophy

ONEX testing emphasizes:

### Core Principles

1. **Protocol-First Testing**: All tests validate protocol compliance and behavior
2. **Registry Swapping**: Use dependency injection and fixture swapping for isolation
3. **Structured Organization**: Mirror `src/omnibase/` directory structure in tests
4. **No Test Markers**: Use directory structure and naming for test organization
5. **Contract Testing**: Validate that implementations follow defined protocols

### Testing Architecture

```
tests/
├── fixtures/                    # Shared fixtures and test data
│   ├── shared_fixture_*.py     # Common fixtures
│   └── data/                   # Shared test data
├── unit/                       # Unit tests mirroring src structure
│   ├── core/                   # Tests for core functionality
│   ├── nodes/                  # Tests for node implementations
│   └── protocols/              # Protocol compliance tests
├── integration/                # Integration tests
└── conftest.py                # Global test configuration
```

### Node-Local Testing

Each node maintains its own test suite:

```
src/omnibase/nodes/<node>/
├── tests/
│   ├── test_main.py           # Primary node tests
│   ├── fixtures/              # Node-specific fixtures
│   │   ├── <node>_fixture_*.py
│   │   └── data/              # Node-specific test data
│   └── conftest.py           # Node test configuration
```

---

## Key Testing Patterns

### Registry Swapping via Fixtures

```python
import pytest
from omnibase.core.registry import Registry

@pytest.fixture
def mock_registry():
    """Provide isolated registry for testing."""
    registry = Registry()
    # Setup test data
    return registry

def test_with_mock_registry(mock_registry):
    # Test uses isolated registry
    assert mock_registry.get_nodes() == []
```

### Protocol Compliance Testing

```python
from omnibase.protocols import NodeProtocol

def test_node_protocol_compliance(test_node):
    """Verify node implements required protocol."""
    assert isinstance(test_node, NodeProtocol)
    assert hasattr(test_node, 'execute')
    assert hasattr(test_node, 'introspect')
```

### Contract Testing

```python
def test_execution_contract(node, valid_input):
    """Test that node execution follows contract."""
    result = node.execute(valid_input)
    
    # Validate result structure
    assert hasattr(result, 'status')
    assert hasattr(result, 'output')
    assert result.status in ['success', 'failure', 'error']
```

---

## Testing Standards

### Coverage Requirements

- **Unit Tests**: >90% code coverage for all core components
- **Integration Tests**: Cover all major workflows and interactions
- **Protocol Tests**: 100% coverage of protocol compliance
- **Node Tests**: >85% coverage for each node implementation

### Quality Gates

- All tests must pass before merge
- No flaky tests allowed in main branch
- Performance tests must meet defined benchmarks
- Security tests must validate all security protocols

### Test Organization

- **Naming**: Use descriptive test names that explain the scenario
- **Structure**: Group related tests in classes or modules
- **Documentation**: Include docstrings explaining test purpose
- **Data**: Use fixtures for test data, avoid hardcoded values

---

## Running Tests

### Basic Test Execution

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/unit/core/test_registry.py

# Run with verbose output
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=src/omnibase
```

### Node-Specific Testing

```bash
# Run tests for specific node
poetry run pytest src/omnibase/nodes/stamper_node/tests/

# Run integration tests
poetry run pytest tests/integration/

# Run protocol compliance tests
poetry run pytest tests/unit/protocols/
```

### CI Testing

```bash
# Full test suite with coverage
poetry run pytest --cov=src/omnibase --cov-report=xml

# Performance tests
poetry run pytest -m performance

# Security tests
poetry run pytest -m security
```

---

## Test Development Guidelines

### Writing Effective Tests

1. **Test One Thing**: Each test should validate a single behavior
2. **Use Descriptive Names**: Test names should explain what is being tested
3. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and validation
4. **Use Fixtures**: Leverage fixtures for setup and teardown
5. **Mock External Dependencies**: Isolate units under test

### Example Test Structure

```python
def test_stamper_node_processes_valid_yaml_file():
    """Test that stamper node successfully processes valid YAML files."""
    # Arrange
    stamper = StamperNode()
    valid_yaml_path = "tests/fixtures/data/valid_metadata.yaml"
    
    # Act
    result = stamper.execute({"file_path": valid_yaml_path})
    
    # Assert
    assert result.status == "success"
    assert "metadata_block" in result.output
    assert result.output["metadata_block"]["hash"] is not None
```

### Error Testing

```python
def test_stamper_node_handles_invalid_yaml_gracefully():
    """Test that stamper node handles invalid YAML with proper error reporting."""
    # Arrange
    stamper = StamperNode()
    invalid_yaml_path = "tests/fixtures/data/invalid_syntax.yaml"
    
    # Act
    result = stamper.execute({"file_path": invalid_yaml_path})
    
    # Assert
    assert result.status == "error"
    assert "yaml_parse_error" in result.error_type
    assert result.error_message is not None
```

---

## Advanced Testing Topics

### Performance Testing

```python
import pytest
import time

@pytest.mark.performance
def test_stamper_performance_large_file():
    """Test stamper performance with large files."""
    start_time = time.time()
    
    # Execute test
    result = stamper.execute({"file_path": "large_test_file.yaml"})
    
    execution_time = time.time() - start_time
    
    assert result.status == "success"
    assert execution_time < 5.0  # Should complete within 5 seconds
```

### Security Testing

```python
@pytest.mark.security
def test_stamper_prevents_path_traversal():
    """Test that stamper prevents path traversal attacks."""
    malicious_path = "../../../etc/passwd"
    
    result = stamper.execute({"file_path": malicious_path})
    
    assert result.status == "error"
    assert "security_violation" in result.error_type
```

### Integration Testing

```python
def test_full_workflow_integration():
    """Test complete workflow from input to output."""
    # Setup complete environment
    registry = setup_test_registry()
    stamper = registry.get_node("stamper_node")
    validator = registry.get_node("validator_node")
    
    # Execute workflow
    stamp_result = stamper.execute(test_input)
    validation_result = validator.execute(stamp_result.output)
    
    # Validate end-to-end behavior
    assert stamp_result.status == "success"
    assert validation_result.status == "success"
```

---

## Troubleshooting

### Common Issues

#### Test Discovery Problems
```bash
# Ensure proper test file naming
pytest --collect-only

# Check for import issues
python -m pytest --tb=short
```

#### Fixture Issues
```bash
# Debug fixture loading
pytest --fixtures

# Verbose fixture output
pytest -v --setup-show
```

#### Performance Issues
```bash
# Profile test execution
pytest --durations=10

# Run specific slow tests
pytest -m slow
```

---

## References

- **[Testing Philosophy](../testing.md)** - Core testing principles and standards
- **[Structured Testing](../structured_testing.md)** - Protocol-driven testing framework
- **[Fixtures Guidelines](./fixtures_guidelines.md)** - Fixture organization and management
- **[Node Testing Guidelines](./node_testing_guidelines.md)** - Node-specific testing patterns
- **[Developer Guide](../developer_guide.md)** - Development best practices

---

**Note:** This testing framework is designed to ensure reliability, maintainability, and scalability across the entire ONEX ecosystem. Follow these guidelines to contribute high-quality, well-tested code. 