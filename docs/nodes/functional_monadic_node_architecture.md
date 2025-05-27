# ONEX Node Architecture: Functional Monadic Node Architecture

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the monadic, functionally composable architecture for ONEX nodes with explicit state modeling and effect tracking  
> **Audience:** Node developers, system architects, maintainers  
> **Series:** Node Architecture  

---

## Overview

ONEX nodes follow a monadic, functionally composable architecture with explicit state modeling, context propagation, and effect tracking. This pattern enables clean node composition, structured execution, introspection, agent simulation, and full replayability.

This document defines the canonical model for functional composition of nodes, extending the existing [Node as a Function](./index.md) conceptual model with monadic principles.

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
    "user.last_updated": "2025-01-27T10:00:00Z"
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

### Ephemeral Nodes
**Characteristics:** Model calls or non-deterministic functions. Return values are captured and replayed for simulation.

```python
class LLMNode(Node[str, str]):
    """Ephemeral node for LLM calls with replay support."""
    
    async def run(self, input: str) -> NodeResult[str]:
        # Check for cached/replayed result first
        if cached_result := self.get_cached_result(input):
            return cached_result
        
        # Make actual LLM call
        response = await self.call_llm(input)
        
        result = NodeResult(
            value=response,
            context=ExecutionContext(
                provenance=["llm_node"],
                logs=[LogEntry("INFO", "LLM call completed", datetime.now())],
                trust_score=0.7,  # Model outputs have inherent uncertainty
                timestamp=datetime.now(),
                metadata={"model": "gpt-4", "tokens": len(response.split())}
            ),
            state_delta={"last_llm_call": datetime.now().isoformat()},
            events=[Event("llm_call", {"input_tokens": len(input.split())}, datetime.now())]
        )
        
        # Cache for replay
        self.cache_result(input, result)
        return result
```

---

## Monadic Composition

Nodes are composed via `bind()` for safe chaining with context propagation:

```python
async def process_pipeline(raw_input: str) -> NodeResult[bool]:
    """Example pipeline using monadic composition."""
    
    # Parse input
    result = await ParseInput().run(raw_input)
    
    # Process data (bind propagates context)
    result = await result.bind(ProcessData().run)
    
    # Add logging (plugin node)
    result = await result.bind(LoggingNode().run)
    
    # Store result
    result = await result.bind(StoreResult().run)
    
    return result
```

### Advanced Composition Patterns

```python
# Parallel execution with gather
async def parallel_processing(input_data: Dict) -> NodeResult[List]:
    """Run multiple nodes in parallel."""
    results = await NodeResult.gather([
        NodeA().run(input_data),
        NodeB().run(input_data),
        NodeC().run(input_data)
    ])
    return results

# Conditional branching
async def conditional_processing(input_data: Dict) -> NodeResult[Any]:
    """Conditional node execution."""
    if input_data.get("type") == "text":
        return await TextProcessor().run(input_data)
    else:
        return await DataProcessor().run(input_data)

# Error recovery with fallback
async def resilient_processing(input_data: Dict) -> NodeResult[Any]:
    """Processing with fallback on failure."""
    try:
        return await PrimaryProcessor().run(input_data)
    except Exception:
        return await FallbackProcessor().run(input_data)
```

---

## Redux-Style State Modeling

Each node produces state deltas that are interpreted by a central reducer:

```python
def global_reducer(state: Dict, action: Dict) -> Dict:
    """Central reducer for state transitions."""
    action_type = action.get("type")
    
    if action_type == "UPDATE_USER":
        return {
            **state,
            "users": {
                **state.get("users", {}),
                action["user_id"]: action["user_data"]
            }
        }
    elif action_type == "INCREMENT_COUNTER":
        return {
            **state,
            "counter": state.get("counter", 0) + 1
        }
    
    return state

# Modular reducers for scalability
def combine_reducers(reducers: Dict[str, Callable]) -> Callable:
    """Combine multiple reducers into one."""
    def combined_reducer(state: Dict, action: Dict) -> Dict:
        new_state = {}
        for key, reducer in reducers.items():
            new_state[key] = reducer(state.get(key), action)
        return new_state
    return combined_reducer

# Usage
app_reducer = combine_reducers({
    "users": user_reducer,
    "sessions": session_reducer,
    "metrics": metrics_reducer
})
```

State history can be snapshotted, diffed, or replayed. Agents can simulate or inspect consequences before committing.

---

## Error Handling in Monads

NodeResult supports a discriminated union for robust error handling:

