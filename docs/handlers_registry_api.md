# ONEX Handlers Registry API

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the API for registering, discovering, and managing file type handlers in the ONEX ecosystem  
> **Audience:** Handler developers, system integrators, platform maintainers  
> **Companion:** [Registry Specification](./registry.md)

---

## Overview

The Handlers Registry API provides a centralized system for managing file type handlers in the ONEX platform. Handlers are responsible for processing specific file types (Python, YAML, Markdown, etc.) and implementing operations like validation, stamping, and transformation.

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

## Registry API

### Handler Registration

#### Register Handler

```python
class HandlerRegistry:
    """Registry for file type handlers."""
    
    def register_handler(
        self, 
        handler: FileHandlerProtocol,
        metadata: HandlerMetadata
    ) -> HandlerResult:
        """Register a new file handler.
        
        Args:
            handler: Handler implementation
            metadata: Handler metadata and capabilities
            
        Returns:
            Result indicating success or failure
            
        Raises:
            HandlerRegistrationError: If registration fails
        """
        # Validate handler implementation
        validation_result = self._validate_handler(handler, metadata)
        if not validation_result.success:
            return validation_result
        
        # Check for conflicts
        conflicts = self._check_conflicts(handler, metadata)
        if conflicts:
            return HandlerResult(
                success=False,
                message=f"Handler conflicts detected: {conflicts}",
                errors=conflicts
            )
        
        # Register handler
        handler_id = self._generate_handler_id(metadata.name, metadata.version)
        self._handlers[handler_id] = {
            "handler": handler,
            "metadata": metadata,
            "registered_at": datetime.utcnow(),
            "status": "active"
        }
        
        # Update indexes
        self._update_indexes(handler_id, metadata)
        
        return HandlerResult(
            success=True,
            message=f"Handler {metadata.name} registered successfully",
            data={"handler_id": handler_id}
        )
```

#### Unregister Handler

```python
def unregister_handler(self, handler_id: str) -> HandlerResult:
    """Unregister a file handler.
    
    Args:
        handler_id: Unique handler identifier
        
    Returns:
        Result indicating success or failure
    """
    if handler_id not in self._handlers:
        return HandlerResult(
            success=False,
            message=f"Handler {handler_id} not found"
        )
    
    # Check if handler is in use
    if self._is_handler_in_use(handler_id):
        return HandlerResult(
            success=False,
            message=f"Handler {handler_id} is currently in use"
        )
    
    # Remove handler
    handler_info = self._handlers.pop(handler_id)
    self._remove_from_indexes(handler_id, handler_info["metadata"])
    
    return HandlerResult(
        success=True,
        message=f"Handler {handler_id} unregistered successfully"
    )
```

### Handler Discovery

#### Find Handlers by File Type

```python
def find_handlers_for_file(self, file_path: Path) -> List[HandlerMetadata]:
    """Find all handlers that can process the given file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        List of handler metadata for compatible handlers
    """
    compatible_handlers = []
    
    # Get file extension and MIME type
    file_extension = file_path.suffix.lower()
    mime_type = self._get_mime_type(file_path)
    
    for handler_id, handler_info in self._handlers.items():
        metadata = handler_info["metadata"]
        handler = handler_info["handler"]
        
        # Check extension compatibility
        if file_extension in metadata.file_extensions:
            compatible_handlers.append(metadata)
            continue
        
        # Check MIME type compatibility
        if mime_type in metadata.mime_types:
            compatible_handlers.append(metadata)
            continue
        
        # Check handler's can_handle method
        if handler.can_handle(file_path):
            compatible_handlers.append(metadata)
    
    # Sort by priority (most specific first)
    return self._sort_handlers_by_priority(compatible_handlers, file_path)
```

#### Find Handlers by Capability

```python
def find_handlers_by_capability(
    self, 
    capability: HandlerCapability,
    file_extension: Optional[str] = None
) -> List[HandlerMetadata]:
    """Find handlers with specific capability.
    
    Args:
        capability: Required capability
        file_extension: Optional file extension filter
        
    Returns:
        List of handler metadata with the capability
    """
    matching_handlers = []
    
    for handler_id, handler_info in self._handlers.items():
        metadata = handler_info["metadata"]
        
        # Check capability
        if capability not in metadata.capabilities:
            continue
        
        # Check file extension if specified
        if file_extension and file_extension not in metadata.file_extensions:
            continue
        
        matching_handlers.append(metadata)
    
    return matching_handlers
```

#### Get Handler Details

