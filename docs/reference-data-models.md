# ONEX Data Models, Composition, and Testing

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define data models, protocol composition patterns, and testing frameworks in the ONEX ecosystem  
> **Audience:** Developers, architects, test engineers  
> **See Also:** [Core Protocols](reference-protocols-core.md), [Registry Protocols](reference-protocols-registry.md)

---

## Overview

This document defines the data models, protocol composition patterns, and testing frameworks used throughout the ONEX platform. It provides the foundation for data structures, protocol combinations, and compliance testing.

---

## Core Data Models

### Principal and Security Models

```python
from typing import Set, List, Dict, Any, Optional
from dataclasses import dataclass
from uuid import UUID

@dataclass
class Principal:
    """Security principal (user, service, etc.)."""
    principal_id: str
    principal_type: str  # user, service, system
    name: str
    roles: Set[str]
    capabilities: List['Capability']
    metadata: Dict[str, Any]

@dataclass
class Capability:
    """Security capability definition."""
    capability_id: str
    name: str
    description: str
    resource_patterns: List[str]
    operations: List[str]
    constraints: Dict[str, Any]

@dataclass
class ExecutionContext:
    """Context for node execution."""
    context_id: str
    principal: Principal
    capabilities: List[Capability]
    environment: Dict[str, str]
    working_directory: 'Path'
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = None
```

### Artifact and Result Models

```python
from datetime import datetime
from pathlib import Path

@dataclass
class Artifact:
    """Execution artifact."""
    artifact_id: str
    name: str
    type: str  # file, data, log, metric
    content: Any
    metadata: Dict[str, Any]
    created_at: datetime
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None

@dataclass
class Result:
    """Generic result container."""
    result_id: str
    status: str
    data: Any
    artifacts: List[Artifact]
    metadata: Dict[str, Any]
    created_at: datetime
    duration_ms: Optional[int] = None
```

### Configuration Models

```python
@dataclass
class ConfigurationItem:
    """Configuration item."""
    key: str
    value: Any
    type: str  # string, int, bool, list, dict
    description: str
    required: bool = False
    default: Any = None
    validation_rules: List[str] = None

@dataclass
class Configuration:
    """Configuration container."""
    config_id: str
    name: str
    version: str
    items: Dict[str, ConfigurationItem]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
```

---

## Protocol Composition Patterns

### Composite Protocols

```python
from typing import Protocol

class NodeProtocol(ExecutionProtocol, LifecycleProtocol, ValidationProtocol, Protocol):
    """Composite protocol for ONEX nodes."""
    
    @property
    def metadata(self) -> 'NodeMetadata':
        """Node metadata."""
        ...
    
    def introspect(self) -> Dict[str, Any]:
        """Get node introspection information."""
        ...

class RegistryNodeProtocol(NodeProtocol, RegistryProtocol, Protocol):
    """Protocol for nodes that can act as registries."""
    
    def get_registry_metadata(self) -> Dict[str, Any]:
        """Get registry-specific metadata."""
        ...
    
    def sync_with_registry(self, other_registry: 'RegistryNodeProtocol') -> bool:
        """Synchronize with another registry."""
        ...

class ValidatingExecutorProtocol(ExecutionProtocol, ValidationProtocol, Protocol):
    """Protocol for executors that validate before execution."""
    
    def validate_and_execute(self, context: 'ExecutionContext') -> 'ExecutionResult':
        """Validate context and execute if valid."""
        validation_result = self.validate(context)
        if not validation_result.success:
            return ExecutionResult(
                status=ExecutionStatus.FAILURE,
                error=f"Validation failed: {validation_result.issues}"
            )
        return self.execute(context)
```

### Protocol Adapters

