# ONEX Handler Implementation Guide

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Implementation examples, CLI usage, and testing for ONEX file type handlers  
> **Audience:** Handler developers, implementers  
> **See Also:** [Handler Protocols](reference-handlers-protocol.md), [Handler Registry](reference-handlers-registry.md)

---

## Overview

This guide provides practical examples for implementing file type handlers, using the CLI interface, and testing handler implementations in the ONEX platform.

---

## Handler Implementation Examples

### Python Handler

```python
import ast
from typing import List, Dict, Any
from pathlib import Path

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
    
    def validate(self, file_path: Path) -> 'HandlerResult':
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
    
    def stamp(self, file_path: Path, metadata: Dict[str, Any]) -> 'HandlerResult':
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
    
    def extract_metadata(self, file_path: Path) -> 'HandlerResult':
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
    
    def _generate_metadata_comment(self, metadata: Dict[str, Any]) -> str:
        """Generate metadata comment block."""
        lines = ["# ONEX Metadata"]
        for key, value in metadata.items():
            lines.append(f"# {key}: {value}")
        lines.append("# End ONEX Metadata")
        return "\n".join(lines) + "\n"
    
    def _insert_stamp(self, content: str, stamp: str) -> str:
        """Insert stamp into Python file content."""
        lines = content.split('\n')
        
        # Find insertion point (after module docstring or at beginning)
        insert_index = 0
        
        # Skip shebang and encoding declarations
        for i, line in enumerate(lines):
            if line.startswith('#!') or 'coding:' in line or 'encoding:' in line:
                insert_index = i + 1
            else:
                break
        
        # Check for module docstring
        if insert_index < len(lines):
            try:
                # Simple check for triple-quoted string at beginning
                remaining_content = '\n'.join(lines[insert_index:])
                tree = ast.parse(remaining_content)
                if (tree.body and isinstance(tree.body[0], ast.Expr) 
                    and isinstance(tree.body[0].value, ast.Str)):
                    # Find end of docstring
                    docstring_lines = tree.body[0].value.s.count('\n') + 1
                    insert_index += docstring_lines + 2  # Account for quotes
            except:
                pass  # If parsing fails, insert at current position
        
        # Insert stamp
        stamp_lines = stamp.rstrip().split('\n')
        lines[insert_index:insert_index] = stamp_lines + ['']
        
        return '\n'.join(lines)
    
    def _extract_stamp_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from stamp comments."""
        metadata = {}
        lines = content.split('\n')
        
        in_metadata = False
        for line in lines:
            line = line.strip()
            if line == "# ONEX Metadata":
                in_metadata = True
                continue
            elif line == "# End ONEX Metadata":
                break
            elif in_metadata and line.startswith('#'):
                # Parse metadata line
                line = line[1:].strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
        
        return metadata
```

### YAML Handler

```python
import yaml
from typing import List, Dict, Any
from pathlib import Path

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
    
    def validate(self, file_path: Path) -> 'HandlerResult':
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
    
    def stamp(self, file_path: Path, metadata: Dict[str, Any]) -> 'HandlerResult':
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
    
    def extract_metadata(self, file_path: Path) -> 'HandlerResult':
        """Extract metadata from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            # Extract ONEX metadata
            metadata = data.get("_onex_metadata", {})
            
            # Add file-level metadata
            metadata.update({
                "keys": list(data.keys()),
                "structure_depth": self._calculate_depth(data),
                "has_lists": self._has_lists(data),
                "has_nested_objects": self._has_nested_objects(data)
            })
            
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
    
    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum depth of nested structure."""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
    
    def _has_lists(self, obj: Any) -> bool:
        """Check if structure contains lists."""
        if isinstance(obj, list):
            return True
        elif isinstance(obj, dict):
            return any(self._has_lists(v) for v in obj.values())
        return False
    
    def _has_nested_objects(self, obj: Any) -> bool:
        """Check if structure contains nested objects."""
        if isinstance(obj, dict):
            for v in obj.values():
                if isinstance(v, (dict, list)):
                    return True
                if self._has_nested_objects(v):
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    return True
                if self._has_nested_objects(item):
                    return True
        return False
```

---

## CLI Usage Examples

### Handler Management Commands