```python
from typing import Union
from enum import Enum

class ErrorType(Enum):
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    VALIDATION = "validation"
    TIMEOUT = "timeout"
    AUTHORIZATION = "authorization"

@dataclass
class ErrorInfo:
    """Structured error information."""
    error_type: ErrorType
    message: str
    code: Optional[str] = None
    trace: Optional[str] = None
    context: Optional[Dict] = None
    retryable: bool = False
    backoff_strategy: Optional[str] = None
    max_attempts: Optional[int] = None

class Success(NodeResult[T]):
    """Successful node result."""
    pass

class Failure(NodeResult[None]):
    """Failed node result with error information."""
    error: ErrorInfo
    
    def __init__(self, error: ErrorInfo, context: ExecutionContext):
        super().__init__(
            value=None,
            context=context,
            state_delta=None,
            events=[Event("error", error.__dict__, datetime.now())]
        )
        self.error = error

# Usage in nodes
async def robust_node_run(self, input: T) -> Union[Success[U], Failure]:
    try:
        result = await self.process(input)
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
```

---

## Asynchronous Support

All `.run()` and `.bind()` calls are `async`, supporting:

* Concurrent execution
* Event-driven nodes
* Streaming/long-running workflows
* Interruptible/resumable stateful computation

```python
class StreamingNode(Node[str, AsyncIterator[str]]):
    """Node that supports streaming output."""
    
    async def run(self, input: str) -> NodeResult[AsyncIterator[str]]:
        async def stream_generator():
            for chunk in self.process_streaming(input):
                yield chunk
        
        return NodeResult(
            value=stream_generator(),
            context=self.build_context(),
            state_delta={"streaming_started": datetime.now().isoformat()},
            events=[Event("stream_start", {"input": input}, datetime.now())]
        )

class InterruptibleNode(Node[Dict, Dict]):
    """Node that can be interrupted and resumed."""
    
    async def run(self, input: Dict) -> NodeResult[Dict]:
        checkpoint = input.get("checkpoint", 0)
        
        for i in range(checkpoint, 100):
            # Check for interruption signal
            if await self.check_interruption():
                return NodeResult(
                    value={"checkpoint": i, "status": "interrupted"},
                    context=self.build_context(),
                    state_delta={"last_checkpoint": i},
                    events=[Event("interrupted", {"checkpoint": i}, datetime.now())]
                )
            
            await self.process_step(i)
        
        return NodeResult(
            value={"status": "completed"},
            context=self.build_context(),
            state_delta={"completed": True},
            events=[Event("completed", {}, datetime.now())]
        )
```

---

## Side Effect Modeling

Effects are made explicit through the event system:

```python
class DatabaseNode(Node[Dict, bool]):
    """Node with explicit side effect modeling."""
    
    async def run(self, input: Dict) -> NodeResult[bool]:
        # Simulate database write
        success = await self.write_to_database(input)
        
        events = [
            Event("db_write_attempt", {"table": input.get("table")}, datetime.now())
        ]
        
        if success:
            events.append(Event("db_write_success", {"rows": 1}, datetime.now()))
        else:
            events.append(Event("db_write_failure", {"error": "connection_failed"}, datetime.now()))
        
        return NodeResult(
            value=success,
            context=self.build_context(),
            state_delta={"last_db_write": datetime.now().isoformat()} if success else None,
            events=events
        )
```

Ephemeral effects (e.g. model outputs) are captured and stored for deterministic replays:

```python
class ReplayableModelNode(Node[str, str]):
    """Model node with replay capability."""
    
    def __init__(self, replay_mode: bool = False):
        self.replay_mode = replay_mode
        self.replay_cache = {}
    
    async def run(self, input: str) -> NodeResult[str]:
        cache_key = self.compute_cache_key(input)
        
        if self.replay_mode and cache_key in self.replay_cache:
            # Return cached result for deterministic replay
            cached_result = self.replay_cache[cache_key]
            return NodeResult(
                value=cached_result["value"],
                context=cached_result["context"],
                state_delta=None,
                events=[Event("replay", {"cache_key": cache_key}, datetime.now())]
            )
        
        # Make actual model call
        result = await self.call_model(input)
        
        node_result = NodeResult(
            value=result,
            context=self.build_context(),
            state_delta={"model_calls": 1},
            events=[Event("model_call", {"input_length": len(input)}, datetime.now())]
        )
        
        # Cache for future replay
        if not self.replay_mode:
            self.replay_cache[cache_key] = {
                "value": result,
                "context": node_result.context
            }
        
        return node_result
```

---

## Agent-Native Benefits

The monadic architecture provides several benefits for agent systems:

