# ONEX Node Architecture: Protocol Definitions

> **Status:** Canonical  
> **Series:** Node Architecture  
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting or legacy documentation. 

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

### Protocol Migration from Foundation

This section defines the strategy for porting protocol interfaces from the legacy Foundation codebase to ONEX. The goal is to maintain functional compatibility while improving interface definitions and adapting to the function-oriented model.

#### ✅ Porting Process

1. Protocol interfaces are extracted from Foundation code.
2. Interfaces are refactored to align with ONEX naming conventions and design principles.
3. Abstract classes are defined in the `src/omnibase/protocol/` directory.
4. Concrete implementations are created in appropriate modules.

#### ✅ Protocol Naming Conventions

| Protocol Type | Naming Pattern | Example |
|---------------|----------------|---------|
| Core Protocol | `Protocol<Functionality>` | `ProtocolValidator` |
| Registry | `<Type>Registry` | `SchemaRegistry` |
| Tool | `<Functionality>Tool` | `ValidationTool` |

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

**Status:** This document defines the canonical protocols that form the foundation of the ONEX component system. All core components must implement these protocols to ensure compatibility and integration with the broader ONEX ecosystem.

---