# ONEX Development Standards

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define comprehensive development standards, naming conventions, file organization, and coding practices for the ONEX ecosystem  
> **Audience:** All contributors, maintainers, and developers  
> **Enforcement:** Required for all contributions, enforced in CI/CD and code review

---

## Overview

This document establishes the canonical development standards for the ONEX ecosystem. All code, documentation, and artifacts must conform to these standards to ensure consistency, maintainability, and professional quality across the entire platform.

---

## Naming Conventions

### File and Directory Naming

#### Python Files and Directories
- **Format:** All lowercase with underscores (`snake_case`)
- **Prefix Pattern:** Use functional prefixes to indicate purpose and scope
- **No camelCase or PascalCase** in filenames (except for legacy compatibility)

#### Reserved Prefixes

| Prefix | Purpose | Examples |
|--------|---------|----------|
| `core_` | Core system components | `core_registry.py`, `core_protocols.py` |
| `protocol_` | Protocol definitions | `protocol_execution.py`, `protocol_validation.py` |
| `cli_` | CLI tools and entrypoints | `cli_main.py`, `cli_validator.py` |
| `test_` | Test files | `test_registry.py`, `test_validation.py` |
| `template_` | Template files | `template_node.py`, `template_validator.py` |
| `node_` | Node implementations | `node_stamper.py`, `node_validator.py` |
| `handler_` | File type handlers | `handler_python.py`, `handler_yaml.py` |
| `schema_` | Schema definitions | `schema_node.py`, `schema_metadata.py` |

#### Examples

```
# Correct naming
src/omnibase/core/core_registry.py
src/omnibase/protocols/protocol_execution.py
src/omnibase/cli_tools/cli_main.py
tests/test_core_registry.py
templates/template_validator_node.py

# Incorrect naming
src/omnibase/core/Registry.py          # PascalCase
src/omnibase/core/coreRegistry.py      # camelCase
src/omnibase/core/registry-core.py     # hyphens
```

### Schema and Data Files
- **Format:** Lowercase with hyphens for YAML/JSON files
- **Extension:** Use appropriate extensions (`.yaml`, `.json`, `.md`)

```
# Schema files
schemas/onex-node.yaml
schemas/execution-result.json
schemas/state-contract.json

# Configuration files
config/development.yaml
config/production.yaml
```

### Directory Structure Standards

```
project-root/
├── src/
│   └── omnibase/
│       ├── core/                    # Core system components
│       │   ├── core_registry.py
│       │   ├── core_protocols.py
│       │   └── core_execution.py
│       ├── protocols/               # Protocol definitions
│       │   ├── protocol_execution.py
│       │   └── protocol_validation.py
│       ├── cli_tools/              # CLI implementations
│       │   ├── cli_main.py
│       │   └── cli_validator.py
│       ├── nodes/                  # Node implementations
│       │   ├── stamper_node/
│       │   ├── validator_node/
│       │   └── tree_generator_node/
│       ├── handlers/               # File type handlers
│       │   ├── handler_python.py
│       │   └── handler_yaml.py
│       └── templates/              # Template files
│           ├── template_node.py
│           └── template_validator.py
├── tests/                          # Test files
│   ├── test_core_registry.py
│   ├── test_protocols.py
│   └── integration/
├── docs/                           # Documentation
│   ├── index.md
│   ├── quickstart.md
│   └── api/
├── schemas/                        # Schema definitions
│   ├── onex-node.yaml
│   └── execution-result.json
└── config/                         # Configuration files
    ├── development.yaml
    └── production.yaml
```

---

## Code Style Standards

### Python Code Standards

#### PEP 8 Compliance
- **Line Length:** Maximum 88 characters (Black formatter standard)
- **Indentation:** 4 spaces (no tabs)
- **Imports:** Organized using isort with Black compatibility
- **Docstrings:** Google-style docstrings for all public functions and classes

#### Import Organization

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Protocol

# Third-party imports
import click
import yaml
from pydantic import BaseModel

# Local imports
from omnibase.core.core_registry import Registry
from omnibase.protocols.protocol_execution import ExecutionProtocol
```

#### Type Annotations
- **Required:** All function signatures must include type annotations
- **Return Types:** Always specify return types
- **Complex Types:** Use `typing` module for complex types

```python
from typing import Dict, List, Optional, Union