```bash
# List all registered handlers
onex handlers list

# List handlers with detailed information
onex handlers list --detailed

# List handlers by capability
onex handlers list --capability validate

# List handlers by file extension
onex handlers list --extension .py

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

# Process file with handler
onex handlers process --handler markdown_handler --file README.md --operation format

# Batch process files
onex handlers batch --handler python_handler --operation validate --pattern "**/*.py"
```

### Advanced CLI Usage

```bash
# Register handler with custom configuration
onex handlers register \
  --handler-path ./handlers/custom_handler.py \
  --name custom_handler \
  --version 1.0.0 \
  --extensions .custom,.cust \
  --capabilities validate,stamp,transform \
  --config-file ./custom_handler_config.yaml

# Test handler with specific options
onex handlers test \
  --handler-name python_handler \
  --file test_script.py \
  --options '{"strict_mode": true, "check_imports": false}'

# Get handler statistics
onex handlers stats

# Export handler configuration
onex handlers export --handler-name yaml_handler --output yaml_handler_config.json

# Import handler configuration
onex handlers import --config-file exported_handlers.json

# Validate handler implementation
onex handlers validate-implementation --handler-path ./new_handler.py
```

---

## Performance Considerations

### Handler Caching

```python
from functools import lru_cache
from typing import Dict, Any

class CachedHandlerRegistry:
    """Registry with caching for improved performance."""
    
    def __init__(self, cache_size: int = 1000):
        super().__init__()
        self._handler_cache = {}
        self._result_cache = {}
        self._cache_size = cache_size
    
    @lru_cache(maxsize=1000)
    def find_handlers_for_file(self, file_path: Path) -> List['HandlerMetadata']:
        """Find handlers with caching."""
        cache_key = f"handlers:{file_path.suffix}:{self._get_mime_type(file_path)}"
        
        if cache_key in self._handler_cache:
            return self._handler_cache[cache_key]
        
        handlers = super().find_handlers_for_file(file_path)
        self._handler_cache[cache_key] = handlers
        return handlers
    
    def _cache_handler_result(
        self, 
        handler_id: str, 
        operation: str, 
        file_path: Path, 
        result: 'HandlerResult'
    ) -> None:
        """Cache handler operation result."""
        cache_key = f"{handler_id}:{operation}:{file_path}:{file_path.stat().st_mtime}"
        self._result_cache[cache_key] = result
        
        # Limit cache size
        if len(self._result_cache) > self._cache_size:
            # Remove oldest entries
            oldest_keys = list(self._result_cache.keys())[:100]
            for key in oldest_keys:
                del self._result_cache[key]
    
    def _get_cached_result(
        self, 
        handler_id: str, 
        operation: str, 
        file_path: Path
    ) -> Optional['HandlerResult']:
        """Get cached handler result."""
        cache_key = f"{handler_id}:{operation}:{file_path}:{file_path.stat().st_mtime}"
        return self._result_cache.get(cache_key)
```

### Lazy Loading

```python
class LazyHandlerRegistry:
    """Registry with lazy handler loading."""
    
    def __init__(self):
        super().__init__()
        self._handler_factories = {}
        self._loaded_handlers = {}
    
    def register_handler_factory(
        self, 
        handler_name: str, 
        factory: Callable[[], 'FileHandlerProtocol']
    ) -> None:
        """Register handler factory for lazy loading."""
        self._handler_factories[handler_name] = factory
    
    def _get_handler(self, handler_name: str) -> 'FileHandlerProtocol':
        """Get handler, loading if necessary."""
        if handler_name not in self._loaded_handlers:
            if handler_name in self._handler_factories:
                self._loaded_handlers[handler_name] = self._handler_factories[handler_name]()
            else:
                raise HandlerNotFoundError(f"Handler {handler_name} not found")
        
        return self._loaded_handlers[handler_name]
    
    def unload_handler(self, handler_name: str) -> None:
        """Unload handler to free memory."""
        if handler_name in self._loaded_handlers:
            handler = self._loaded_handlers[handler_name]
            if hasattr(handler, 'shutdown'):
                handler.shutdown()
            del self._loaded_handlers[handler_name]
```

---

## Testing Framework

### Handler Testing Framework

