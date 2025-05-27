<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: architecture-node-monadic-core.md
version: 1.0.0
uuid: 96d17916-bb43-4bb6-ac84-08d8e921f1e4
author: OmniNode Team
created_at: 2025-05-27T12:29:21.075511
last_modified_at: 2025-05-27T17:26:51.918439
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 556be7d5855d6553844e59dd4e75104af3a0a03dba47d588d8108fedd5b05984
entrypoint: python@architecture-node-monadic-core.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.architecture_node_monadic_core
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Architecture: Monadic Core Principles

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Define the core monadic principles and interfaces for ONEX nodes  
> **Audience:** Node developers, system architects  
> **See Also:** [Node Composition](architecture-node-composition.md), [Monadic Implementation Guide](guide-node-monadic-implementation.md)

---

## Overview

ONEX nodes follow a monadic, functionally composable architecture with explicit state modeling, context propagation, and effect tracking. This document defines the core principles and interfaces that enable clean node composition, structured execution, introspection, and full replayability.

---

## Core Design Principles

### Node as a Computation Unit

Each node is a computation from `input -> output` that returns a `NodeResult`, encapsulating:

* Output value
* Execution context (provenance, logs, trust, timestamp)
* Optional side effect metadata
* Optional state diffs

### Minimal Interface

```python
from typing import Generic, TypeVar, Optional, Dict, List, Callable, Awaitable
from datetime import datetime

T = TypeVar('T')
U = TypeVar('U')

class NodeResult(Generic[T]):
    """Monadic result wrapper for node execution."""
    value: T
    context: ExecutionContext
    state_delta: Optional[Dict] = None
    events: Optional[List[Event]] = None

    async def bind(self, f: Callable[[T], Awaitable['NodeResult[U]']]) -> 'NodeResult[U]':
        """Monadic bind operation for composing nodes."""
        return await f(self.value)

class Node(Generic[T, U]):
    """Base node interface for monadic composition."""
    async def run(self, input: T) -> NodeResult[U]:
        """Execute the node with given input."""
        ...
```

### ExecutionContext Structure

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class LogEntry:
    """Structured log entry."""
    level: str
    message: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ExecutionContext:
    """Execution context for node runs."""
    provenance: List[str]             # trace of node invocations
    logs: List[LogEntry]             # structured logs per step
    trust_score: float               # numeric trust level (0.0-1.0)
    timestamp: datetime              # execution timestamp
    metadata: Dict[str, Any]         # additional ad hoc data
    session_id: Optional[str] = None # session identifier
    correlation_id: Optional[str] = None # correlation identifier
```

### Event Structure

```python
@dataclass
class Event:
    """Structured event for side effects and observability."""
    type: str                        # e.g., "log", "metric", "alert", "db_write"
    payload: Dict[str, Any]          # structured content
    timestamp: datetime
    source: Optional[str] = None     # source node identifier
    correlation_id: Optional[str] = None
```

### State Delta Format

State deltas follow a structured contract for composability:

* JSON Patch-style object diffs (RFC 6902)
* OR key-value overwrite map (e.g., `{"users[123].status": "active"}`)
* Must be serializable and composable

```python
# Example state delta formats
state_delta = {
    "op": "replace",
    "path": "/user/status", 
    "value": "active"
}

# Or simple key-value format
state_delta = {
    "user.status": "active",
    "user.last_updated": "2025-05-27T10:00:00Z"
}
```

---

## Node Types and Monadic Classification

### Pure Nodes
**Characteristics:** Deterministic, no side effects. Equivalent to `Identity` monad.

```python
class PureTextProcessor(Node[str, str]):
    """Pure functional text processing node."""
    
    async def run(self, input: str) -> NodeResult[str]:
        processed = input.strip().lower()
        
        return NodeResult(
            value=processed,
            context=ExecutionContext(
                provenance=["text_processor"],
                logs=[],
                trust_score=1.0,
                timestamp=datetime.now(),
                metadata={"input_length": len(input)}
            ),
            state_delta=None,
            events=[]
        )
