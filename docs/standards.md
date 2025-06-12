<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: standards.md
version: 1.0.0
uuid: 5e7c3f06-1e06-4515-90d3-02612f1754d0
author: OmniNode Team
created_at: 2025-05-27T06:04:38.298445
last_modified_at: 2025-05-27T17:26:51.842558
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 5d0548a4bfac33f2825e57da46502a623cc00fb57fbac037f3e5524ffe6ee8f0
entrypoint: python@standards.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.standards
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Development Standards

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
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
│       │   └── node_tree_generator/
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

- [Testing Guidelines](./testing.md)
- [Developer Guide](./developer_guide.md)
- [Contributing Guidelines](./contributing.md)
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

## Logging and Traceability Standards

### Overview
All ONEX nodes must implement comprehensive logging and traceability to enable debugging, monitoring, and audit trails. This section defines the canonical patterns for structured logging, event tracing, and field summarization.

### Core Traceability Fields

#### Required Fields (All Events)
All log events and state models must include these core fields:

```python
from omnibase.model.model_semver import SemVerModel
from omnibase.enums import LogLevelEnum, OnexStatus

class BaseTraceableModel(BaseModel):
    """Base model with required traceability fields."""
    
    # Schema and versioning
    schema_version: SemVerModel = Field(
        default_factory=lambda: SemVerModel.parse("1.0.0"),
        description="Schema version for forward compatibility"
    )
    
    # Core identification
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when the event occurred"
    )
    node_name: str = Field(..., description="Name of the source node or service")
    node_version: SemVerModel = Field(..., description="Version of the source node")
    
    # Event classification
    event_type: str = Field(..., description="Type of event (error, info, audit, metric)")
    severity: LogLevelEnum = Field(..., description="Log severity level")
```

#### Contextual Fields (Strongly Recommended)
These fields provide valuable context for understanding event relationships:

```python
class ContextualTraceableModel(BaseTraceableModel):
    """Extended model with contextual traceability fields."""
    
    # Event relationships
    event_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this specific event"
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="ID shared across related events for grouping"
    )
    parent_event_id: Optional[str] = Field(
        default=None,
        description="ID of the immediate preceding event in causality chain"
    )
    
    # Distributed tracing
    trace_id: Optional[str] = Field(
        default=None,
        description="Distributed tracing ID (OpenTelemetry compatible)"
    )
    span_id: Optional[str] = Field(
        default=None,
        description="Span ID for distributed tracing"
    )
    
    # User/session context
    request_id: Optional[str] = Field(default=None, description="Request identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    
    # Business context
    operation: Optional[str] = Field(
        default=None,
        description="Business operation or action being performed"
    )
    tags: Optional[Dict[str, str]] = Field(
        default=None,
        description="Custom context tags for filtering and analysis"
    )
```

#### Extended Metadata (Optional)
For infrastructure monitoring and debugging:

```python
class ExtendedTraceableModel(ContextualTraceableModel):
    """Full model with extended metadata fields."""
    
    # Infrastructure context
    host: Optional[str] = Field(default=None, description="Hostname of the source machine")
    container_id: Optional[str] = Field(default=None, description="Container ID if applicable")
    pod_name: Optional[str] = Field(default=None, description="Kubernetes pod name")
    
    # Error context
    error_code: Optional[str] = Field(default=None, description="Specific error code")
    exception_type: Optional[str] = Field(default=None, description="Exception type")
    stack_trace: Optional[str] = Field(
        default=None,
        description="Stack trace (subject to summarization)"
    )
```

### Field Summarization Pattern

#### Summarization Utility
For long optional fields that may contain large amounts of data:

