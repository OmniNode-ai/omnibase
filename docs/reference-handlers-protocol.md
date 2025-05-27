# ONEX Handler Protocols and Interfaces

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define protocols and interfaces for file type handlers in the ONEX ecosystem  
> **Audience:** Handler developers, system integrators  
> **See Also:** [Handler Registry](reference-handlers-registry.md), [Handler Implementation Guide](guide-handlers-implementation.md)

---

## Overview

This document defines the protocols and interfaces for file type handlers in the ONEX platform. Handlers are responsible for processing specific file types (Python, YAML, Markdown, etc.) and implementing operations like validation, stamping, and transformation.

---

## Handler Protocol

### Base Handler Protocol

```python
from typing import Protocol, List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

@dataclass
class HandlerResult:
    """Result of a handler operation."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = None

class FileHandlerProtocol(Protocol):
    """Protocol for file type handlers."""
    
    @property
    def name(self) -> str:
        """Handler name (e.g., 'python_handler')."""
        ...
    
    @property
    def file_extensions(self) -> List[str]:
        """Supported file extensions (e.g., ['.py', '.pyi'])."""
        ...
    
    @property
    def mime_types(self) -> List[str]:
        """Supported MIME types (e.g., ['text/x-python'])."""
        ...
    
    @property
    def version(self) -> str:
        """Handler version."""
        ...
    
    def can_handle(self, file_path: Path) -> bool:
        """Check if handler can process the given file."""
        ...
    
    def validate(self, file_path: Path) -> HandlerResult:
        """Validate file content and structure."""
        ...
    
    def stamp(self, file_path: Path, metadata: Dict[str, Any]) -> HandlerResult:
        """Add metadata stamp to file."""
        ...
    
    def extract_metadata(self, file_path: Path) -> HandlerResult:
        """Extract existing metadata from file."""
        ...
```

### Handler Capabilities

```python
from enum import Enum

class HandlerCapability(Enum):
    """Handler capabilities."""
    VALIDATE = "validate"           # Can validate file syntax/structure
    STAMP = "stamp"                # Can add metadata stamps
    EXTRACT = "extract"             # Can extract metadata
    TRANSFORM = "transform"         # Can transform file content
    LINT = "lint"                  # Can perform linting
    FORMAT = "format"              # Can format file content
    ANALYZE = "analyze"            # Can analyze file content

@dataclass
class HandlerMetadata:
    """Handler metadata and capabilities."""
    name: str
    version: str
    description: str
    author: str
    file_extensions: List[str]
    mime_types: List[str]
    capabilities: List[HandlerCapability]
    dependencies: List[str]
    configuration_schema: Optional[Dict[str, Any]] = None
```

---

## Extended Handler Protocols

### Validation Protocol

```python
class ValidationHandlerProtocol(FileHandlerProtocol, Protocol):
    """Protocol for handlers that support validation."""
    
    def validate_syntax(self, file_path: Path) -> HandlerResult:
        """Validate file syntax only."""
        ...
    
    def validate_structure(self, file_path: Path) -> HandlerResult:
        """Validate file structure and semantics."""
        ...
    
    def validate_schema(self, file_path: Path, schema: Dict[str, Any]) -> HandlerResult:
        """Validate file against provided schema."""
        ...
    
    def get_validation_rules(self) -> List[str]:
        """Get list of validation rules supported by this handler."""
        ...
```

### Transform Protocol

```python
class TransformHandlerProtocol(FileHandlerProtocol, Protocol):
    """Protocol for handlers that support transformation."""
    
    def transform(self, file_path: Path, target_format: str, **options) -> HandlerResult:
        """Transform file to target format."""
        ...
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported transformation formats."""
        ...
    
    def can_transform_to(self, target_format: str) -> bool:
        """Check if handler can transform to target format."""
        ...
```

### Formatting Protocol