```

### Impure Nodes
**Characteristics:** May access internal state, external services, or include cost/model calls.

```python
class ApiCallNode(Node[Dict, Dict]):
    """Impure node that makes external API calls."""
    
    async def run(self, input: Dict) -> NodeResult[Dict]:
        try:
            response = await self.make_api_call(input)
            
            return NodeResult(
                value=response,
                context=ExecutionContext(
                    provenance=["api_call"],
                    logs=[LogEntry("INFO", "API call successful", datetime.now())],
                    trust_score=0.8,  # Lower trust due to external dependency
                    timestamp=datetime.now(),
                    metadata={"api_endpoint": input.get("url")}
                ),
                state_delta={"last_api_call": datetime.now().isoformat()},
                events=[Event("api_call", {"url": input.get("url")}, datetime.now())]
            )
        except Exception as e:
            return NodeResult(
                value={},
                context=ExecutionContext(
                    provenance=["api_call"],
                    logs=[LogEntry("ERROR", str(e), datetime.now())],
                    trust_score=0.0,
                    timestamp=datetime.now(),
                    metadata={"error": str(e)}
                ),
                state_delta=None,
                events=[Event("api_error", {"error": str(e)}, datetime.now())]
            )
```

### Plugin Nodes
**Characteristics:** Emit side effects only (e.g. logging, telemetry). Equivalent to `Writer` monad.

```python
class LoggingNode(Node[Any, Any]):
    """Plugin node for logging side effects."""
    
    async def run(self, input: Any) -> NodeResult[Any]:
        log_event = Event(
            type="log",
            payload={"input": str(input)},
            timestamp=datetime.now(),
            source="logging_node"
        )
        
        return NodeResult(
            value=input,  # Pass through unchanged
            context=ExecutionContext(
                provenance=["logging_node"],
                logs=[LogEntry("INFO", f"Logged input: {input}", datetime.now())],
                trust_score=1.0,
                timestamp=datetime.now(),
                metadata={}
            ),
            state_delta=None,
            events=[log_event]
        )
```

### Stateful Nodes
**Characteristics:** Maintain internal state across invocations. Equivalent to `State` monad.

```python
class CounterNode(Node[int, int]):
    """Stateful node that maintains a counter."""
    
    def __init__(self):
        self.counter = 0
    
    async def run(self, input: int) -> NodeResult[int]:
        old_counter = self.counter
        self.counter += input
        
        return NodeResult(
            value=self.counter,
            context=ExecutionContext(
                provenance=["counter_node"],
                logs=[LogEntry("INFO", f"Counter: {old_counter} -> {self.counter}", datetime.now())],
                trust_score=1.0,
                timestamp=datetime.now(),
                metadata={"increment": input}
            ),
            state_delta={"counter": {"old": old_counter, "new": self.counter}},
            events=[Event("counter_updated", {"old": old_counter, "new": self.counter}, datetime.now())]
        )
```

---

## Monadic Operations

### Bind Operation

The `bind` operation enables monadic composition by chaining nodes together:

```python
async def bind_example():
    """Example of monadic bind operation."""
    
    # Create initial result
    initial_result = NodeResult(
        value="hello world",
        context=ExecutionContext(
            provenance=["initial"],
            logs=[],
            trust_score=1.0,
            timestamp=datetime.now(),
            metadata={}
        )
    )
    
    # Bind to text processor
    processor = PureTextProcessor()
    final_result = await initial_result.bind(processor.run)
    
    print(f"Final value: {final_result.value}")  # "hello world"
    print(f"Provenance: {final_result.context.provenance}")  # ["initial", "text_processor"]