```python
from typing import Optional, Dict, Any

def summarize_long_field(
    content: str, 
    max_length: int = 2048,
    summary_mode: str = "head_tail"
) -> Dict[str, Any]:
    """
    Summarize long field content with metadata.
    
    Args:
        content: Original content to summarize
        max_length: Maximum allowed length before summarization
        summary_mode: Summarization strategy ("head_tail", "hash", "truncate")
    
    Returns:
        Dictionary with summarized content and metadata
    """
    if len(content) <= max_length:
        return {"content": content, "truncated": False}
    
    if summary_mode == "head_tail":
        head_size = max_length // 2 - 50
        tail_size = max_length // 2 - 50
        summary = f"{content[:head_size]}\n... [TRUNCATED {len(content) - max_length} chars] ...\n{content[-tail_size:]}"
    elif summary_mode == "hash":
        import hashlib
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        summary = f"[CONTENT_HASH: {content_hash}, LENGTH: {len(content)}]"
    else:  # truncate
        summary = content[:max_length] + "... [TRUNCATED]"
    
    return {
        "content": summary,
        "truncated": True,
        "original_length": len(content),
        "summary_mode": summary_mode
    }

# Usage in models
class LogEventModel(BaseModel):
    message: str
    stack_trace: Optional[Dict[str, Any]] = None
    
    @field_validator("stack_trace", mode="before")
    @classmethod
    def summarize_stack_trace(cls, v):
        if isinstance(v, str):
            return summarize_long_field(v, max_length=1024)
        return v
```

#### Runtime Tool Integration
The ONEX runtime provides a dedicated field summarization tool for production use:

```python
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_field_summarization import (
    tool_field_summarization
)
from omnibase.runtimes.onex_runtime.v1_0_0.protocol.tool_field_summarization_protocol import (
    FieldSummarizationRequest,
    BatchSummarizationRequest
)

# Single field summarization
request = FieldSummarizationRequest(
    content="Very long error message or stack trace...",
    max_length=1024,
    summary_mode="head_tail"
)
result = tool_field_summarization.summarize_field(request)

print(f"Summarized: {result.content}")
print(f"Truncated: {result.truncated}")
print(f"Original length: {result.original_length}")

# Batch field summarization
log_data = {
    "message": "Operation completed",
    "error_details": "x" * 5000,  # Very long error details
    "stack_trace": "y" * 3000,   # Long stack trace
    "status": "error"
}

field_config = {
    "error_details": {"max_length": 500, "summary_mode": "head_tail"},
    "stack_trace": {"max_length": 800, "summary_mode": "hash"}
}

batch_request = BatchSummarizationRequest(
    data=log_data,
    field_config=field_config
)
batch_result = tool_field_summarization.summarize_batch(batch_request)

# Access summarized data
summarized_data = batch_result.data
metadata = batch_result.summarization_metadata

# Check if fields were truncated
if metadata["error_details"]["truncated"]:
    print(f"Error details truncated from {metadata['error_details']['original_length']} chars")
```

#### Summarization Modes

**head_tail Mode (Recommended)**
- Preserves beginning and end of content
- Shows truncation marker with character count
- Best for stack traces and error messages

**hash Mode**
- Replaces content with SHA256 hash and length
- Minimal space usage
- Best for large payloads where content preview isn't needed

**truncate Mode**
- Simple truncation with marker
- Fastest processing
- Best for simple text content

#### Integration with Pydantic Models

```python
from pydantic import BaseModel, field_validator

class ErrorEventModel(BaseModel):
    """Event model with automatic field summarization."""
    
    message: str
    error_details: Optional[str] = None
    stack_trace: Optional[str] = None
    
    @field_validator("error_details", mode="before")
    @classmethod
    def summarize_error_details(cls, v):
        if isinstance(v, str) and len(v) > 1024:
            request = FieldSummarizationRequest(
                content=v,
                max_length=1024,
                summary_mode="head_tail"
            )
            result = tool_field_summarization.summarize_field(request)
            return result.content
        return v
    
    @field_validator("stack_trace", mode="before")
    @classmethod
    def summarize_stack_trace(cls, v):
        if isinstance(v, str) and len(v) > 2048:
            request = FieldSummarizationRequest(
                content=v,
                max_length=2048,
                summary_mode="hash"
            )
            result = tool_field_summarization.summarize_field(request)
            return result.content
        return v
```

#### Configuration and Best Practices

**Field Length Limits**
- **Default:** 2048 characters for most fields
- **Stack traces:** 2048 characters (use hash mode for very long traces)
- **Error messages:** 1024 characters (use head_tail mode)
- **Debug output:** 512 characters (use truncate mode)

**Performance Considerations**
- Field summarization adds minimal overhead (~1ms per field)
- Hash mode is fastest, head_tail mode preserves most information
- Use batch processing for multiple fields to improve efficiency

**Monitoring and Alerts**
- Monitor summarization frequency to detect log bloat issues
- Alert when >10% of events require summarization
- Track original vs. summarized content ratios