```python
def get_handler(self, handler_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed handler information.
    
    Args:
        handler_id: Handler identifier
        
    Returns:
        Handler information or None if not found
    """
    if handler_id not in self._handlers:
        return None
    
    handler_info = self._handlers[handler_id]
    return {
        "handler_id": handler_id,
        "metadata": handler_info["metadata"],
        "registered_at": handler_info["registered_at"],
        "status": handler_info["status"],
        "usage_stats": self._get_usage_stats(handler_id)
    }
```

### Handler Execution

#### Execute Handler Operation

```python
def execute_handler_operation(
    self,
    handler_id: str,
    operation: str,
    file_path: Path,
    **kwargs
) -> HandlerResult:
    """Execute a handler operation.
    
    Args:
        handler_id: Handler identifier
        operation: Operation name (validate, stamp, extract, etc.)
        file_path: Target file path
        **kwargs: Additional operation parameters
        
    Returns:
        Operation result
    """
    if handler_id not in self._handlers:
        return HandlerResult(
            success=False,
            message=f"Handler {handler_id} not found"
        )
    
    handler_info = self._handlers[handler_id]
    handler = handler_info["handler"]
    metadata = handler_info["metadata"]
    
    # Check if handler supports the operation
    operation_capability = self._operation_to_capability(operation)
    if operation_capability not in metadata.capabilities:
        return HandlerResult(
            success=False,
            message=f"Handler {handler_id} does not support {operation}"
        )
    
    # Execute operation
    try:
        if operation == "validate":
            result = handler.validate(file_path)
        elif operation == "stamp":
            stamp_metadata = kwargs.get("metadata", {})
            result = handler.stamp(file_path, stamp_metadata)
        elif operation == "extract":
            result = handler.extract_metadata(file_path)
        else:
            # Try to call operation method dynamically
            operation_method = getattr(handler, operation, None)
            if operation_method:
                result = operation_method(file_path, **kwargs)
            else:
                return HandlerResult(
                    success=False,
                    message=f"Operation {operation} not supported"
                )
        
        # Update usage statistics
        self._update_usage_stats(handler_id, operation, result.success)
        
        return result
        
    except Exception as e:
        return HandlerResult(
            success=False,
            message=f"Handler operation failed: {str(e)}",
            errors=[str(e)]
        )
```

---

## Built-in Handlers

### Python Handler

```python
class PythonHandler:
    """Handler for Python files (.py, .pyi)."""
    
    @property
    def name(self) -> str:
        return "python_handler"
    
    @property
    def file_extensions(self) -> List[str]:
        return [".py", ".pyi"]
    
    @property
    def mime_types(self) -> List[str]:
        return ["text/x-python", "application/x-python"]
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a Python file."""
        if file_path.suffix.lower() in self.file_extensions:
            return True
        
        # Check shebang for Python scripts
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                return first_line.startswith('#!') and 'python' in first_line
        except (UnicodeDecodeError, IOError):
            return False
    
    def validate(self, file_path: Path) -> HandlerResult:
        """Validate Python syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Parse AST to check syntax
            ast.parse(source, filename=str(file_path))
            
            return HandlerResult(
                success=True,
                message="Python syntax is valid"
            )
            
        except SyntaxError as e:
            return HandlerResult(
                success=False,
                message=f"Python syntax error: {e.msg}",
                errors=[f"Line {e.lineno}: {e.msg}"]
            )
        except Exception as e:
            return HandlerResult(
                success=False,
                message=f"Validation failed: {str(e)}",
                errors=[str(e)]
            )
    
    def stamp(self, file_path: Path, metadata: Dict[str, Any]) -> HandlerResult:
        """Add metadata stamp to Python file."""
        try:
            # Read existing content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate metadata comment
            stamp_comment = self._generate_metadata_comment(metadata)
            
            # Insert stamp after module docstring or at beginning
            modified_content = self._insert_stamp(content, stamp_comment)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return HandlerResult(
                success=True,
                message="Metadata stamp added successfully"
            )
            
        except Exception as e:
            return HandlerResult(
                success=False,
                message=f"Stamping failed: {str(e)}",
                errors=[str(e)]
            )
    
    def extract_metadata(self, file_path: Path) -> HandlerResult:
        """Extract metadata from Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to extract metadata
            tree = ast.parse(content)
            metadata = {}
            
            # Extract module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) 
                and isinstance(tree.body[0].value, ast.Str)):
                metadata["docstring"] = tree.body[0].value.s
            
            # Extract metadata comments
            stamp_metadata = self._extract_stamp_metadata(content)
            if stamp_metadata:
                metadata.update(stamp_metadata)
            
            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    imports.extend([f"{module}.{alias.name}" for alias in node.names])
            
            metadata["imports"] = imports
            
            return HandlerResult(
                success=True,
                message="Metadata extracted successfully",
                data=metadata
            )
            
        except Exception as e:
            return HandlerResult(
                success=False,
                message=f"Metadata extraction failed: {str(e)}",
                errors=[str(e)]
            )
```