```python
class ProtocolAdapter:
    """Base class for protocol adapters."""
    
    def __init__(self, adaptee: Any):
        self.adaptee = adaptee
    
    def supports_protocol(self, protocol_type: type) -> bool:
        """Check if adaptee supports protocol."""
        return isinstance(self.adaptee, protocol_type)

class ExecutionAdapter(ProtocolAdapter):
    """Adapter for ExecutionProtocol."""
    
    def execute(self, context: 'ExecutionContext') -> 'ExecutionResult':
        """Adapt execution call."""
        if hasattr(self.adaptee, 'run'):
            # Adapt 'run' method to 'execute'
            result = self.adaptee.run(context)
            return self._convert_result(result)
        elif hasattr(self.adaptee, '__call__'):
            # Adapt callable to execute
            result = self.adaptee(context)
            return self._convert_result(result)
        else:
            raise NotImplementedError("Adaptee does not support execution")
    
    def _convert_result(self, result: Any) -> 'ExecutionResult':
        """Convert result to ExecutionResult."""
        if isinstance(result, ExecutionResult):
            return result
        elif isinstance(result, bool):
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS if result else ExecutionStatus.FAILURE
            )
        else:
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output=str(result)
            )

class RegistryAdapter(ProtocolAdapter):
    """Adapter for RegistryProtocol."""
    
    def register_node(self, metadata: 'NodeMetadata') -> bool:
        """Adapt node registration."""
        if hasattr(self.adaptee, 'add_node'):
            return self.adaptee.add_node(metadata)
        elif hasattr(self.adaptee, 'register'):
            return self.adaptee.register(metadata)
        else:
            raise NotImplementedError("Adaptee does not support node registration")
```

---

## Protocol Testing Framework

### Protocol Compliance Testing