```

### Functor Operations

```python
class NodeResult(Generic[T]):
    """Extended NodeResult with functor operations."""
    
    def map(self, f: Callable[[T], U]) -> 'NodeResult[U]':
        """Apply function to wrapped value without changing context."""
        return NodeResult(
            value=f(self.value),
            context=self.context,
            state_delta=self.state_delta,
            events=self.events
        )
    
    def map_context(self, f: Callable[[ExecutionContext], ExecutionContext]) -> 'NodeResult[T]':
        """Apply function to execution context."""
        return NodeResult(
            value=self.value,
            context=f(self.context),
            state_delta=self.state_delta,
            events=self.events
        )

# Usage example
result = NodeResult(value=42, context=base_context)
doubled = result.map(lambda x: x * 2)  # value becomes 84
```

### Applicative Operations

```python
class NodeResult(Generic[T]):
    """Extended NodeResult with applicative operations."""
    
    @staticmethod
    def pure(value: T) -> 'NodeResult[T]':
        """Wrap a pure value in NodeResult."""
        return NodeResult(
            value=value,
            context=ExecutionContext(
                provenance=[],
                logs=[],
                trust_score=1.0,
                timestamp=datetime.now(),
                metadata={}
            ),
            state_delta=None,
            events=[]
        )
    
    def apply(self, f_result: 'NodeResult[Callable[[T], U]]') -> 'NodeResult[U]':
        """Apply a wrapped function to a wrapped value."""
        # Combine contexts
        combined_context = ExecutionContext(
            provenance=f_result.context.provenance + self.context.provenance,
            logs=f_result.context.logs + self.context.logs,
            trust_score=min(f_result.context.trust_score, self.context.trust_score),
            timestamp=max(f_result.context.timestamp, self.context.timestamp),
            metadata={**f_result.context.metadata, **self.context.metadata}
        )
        
        return NodeResult(
            value=f_result.value(self.value),
            context=combined_context,
            state_delta=self.state_delta,  # Could merge deltas
            events=(f_result.events or []) + (self.events or [])
        )

# Usage example
add_func = NodeResult.pure(lambda x: lambda y: x + y)
value1 = NodeResult.pure(10)
value2 = NodeResult.pure(20)

result = value2.apply(value1.apply(add_func))  # 30
```

---

## Error Handling

### Result Types

```python
from enum import Enum
from typing import Union

class ErrorType(Enum):
    """Types of errors that can occur in node execution."""
    VALIDATION = "validation"
    TIMEOUT = "timeout"
    NETWORK = "network"
    PERMISSION = "permission"
    RESOURCE = "resource"
    INTERNAL = "internal"

@dataclass
class ErrorInfo:
    """Structured error information."""
    error_type: ErrorType
    message: str
    retryable: bool = False
    backoff_strategy: Optional[str] = None
    max_attempts: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class Success(NodeResult[T]):
    """Successful node execution result."""
    pass

class Failure(Generic[T]):
    """Failed node execution result."""
    error: ErrorInfo
    context: ExecutionContext
    
    async def bind(self, f: Callable[[T], Awaitable[NodeResult[U]]]) -> 'Failure[U]':
        """Bind operation for failures (short-circuits)."""
        return Failure(error=self.error, context=self.context)

# Type alias for node results
NodeExecutionResult = Union[Success[T], Failure[T]]
```

### Error Propagation

```python
class ErrorHandlingNode(Node[T, U]):
    """Base class with error handling patterns."""
    
    async def run(self, input: T) -> NodeExecutionResult[U]:
        try:
            result = await self.execute_logic(input)
            return Success(
                value=result,
                context=self.build_context(),
                state_delta=self.compute_delta(),
                events=self.get_events()
            )
        except ValidationError as e:
            return Failure(
                error=ErrorInfo(
                    error_type=ErrorType.VALIDATION,
                    message=str(e),
                    retryable=False
                ),
                context=self.build_error_context(e)
            )
        except TimeoutError as e:
            return Failure(
                error=ErrorInfo(
                    error_type=ErrorType.TIMEOUT,
                    message=str(e),
                    retryable=True,
                    backoff_strategy="exponential",
                    max_attempts=3
                ),
                context=self.build_error_context(e)
            )
    
    async def execute_logic(self, input: T) -> U:
        """Override this method with actual node logic."""
        raise NotImplementedError
    
    def build_context(self) -> ExecutionContext:
        """Build execution context for successful execution."""
        return ExecutionContext(
            provenance=[self.__class__.__name__.lower()],
            logs=[],
            trust_score=1.0,
            timestamp=datetime.now(),
            metadata={}
        )
    
    def build_error_context(self, error: Exception) -> ExecutionContext:
        """Build execution context for error cases."""
        return ExecutionContext(
            provenance=[self.__class__.__name__.lower()],
            logs=[LogEntry("ERROR", str(error), datetime.now())],
            trust_score=0.0,
            timestamp=datetime.now(),
            metadata={"error_type": type(error).__name__}
        )