def process_nodes(
    nodes: List[str], 
    config: Dict[str, Any], 
    strict_mode: bool = False
) -> Dict[str, Union[str, int]]:
    """Process a list of nodes with given configuration.
    
    Args:
        nodes: List of node names to process
        config: Configuration dictionary
        strict_mode: Whether to use strict validation
        
    Returns:
        Dictionary containing processing results
        
    Raises:
        ValidationError: If node validation fails
    """
    pass
```

#### Error Handling
- **Specific Exceptions:** Use specific exception types, not bare `except:`
- **Error Messages:** Include context and actionable information
- **Logging:** Use structured logging for all error conditions

```python
import logging
from omnibase.core.exceptions import ValidationError, RegistryError

logger = logging.getLogger(__name__)

def validate_node(node_path: str) -> bool:
    try:
        # Validation logic
        pass
    except FileNotFoundError as e:
        logger.error(
            "Node file not found",
            extra={
                "node_path": node_path,
                "error": str(e)
            }
        )
        raise ValidationError(f"Node file not found: {node_path}") from e
    except Exception as e:
        logger.error(
            "Unexpected error during validation",
            extra={
                "node_path": node_path,
                "error_type": type(e).__name__,
                "error": str(e)
            }
        )
        raise
```

### Documentation Standards

#### Markdown Standards
- **Headers:** Use ATX-style headers (`#`, `##`, `###`)
- **Code Blocks:** Always specify language for syntax highlighting
- **Links:** Use reference-style links for better maintainability
- **Tables:** Use GitHub Flavored Markdown table syntax

#### Documentation Structure

```markdown
# Document Title

> **Status:** [Draft|Active|Deprecated]  
> **Last Updated:** YYYY-MM-DD  
> **Purpose:** Brief description of document purpose  
> **Audience:** Target audience  

---

## Overview

Brief overview of the document content.

---

## Section 1

Content with proper formatting.

### Subsection

More detailed content.

```language
code examples
```

---

## References

- [Related Document](./related.md)
- [External Link](https://example.com)
```

---

## Testing Standards

### Test File Organization
- **Location:** Tests mirror source structure in `tests/` directory
- **Naming:** Test files prefixed with `test_`
- **Structure:** Group tests by functionality, not by file

```
tests/
├── test_core_registry.py
├── test_protocols.py
├── integration/
│   ├── test_cli_integration.py
│   └── test_node_execution.py
├── fixtures/
│   ├── sample_nodes/
│   └── test_data.yaml
└── conftest.py
```

### Test Implementation Standards

#### Test Naming
- **Format:** `test_<functionality>_<condition>_<expected_result>`
- **Descriptive:** Test names should clearly describe what is being tested

```python
def test_registry_register_node_with_valid_metadata_succeeds():
    """Test that registering a node with valid metadata succeeds."""
    pass

def test_registry_register_node_with_invalid_uuid_raises_validation_error():
    """Test that registering a node with invalid UUID raises ValidationError."""
    pass
```

#### Test Structure
- **Arrange-Act-Assert:** Follow AAA pattern
- **Fixtures:** Use pytest fixtures for test data and setup
- **Mocking:** Mock external dependencies, not internal logic

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def sample_node_metadata():
    """Provide sample node metadata for testing."""
    return {
        "name": "test_node",
        "version": "1.0.0",
        "uuid": "550e8400-e29b-41d4-a716-446655440000"
    }

def test_registry_register_node_success(sample_node_metadata):
    # Arrange
    registry = Registry()
    
    # Act
    result = registry.register_node(sample_node_metadata)
    
    # Assert
    assert result.success is True
    assert result.node_id == sample_node_metadata["uuid"]
```

---

## Configuration Standards

### Configuration File Format
- **Primary Format:** YAML for human-readable configuration
- **Schema Validation:** All configuration files must have corresponding schemas
- **Environment Overrides:** Support environment variable overrides

#### Configuration Structure

```yaml
# config/development.yaml
environment: development

logging:
  level: debug
  format: json
  handlers:
    - console
    - file

