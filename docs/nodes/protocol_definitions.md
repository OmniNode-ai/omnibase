<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: 289631d7-3420-4a4f-83f9-2cfa7679242e -->
<!-- name: protocol_definitions.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:20:02.923040 -->
<!-- last_modified_at: 2025-05-19T16:20:02.923052 -->
<!-- description: Stamped Markdown file: protocol_definitions.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: 11252d8209e3cbbcea2e6a4f6602b3956cd2607333940dd0f456cec5cee7ba5c -->
<!-- entrypoint: {'type': 'markdown', 'target': 'protocol_definitions.md'} -->
<!-- namespace: onex.stamped.protocol_definitions.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

# ONEX Node Architecture: Protocol Definitions

> **Status:** Canonical  
> **Series:** Node Architecture  
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting documentation.  
> **Related documents:** [Node Contracts](./node_contracts.md), [State Reducers](./state_reducers.md), [Functional Monadic Node Architecture](./functional_monadic_node_architecture.md)

## 10 - Protocol Definitions

### Context & Origin

This document defines the foundational protocol interfaces that core components and nodes must adhere to. These interfaces establish a consistent, predictable way for node functions to communicate with one another and with the ONEX runtime environment. The protocols emerged from the need to standardize interactions between diverse node implementations while preserving the function-oriented architecture.

---

### Core Protocol Interfaces

ONEX protocols define abstract interfaces that concrete implementations must fulfill. These protocols ensure compatibility and predictable behavior across the system.

#### ✅ Protocol Hierarchy

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

#### ✅ Standard Protocol Implementation

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


---

### Protocol Implementation Requirements

When implementing a protocol interface, components must adhere to specific requirements to ensure compatibility and reliability.

#### ✅ Implementation Requirements

* All abstract methods must be implemented with the exact signatures defined in the protocol.
* Implementation classes should import the protocol from `omnibase.protocol.<protocol_module>`.
* Additional helper methods may be added, but core protocol methods must maintain their defined behavior.
* Protocol implementations should be thoroughly tested against the protocol's expected behavior.

#### ✅ Protocol Extensions for Execution Planning and Performance

Protocol-based components involved in execution (e.g., validators, planners, cache layers, reducers) should implement optional support for execution-aware extensions, including:

* `get_execution_profile(self) -> dict`: Returns an optional execution profile for use in planner optimization (`speed`, `accuracy`, `efficiency`).
* 
  ```python
  from pydantic import BaseModel

  class StateContractInput(BaseModel):
      ...
  ```

* `get_cache_key_hint(self, input_state: StateContractInput) -> str`: Returns a hash or identifier that informs memoization or cache strategies.
* `supports_memoization_tier(self) -> bool`: Indicates whether the component can participate in `deep` memoization contexts (e.g., within composite subgraphs).
* `snapshot_state(self) -> dict`: Optional reducer method to emit a resumable snapshot of internal state.

These optional methods enhance integration with the `memoization_tier`, planner optimizations, and stateful node execution tracking in ONEX.

Implementations are expected to use concrete, schema-bound types for all method inputs and outputs, consistent with the declared `state_contract` in their `.onex` metadata.

---

### Monadic Node Protocols

As outlined in the [Functional Monadic Node Architecture](./functional_monadic_node_architecture.md) document, ONEX will introduce new protocol interfaces in M2 to support monadic composition of nodes with explicit state tracking and effect management.

#### ✅ NodeResult Protocol

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

#### ✅ Node Protocol

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

These protocols will enhance node composition with:

1. **Context Propagation**: Execution context flows through node chains
2. **State Delta Tracking**: Explicit tracking of state changes
3. **Effect Management**: Structured events for side effects
4. **Monadic Composition**: Type-safe, context-aware node chaining

Implementation of these protocols is scheduled for M2 (Q3 2025) with full event propagation and simulation support by M4 (Q1 2026) as specified in the Functional Monadic Node Architecture document.

---

**Status:** This document defines the canonical protocols that form the foundation of the ONEX component system. All core components must implement these protocols to ensure compatibility and integration with the broader ONEX ecosystem.

---
