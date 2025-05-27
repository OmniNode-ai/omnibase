<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: protocol_definitions.md
version: 1.0.0
uuid: d39fe7ef-3a49-455b-bb74-9eb2b411054e
author: OmniNode Team
created_at: 2025-05-27T07:53:26.132205
last_modified_at: 2025-05-27T17:26:51.872763
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 20a8c5ec61ccab684d770291a58f483cecefed49dd4ea42c75aaaf0ec2db6f22
entrypoint: python@protocol_definitions.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.protocol_definitions
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Architecture: Protocol Definitions

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Define foundational protocol interfaces that core components and nodes must adhere to  
> **Audience:** Node developers, system architects, protocol implementers  
> **Series:** Node Architecture  

---

## Overview

This document defines the foundational protocol interfaces that core components and nodes must adhere to. These interfaces establish a consistent, predictable way for node functions to communicate with one another and with the ONEX runtime environment. The protocols emerged from the need to standardize interactions between diverse node implementations while preserving the function-oriented architecture.

---

## Core Protocol Interfaces

ONEX protocols define abstract interfaces that concrete implementations must fulfill. These protocols ensure compatibility and predictable behavior across the system.

### Protocol Hierarchy

```
ProtocolBase
├── RegistryProtocol
├── ProtocolValidator
├── ProtocolStamper
├── ReducerProtocol
├── ProtocolCLI
└── ProtocolTool
```

Each protocol interface is defined using abstract classes, defining required methods and their signatures.

### Standard Protocol Implementation

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional

class ProtocolValidator(ABC):
    """Protocol for validators that check onex node metadata conformance."""
    
    @abstractmethod
    def validate(self, path: str) -> bool:
        """
        Validate an ONEX metadata file at the given path.
        
        Args:
            path: Path to the .onex file to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_validation_errors(self) -> list:
        """
        Get detailed validation errors from the last validation.
        
        Returns:
            list: List of validation error details
        """
        pass
```

---

## Protocol Implementation Requirements

When implementing a protocol interface, components must adhere to specific requirements to ensure compatibility and reliability.

### Implementation Requirements

* All abstract methods must be implemented with the exact signatures defined in the protocol
* Implementation classes should import the protocol from `omnibase.protocol.<protocol_module>`
* Additional helper methods may be added, but core protocol methods must maintain their defined behavior
* Protocol implementations should be thoroughly tested against the protocol's expected behavior

### Protocol Extensions for Execution Planning and Performance

Protocol-based components involved in execution (e.g., validators, planners, cache layers, reducers) should implement optional support for execution-aware extensions, including:

* `get_execution_profile(self) -> dict`: Returns an optional execution profile for use in planner optimization (`speed`, `accuracy`, `efficiency`)
* 
  ```python
  from pydantic import BaseModel

  class StateContractInput(BaseModel):
      ...
  ```

* `get_cache_key_hint(self, input_state: StateContractInput) -> str`: Returns a hash or identifier that informs memoization or cache strategies
* `supports_memoization_tier(self) -> bool`: Indicates whether the component can participate in `deep` memoization contexts (e.g., within composite subgraphs)
* `snapshot_state(self) -> dict`: Optional reducer method to emit a resumable snapshot of internal state

These optional methods enhance integration with the `memoization_tier`, planner optimizations, and stateful node execution tracking in ONEX.

Implementations are expected to use concrete, schema-bound types for all method inputs and outputs, consistent with the declared `state_contract` in their `.onex` metadata.

---

## Monadic Node Protocols

ONEX supports monadic composition of nodes with explicit state tracking and effect management through advanced protocol interfaces.

### NodeResult Protocol

```python
from typing import Generic, TypeVar, Awaitable, Callable, Optional, Dict, List, Any
from datetime import datetime

T = TypeVar('T')
U = TypeVar('U')

class ExecutionContext:
    """Context information for node execution."""
    provenance: List[str]             # trace of node invocations
    logs: List[LogEntry]              # structured logs per step
    trust_score: float                # numeric or enum-based trust level
    timestamp: datetime               # execution timestamp
    metadata: Dict[str, Any]          # additional ad hoc data

class Event:
    """Structured event emitted during node execution."""
    type: str                         # e.g., "log", "metric", "alert"
    payload: Dict[str, Any]           # structured content
    timestamp: datetime

class NodeResult(Generic[T]):
    """Monadic result wrapper for node execution."""
    
    value: T
    context: ExecutionContext
    state_delta: Optional[Dict] = None
    events: Optional[List[Event]] = None

    async def bind(self, f: Callable[[T], Awaitable['NodeResult[U]']]) -> 'NodeResult[U]':
        """
        Monadic bind operation for composition.
        
        Args:
            f: Function to compose with this result
            
        Returns:
            NodeResult containing the composed result
        """
        # Implementation will propagate context, merge state deltas, and concatenate events
        return await f(self.value)
```

### Node Protocol

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Awaitable

T = TypeVar('T')  # Input type
U = TypeVar('U')  # Output type

class Node(Generic[T, U], ABC):
    """Protocol for monadic node implementation."""
    
    @abstractmethod
    async def run(self, input: T) -> NodeResult[U]:
        """
        Run the node with the given input.
        
        Args:
            input: Input value of type T
            
        Returns:
            NodeResult containing output of type U
        """
        pass
```

These protocols enhance node composition with:

1. **Context Propagation**: Execution context flows through node chains
2. **State Delta Tracking**: Explicit tracking of state changes
3. **Effect Management**: Structured events for side effects
4. **Monadic Composition**: Type-safe, context-aware node chaining

---

## Registry Protocol

The registry protocol defines how components discover and interact with the ONEX registry system.

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class RegistryProtocol(ABC):
    """Protocol for registry implementations."""
    
    @abstractmethod
    def get_node(self, node_id: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve node metadata by ID and optional version.
        
        Args:
            node_id: Unique identifier for the node
            version: Optional version specifier
            
        Returns:
            Dict containing node metadata
        """
        pass
    
    @abstractmethod
    def list_nodes(self) -> List[str]:
        """
        List all available node IDs.
        
        Returns:
            List of node identifiers
        """
        pass
    
    @abstractmethod
    def register_node(self, node_metadata: Dict[str, Any]) -> bool:
        """
        Register a new node with the registry.
        
        Args:
            node_metadata: Complete node metadata
            
        Returns:
            bool: True if registration successful
        """
        pass