```python
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator

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
    
    def test_handler_operations(self):
        """Test handler operations."""
        # Register and get handler
        self.test_handler_registration()
        handler = self.registry.get_handler("test_handler@1.0.0")
        assert handler is not None
        
        # Create test file
        test_file = self.create_test_file("test.test", "valid content")
        
        # Test validation
        result = handler.validate(test_file)
        assert isinstance(result, HandlerResult)
        
        # Test stamping
        metadata = {"test_key": "test_value"}
        result = handler.stamp(test_file, metadata)
        assert isinstance(result, HandlerResult)
        
        # Test metadata extraction
        result = handler.extract_metadata(test_file)
        assert isinstance(result, HandlerResult)

class MockHandler:
    """Mock handler for testing."""
    
    @property
    def name(self) -> str:
        return "mock_handler"
    
    @property
    def file_extensions(self) -> List[str]:
        return [".test"]
    
    @property
    def mime_types(self) -> List[str]:
        return ["text/test"]
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix == ".test"
    
    def validate(self, file_path: Path) -> 'HandlerResult':
        return HandlerResult(success=True, message="Mock validation passed")
    
    def stamp(self, file_path: Path, metadata: Dict[str, Any]) -> 'HandlerResult':
        return HandlerResult(success=True, message="Mock stamping completed")
    
    def extract_metadata(self, file_path: Path) -> 'HandlerResult':
        return HandlerResult(
            success=True, 
            message="Mock metadata extracted",
            data={"mock_key": "mock_value"}
        )

# Pytest fixtures
@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """Fixture for temporary directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def handler_registry() -> HandlerRegistry:
    """Fixture for handler registry."""
    return HandlerRegistry()

@pytest.fixture
def mock_handler() -> MockHandler:
    """Fixture for mock handler."""
    return MockHandler()

# Example test using fixtures
def test_python_handler_validation(temp_directory):
    """Test Python handler validation."""
    handler = PythonHandler()
    
    # Test valid Python file
    valid_file = temp_directory / "valid.py"
    valid_file.write_text("print('Hello, World!')")
    
    result = handler.validate(valid_file)
    assert result.success
    assert "valid" in result.message
    
    # Test invalid Python file
    invalid_file = temp_directory / "invalid.py"
    invalid_file.write_text("print('Hello, World!'")  # Missing closing quote
    
    result = handler.validate(invalid_file)
    assert not result.success
    assert "syntax error" in result.message.lower()

def test_yaml_handler_stamping(temp_directory):
    """Test YAML handler stamping."""
    handler = YAMLHandler()
    
    # Create YAML file
    yaml_file = temp_directory / "test.yaml"
    yaml_file.write_text("key: value\nlist:\n  - item1\n  - item2")
    
    # Test stamping
    metadata = {"version": "1.0.0", "author": "test"}
    result = handler.stamp(yaml_file, metadata)
    assert result.success
    
    # Verify metadata was added
    import yaml
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    assert "_onex_metadata" in data
    assert data["_onex_metadata"]["version"] == "1.0.0"
    assert data["_onex_metadata"]["author"] == "test"
```

---

## Best Practices

### Handler Development Guidelines

1. **Error Handling**: Always return `HandlerResult` objects with appropriate success/failure status
2. **File Safety**: Use temporary files for modifications and atomic operations
3. **Encoding**: Always specify UTF-8 encoding when reading/writing files
4. **Performance**: Implement caching for expensive operations
5. **Testing**: Write comprehensive tests for all handler operations
6. **Documentation**: Document handler capabilities and configuration options
7. **Validation**: Validate inputs and provide meaningful error messages
8. **Compatibility**: Support multiple file formats and versions when possible

### Configuration Management

```python
# Example handler configuration schema
HANDLER_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "enabled": {"type": "boolean", "default": True},
        "priority": {"type": "integer", "minimum": 0, "maximum": 1000, "default": 100},
        "options": {
            "type": "object",
            "properties": {
                "strict_validation": {"type": "boolean", "default": False},
                "auto_format": {"type": "boolean", "default": False},
                "backup_files": {"type": "boolean", "default": True}
            }
        }
    }
}
```

---

## See Also

- [Handler Protocols](reference-handlers-protocol.md) - Handler protocols and interfaces
- [Handler Registry](reference-handlers-registry.md) - Registry API and management
- [Testing Guide](testing.md) - Comprehensive testing framework
- [CLI Interface](cli_interface.md) - Command-line interface documentation 