```python
import pytest
from typing import Type, Any, List
from abc import ABC, abstractmethod

class ProtocolTestCase(ABC):
    """Base class for protocol compliance tests."""
    
    @abstractmethod
    def get_test_implementation(self) -> Any:
        """Get implementation to test."""
        ...
    
    @abstractmethod
    def get_protocol_type(self) -> Type:
        """Get protocol type to test against."""
        ...
    
    def test_protocol_compliance(self):
        """Test that implementation complies with protocol."""
        implementation = self.get_test_implementation()
        protocol = self.get_protocol_type()
        
        # Check that all protocol methods are implemented
        protocol_methods = self._get_protocol_methods(protocol)
        for method_name in protocol_methods:
            assert hasattr(implementation, method_name), \
                f"Implementation missing method: {method_name}"
        
        # Check method signatures
        for method_name in protocol_methods:
            impl_method = getattr(implementation, method_name)
            assert callable(impl_method), \
                f"Method {method_name} is not callable"
    
    def _get_protocol_methods(self, protocol: Type) -> List[str]:
        """Get list of methods defined in protocol."""
        methods = []
        for attr_name in dir(protocol):
            if not attr_name.startswith('_'):
                attr = getattr(protocol, attr_name)
                if callable(attr):
                    methods.append(attr_name)
        return methods

class ExecutionProtocolTest(ProtocolTestCase):
    """Test case for ExecutionProtocol compliance."""
    
    def get_protocol_type(self) -> Type:
        return ExecutionProtocol
    
    def test_execution_protocol(self):
        """Test ExecutionProtocol compliance."""
        executor = self.get_test_implementation()
        self.test_protocol_compliance()
        
        # Test execution with mock context
        mock_context = self._create_mock_context()
        result = executor.execute(mock_context)
        
        assert isinstance(result, ExecutionResult)
        assert isinstance(result.status, ExecutionStatus)
    
    def test_context_validation(self):
        """Test context validation."""
        executor = self.get_test_implementation()
        mock_context = self._create_mock_context()
        
        is_valid = executor.validate_context(mock_context)
        assert isinstance(is_valid, bool)
    
    def test_required_capabilities(self):
        """Test required capabilities."""
        executor = self.get_test_implementation()
        capabilities = executor.get_required_capabilities()
        
        assert isinstance(capabilities, list)
        for cap in capabilities:
            assert isinstance(cap, Capability)
    
    def _create_mock_context(self) -> ExecutionContext:
        """Create mock execution context for testing."""
        return ExecutionContext(
            context_id="test-context",
            principal=Principal(
                principal_id="test-user",
                principal_type="user",
                name="Test User",
                roles=set(),
                capabilities=[],
                metadata={}
            ),
            capabilities=[],
            environment={},
            working_directory=Path("/tmp")
        )

class RegistryProtocolTest(ProtocolTestCase):
    """Test case for RegistryProtocol compliance."""
    
    def get_protocol_type(self) -> Type:
        return RegistryProtocol
    
    def test_registry_protocol(self):
        """Test RegistryProtocol compliance."""
        registry = self.get_test_implementation()
        self.test_protocol_compliance()
        
        # Test node registration
        mock_metadata = self._create_mock_metadata()
        success = registry.register_node(mock_metadata)
        assert isinstance(success, bool)
        
        # Test node retrieval
        if success:
            retrieved = registry.get_node(mock_metadata.uuid)
            assert retrieved is not None
            assert retrieved.uuid == mock_metadata.uuid
    
    def test_node_discovery(self):
        """Test node discovery functionality."""
        registry = self.get_test_implementation()
        
        # Test listing all nodes
        all_nodes = registry.list_all_nodes()
        assert isinstance(all_nodes, list)
        
        # Test finding nodes with criteria
        criteria = SearchCriteria(name_pattern="test*")
        found_nodes = registry.find_nodes(criteria)
        assert isinstance(found_nodes, list)
    
    def _create_mock_metadata(self) -> NodeMetadata:
        """Create mock node metadata for testing."""
        return NodeMetadata(
            uuid=UUID('12345678-1234-5678-1234-567812345678'),
            name="test_node",
            version="1.0.0",
            description="Test node",
            author="test_author",
            tags=["test"],
            dependencies=[],
            capabilities=["test_capability"],
            lifecycle_state=LifecycleState.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

class ValidationProtocolTest(ProtocolTestCase):
    """Test case for ValidationProtocol compliance."""
    
    def get_protocol_type(self) -> Type:
        return ValidationProtocol
    
    def test_validation_protocol(self):
        """Test ValidationProtocol compliance."""
        validator = self.get_test_implementation()
        self.test_protocol_compliance()
        
        # Test validation
        test_data = {"test": "data"}
        result = validator.validate(test_data)
        
        assert isinstance(result, ValidationResult)
        assert isinstance(result.success, bool)
        assert isinstance(result.issues, list)
    
    def test_validation_rules(self):
        """Test validation rules."""
        validator = self.get_test_implementation()
        rules = validator.get_validation_rules()
        
        assert isinstance(rules, list)
        for rule in rules:
            assert isinstance(rule, str)
    
    def test_quick_validation(self):
        """Test quick validation check."""
        validator = self.get_test_implementation()
        test_data = {"test": "data"}
        
        is_valid = validator.is_valid(test_data)
        assert isinstance(is_valid, bool)
```

### Test Fixtures and Utilities