registry:
  backend: filesystem
  path: ./registry
  cache_enabled: true

validation:
  strict_mode: false
  error_categories:
    - schema
    - metadata
    - lifecycle

nodes:
  discovery_paths:
    - src/omnibase/nodes
    - ~/.onex/nodes
  auto_reload: true
```

### Environment Variables
- **Naming:** Use `ONEX_` prefix for all environment variables
- **Format:** UPPERCASE with underscores
- **Mapping:** Follow configuration hierarchy

```bash
# Environment variable mapping
ONEX_ENVIRONMENT=production
ONEX_LOGGING_LEVEL=info
ONEX_REGISTRY_BACKEND=redis
ONEX_REGISTRY_URL=redis://localhost:6379
ONEX_VALIDATION_STRICT_MODE=true
```

---

## Version Control Standards

### Git Workflow
- **Branching:** Use feature branches for all changes
- **Commits:** Follow conventional commit format
- **Pull Requests:** Required for all changes to main branch

#### Commit Message Format

```
<type>(<scope>): <description>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(registry): add node discovery caching

Implement LRU cache for node discovery to improve performance
during repeated lookups. Cache size is configurable via
ONEX_REGISTRY_CACHE_SIZE environment variable.

Closes #123
```

### Branch Naming
- **Format:** `<type>/<description>`
- **Examples:** `feat/node-caching`, `fix/validation-error`, `docs/api-reference`

---

## Security Standards

### Code Security
- **Input Validation:** Validate all external inputs
- **Secrets Management:** Never commit secrets to version control
- **Dependencies:** Regularly update and audit dependencies
- **Permissions:** Follow principle of least privilege

#### Secure Coding Practices

```python
import secrets
from pathlib import Path
from typing import Optional

def load_secret(secret_name: str) -> Optional[str]:
    """Load secret from secure location.
    
    Args:
        secret_name: Name of the secret to load
        
    Returns:
        Secret value if found, None otherwise
    """
    # Check environment first
    env_value = os.getenv(f"ONEX_SECRET_{secret_name.upper()}")
    if env_value:
        return env_value
    
    # Check secure file location
    secret_path = Path("/run/secrets") / secret_name
    if secret_path.exists():
        return secret_path.read_text().strip()
    
    return None

def generate_correlation_id() -> str:
    """Generate cryptographically secure correlation ID."""
    return secrets.token_urlsafe(16)
```

---

## Performance Standards

### Code Performance
- **Complexity:** Avoid O(n²) algorithms where possible
- **Memory Usage:** Use generators for large datasets
- **Caching:** Implement appropriate caching strategies
- **Profiling:** Profile performance-critical code paths

#### Performance Guidelines

```python
from functools import lru_cache
from typing import Iterator, List

@lru_cache(maxsize=128)
def expensive_computation(input_data: str) -> str:
    """Cached expensive computation."""
    # Expensive operation here
    pass

def process_large_dataset(data: List[str]) -> Iterator[str]:
    """Process large dataset using generator for memory efficiency."""
    for item in data:
        yield process_item(item)

# Use generator expressions for memory efficiency
processed_items = (process_item(item) for item in large_list)
```

### Resource Management
- **File Handles:** Always use context managers for file operations
- **Network Connections:** Implement connection pooling
- **Memory:** Monitor memory usage in long-running processes

```python
from contextlib import contextmanager
from pathlib import Path

@contextmanager
def safe_file_operation(file_path: Path, mode: str = 'r'):
    """Safe file operation with proper resource cleanup."""
    file_handle = None
    try:
        file_handle = file_path.open(mode)
        yield file_handle
    finally:
        if file_handle:
            file_handle.close()

# Usage
with safe_file_operation(Path("data.txt")) as f:
    content = f.read()
```

---

## Quality Assurance Standards

### Code Quality Metrics
- **Test Coverage:** Minimum 80% code coverage
- **Complexity:** Maximum cyclomatic complexity of 10
- **Documentation:** All public APIs must be documented
- **Type Coverage:** 100% type annotation coverage

### Automated Quality Checks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=88", "--extend-ignore=E203,W503"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML]
```

### CI/CD Quality Gates

