# ONEX Handler Registry API

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the API for registering, discovering, and managing file type handlers in the ONEX ecosystem  
> **Audience:** System integrators, platform maintainers  
> **See Also:** [Handler Protocols](reference-handlers-protocol.md), [Handler Implementation Guide](guide-handlers-implementation.md)

---

## Overview

The Handlers Registry API provides a centralized system for managing file type handlers in the ONEX platform. This document defines the registration, discovery, and management APIs for handlers.

---

## Registry API

### Handler Registration

#### Register Handler

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

class HandlerRegistry:
    """Registry for file type handlers."""
    
    def __init__(self):
        self._handlers: Dict[str, Dict[str, Any]] = {}
        self._extension_index: Dict[str, List[str]] = {}
        self._mime_type_index: Dict[str, List[str]] = {}
        self._capability_index: Dict[str, List[str]] = {}
    
    def register_handler(
        self, 
        handler: 'FileHandlerProtocol',
        metadata: 'HandlerMetadata'
    ) -> 'HandlerResult':
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
    
    def _validate_handler(
        self, 
        handler: 'FileHandlerProtocol', 
        metadata: 'HandlerMetadata'
    ) -> 'HandlerResult':
        """Validate handler implementation and metadata."""
        from .reference_handlers_protocol import HandlerValidator
        
        # Validate handler protocol compliance
        handler_validation = HandlerValidator.validate_handler(handler)
        if not handler_validation.success:
            return handler_validation
        
        # Validate metadata
        metadata_validation = HandlerValidator.validate_metadata(metadata)
        if not metadata_validation.success:
            return metadata_validation
        
        return HandlerResult(success=True, message="Handler validation passed")
    
    def _check_conflicts(
        self, 
        handler: 'FileHandlerProtocol', 
        metadata: 'HandlerMetadata'
    ) -> List[str]:
        """Check for handler conflicts."""
        conflicts = []
        
        # Check for duplicate handler names
        for handler_id, handler_info in self._handlers.items():
            existing_metadata = handler_info["metadata"]
            if existing_metadata.name == metadata.name:
                if existing_metadata.version == metadata.version:
                    conflicts.append(f"Handler {metadata.name}@{metadata.version} already registered")
        
        return conflicts
    
    def _generate_handler_id(self, name: str, version: str) -> str:
        """Generate unique handler ID."""
        return f"{name}@{version}"
    
    def _update_indexes(self, handler_id: str, metadata: 'HandlerMetadata') -> None:
        """Update registry indexes."""
        # Update extension index
        for ext in metadata.file_extensions:
            if ext not in self._extension_index:
                self._extension_index[ext] = []
            self._extension_index[ext].append(handler_id)
        
        # Update MIME type index
        for mime_type in metadata.mime_types:
            if mime_type not in self._mime_type_index:
                self._mime_type_index[mime_type] = []
            self._mime_type_index[mime_type].append(handler_id)
        
        # Update capability index
        for capability in metadata.capabilities:
            cap_name = capability.value if hasattr(capability, 'value') else str(capability)
            if cap_name not in self._capability_index:
                self._capability_index[cap_name] = []
            self._capability_index[cap_name].append(handler_id)
```

#### Unregister Handler

```python
def unregister_handler(self, handler_id: str) -> 'HandlerResult':
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

def _is_handler_in_use(self, handler_id: str) -> bool:
    """Check if handler is currently in use."""
    # Implementation would check active operations
    return False

def _remove_from_indexes(self, handler_id: str, metadata: 'HandlerMetadata') -> None:
    """Remove handler from indexes."""
    # Remove from extension index
    for ext in metadata.file_extensions:
        if ext in self._extension_index:
            self._extension_index[ext] = [
                h for h in self._extension_index[ext] if h != handler_id
            ]
            if not self._extension_index[ext]:
                del self._extension_index[ext]
    
    # Remove from MIME type index
    for mime_type in metadata.mime_types:
        if mime_type in self._mime_type_index:
            self._mime_type_index[mime_type] = [
                h for h in self._mime_type_index[mime_type] if h != handler_id
            ]
            if not self._mime_type_index[mime_type]:
                del self._mime_type_index[mime_type]
    
    # Remove from capability index
    for capability in metadata.capabilities:
        cap_name = capability.value if hasattr(capability, 'value') else str(capability)
        if cap_name in self._capability_index:
            self._capability_index[cap_name] = [
                h for h in self._capability_index[cap_name] if h != handler_id
            ]
            if not self._capability_index[cap_name]:
                del self._capability_index[cap_name]
