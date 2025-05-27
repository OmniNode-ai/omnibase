<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: developer_guide.md
version: 1.0.0
uuid: ecf521a9-f6c4-428f-8584-0cd4c43e1903
author: OmniNode Team
created_at: 2025-05-27T05:46:58.623821
last_modified_at: 2025-05-27T17:26:51.838966
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: e4ccc965a826c1c4f4532839c906c728cd52916918fefa246b0d91d936fc1448
entrypoint: python@developer_guide.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.developer_guide
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# OmniBase Developer Guide

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Audience:** Contributors implementing core interfaces, validators, tools, plugins, and infrastructure nodes  
> **Purpose:** Guidelines for Protocol vs ABC usage, protocol-driven development, and pull request standards

---

## Overview

This guide provides essential patterns and conventions for developing within the ONEX ecosystem. It covers when to use Protocols vs Abstract Base Classes, how to implement protocol-driven engines, and the standards for contributing code.

---

## Protocols vs Abstract Base Classes (ABCs)

### When to Use Each

| Use Case | Protocol | ABC |
|----------|----------|-----|
| Third-party plugin interfaces | ✅ Yes | ❌ No |
| Internal base class with shared logic | ❌ No | ✅ Yes |
| Interface contract based on method shape only | ✅ Yes | ❌ No |
| Requires subclassing enforcement or `super()` logic | ❌ No | ✅ Yes |
| Behavior-first pattern, runtime agnostic | ✅ Yes | ❌ No |
| Static typing + duck-typed implementation | ✅ Yes | ❌ No |
| Cross-boundary usage (tools, agents, plugins) | ✅ Yes | ❌ No |
| Tight control over subclass lifecycle | ❌ No | ✅ Yes |

### Use `Protocol` When...

#### 1. Defining Interfaces Across Plugin or Tool Boundaries

Use `Protocol` when you want to define *capabilities* or *contracts* that third-party code or tools will implement **without requiring inheritance**.

```python
from typing import Protocol

class ProtocolValidate(Protocol):
    def validate(self, path: str) -> bool: ...
```

This allows:
- Structural typing (`hasattr()`-style compatibility)
- Lightweight contracts
- Flexible mocking and test fakes

#### 2. You Don't Control All Implementations

Use protocols when the implementations may live:
- In user-injected agents
- In external packages
- In plugin discovery registries

### Use `ABC` When...

#### 1. You Require Subclassing with Shared Behavior

Use `ABC` when:
- You need to share logic across subclasses.
- You want to enforce inheritance (e.g., internal base node scaffolds).
- You need `@abstractmethod` enforcement and `super()` semantics.

```python
from abc import ABC, abstractmethod

class OmniBaseNode(ABC):
    @abstractmethod
    def execute(self): ...

    def log_metadata(self):
        print(self.__class__.__name__)
```

---

## Concrete Guidelines

### Tooling Interfaces (e.g., CLI, Stamp, Validate)
→ Use `Protocol`

### Validator and Registry APIs
→ Use `Protocol` for registration, plugin loading, and schema access  
→ Use `ABC` only if subclassing internally (e.g., default error-handling behavior)

### Reducer Interfaces
→ Use `Protocol` unless base classes will provide concrete reducer logic  
→ ABCs allowed for stateful node types later in ONEX

---

## Protocol-Driven Development

### Protocol-Driven Engines and Registry Exposure

When implementing a new tool or validator (e.g., the ONEX Metadata Stamper):

1. **Define core logic as a Python Protocol** (see [Core Protocols](./reference-protocols-core.md))
2. **Register protocol-driven engines** in the protocol registry to enable dynamic discovery and selection at runtime or via CLI
3. **Expose all dependencies** via constructor or fixture injection—never hardcode or use global state
4. **Ensure test harnesses use fixture-injectable engines**, supporting both real and in-memory/mock contexts for context-agnostic testing

See [docs/testing.md](./testing.md) for canonical registry and fixture-injection patterns.

### Example Protocol Implementation

