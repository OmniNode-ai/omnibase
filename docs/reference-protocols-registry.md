<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: reference-protocols-registry.md
version: 1.0.0
uuid: 3d07b086-3679-468d-a782-e569c70c3554
author: OmniNode Team
created_at: 2025-05-27T09:22:19.585974
last_modified_at: 2025-05-27T17:26:51.873397
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: e2c57c7566072a8a814979a2c0b3306977e08395c6563d7daba072f1b9ca7224
entrypoint: python@reference-protocols-registry.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.reference_protocols_registry
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Registry, Validation, and Handler Protocols

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Define registry, discovery, validation, and handler protocols in the ONEX ecosystem  
> **Audience:** Developers, architects, system integrators  
> **See Also:** [Core Protocols](reference-protocols-core.md), [Data Models](reference-data-models.md)

---

## Overview

This document defines the protocols for registry management, node discovery, validation, and file handling in the ONEX platform. These protocols enable dynamic discovery, validation, and processing of nodes and data.

---

## Registry Protocols

### RegistryProtocol

```python
from typing import Protocol, List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

@dataclass
class NodeMetadata:
    """Node metadata structure."""
    uuid: UUID
    name: str
    version: str
    description: str
    author: str
    tags: List[str]
    dependencies: List[str]
    capabilities: List[str]
    lifecycle_state: 'LifecycleState'
    created_at: datetime
    updated_at: datetime

class RegistryProtocol(Protocol):
    """Protocol for node registries."""
    
    def register_node(self, metadata: NodeMetadata) -> bool:
        """Register a new node.
        
        Args:
            metadata: Node metadata
            
        Returns:
            True if registration was successful
        """
        ...
    
    def unregister_node(self, node_uuid: UUID) -> bool:
        """Unregister a node.
        
        Args:
            node_uuid: UUID of node to unregister
            
        Returns:
            True if unregistration was successful
        """
        ...
    
    def get_node(self, node_uuid: UUID) -> Optional[NodeMetadata]:
        """Get node metadata by UUID.
        
        Args:
            node_uuid: Node UUID
            
        Returns:
            Node metadata if found, None otherwise
        """
        ...
    
    def find_nodes(self, criteria: 'SearchCriteria') -> List[NodeMetadata]:
        """Find nodes matching criteria.
        
        Args:
            criteria: Search criteria
            
        Returns:
            List of matching node metadata
        """
        ...
    
    def list_all_nodes(self) -> List[NodeMetadata]:
        """List all registered nodes.
        
        Returns:
            List of all node metadata
        """
        ...
```

### DiscoveryProtocol

```python
@dataclass
class SearchCriteria:
    """Search criteria for node discovery."""
    name_pattern: Optional[str] = None
    tags: Optional[List[str]] = None
    capabilities: Optional[List[str]] = None
    lifecycle_states: Optional[List['LifecycleState']] = None
    author: Optional[str] = None
    version_pattern: Optional[str] = None

class DiscoveryProtocol(Protocol):
    """Protocol for node discovery."""
    
    def discover_nodes(
        self, 
        criteria: SearchCriteria,
        limit: Optional[int] = None
    ) -> List[NodeMetadata]:
        """Discover nodes matching criteria.
        
        Args:
            criteria: Search criteria
            limit: Maximum number of results
            
        Returns:
            List of discovered nodes
        """
        ...
    
    def discover_by_capability(
        self, 
        capability: str
    ) -> List[NodeMetadata]:
        """Discover nodes with specific capability.
        
        Args:
            capability: Required capability
            
        Returns:
            List of nodes with the capability
        """
        ...
    
    def discover_by_tags(self, tags: List[str]) -> List[NodeMetadata]:
        """Discover nodes with specific tags.
        
        Args:
            tags: Required tags
            
        Returns:
            List of nodes with matching tags
        """
        ...
```

### VersionProtocol

```python
from typing import Protocol, List, Optional
from dataclasses import dataclass

@dataclass
class Version:
    """Version information."""
    major: int
    minor: int
    patch: int
    pre_release: Optional[str] = None
    build: Optional[str] = None
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            version += f"-{self.pre_release}"
        if self.build:
            version += f"+{self.build}"
        return version

class VersionProtocol(Protocol):
    """Protocol for version management."""
    
    def get_latest_version(self, node_name: str) -> Optional[Version]:
        """Get latest version of a node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Latest version if found, None otherwise
        """
        ...
    
    def get_all_versions(self, node_name: str) -> List[Version]:
        """Get all versions of a node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            List of all versions
        """
        ...
    
    def is_compatible(self, version1: Version, version2: Version) -> bool:
        """Check if two versions are compatible.
        
        Args:
            version1: First version
            version2: Second version
            
        Returns:
            True if versions are compatible
        """
        ...
    
    def compare_versions(self, version1: Version, version2: Version) -> int:
        """Compare two versions.
        
        Args:
            version1: First version
            version2: Second version
            
        Returns:
            -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        ...
```

---

## Validation Protocols

### ValidationProtocol

```python
from typing import Protocol, List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ValidationIssue:
    """Validation issue information."""
    severity: str  # error, warning, info
    message: str
    location: Optional[str] = None
    code: Optional[str] = None

@dataclass
class ValidationResult:
    """Result of validation operation."""
    success: bool
    issues: List[ValidationIssue]
    metadata: Dict[str, Any] = None

class ValidationProtocol(Protocol):
    """Protocol for validation operations."""
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate data.
        
        Args:
            data: Data to validate
            
        Returns:
            Validation result
        """
        ...
    
    def get_validation_rules(self) -> List[str]:
        """Get list of validation rules.
        
        Returns:
            List of validation rule identifiers
        """
        ...
    
    def is_valid(self, data: Any) -> bool:
        """Quick validation check.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid
        """
        ...
```