```

### Handler Discovery

```python
def find_handlers_for_file(self, file_path: Path) -> List['HandlerMetadata']:
    """Find handlers that can process the given file.
    
    Args:
        file_path: Path to file
        
    Returns:
        List of compatible handler metadata
    """
    compatible_handlers = []
    
    # Get file extension
    file_ext = file_path.suffix.lower()
    
    # Find handlers by extension
    if file_ext in self._extension_index:
        for handler_id in self._extension_index[file_ext]:
            handler_info = self._handlers.get(handler_id)
            if handler_info and handler_info["status"] == "active":
                handler = handler_info["handler"]
                if handler.can_handle(file_path):
                    compatible_handlers.append(handler_info["metadata"])
    
    # Get MIME type and find handlers
    mime_type = self._get_mime_type(file_path)
    if mime_type and mime_type in self._mime_type_index:
        for handler_id in self._mime_type_index[mime_type]:
            handler_info = self._handlers.get(handler_id)
            if handler_info and handler_info["status"] == "active":
                handler = handler_info["handler"]
                if handler.can_handle(file_path):
                    metadata = handler_info["metadata"]
                    if metadata not in compatible_handlers:
                        compatible_handlers.append(metadata)
    
    # Sort by priority (if available) or name
    compatible_handlers.sort(key=lambda h: (getattr(h, 'priority', 100), h.name))
    
    return compatible_handlers

def find_handlers_by_capability(self, capability: str) -> List['HandlerMetadata']:
    """Find handlers with specific capability.
    
    Args:
        capability: Required capability
        
    Returns:
        List of handler metadata with the capability
    """
    handlers = []
    
    if capability in self._capability_index:
        for handler_id in self._capability_index[capability]:
            handler_info = self._handlers.get(handler_id)
            if handler_info and handler_info["status"] == "active":
                handlers.append(handler_info["metadata"])
    
    return handlers

def get_handler(self, handler_id: str) -> Optional['FileHandlerProtocol']:
    """Get handler by ID.
    
    Args:
        handler_id: Handler identifier
        
    Returns:
        Handler instance if found, None otherwise
    """
    handler_info = self._handlers.get(handler_id)
    if handler_info and handler_info["status"] == "active":
        return handler_info["handler"]
    return None

def get_handler_metadata(self, handler_id: str) -> Optional['HandlerMetadata']:
    """Get handler metadata by ID.
    
    Args:
        handler_id: Handler identifier
        
    Returns:
        Handler metadata if found, None otherwise
    """
    handler_info = self._handlers.get(handler_id)
    if handler_info:
        return handler_info["metadata"]
    return None

def list_all_handlers(self) -> List['HandlerMetadata']:
    """List all registered handlers.
    
    Returns:
        List of all handler metadata
    """
    return [
        handler_info["metadata"] 
        for handler_info in self._handlers.values()
        if handler_info["status"] == "active"
    ]

def _get_mime_type(self, file_path: Path) -> Optional[str]:
    """Get MIME type for file."""
    import mimetypes
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type
```

---

## Handler Management

### Handler Status Management

```python
def enable_handler(self, handler_id: str) -> 'HandlerResult':
    """Enable a handler.
    
    Args:
        handler_id: Handler identifier
        
    Returns:
        Result indicating success or failure
    """
    if handler_id not in self._handlers:
        return HandlerResult(
            success=False,
            message=f"Handler {handler_id} not found"
        )
    
    self._handlers[handler_id]["status"] = "active"
    
    return HandlerResult(
        success=True,
        message=f"Handler {handler_id} enabled"
    )

def disable_handler(self, handler_id: str) -> 'HandlerResult':
    """Disable a handler.
    
    Args:
        handler_id: Handler identifier
        
    Returns:
        Result indicating success or failure
    """
    if handler_id not in self._handlers:
        return HandlerResult(
            success=False,
            message=f"Handler {handler_id} not found"
        )
    
    self._handlers[handler_id]["status"] = "disabled"
    
    return HandlerResult(
        success=True,
        message=f"Handler {handler_id} disabled"
    )

def get_handler_status(self, handler_id: str) -> Optional[str]:
    """Get handler status.
    
    Args:
        handler_id: Handler identifier
        
    Returns:
        Handler status if found, None otherwise
    """
    handler_info = self._handlers.get(handler_id)
    if handler_info:
        return handler_info["status"]
    return None