```

---

## Stamper Protocol

The stamper protocol defines how metadata stamping operations are performed.

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class ProtocolStamper(ABC):
    """Protocol for metadata stamping implementations."""
    
    @abstractmethod
    def stamp_file(self, file_path: Path, metadata: Dict[str, Any]) -> bool:
        """
        Stamp a file with metadata.
        
        Args:
            file_path: Path to the file to stamp
            metadata: Metadata to embed
            
        Returns:
            bool: True if stamping successful
        """
        pass
    
    @abstractmethod
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from a stamped file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict containing extracted metadata
        """
        pass
    
    @abstractmethod
    def validate_stamp(self, file_path: Path) -> bool:
        """
        Validate that a file's stamp is correct and current.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            bool: True if stamp is valid
        """
        pass
```

---

## CLI Protocol

The CLI protocol defines how command-line interfaces are implemented.

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ProtocolCLI(ABC):
    """Protocol for CLI implementations."""
    
    @abstractmethod
    def execute(self, args: List[str]) -> Dict[str, Any]:
        """
        Execute the CLI command with given arguments.
        
        Args:
            args: Command line arguments
            
        Returns:
            Dict containing execution results
        """
        pass
    
    @abstractmethod
    def get_help(self) -> str:
        """
        Get help text for the CLI command.
        
        Returns:
            str: Help text
        """
        pass
    
    @abstractmethod
    def validate_args(self, args: List[str]) -> bool:
        """
        Validate command line arguments.
        
        Args:
            args: Arguments to validate
            
        Returns:
            bool: True if arguments are valid
        """
        pass
```

---

## Best Practices

### Protocol Design

1. **Keep interfaces minimal**: Only include essential methods
2. **Use type hints**: Provide clear type annotations for all methods
3. **Document thoroughly**: Include comprehensive docstrings
4. **Design for extension**: Allow for optional methods and future enhancements
5. **Maintain backward compatibility**: Avoid breaking changes to existing protocols

### Implementation Guidelines

1. **Follow the protocol exactly**: Implement all required methods with correct signatures
2. **Handle errors gracefully**: Provide meaningful error messages and proper exception handling
3. **Test comprehensively**: Verify protocol compliance through thorough testing
4. **Document deviations**: Clearly document any protocol extensions or variations
5. **Use dependency injection**: Make protocols injectable for testing and flexibility

### Testing Protocols

```python
import pytest
from abc import ABC

def test_protocol_compliance(implementation_class, protocol_class):
    """Test that an implementation follows a protocol."""
    assert issubclass(implementation_class, protocol_class)
    
    # Verify all abstract methods are implemented
    abstract_methods = {
        name for name, method in protocol_class.__dict__.items()
        if getattr(method, '__isabstractmethod__', False)
    }
    
    implemented_methods = set(implementation_class.__dict__.keys())
    missing_methods = abstract_methods - implemented_methods
    
    assert not missing_methods, f"Missing methods: {missing_methods}"
```

---

## References

- [Node Architecture Index](./index.md) - Overview of node architecture series
- [Node Contracts](./node_contracts.md) - Contract-first node design
- [Structural Conventions](./structural_conventions.md) - Directory structure and file layout
- [Monadic Node Core](./architecture-node-monadic-core.md) - Core monadic principles and interfaces
- [Node Composition](./architecture-node-composition.md) - Composition patterns and execution models
- [State Reducers](./state_reducers.md) - State management and reducers
- [Core Protocols](../reference-protocols-core.md) - Core protocol definitions and execution
- [Registry Protocols](../reference-protocols-registry.md) - Registry, validation, handler protocols
- [Data Models](../reference-data-models.md) - Data models, composition, testing

---

**Note:** These protocol definitions form the foundation of the ONEX component system. All core components must implement these protocols to ensure compatibility and integration with the broader ONEX ecosystem.