### ComplianceProtocol

```python
class ComplianceProtocol(Protocol):
    """Protocol for compliance checking."""
    
    def check_compliance(self, component: Any) -> ValidationResult:
        """Check component compliance.
        
        Args:
            component: Component to check
            
        Returns:
            Compliance validation result
        """
        ...
    
    def get_compliance_standards(self) -> List[str]:
        """Get list of compliance standards.
        
        Returns:
            List of compliance standard identifiers
        """
        ...
    
    def is_compliant(self, component: Any) -> bool:
        """Quick compliance check.
        
        Args:
            component: Component to check
            
        Returns:
            True if component is compliant
        """
        ...
```

### SchemaProtocol

```python
class SchemaProtocol(Protocol):
    """Protocol for schema validation."""
    
    def validate_schema(self, data: Any, schema: Dict[str, Any]) -> ValidationResult:
        """Validate data against schema.
        
        Args:
            data: Data to validate
            schema: Schema definition
            
        Returns:
            Validation result
        """
        ...
    
    def load_schema(self, schema_path: str) -> Dict[str, Any]:
        """Load schema from file.
        
        Args:
            schema_path: Path to schema file
            
        Returns:
            Schema definition
        """
        ...
    
    def get_schema_version(self, schema: Dict[str, Any]) -> Optional[str]:
        """Get schema version.
        
        Args:
            schema: Schema definition
            
        Returns:
            Schema version if available
        """
        ...
    
    def is_schema_compatible(
        self, 
        schema1: Dict[str, Any], 
        schema2: Dict[str, Any]
    ) -> bool:
        """Check if schemas are compatible.
        
        Args:
            schema1: First schema
            schema2: Second schema
            
        Returns:
            True if schemas are compatible
        """
        ...
```

---

## Handler Protocols

### FileHandlerProtocol

```python
from typing import Protocol, List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

@dataclass
class HandlerResult:
    """Result of handler operation."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None

class FileHandlerProtocol(Protocol):
    """Protocol for file type handlers."""
    
    @property
    def name(self) -> str:
        """Handler name."""
        ...
    
    @property
    def file_extensions(self) -> List[str]:
        """Supported file extensions."""
        ...
    
    @property
    def mime_types(self) -> List[str]:
        """Supported MIME types."""
        ...
    
    def can_handle(self, file_path: Path) -> bool:
        """Check if handler can process file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if handler can process the file
        """
        ...
    
    def validate(self, file_path: Path) -> HandlerResult:
        """Validate file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            Validation result
        """
        ...
    
    def process(self, file_path: Path, **kwargs) -> HandlerResult:
        """Process file with handler.
        
        Args:
            file_path: Path to file
            **kwargs: Additional processing parameters
            
        Returns:
            Processing result
        """
        ...
```

### ProcessorProtocol

```python
from typing import Protocol, Any

class ProcessorProtocol(Protocol):
    """Protocol for data processors."""
    
    def process(self, input_data: Any, **kwargs) -> Any:
        """Process input data.
        
        Args:
            input_data: Data to process
            **kwargs: Processing parameters
            
        Returns:
            Processed data
        """
        ...
    
    def supports_input_type(self, input_type: type) -> bool:
        """Check if processor supports input type.
        
        Args:
            input_type: Type to check
            
        Returns:
            True if type is supported
        """
        ...
    
    def get_output_type(self, input_type: type) -> type:
        """Get output type for given input type.
        
        Args:
            input_type: Input data type
            
        Returns:
            Output data type
        """
        ...
```

### TransformProtocol

```python
class TransformProtocol(Protocol):
    """Protocol for data transformations."""
    
    def transform(self, source: Any, target_format: str) -> Any:
        """Transform data to target format.
        
        Args:
            source: Source data
            target_format: Target format identifier
            
        Returns:
            Transformed data
        """
        ...
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported target formats.
        
        Returns:
            List of format identifiers
        """
        ...
    
    def can_transform(self, source_type: type, target_format: str) -> bool:
        """Check if transformation is supported.
        
        Args:
            source_type: Source data type
            target_format: Target format
            
        Returns:
            True if transformation is supported
        """
        ...
```

---

## Composite Registry Protocols

### RegistryNodeProtocol

```python
class RegistryNodeProtocol(RegistryProtocol, DiscoveryProtocol, VersionProtocol, Protocol):
    """Protocol for nodes that can act as registries."""
    
    def get_registry_metadata(self) -> Dict[str, Any]:
        """Get registry-specific metadata."""
        ...
    
    def sync_with_registry(self, other_registry: 'RegistryNodeProtocol') -> bool:
        """Synchronize with another registry."""
        ...
```

### ValidatingRegistryProtocol

```python
class ValidatingRegistryProtocol(RegistryProtocol, ValidationProtocol, Protocol):
    """Protocol for registries that validate nodes before registration."""
    
    def register_with_validation(self, metadata: NodeMetadata) -> ValidationResult:
        """Register node with validation."""
        validation_result = self.validate(metadata)
        if validation_result.success:
            success = self.register_node(metadata)
            if not success:
                validation_result.success = False
                validation_result.issues.append(
                    ValidationIssue(
                        severity="error",
                        message="Registration failed",
                        code="REGISTRATION_FAILED"
                    )
                )
        return validation_result
```

---

## See Also

- [Core Protocols](reference-protocols-core.md) - Core execution and lifecycle protocols
- [Data Models](reference-data-models.md) - Data models, composition, and testing
- [Registry Specification](registry.md) - Registry implementation details
- [Error Handling](error_handling.md) - Error handling patterns
- [Node Development Guide](developer_guide.md) - Node development practices