### Correlation ID Propagation

#### Automatic Propagation
Ensure correlation IDs flow through all system components:

```python
from contextvars import ContextVar
from typing import Optional

# Context variable for correlation ID
correlation_context: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

def get_correlation_id() -> str:
    """Get current correlation ID or generate new one."""
    current_id = correlation_context.get()
    if current_id is None:
        current_id = str(uuid4())
        correlation_context.set(current_id)
    return current_id

def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current context."""
    correlation_context.set(correlation_id)

# Usage in event emission
def emit_event(event_type: str, message: str, **kwargs):
    """Emit event with automatic correlation ID."""
    correlation_id = kwargs.get('correlation_id') or get_correlation_id()
    
    event = OnexEvent(
        event_type=event_type,
        correlation_id=correlation_id,
        schema_version=SemVerModel.parse("1.0.0"),
        # ... other fields
    )
    event_bus.publish(event)
```

### Multi-Channel Logging Architecture

#### Channel Protocol
Define a protocol for different output channels:

```python
from typing import Protocol, List

class LogChannel(Protocol):
    """Protocol for log output channels."""
    
    def emit(self, event: OnexEvent) -> None:
        """Emit a log event to this channel."""
        ...
    
    def close(self) -> None:
        """Close the channel and cleanup resources."""
        ...

class MultiChannelLogger:
    """Logger that dispatches to multiple channels."""
    
    def __init__(self, channels: List[LogChannel]):
        self.channels = channels
    
    def emit(self, event: OnexEvent) -> None:
        """Emit event to all channels with error isolation."""
        for channel in self.channels:
            try:
                channel.emit(event)
            except Exception as e:
                # Log channel failure without causing cascade
                print(f"Channel {channel.__class__.__name__} failed: {e}", file=sys.stderr)
    
    def close(self) -> None:
        """Close all channels."""
        for channel in self.channels:
            try:
                channel.close()
            except Exception:
                pass  # Best effort cleanup
```

#### Channel Configuration
Configure logging channels via YAML:

```yaml
# config/logging.yaml
logging:
  channels:
    - type: kafka
      topic: onex_events
      bootstrap_servers: localhost:9092
      
    - type: file
      path: /var/log/onex/events.log
      rotation: daily
      
    - type: prometheus
      metric_filter: ["latency", "error_rate"]
      
  default_format: json
  correlation_ids: enabled
  field_summarization:
    max_length: 2048
    mode: head_tail
```

### Schema Evolution Policy

#### Versioning Strategy
- **Schema Version:** All models include `schema_version` field using SemVerModel
- **Backward Compatibility:** Minor versions must be backward compatible
- **Breaking Changes:** Major version increments for breaking changes
- **Migration:** Provide migration utilities for schema upgrades

```python
class SchemaVersionManager:
    """Manage schema version compatibility."""
    
    CURRENT_VERSION = SemVerModel.parse("1.0.0")
    SUPPORTED_VERSIONS = ["1.0.0"]
    
    @classmethod
    def is_compatible(cls, version: SemVerModel) -> bool:
        """Check if schema version is compatible."""
        return str(version) in cls.SUPPORTED_VERSIONS
    
    @classmethod
    def migrate_if_needed(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate data to current schema version if needed."""
        schema_version = data.get("schema_version", "1.0.0")
        if schema_version != str(cls.CURRENT_VERSION):
            # Perform migration logic
            data = cls._migrate_from_version(data, schema_version)
        return data
```

### Implementation Guidelines

#### Node Integration
All ONEX nodes must implement the traceability pattern:

1. **State Models:** Include traceability fields in input/output state models
2. **Event Emission:** Use structured logging for all significant events
3. **Error Handling:** Include correlation IDs in all error responses
4. **Configuration:** Support field summarization configuration

#### Testing Requirements
- **Traceability Tests:** Verify correlation ID propagation
- **Summarization Tests:** Test field summarization with oversized content
- **Schema Tests:** Validate schema version handling
- **Channel Tests:** Test multi-channel logging with failure scenarios

#### Performance Considerations
- **Lazy Evaluation:** Only generate expensive fields when needed
- **Caching:** Cache correlation IDs within request context
- **Batching:** Batch log events for high-throughput scenarios
- **Sampling:** Implement sampling for high-volume debug logs

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