### Full Introspection
```python
async def introspect_node(node: Node) -> Dict:
    """Get comprehensive node metadata."""
    return {
        "input_type": node.get_input_type(),
        "output_type": node.get_output_type(),
        "side_effects": node.get_side_effects(),
        "trust_level": node.get_trust_level(),
        "dependencies": node.get_dependencies(),
        "cost_estimate": node.get_cost_estimate()
    }
```

### Simulation and Planning
```python
async def simulate_workflow(nodes: List[Node], input_data: Any) -> Dict:
    """Simulate workflow execution without side effects."""
    simulation_context = ExecutionContext(
        provenance=[],
        logs=[],
        trust_score=1.0,
        timestamp=datetime.now(),
        metadata={"simulation": True}
    )
    
    # Run nodes in simulation mode
    results = []
    for node in nodes:
        node.set_simulation_mode(True)
        result = await node.run(input_data)
        results.append(result)
        input_data = result.value
    
    return {
        "final_result": input_data,
        "execution_trace": [r.context.provenance for r in results],
        "estimated_cost": sum(r.context.metadata.get("cost", 0) for r in results),
        "trust_score": min(r.context.trust_score for r in results)
    }
```

### Declarative Tool Composition
```python
# Tools are just composed node chains
text_analysis_tool = Pipeline([
    TextNormalizer(),
    SentimentAnalyzer(),
    EntityExtractor(),
    ResultFormatter()
])

# Agents can compose workflows declaratively
workflow = {
    "name": "document_processing",
    "nodes": [
        {"type": "text_extractor", "config": {"format": "pdf"}},
        {"type": "text_analyzer", "config": {"include_sentiment": True}},
        {"type": "result_store", "config": {"database": "documents"}}
    ],
    "error_handling": {
        "retry_transient": True,
        "max_attempts": 3,
        "fallback_node": "manual_review"
    }
}
```

---

## Implementation Considerations

### Trust Level Propagation

Trust metadata propagation follows these rules:

```python
def propagate_trust(node_a_trust: float, node_b_trust: float) -> float:
    """Propagate trust scores through node composition."""
    # Conservative approach: take minimum
    return min(node_a_trust, node_b_trust)

def elevate_trust(current_trust: float, validation_passed: bool) -> float:
    """Elevate trust if validation passes."""
    if validation_passed and current_trust < 1.0:
        return min(current_trust + 0.1, 1.0)
    return current_trust
```

### Performance Optimizations

```python
# Immutable data structures for efficient state diffs
from pyrsistent import pmap, pvector

class OptimizedState:
    """Optimized state using immutable data structures."""
    
    def __init__(self, data: Dict):
        self._data = pmap(data)
    
    def update(self, delta: Dict) -> 'OptimizedState':
        """Efficient state update with structure sharing."""
        return OptimizedState(self._data.update(delta))
    
    def diff(self, other: 'OptimizedState') -> Dict:
        """Compute efficient diff between states."""
        # Implementation using structure sharing
        pass

# Batched reducer updates
class BatchedReducer:
    """Reducer that batches updates for performance."""
    
    def __init__(self, base_reducer: Callable):
        self.base_reducer = base_reducer
        self.pending_actions = []
    
    def add_action(self, action: Dict):
        """Add action to batch."""
        self.pending_actions.append(action)
    
    def flush(self, state: Dict) -> Dict:
        """Apply all pending actions."""
        for action in self.pending_actions:
            state = self.base_reducer(state, action)
        self.pending_actions.clear()
        return state
```

### Observability Integration

```python
# OpenTelemetry integration
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

class TracedNode(Node[T, U]):
    """Node with distributed tracing support."""
    
    async def run(self, input: T) -> NodeResult[U]:
        tracer = trace.get_tracer(__name__)
        
        with tracer.start_as_current_span(f"node.{self.__class__.__name__}") as span:
            span.set_attribute("node.type", self.__class__.__name__)
            span.set_attribute("input.size", len(str(input)))
            
            try:
                result = await self._execute(input)
                span.set_status(Status(StatusCode.OK))
                span.set_attribute("output.size", len(str(result.value)))
                return result
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
```

---

## Practical Example