### YAML Handler

```python
class YAMLHandler:
    """Handler for YAML files (.yaml, .yml)."""
    
    @property
    def name(self) -> str:
        return "yaml_handler"
    
    @property
    def file_extensions(self) -> List[str]:
        return [".yaml", ".yml"]
    
    @property
    def mime_types(self) -> List[str]:
        return ["application/x-yaml", "text/yaml"]
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a YAML file."""
        return file_path.suffix.lower() in self.file_extensions
    
    def validate(self, file_path: Path) -> HandlerResult:
        """Validate YAML syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            
            return HandlerResult(
                success=True,
                message="YAML syntax is valid"
            )
            
        except yaml.YAMLError as e:
            return HandlerResult(
                success=False,
                message=f"YAML syntax error: {str(e)}",
                errors=[str(e)]
            )
        except Exception as e:
            return HandlerResult(
                success=False,
                message=f"Validation failed: {str(e)}",
                errors=[str(e)]
            )
    
    def stamp(self, file_path: Path, metadata: Dict[str, Any]) -> HandlerResult:
        """Add metadata stamp to YAML file."""
        try:
            # Read existing content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML
            data = yaml.safe_load(content) or {}
            
            # Add metadata section
            if "_onex_metadata" not in data:
                data["_onex_metadata"] = {}
            
            data["_onex_metadata"].update(metadata)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            return HandlerResult(
                success=True,
                message="Metadata stamp added successfully"
            )
            
        except Exception as e:
            return HandlerResult(
                success=False,
                message=f"Stamping failed: {str(e)}",
                errors=[str(e)]
            )
    
    def extract_metadata(self, file_path: Path) -> HandlerResult:
        """Extract metadata from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            # Extract ONEX metadata
            metadata = data.get("_onex_metadata", {})
            
            # Extract schema information
            if "$schema" in data:
                metadata["schema"] = data["$schema"]
            
            # Extract top-level keys as structure info
            metadata["structure"] = {
                "top_level_keys": list(data.keys()),
                "total_keys": len(data)
            }
            
            return HandlerResult(
                success=True,
                message="Metadata extracted successfully",
                data=metadata
            )
            
        except Exception as e:
            return HandlerResult(
                success=False,
                message=f"Metadata extraction failed: {str(e)}",
                errors=[str(e)]
            )
```

---

## Handler Configuration

### Configuration Schema

```yaml
# Handler configuration schema
handler_config:
  python_handler:
    enabled: true
    priority: 10
    options:
      check_syntax: true
      check_imports: true
      stamp_location: "after_docstring"
      metadata_format: "comment"
  
  yaml_handler:
    enabled: true
    priority: 10
    options:
      validate_schema: true
      preserve_comments: true
      stamp_location: "metadata_section"
      sort_keys: false
  
  markdown_handler:
    enabled: true
    priority: 5
    options:
      validate_links: true
      check_frontmatter: true
      stamp_location: "frontmatter"
      preserve_formatting: true
```

### Dynamic Configuration

```python
class HandlerConfiguration:
    """Handler configuration management."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("handler_config.yaml")
        self.config = self._load_config()
    
    def get_handler_config(self, handler_name: str) -> Dict[str, Any]:
        """Get configuration for specific handler."""
        return self.config.get(handler_name, {})
    
    def update_handler_config(
        self, 
        handler_name: str, 
        config: Dict[str, Any]
    ) -> None:
        """Update handler configuration."""
        self.config[handler_name] = config
        self._save_config()
    
    def is_handler_enabled(self, handler_name: str) -> bool:
        """Check if handler is enabled."""
        handler_config = self.get_handler_config(handler_name)
        return handler_config.get("enabled", True)
    
    def get_handler_priority(self, handler_name: str) -> int:
        """Get handler priority."""
        handler_config = self.get_handler_config(handler_name)
        return handler_config.get("priority", 0)
```

---

## CLI Integration

### Handler Management Commands

```bash
# List all registered handlers
onex handlers list

# List handlers for specific file type
onex handlers list --file-type python

# Get detailed handler information
onex handlers info --handler-name python_handler

# Test handler on specific file
onex handlers test --handler-name yaml_handler --file config.yaml

# Register new handler
onex handlers register --handler-path ./my_handler.py --config ./handler_config.yaml

# Unregister handler
onex handlers unregister --handler-name my_handler

# Enable/disable handler
onex handlers enable --handler-name python_handler
onex handlers disable --handler-name python_handler

# Update handler configuration
onex handlers config --handler-name yaml_handler --set validate_schema=false
```