```python
class FormattingHandlerProtocol(FileHandlerProtocol, Protocol):
    """Protocol for handlers that support code formatting."""
    
    def format_file(self, file_path: Path, **options) -> HandlerResult:
        """Format file content according to style rules."""
        ...
    
    def check_formatting(self, file_path: Path) -> HandlerResult:
        """Check if file is properly formatted."""
        ...
    
    def get_formatting_options(self) -> Dict[str, Any]:
        """Get available formatting options."""
        ...
```

### Linting Protocol

```python
class LintingHandlerProtocol(FileHandlerProtocol, Protocol):
    """Protocol for handlers that support linting."""
    
    def lint(self, file_path: Path, **options) -> HandlerResult:
        """Perform linting on file."""
        ...
    
    def get_lint_rules(self) -> List[str]:
        """Get list of available lint rules."""
        ...
    
    def configure_linting(self, rules: Dict[str, Any]) -> bool:
        """Configure linting rules."""
        ...
```

---

## Handler Configuration

### Configuration Schema

```python
@dataclass
class HandlerConfiguration:
    """Handler configuration."""
    handler_name: str
    enabled: bool = True
    priority: int = 100
    options: Dict[str, Any] = None
    
    def validate(self) -> bool:
        """Validate configuration."""
        if self.priority < 0 or self.priority > 1000:
            return False
        return True

class ConfigurableHandlerProtocol(FileHandlerProtocol, Protocol):
    """Protocol for configurable handlers."""
    
    def configure(self, config: HandlerConfiguration) -> bool:
        """Configure handler with provided configuration."""
        ...
    
    def get_configuration(self) -> HandlerConfiguration:
        """Get current handler configuration."""
        ...
    
    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get JSON schema for handler configuration."""
        ...
    
    def validate_configuration(self, config: Dict[str, Any]) -> HandlerResult:
        """Validate configuration against schema."""
        ...
```

---

## Handler Lifecycle

### Lifecycle Protocol

```python
from enum import Enum

class HandlerState(Enum):
    """Handler lifecycle states."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    DISABLED = "disabled"

class LifecycleHandlerProtocol(FileHandlerProtocol, Protocol):
    """Protocol for handlers with lifecycle management."""
    
    @property
    def state(self) -> HandlerState:
        """Current handler state."""
        ...
    
    def initialize(self) -> HandlerResult:
        """Initialize handler resources."""
        ...
    
    def shutdown(self) -> HandlerResult:
        """Shutdown handler and cleanup resources."""
        ...
    
    def health_check(self) -> HandlerResult:
        """Check handler health status."""
        ...
    
    def reset(self) -> HandlerResult:
        """Reset handler to initial state."""
        ...
```

---

## Handler Composition

### Composite Handler Protocol

```python
class CompositeHandlerProtocol(
    ValidationHandlerProtocol,
    TransformHandlerProtocol,
    FormattingHandlerProtocol,
    LintingHandlerProtocol,
    ConfigurableHandlerProtocol,
    LifecycleHandlerProtocol,
    Protocol
):
    """Composite protocol for full-featured handlers."""
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations."""
        ...
    
    def supports_operation(self, operation: str) -> bool:
        """Check if handler supports specific operation."""
        ...
```

### Handler Adapter