```python
# Complete pipeline example
class ParseInput(Node[str, Dict]):
    async def run(self, input: str) -> NodeResult[Dict]:
        try:
            parsed = json.loads(input)
            return NodeResult(
                value=parsed,
                context=ExecutionContext(
                    provenance=["parse_input"],
                    logs=[LogEntry("INFO", "Input parsed successfully", datetime.now())],
                    trust_score=1.0,
                    timestamp=datetime.now(),
                    metadata={"input_length": len(input)}
                ),
                state_delta=None,
                events=[]
            )
        except json.JSONDecodeError as e:
            return Failure(
                error=ErrorInfo(
                    error_type=ErrorType.VALIDATION,
                    message=f"Invalid JSON: {str(e)}",
                    retryable=False
                ),
                context=ExecutionContext(
                    provenance=["parse_input"],
                    logs=[LogEntry("ERROR", f"JSON parse error: {str(e)}", datetime.now())],
                    trust_score=0.0,
                    timestamp=datetime.now(),
                    metadata={"error": str(e)}
                )
            )

class ProcessData(Node[Dict, Dict]):
    async def run(self, input: Dict) -> NodeResult[Dict]:
        # Simulate data processing
        result = {
            "processed": True,
            "data": input,
            "timestamp": datetime.now().isoformat()
        }
        
        return NodeResult(
            value=result,
            context=ExecutionContext(
                provenance=["process_data"],
                logs=[LogEntry("INFO", "Data processed", datetime.now())],
                trust_score=0.9,
                timestamp=datetime.now(),
                metadata={"processing_time_ms": 150}
            ),
            state_delta={"last_processed": result},
            events=[Event("data_processed", {"record_count": 1}, datetime.now())]
        )

class StoreResult(Node[Dict, bool]):
    async def run(self, input: Dict) -> NodeResult[bool]:
        # Simulate database storage
        success = await self.store_to_database(input)
        
        return NodeResult(
            value=success,
            context=ExecutionContext(
                provenance=["store_result"],
                logs=[LogEntry("INFO", "Data stored", datetime.now())],
                trust_score=0.8,
                timestamp=datetime.now(),
                metadata={"storage_backend": "postgresql"}
            ),
            state_delta={"last_storage": datetime.now().isoformat()},
            events=[Event("data_stored", {"success": success}, datetime.now())]
        )

# Pipeline execution
async def run_pipeline(raw_input: str) -> NodeResult[bool]:
    """Execute complete data processing pipeline."""
    
    # Parse input
    result = await ParseInput().run(raw_input)
    if isinstance(result, Failure):
        return result
    
    # Process data
    result = await result.bind(ProcessData().run)
    if isinstance(result, Failure):
        return result
    
    # Store result
    result = await result.bind(StoreResult().run)
    
    return result

# Usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        raw_data = '{"user_id": 123, "action": "login"}'
        result = await run_pipeline(raw_data)
        
        if isinstance(result, Success):
            print(f"Pipeline completed successfully: {result.value}")
            print(f"Trust score: {result.context.trust_score}")
            print(f"Events: {len(result.events)}")
        else:
            print(f"Pipeline failed: {result.error.message}")
    
    asyncio.run(main())
```

---

## Relationship to Existing Architecture

This functional monadic architecture builds upon and enhances several existing architectural concepts:

- **Extends** the [Node as a Function](./index.md) model with explicit monadic composition
- **Formalizes** [State Reducers](./state_reducers.md) approach with explicit state deltas
- **Aligns with** [Node Typology](./node_typology.md) but explicitly categorizes nodes based on functional purity
- **Enhances** [Node Contracts](./node_contracts.md) with structured, monad-based result types
- **Complements** [Protocol Definitions](./protocol_definitions.md) with specific interfaces for monadic composition
- **Supports** [Sessions and Streaming](./sessions_and_streaming.md) through asynchronous monadic operations

---

## Benefits Summary

This architecture provides:

* **Functional purity**: Clear separation of pure and impure operations
* **Monadic composition**: Safe, composable node chaining with context propagation
* **Redux-like state semantics**: Predictable state management with time-travel debugging
* **Agent-native design**: Full introspection, simulation, and declarative composition
* **Minimal overhead**: Builds on existing execution context with structured enhancements
* **Strong guarantees**: Composability, reproducibility, testability, and planning support

---

## References

- [Node Architecture Index](./index.md) - Overview of node architecture series
- [State Reducers](./state_reducers.md) - State management and reducer patterns
- [Node Typology](./node_typology.md) - Node categorization and execution model
- [Node Contracts](./node_contracts.md) - Contract-first node design
- [Protocol Definitions](./protocol_definitions.md) - Core protocol interfaces
- [Sessions and Streaming](./sessions_and_streaming.md) - Session lifecycle and streaming architecture

---

**Note:** This document defines the canonical functional monadic architecture for ONEX nodes. It provides a robust foundation for composable, observable, and agent-friendly node execution with strong guarantees for reproducibility and testability. 