```

---

## Context Propagation

### Context Merging

```python
class ContextMerger:
    """Utility for merging execution contexts."""
    
    @staticmethod
    def merge_contexts(contexts: List[ExecutionContext]) -> ExecutionContext:
        """Merge multiple execution contexts."""
        if not contexts:
            return ExecutionContext(
                provenance=[],
                logs=[],
                trust_score=1.0,
                timestamp=datetime.now(),
                metadata={}
            )
        
        # Combine provenance chains
        combined_provenance = []
        for ctx in contexts:
            combined_provenance.extend(ctx.provenance)
        
        # Combine logs chronologically
        all_logs = []
        for ctx in contexts:
            all_logs.extend(ctx.logs)
        all_logs.sort(key=lambda log: log.timestamp)
        
        # Take minimum trust score
        min_trust = min(ctx.trust_score for ctx in contexts)
        
        # Take latest timestamp
        latest_timestamp = max(ctx.timestamp for ctx in contexts)
        
        # Merge metadata (later contexts override earlier ones)
        combined_metadata = {}
        for ctx in contexts:
            combined_metadata.update(ctx.metadata)
        
        return ExecutionContext(
            provenance=combined_provenance,
            logs=all_logs,
            trust_score=min_trust,
            timestamp=latest_timestamp,
            metadata=combined_metadata
        )
```

### Context Enhancement

```python
class ContextEnhancer:
    """Utility for enhancing execution contexts."""
    
    @staticmethod
    def add_provenance(context: ExecutionContext, node_name: str) -> ExecutionContext:
        """Add node to provenance chain."""
        return ExecutionContext(
            provenance=context.provenance + [node_name],
            logs=context.logs,
            trust_score=context.trust_score,
            timestamp=context.timestamp,
            metadata=context.metadata,
            session_id=context.session_id,
            correlation_id=context.correlation_id
        )
    
    @staticmethod
    def add_log(context: ExecutionContext, log_entry: LogEntry) -> ExecutionContext:
        """Add log entry to context."""
        return ExecutionContext(
            provenance=context.provenance,
            logs=context.logs + [log_entry],
            trust_score=context.trust_score,
            timestamp=context.timestamp,
            metadata=context.metadata,
            session_id=context.session_id,
            correlation_id=context.correlation_id
        )
    
    @staticmethod
    def update_trust(context: ExecutionContext, new_trust: float) -> ExecutionContext:
        """Update trust score (takes minimum)."""
        return ExecutionContext(
            provenance=context.provenance,
            logs=context.logs,
            trust_score=min(context.trust_score, new_trust),
            timestamp=context.timestamp,
            metadata=context.metadata,
            session_id=context.session_id,
            correlation_id=context.correlation_id
        )
```

---

## See Also

- [Node Composition](architecture-node-composition.md) - Composition patterns and execution models
- [Monadic Implementation Guide](guide-node-monadic-implementation.md) - Implementation examples and practical usage
- [Node Architecture Index](nodes/index.md) - Overview of node architecture series
- [State Reducers](nodes/state_reducers.md) - State management patterns
- [Node Contracts](nodes/node_contracts.md) - Contract-first node design