### Handler Operations

```bash
# Validate file using specific handler
onex handlers validate --handler python_handler --file script.py

# Stamp file with metadata
onex handlers stamp --handler yaml_handler --file config.yaml --metadata '{"version": "1.0.0"}'

# Extract metadata from file
onex handlers extract --handler python_handler --file module.py

# Find compatible handlers for file
onex handlers find --file unknown_file.ext
```

---

## Error Handling

### Handler-Specific Errors

```python
class HandlerError(Exception):
    """Base exception for handler errors."""
    pass

class HandlerRegistrationError(HandlerError):
    """Handler registration failed."""
    pass

class HandlerNotFoundError(HandlerError):
    """Handler not found."""
    pass

class HandlerOperationError(HandlerError):
    """Handler operation failed."""
    pass

class HandlerConfigurationError(HandlerError):
    """Handler configuration error."""
    pass
```

### Error Codes

| Code | Category | Description |
|------|----------|-------------|
| HR001 | Registration | Handler already registered |
| HR002 | Registration | Invalid handler implementation |
| HR003 | Registration | Handler metadata validation failed |
| HR004 | Discovery | No compatible handlers found |
| HR005 | Discovery | Multiple handlers conflict |
| HR006 | Operation | Handler operation not supported |
| HR007 | Operation | Handler execution failed |
| HR008 | Configuration | Invalid handler configuration |

---

## Performance Considerations

### Handler Caching

```python
class CachedHandlerRegistry(HandlerRegistry):
    """Registry with caching for improved performance."""
    
    def __init__(self, cache_size: int = 1000):
        super().__init__()
        self._handler_cache = LRUCache(cache_size)
        self._result_cache = LRUCache(cache_size)
    
    def find_handlers_for_file(self, file_path: Path) -> List[HandlerMetadata]:
        """Find handlers with caching."""
        cache_key = f"handlers:{file_path.suffix}:{self._get_mime_type(file_path)}"
        
        if cache_key in self._handler_cache:
            return self._handler_cache[cache_key]
        
        handlers = super().find_handlers_for_file(file_path)
        self._handler_cache[cache_key] = handlers
        return handlers
```

### Lazy Loading

```python
class LazyHandlerRegistry(HandlerRegistry):
    """Registry with lazy handler loading."""
    
    def __init__(self):
        super().__init__()
        self._handler_factories = {}
        self._loaded_handlers = {}
    
    def register_handler_factory(
        self, 
        handler_name: str, 
        factory: Callable[[], FileHandlerProtocol]
    ) -> None:
        """Register handler factory for lazy loading."""
        self._handler_factories[handler_name] = factory
    
    def _get_handler(self, handler_name: str) -> FileHandlerProtocol:
        """Get handler, loading if necessary."""
        if handler_name not in self._loaded_handlers:
            if handler_name in self._handler_factories:
                self._loaded_handlers[handler_name] = self._handler_factories[handler_name]()
            else:
                raise HandlerNotFoundError(f"Handler {handler_name} not found")
        
        return self._loaded_handlers[handler_name]
```

---

## Testing

### Handler Testing Framework

```python
class HandlerTestCase:
    """Base class for handler tests."""
    
    def setUp(self):
        self.registry = HandlerRegistry()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """Create test file with content."""
        file_path = Path(self.temp_dir) / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def test_handler_registration(self):
        """Test handler registration."""
        handler = MockHandler()
        metadata = HandlerMetadata(
            name="test_handler",
            version="1.0.0",
            description="Test handler",
            author="Test",
            file_extensions=[".test"],
            mime_types=["text/test"],
            capabilities=[HandlerCapability.VALIDATE]
        )
        
        result = self.registry.register_handler(handler, metadata)
        assert result.success
    
    def test_handler_discovery(self):
        """Test handler discovery."""
        # Register test handler
        self.test_handler_registration()
        
        # Create test file
        test_file = self.create_test_file("test.test", "test content")
        
        # Find handlers
        handlers = self.registry.find_handlers_for_file(test_file)
        assert len(handlers) > 0
        assert handlers[0].name == "test_handler"
```

---

## References

- [Registry Specification](./registry.md)
- [File Type Standards](./standards.md#canonical-file-types)
- [CLI Interface](./cli_interface.md)
- [Error Handling](./error_handling.md)

---

**Note:** The Handlers Registry API is designed to be extensible and pluggable. New handlers can be easily added by implementing the `FileHandlerProtocol` and registering them with the registry. All handlers should follow the established patterns and conventions for consistency and reliability. 