```

### Handler Configuration

```python
def configure_handler(
    self, 
    handler_id: str, 
    config: Dict[str, Any]
) -> 'HandlerResult':
    """Configure a handler.
    
    Args:
        handler_id: Handler identifier
        config: Configuration parameters
        
    Returns:
        Result indicating success or failure
    """
    handler_info = self._handlers.get(handler_id)
    if not handler_info:
        return HandlerResult(
            success=False,
            message=f"Handler {handler_id} not found"
        )
    
    handler = handler_info["handler"]
    
    # Check if handler supports configuration
    if not hasattr(handler, 'configure'):
        return HandlerResult(
            success=False,
            message=f"Handler {handler_id} does not support configuration"
        )
    
    try:
        # Validate configuration if handler supports it
        if hasattr(handler, 'validate_configuration'):
            validation_result = handler.validate_configuration(config)
            if not validation_result.success:
                return validation_result
        
        # Apply configuration
        from .reference_handlers_protocol import HandlerConfiguration
        handler_config = HandlerConfiguration(
            handler_name=handler_info["metadata"].name,
            options=config
        )
        
        success = handler.configure(handler_config)
        if not success:
            return HandlerResult(
                success=False,
                message=f"Failed to configure handler {handler_id}"
            )
        
        # Store configuration
        handler_info["configuration"] = config
        handler_info["configured_at"] = datetime.utcnow()
        
        return HandlerResult(
            success=True,
            message=f"Handler {handler_id} configured successfully"
        )
        
    except Exception as e:
        return HandlerResult(
            success=False,
            message=f"Configuration failed: {str(e)}",
            errors=[str(e)]
        )

def get_handler_configuration(self, handler_id: str) -> Optional[Dict[str, Any]]:
    """Get handler configuration.
    
    Args:
        handler_id: Handler identifier
        
    Returns:
        Handler configuration if found, None otherwise
    """
    handler_info = self._handlers.get(handler_id)
    if handler_info:
        return handler_info.get("configuration")
    return None
```

---

## Registry Statistics

### Usage Statistics

```python
def get_registry_statistics(self) -> Dict[str, Any]:
    """Get registry statistics.
    
    Returns:
        Dictionary containing registry statistics
    """
    total_handlers = len(self._handlers)
    active_handlers = len([
        h for h in self._handlers.values() 
        if h["status"] == "active"
    ])
    disabled_handlers = total_handlers - active_handlers
    
    # Count handlers by capability
    capability_counts = {}
    for handler_info in self._handlers.values():
        for capability in handler_info["metadata"].capabilities:
            cap_name = capability.value if hasattr(capability, 'value') else str(capability)
            capability_counts[cap_name] = capability_counts.get(cap_name, 0) + 1
    
    # Count handlers by file extension
    extension_counts = {}
    for handler_info in self._handlers.values():
        for ext in handler_info["metadata"].file_extensions:
            extension_counts[ext] = extension_counts.get(ext, 0) + 1
    
    return {
        "total_handlers": total_handlers,
        "active_handlers": active_handlers,
        "disabled_handlers": disabled_handlers,
        "handlers_by_capability": capability_counts,
        "handlers_by_extension": extension_counts,
        "supported_extensions": list(self._extension_index.keys()),
        "supported_mime_types": list(self._mime_type_index.keys())
    }

def get_handler_info(self, handler_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed handler information.
    
    Args:
        handler_id: Handler identifier
        
    Returns:
        Handler information if found, None otherwise
    """
    handler_info = self._handlers.get(handler_id)
    if not handler_info:
        return None
    
    metadata = handler_info["metadata"]
    handler = handler_info["handler"]
    
    info = {
        "handler_id": handler_id,
        "name": metadata.name,
        "version": metadata.version,
        "description": metadata.description,
        "author": metadata.author,
        "file_extensions": metadata.file_extensions,
        "mime_types": metadata.mime_types,
        "capabilities": [
            cap.value if hasattr(cap, 'value') else str(cap) 
            for cap in metadata.capabilities
        ],
        "dependencies": metadata.dependencies,
        "status": handler_info["status"],
        "registered_at": handler_info["registered_at"].isoformat(),
        "configuration": handler_info.get("configuration"),
        "configured_at": handler_info.get("configured_at")
    }
    
    # Add handler-specific information if available
    if hasattr(handler, 'health_check'):
        try:
            health_result = handler.health_check()
            info["health_status"] = {
                "healthy": health_result.success,
                "message": health_result.message
            }
        except Exception as e:
            info["health_status"] = {
                "healthy": False,
                "message": f"Health check failed: {str(e)}"
            }
    
    return info
```

---

## Error Handling

### Registry-Specific Errors

```python
class HandlerRegistryError(Exception):
    """Base exception for handler registry errors."""
    pass

class HandlerRegistrationError(HandlerRegistryError):
    """Handler registration failed."""
    pass

class HandlerNotFoundError(HandlerRegistryError):
    """Handler not found."""
    pass

class HandlerOperationError(HandlerRegistryError):
    """Handler operation failed."""
    pass

class HandlerConfigurationError(HandlerRegistryError):
    """Handler configuration error."""
    pass

class HandlerConflictError(HandlerRegistryError):
    """Handler conflict detected."""
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
| HR009 | Management | Handler not found |
| HR010 | Management | Handler in use, cannot unregister |

---

## See Also

- [Handler Protocols](reference-handlers-protocol.md) - Handler protocols and interfaces
- [Handler Implementation Guide](guide-handlers-implementation.md) - Implementation examples and testing
- [Registry Specification](registry.md) - Core registry concepts
- [CLI Interface](cli_interface.md) - Command-line interface 