```python
from typing import Protocol, List
from pathlib import Path

class StamperEngine(Protocol):
    """Protocol for metadata stamping engines"""
    
    def stamp_file(self, file_path: Path) -> bool:
        """Stamp a single file with metadata"""
        ...
    
    def stamp_directory(self, directory: Path, patterns: List[str]) -> int:
        """Stamp all matching files in directory"""
        ...
    
    def validate_stamp(self, file_path: Path) -> bool:
        """Validate existing stamp in file"""
        ...

class RealStamperEngine:
    """Real implementation that works with filesystem"""
    
    def __init__(self, config_manager, file_handler):
        self.config = config_manager
        self.file_handler = file_handler
    
    def stamp_file(self, file_path: Path) -> bool:
        # Implementation using real file I/O
        pass

class InMemoryStamperEngine:
    """In-memory implementation for testing"""
    
    def __init__(self, mock_filesystem):
        self.fs = mock_filesystem
    
    def stamp_file(self, file_path: Path) -> bool:
        # Implementation using mock filesystem
        pass

# Registry registration
from omnibase.registry import ProtocolRegistry

registry = ProtocolRegistry()
registry.register_engine("stamper", RealStamperEngine(config, file_handler))
registry.register_engine("stamper_test", InMemoryStamperEngine(mock_fs))
```

---

## Development Patterns

### Dependency Injection

Always use dependency injection for external dependencies:

```python
# ❌ Bad: Hardcoded dependencies
class MyValidator:
    def validate(self, path: str) -> bool:
        with open(path, 'r') as f:  # Hardcoded file I/O
            content = f.read()
        return self._check_content(content)

# ✅ Good: Injected dependencies
class MyValidator:
    def __init__(self, file_reader: FileReader):
        self.file_reader = file_reader
    
    def validate(self, path: str) -> bool:
        content = self.file_reader.read(path)
        return self._check_content(content)
```

### Registry Integration

Register all components in the appropriate registry:

```python
from omnibase.registry import ValidatorRegistry

class MyValidator:
    def validate(self, path: str) -> bool:
        # Implementation
        pass

# Register the validator
registry = ValidatorRegistry()
registry.register("my_validator", MyValidator(file_reader))
```

### Error Handling

Use structured error types from the OmniBase error hierarchy:

```python
from omnibase.errors import ValidationError, OmniBaseError

class MyValidator:
    def validate(self, path: str) -> bool:
        try:
            # Validation logic
            pass
        except FileNotFoundError:
            raise ValidationError(
                error_code="VALIDATOR_ERROR_001",
                message=f"File not found: {path}",
                suggestions=["Check file path", "Ensure file exists"]
            )
        except Exception as e:
            raise OmniBaseError(f"Unexpected error: {e}")
```

---

## Testing Guidelines

### Protocol-Based Testing

Use protocol-based testing for maximum flexibility:

```python
import pytest
from typing import Protocol

class ValidatorProtocol(Protocol):
    def validate(self, path: str) -> bool: ...

def test_validator_with_protocol(validator: ValidatorProtocol):
    """Test that works with any validator implementation"""
    result = validator.validate("test_file.py")
    assert isinstance(result, bool)

# Test with real implementation
def test_real_validator():
    validator = RealValidator(file_reader=RealFileReader())
    test_validator_with_protocol(validator)

# Test with mock implementation
def test_mock_validator():
    validator = MockValidator()
    test_validator_with_protocol(validator)
```

### Fixture Injection

Use fixture injection for test dependencies:

```python
@pytest.fixture
def file_reader():
    return MockFileReader()

@pytest.fixture
def validator(file_reader):
    return MyValidator(file_reader)

def test_validator_success(validator):
    result = validator.validate("valid_file.py")
    assert result is True
```

---

## Pull Request Standards

### Pull Request Template

All contributors must use the canonical pull request template for every PR. The template enforces:

- **Summary**: Clear description of the change and its context
- **Type of change**: Feature, bugfix, docs, refactor, CI
- **Details**: Specific changes, testing approach, and documentation updates
- **Reviewer guidance**: How to review and test the changes
- **Issue linkage**: Connection to related issues or milestones

### Template Structure

```markdown
## Summary
Brief description of what this PR does and why.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] CI/CD changes

## Changes Made
- Specific change 1
- Specific change 2
- Specific change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] All tests pass

## Documentation
- [ ] Code comments updated
- [ ] Documentation updated
- [ ] Examples updated (if applicable)

## Reviewer Notes
Specific guidance for reviewers on what to focus on.

## Related Issues
Closes #123
Related to #456
```