```yaml
# Quality gates in CI
quality_checks:
  - name: "Code formatting"
    command: "black --check src/"
    
  - name: "Import sorting"
    command: "isort --check-only src/"
    
  - name: "Linting"
    command: "flake8 src/"
    
  - name: "Type checking"
    command: "mypy src/"
    
  - name: "Test coverage"
    command: "pytest --cov=src --cov-report=term-missing --cov-fail-under=80"
    
  - name: "Security scan"
    command: "bandit -r src/"
```

---

## Documentation Standards

### API Documentation
- **Format:** Use Google-style docstrings
- **Coverage:** Document all public functions, classes, and modules
- **Examples:** Include usage examples in docstrings
- **Type Information:** Include parameter and return types

```python
def register_node(
    self, 
    node_metadata: Dict[str, Any], 
    validate: bool = True
) -> RegistrationResult:
    """Register a new node in the registry.
    
    This method validates the node metadata and adds it to the registry.
    If validation is enabled, the metadata is checked against the schema
    before registration.
    
    Args:
        node_metadata: Dictionary containing node metadata including
            name, version, uuid, and other required fields.
        validate: Whether to validate metadata before registration.
            Defaults to True.
    
    Returns:
        RegistrationResult containing success status, node ID, and
        any validation errors.
    
    Raises:
        ValidationError: If metadata validation fails and validate=True.
        RegistryError: If registration fails due to registry issues.
    
    Example:
        >>> registry = Registry()
        >>> metadata = {
        ...     "name": "my_node",
        ...     "version": "1.0.0",
        ...     "uuid": "550e8400-e29b-41d4-a716-446655440000"
        ... }
        >>> result = registry.register_node(metadata)
        >>> print(result.success)
        True
    """
    pass
```

### User Documentation
- **Structure:** Follow consistent document structure
- **Examples:** Provide practical, working examples
- **Cross-references:** Link related documents
- **Maintenance:** Keep documentation up-to-date with code changes

---

## Deployment Standards

### Container Standards
- **Base Images:** Use official, minimal base images
- **Security:** Run containers as non-root users
- **Health Checks:** Implement health check endpoints
- **Resource Limits:** Set appropriate resource limits

```dockerfile
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r onex && useradd -r -g onex onex

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Set ownership
RUN chown -R onex:onex /app

# Switch to non-root user
USER onex

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000
CMD ["python", "-m", "src.omnibase.cli_tools.cli_main"]
```

### Environment Configuration
- **Separation:** Separate configuration for each environment
- **Secrets:** Use secure secret management
- **Monitoring:** Include monitoring configuration
- **Backup:** Implement backup and recovery procedures

---

## Compliance and Governance

### Code Review Standards
- **Required Reviews:** All changes require at least one review
- **Review Checklist:** Use standardized review checklist
- **Automated Checks:** All automated checks must pass
- **Documentation:** Update documentation with code changes

#### Review Checklist

- [ ] Code follows naming conventions
- [ ] All functions have type annotations
- [ ] Tests cover new functionality
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced
- [ ] Performance impact considered
- [ ] Error handling is appropriate
- [ ] Logging is adequate

### Release Standards
- **Versioning:** Follow semantic versioning (SemVer)
- **Changelog:** Maintain detailed changelog
- **Testing:** All tests must pass before release
- **Documentation:** Update version-specific documentation

---

## Tool Configuration

### Development Tools

#### Black (Code Formatting)
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

#### isort (Import Sorting)
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["omnibase"]
known_third_party = ["click", "yaml", "pydantic"]
```

#### MyPy (Type Checking)
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
```

#### Pytest (Testing)
```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests"
]
```

---

## Enforcement

### Automated Enforcement
- **Pre-commit Hooks:** Enforce standards before commit
- **CI/CD Pipeline:** Validate standards in CI
- **Code Review:** Manual review for compliance
- **Quality Gates:** Block deployment on standard violations

### Manual Review
- **Checklist:** Use standardized review checklist
- **Training:** Provide training on standards
- **Documentation:** Maintain up-to-date standards documentation
- **Feedback:** Provide constructive feedback on violations

---

## References

- [Python PEP 8](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

**Note:** These standards are living documents and will evolve with the project. All changes to standards must be reviewed and approved by the maintainer team. 