```python
class HandlerAdapter:
    """Adapter for legacy handlers."""
    
    def __init__(self, legacy_handler: Any):
        self.legacy_handler = legacy_handler
    
    def adapt_to_protocol(self) -> FileHandlerProtocol:
        """Adapt legacy handler to FileHandlerProtocol."""
        class AdaptedHandler:
            def __init__(self, handler):
                self._handler = handler
            
            @property
            def name(self) -> str:
                return getattr(self._handler, 'name', 'unknown')
            
            @property
            def file_extensions(self) -> List[str]:
                return getattr(self._handler, 'extensions', [])
            
            @property
            def mime_types(self) -> List[str]:
                return getattr(self._handler, 'mime_types', [])
            
            @property
            def version(self) -> str:
                return getattr(self._handler, 'version', '1.0.0')
            
            def can_handle(self, file_path: Path) -> bool:
                if hasattr(self._handler, 'can_handle'):
                    return self._handler.can_handle(file_path)
                return file_path.suffix in self.file_extensions
            
            def validate(self, file_path: Path) -> HandlerResult:
                if hasattr(self._handler, 'validate'):
                    result = self._handler.validate(file_path)
                    if isinstance(result, HandlerResult):
                        return result
                    return HandlerResult(success=bool(result), message=str(result))
                return HandlerResult(success=True, message="Validation not supported")
            
            def stamp(self, file_path: Path, metadata: Dict[str, Any]) -> HandlerResult:
                if hasattr(self._handler, 'stamp'):
                    result = self._handler.stamp(file_path, metadata)
                    if isinstance(result, HandlerResult):
                        return result
                    return HandlerResult(success=bool(result), message=str(result))
                return HandlerResult(success=False, message="Stamping not supported")
            
            def extract_metadata(self, file_path: Path) -> HandlerResult:
                if hasattr(self._handler, 'extract_metadata'):
                    result = self._handler.extract_metadata(file_path)
                    if isinstance(result, HandlerResult):
                        return result
                    return HandlerResult(success=True, message="Metadata extracted", data=result)
                return HandlerResult(success=False, message="Metadata extraction not supported")
        
        return AdaptedHandler(self.legacy_handler)
```

---

## Handler Validation

### Protocol Compliance

```python
class HandlerValidator:
    """Validator for handler protocol compliance."""
    
    @staticmethod
    def validate_handler(handler: FileHandlerProtocol) -> HandlerResult:
        """Validate handler implementation."""
        errors = []
        
        # Check required properties
        try:
            name = handler.name
            if not name or not isinstance(name, str):
                errors.append("Handler name must be a non-empty string")
        except Exception as e:
            errors.append(f"Handler name property error: {e}")
        
        try:
            extensions = handler.file_extensions
            if not isinstance(extensions, list) or not extensions:
                errors.append("Handler must support at least one file extension")
        except Exception as e:
            errors.append(f"File extensions property error: {e}")
        
        try:
            mime_types = handler.mime_types
            if not isinstance(mime_types, list):
                errors.append("MIME types must be a list")
        except Exception as e:
            errors.append(f"MIME types property error: {e}")
        
        try:
            version = handler.version
            if not version or not isinstance(version, str):
                errors.append("Handler version must be a non-empty string")
        except Exception as e:
            errors.append(f"Handler version property error: {e}")
        
        # Check required methods
        required_methods = ['can_handle', 'validate', 'stamp', 'extract_metadata']
        for method_name in required_methods:
            if not hasattr(handler, method_name):
                errors.append(f"Handler missing required method: {method_name}")
            elif not callable(getattr(handler, method_name)):
                errors.append(f"Handler {method_name} is not callable")
        
        return HandlerResult(
            success=len(errors) == 0,
            message="Handler validation completed",
            errors=errors
        )
    
    @staticmethod
    def validate_metadata(metadata: HandlerMetadata) -> HandlerResult:
        """Validate handler metadata."""
        errors = []
        
        if not metadata.name:
            errors.append("Handler name is required")
        
        if not metadata.version:
            errors.append("Handler version is required")
        
        if not metadata.file_extensions:
            errors.append("At least one file extension is required")
        
        if not metadata.capabilities:
            errors.append("At least one capability is required")
        
        # Validate version format
        import re
        version_pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'
        if metadata.version and not re.match(version_pattern, metadata.version):
            errors.append("Invalid version format (expected: major.minor.patch)")
        
        return HandlerResult(
            success=len(errors) == 0,
            message="Metadata validation completed",
            errors=errors
        )
```

---

## See Also

- [Handler Registry](reference-handlers-registry.md) - Registry API and management
- [Handler Implementation Guide](guide-handlers-implementation.md) - Implementation examples and testing
- [Registry Specification](registry.md) - Core registry concepts
- [File Type Standards](standards.md) - File type conventions 