### Enforcement

- The PR template is auto-populated by GitHub for all new PRs
- CI checks validate that PRs follow the required structure
- Deviations must be justified and may block merge until resolved

---

## Code Quality Standards

### Type Annotations

All production code must include type annotations:

```python
from typing import List, Optional, Dict, Any

def process_files(
    file_paths: List[str], 
    config: Dict[str, Any],
    dry_run: bool = False
) -> Optional[List[str]]:
    """Process files with given configuration"""
    if dry_run:
        return None
    
    results: List[str] = []
    for path in file_paths:
        result = process_single_file(path, config)
        results.append(result)
    
    return results
```

### Documentation Standards

Use comprehensive docstrings with examples:

```python
def validate_metadata(file_path: str, schema: Dict[str, Any]) -> bool:
    """Validate metadata block against schema.
    
    Args:
        file_path: Path to file containing metadata
        schema: Pydantic schema for validation
        
    Returns:
        True if metadata is valid, False otherwise
        
    Raises:
        ValidationError: If metadata format is invalid
        FileNotFoundError: If file doesn't exist
        
    Example:
        >>> schema = {"type": "validator", "version": "1.0.0"}
        >>> validate_metadata("my_file.py", schema)
        True
    """
    # Implementation
    pass
```

### Naming Conventions

Follow the project naming conventions:

- **Files/directories**: lowercase with underscores (`my_validator.py`)
- **Functions/variables**: snake_case (`validate_file`)
- **Classes**: PascalCase (`MyValidator`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- **Private methods**: leading underscore (`_internal_method`)

---

## CLI Integration

### Adding CLI Commands

When adding new CLI commands to the ONEX CLI:

1. **Add command to CLI main**: Update `src/omnibase/cli_tools/onex/v1_0_0/cli_main.py`
2. **Implement command logic**: Create dedicated command modules
3. **Add help text**: Provide comprehensive help and examples
4. **Write tests**: Include both unit and integration tests
5. **Update documentation**: Add to CLI documentation

### Example CLI Command

```python
import click
from omnibase.registry import get_registry

@click.command()
@click.argument('node_name')
@click.option('--version', help='Specific version to run')
@click.option('--args', help='Arguments to pass to node (JSON format)')
def run_node(node_name: str, version: str = None, args: str = None):
    """Run a registered ONEX node"""
    registry = get_registry()
    node = registry.resolve(node_name, version)
    
    if args:
        import json
        parsed_args = json.loads(args)
        result = node.execute(*parsed_args)
    else:
        result = node.execute()
    
    click.echo(f"Node execution result: {result}")
```

---

## Best Practices Summary

### For Protocol Design

1. **Use Protocols for interfaces**: Especially cross-boundary interfaces
2. **Use ABCs for shared behavior**: When you need inheritance and shared logic
3. **Keep protocols minimal**: Focus on essential methods only
4. **Document protocol contracts**: Clear docstrings explaining expected behavior

### For Implementation

1. **Inject dependencies**: Never hardcode external dependencies
2. **Register components**: Use appropriate registries for discovery
3. **Handle errors gracefully**: Use structured error types
4. **Write comprehensive tests**: Cover both success and failure cases

### For Contributions

1. **Follow the PR template**: Use the canonical template for all PRs
2. **Include type annotations**: All production code must be typed
3. **Write documentation**: Code comments and user-facing docs
4. **Test thoroughly**: Unit, integration, and manual testing

---

## References

- [PEP 544 – Structural Subtyping via Protocols](https://peps.python.org/pep-0544/)
- [Typing Extensions: Protocols](https://typing.readthedocs.io/en/latest/source/protocol.html)
- [abc — Abstract Base Classes](https://docs.python.org/3/library/abc.html)
- [Core Protocols](./reference-protocols-core.md) - Core protocol definitions
- [Registry Protocols](./reference-protocols-registry.md) - Registry and validation protocols
- [docs/testing.md](./testing.md) - Testing guidelines
- [docs/contributing.md](./contributing.md) - Contribution workflow

---

> Use `Protocol` for any interface that could be implemented outside the core, and `ABC` when you're implementing a concrete subclass pattern inside it.