```python
import pytest
from typing import Generator

@pytest.fixture
def mock_execution_context() -> ExecutionContext:
    """Fixture for mock execution context."""
    return ExecutionContext(
        context_id="test-context",
        principal=Principal(
            principal_id="test-user",
            principal_type="user",
            name="Test User",
            roles={"user"},
            capabilities=[],
            metadata={}
        ),
        capabilities=[],
        environment={"TEST_ENV": "true"},
        working_directory=Path("/tmp/test")
    )

@pytest.fixture
def mock_node_metadata() -> NodeMetadata:
    """Fixture for mock node metadata."""
    return NodeMetadata(
        uuid=UUID('12345678-1234-5678-1234-567812345678'),
        name="test_node",
        version="1.0.0",
        description="Test node for unit testing",
        author="test_author",
        tags=["test", "mock"],
        dependencies=[],
        capabilities=["test_capability"],
        lifecycle_state=LifecycleState.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

@pytest.fixture
def temporary_registry() -> Generator[Dict[UUID, NodeMetadata], None, None]:
    """Fixture for temporary in-memory registry."""
    registry = {}
    yield registry
    registry.clear()

class MockExecutor:
    """Mock executor for testing."""
    
    def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Mock execution."""
        return ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            output="Mock execution completed",
            duration_ms=100
        )
    
    def validate_context(self, context: ExecutionContext) -> bool:
        """Mock context validation."""
        return context.principal.principal_type == "user"
    
    def get_required_capabilities(self) -> List[Capability]:
        """Mock required capabilities."""
        return []

class MockRegistry:
    """Mock registry for testing."""
    
    def __init__(self):
        self._nodes: Dict[UUID, NodeMetadata] = {}
    
    def register_node(self, metadata: NodeMetadata) -> bool:
        """Mock node registration."""
        self._nodes[metadata.uuid] = metadata
        return True
    
    def unregister_node(self, node_uuid: UUID) -> bool:
        """Mock node unregistration."""
        if node_uuid in self._nodes:
            del self._nodes[node_uuid]
            return True
        return False
    
    def get_node(self, node_uuid: UUID) -> Optional[NodeMetadata]:
        """Mock node retrieval."""
        return self._nodes.get(node_uuid)
    
    def find_nodes(self, criteria: SearchCriteria) -> List[NodeMetadata]:
        """Mock node search."""
        # Simple mock implementation
        return list(self._nodes.values())
    
    def list_all_nodes(self) -> List[NodeMetadata]:
        """Mock list all nodes."""
        return list(self._nodes.values())
```

---

## Data Validation and Serialization

### Validation Utilities

```python
from typing import Any, Dict, List
import jsonschema

class DataValidator:
    """Utility for data validation."""
    
    @staticmethod
    def validate_node_metadata(metadata: NodeMetadata) -> ValidationResult:
        """Validate node metadata."""
        issues = []
        
        # Check required fields
        if not metadata.name:
            issues.append(ValidationIssue(
                severity="error",
                message="Node name is required",
                code="MISSING_NAME"
            ))
        
        if not metadata.version:
            issues.append(ValidationIssue(
                severity="error",
                message="Node version is required",
                code="MISSING_VERSION"
            ))
        
        # Check version format
        if metadata.version and not DataValidator._is_valid_version(metadata.version):
            issues.append(ValidationIssue(
                severity="error",
                message="Invalid version format",
                code="INVALID_VERSION"
            ))
        
        return ValidationResult(
            success=len([i for i in issues if i.severity == "error"]) == 0,
            issues=issues
        )
    
    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """Check if version string is valid."""
        import re
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?(\+[a-zA-Z0-9]+)?$'
        return bool(re.match(pattern, version))

class DataSerializer:
    """Utility for data serialization."""
    
    @staticmethod
    def serialize_metadata(metadata: NodeMetadata) -> Dict[str, Any]:
        """Serialize node metadata to dictionary."""
        return {
            "uuid": str(metadata.uuid),
            "name": metadata.name,
            "version": metadata.version,
            "description": metadata.description,
            "author": metadata.author,
            "tags": metadata.tags,
            "dependencies": metadata.dependencies,
            "capabilities": metadata.capabilities,
            "lifecycle_state": metadata.lifecycle_state.value,
            "created_at": metadata.created_at.isoformat(),
            "updated_at": metadata.updated_at.isoformat()
        }
    
    @staticmethod
    def deserialize_metadata(data: Dict[str, Any]) -> NodeMetadata:
        """Deserialize dictionary to node metadata."""
        return NodeMetadata(
            uuid=UUID(data["uuid"]),
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data["author"],
            tags=data["tags"],
            dependencies=data["dependencies"],
            capabilities=data["capabilities"],
            lifecycle_state=LifecycleState(data["lifecycle_state"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
```

---

## See Also

- [Core Protocols](reference-protocols-core.md) - Core execution and lifecycle protocols
- [Registry Protocols](reference-protocols-registry.md) - Registry, discovery, and validation protocols
- [Testing Guide](testing.md) - Comprehensive testing framework
- [Error Handling](error_handling.md) - Error handling patterns
- [Node Development Guide](developer_guide.md) - Node development practices 