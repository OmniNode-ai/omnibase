<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: architecture-node-composition.md
version: 1.0.0
uuid: 0ff5ab92-cfc7-461b-9bd9-35a882c2ef69
author: OmniNode Team
created_at: 2025-05-27T12:31:07.194818
last_modified_at: 2025-05-27T17:26:51.854076
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 959d5ab9fb5e0943cfdafa8bea00f38a05c231258c9ef2e08deae2d192e6a15c
entrypoint: python@architecture-node-composition.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.architecture_node_composition
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Architecture: Composition Patterns

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define composition patterns and execution models for monadic ONEX nodes  
> **Audience:** Node developers, system architects  
> **See Also:** [Monadic Core Principles](architecture-node-monadic-core.md), [Monadic Implementation Guide](guide-node-monadic-implementation.md)

---

## Overview

This document defines the composition patterns and execution models that enable complex workflows through monadic node composition. It covers sequential composition, parallel execution, conditional flows, and advanced patterns for building robust node pipelines.

---

## Sequential Composition

### Basic Chaining

```python
async def sequential_pipeline(input_data: str) -> NodeResult[Dict]:
    """Example of sequential node composition."""
    
    # Step 1: Parse input
    parser = JsonParserNode()
    parse_result = await parser.run(input_data)
    if isinstance(parse_result, Failure):
        return parse_result
    
    # Step 2: Validate data
    validator = DataValidatorNode()
    validation_result = await parse_result.bind(validator.run)
    if isinstance(validation_result, Failure):
        return validation_result
    
    # Step 3: Transform data
    transformer = DataTransformerNode()
    final_result = await validation_result.bind(transformer.run)
    
    return final_result

# Alternative using monadic composition
async def sequential_pipeline_monadic(input_data: str) -> NodeResult[Dict]:
    """Same pipeline using pure monadic composition."""
    
    initial_result = NodeResult.pure(input_data)
    
    return await (initial_result
                  .bind(JsonParserNode().run)
                  .bind(DataValidatorNode().run)
                  .bind(DataTransformerNode().run))
```

### Pipeline Builder

```python
class Pipeline:
    """Builder for sequential node pipelines."""
    
    def __init__(self):
        self.nodes: List[Node] = []
    
    def add_node(self, node: Node) -> 'Pipeline':
        """Add node to pipeline."""
        self.nodes.append(node)
        return self
    
    def then(self, node: Node) -> 'Pipeline':
        """Alias for add_node for fluent interface."""
        return self.add_node(node)
    
    async def execute(self, input_data: Any) -> NodeResult[Any]:
        """Execute the pipeline."""
        result = NodeResult.pure(input_data)
        
        for node in self.nodes:
            result = await result.bind(node.run)
            if isinstance(result, Failure):
                return result
        
        return result

# Usage
pipeline = (Pipeline()
           .then(JsonParserNode())
           .then(DataValidatorNode())
           .then(DataTransformerNode()))

result = await pipeline.execute(input_data)
```

---

## Parallel Composition

### Concurrent Execution

```python
import asyncio
from typing import List, Tuple

class ParallelComposer:
    """Utility for parallel node execution."""
    
    @staticmethod
    async def run_parallel(
        nodes: List[Node], 
        input_data: Any
    ) -> List[NodeResult]:
        """Run multiple nodes in parallel with same input."""
        tasks = [node.run(input_data) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to Failure results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(Failure(
                    error=ErrorInfo(
                        error_type=ErrorType.INTERNAL,
                        message=str(result),
                        retryable=False
                    ),
                    context=ExecutionContext(
                        provenance=["parallel_execution"],
                        logs=[LogEntry("ERROR", str(result), datetime.now())],
                        trust_score=0.0,
                        timestamp=datetime.now(),
                        metadata={"exception_type": type(result).__name__}
                    )
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    @staticmethod
    async def run_parallel_with_aggregation(
        nodes: List[Node],
        input_data: Any,
        aggregator: Callable[[List[NodeResult]], NodeResult]
    ) -> NodeResult:
        """Run nodes in parallel and aggregate results."""
        results = await ParallelComposer.run_parallel(nodes, input_data)
        return aggregator(results)

# Example aggregator functions
def take_first_success(results: List[NodeResult]) -> NodeResult:
    """Return first successful result."""
    for result in results:
        if isinstance(result, Success):
            return result
    
    # All failed, return first failure
    return results[0] if results else Failure(
        error=ErrorInfo(ErrorType.INTERNAL, "No results"),
        context=ExecutionContext([], [], 0.0, datetime.now(), {})
    )

def merge_all_results(results: List[NodeResult]) -> NodeResult:
    """Merge all successful results."""
    successful_results = [r for r in results if isinstance(r, Success)]
    
    if not successful_results:
        return results[0] if results else Failure(
            error=ErrorInfo(ErrorType.INTERNAL, "No successful results"),
            context=ExecutionContext([], [], 0.0, datetime.now(), {})
        )
    
    # Merge values (assuming they're dictionaries)
    merged_value = {}
    all_contexts = []
    all_events = []
    
    for result in successful_results:
        if isinstance(result.value, dict):
            merged_value.update(result.value)
        all_contexts.append(result.context)
        if result.events:
            all_events.extend(result.events)
    
    return NodeResult(
        value=merged_value,
        context=ContextMerger.merge_contexts(all_contexts),
        state_delta=None,
        events=all_events
    )
```

### Fan-Out/Fan-In Pattern

```python
class FanOutFanInNode(Node[Any, Dict]):
    """Node that fans out to multiple processors and fans in results."""
    
    def __init__(self, processors: List[Node], aggregator: Callable = merge_all_results):
        self.processors = processors
        self.aggregator = aggregator
    
    async def run(self, input_data: Any) -> NodeResult[Dict]:
        # Fan out: run all processors in parallel
        results = await ParallelComposer.run_parallel(self.processors, input_data)
        
        # Fan in: aggregate results
        aggregated = self.aggregator(results)
        
        # Add our own context
        if isinstance(aggregated, Success):
            enhanced_context = ContextEnhancer.add_provenance(
                aggregated.context, 
                "fan_out_fan_in"
            )
            return NodeResult(
                value=aggregated.value,
                context=enhanced_context,
                state_delta=aggregated.state_delta,
                events=aggregated.events
            )
        
        return aggregated

# Usage
processors = [
    TextAnalysisNode(),
    SentimentAnalysisNode(),
    EntityExtractionNode()
]

fan_out_node = FanOutFanInNode(processors, merge_all_results)
result = await fan_out_node.run("Analyze this text")
```

---

## Conditional Composition

### Conditional Execution

```python
class ConditionalNode(Node[Any, Any]):
    """Node that executes different paths based on conditions."""
    
    def __init__(
        self,
        condition: Callable[[Any], bool],
        true_node: Node,
        false_node: Optional[Node] = None
    ):
        self.condition = condition
        self.true_node = true_node
        self.false_node = false_node
    
    async def run(self, input_data: Any) -> NodeResult[Any]:
        if self.condition(input_data):
            result = await self.true_node.run(input_data)
            path = "true_branch"
        elif self.false_node:
            result = await self.false_node.run(input_data)
            path = "false_branch"
        else:
            # Pass through unchanged
            result = NodeResult.pure(input_data)
            path = "passthrough"
        
        # Add conditional execution to provenance
        if isinstance(result, Success):
            enhanced_context = ContextEnhancer.add_provenance(
                result.context,
                f"conditional_{path}"
            )
            return NodeResult(
                value=result.value,
                context=enhanced_context,
                state_delta=result.state_delta,
                events=result.events
            )
        
        return result

# Usage
def is_large_data(data: Any) -> bool:
    return len(str(data)) > 1000

conditional_processor = ConditionalNode(
    condition=is_large_data,
    true_node=LargeDataProcessorNode(),
    false_node=SmallDataProcessorNode()
)
```

### Switch/Case Pattern

```python
class SwitchNode(Node[Any, Any]):
    """Node that routes to different processors based on input type/value."""
    
    def __init__(self, cases: Dict[Any, Node], default_node: Optional[Node] = None):
        self.cases = cases
        self.default_node = default_node
    
    async def run(self, input_data: Any) -> NodeResult[Any]:
        # Determine which case to execute
        case_key = self.determine_case(input_data)
        
        if case_key in self.cases:
            selected_node = self.cases[case_key]
            result = await selected_node.run(input_data)
            path = f"case_{case_key}"
        elif self.default_node:
            result = await self.default_node.run(input_data)
            path = "default"
        else:
            result = NodeResult.pure(input_data)
            path = "passthrough"
        
        # Add switch execution to provenance
        if isinstance(result, Success):
            enhanced_context = ContextEnhancer.add_provenance(
                result.context,
                f"switch_{path}"
            )
            return NodeResult(
                value=result.value,
                context=enhanced_context,
                state_delta=result.state_delta,
                events=result.events
            )
        
        return result
    
    def determine_case(self, input_data: Any) -> Any:
        """Override this method to implement case selection logic."""
        if isinstance(input_data, dict) and "type" in input_data:
            return input_data["type"]
        return type(input_data).__name__

# Usage
data_processors = SwitchNode(
    cases={
        "text": TextProcessorNode(),
        "image": ImageProcessorNode(),
        "audio": AudioProcessorNode()
    },
    default_node=GenericProcessorNode()
)
```

---

## Asynchronous Support

### Streaming Nodes

```python
from typing import AsyncIterator

class StreamingNode(Node[Any, AsyncIterator[Any]]):
    """Node that supports streaming output."""
    
    async def run(self, input_data: Any) -> NodeResult[AsyncIterator[Any]]:
        async def stream_generator():
            # Process input in chunks
            chunks = self.chunk_input(input_data)
            for chunk in chunks:
                processed_chunk = await self.process_chunk(chunk)
                yield processed_chunk
        
        return NodeResult(
            value=stream_generator(),
            context=ExecutionContext(
                provenance=["streaming_node"],
                logs=[LogEntry("INFO", "Streaming started", datetime.now())],
                trust_score=1.0,
                timestamp=datetime.now(),
                metadata={"streaming": True}
            ),
            state_delta={"streaming_started": datetime.now().isoformat()},
            events=[Event("stream_start", {"input_size": len(str(input_data))}, datetime.now())]
        )
    
    def chunk_input(self, input_data: Any) -> List[Any]:
        """Override to implement input chunking logic."""
        if isinstance(input_data, str):
            # Split text into sentences
            return input_data.split('.')
        elif isinstance(input_data, list):
            # Process list in batches
            batch_size = 10
            return [input_data[i:i+batch_size] for i in range(0, len(input_data), batch_size)]
        else:
            return [input_data]
    
    async def process_chunk(self, chunk: Any) -> Any:
        """Override to implement chunk processing logic."""
        # Simulate async processing
        await asyncio.sleep(0.1)
        return f"processed: {chunk}"

# Usage
async def consume_stream(stream_result: NodeResult[AsyncIterator[Any]]):
    """Example of consuming streaming output."""
    async for chunk in stream_result.value:
        print(f"Received chunk: {chunk}")
```

### Interruptible Nodes

```python
class InterruptibleNode(Node[Dict, Dict]):
    """Node that can be interrupted and resumed."""
    
    def __init__(self):
        self.interruption_flag = asyncio.Event()
    
    async def run(self, input_data: Dict) -> NodeResult[Dict]:
        checkpoint = input_data.get("checkpoint", 0)
        total_steps = input_data.get("total_steps", 100)
        
        for i in range(checkpoint, total_steps):
            # Check for interruption
            if self.interruption_flag.is_set():
                return NodeResult(
                    value={
                        "status": "interrupted",
                        "checkpoint": i,
                        "progress": i / total_steps
                    },
                    context=ExecutionContext(
                        provenance=["interruptible_node"],
                        logs=[LogEntry("WARN", f"Interrupted at step {i}", datetime.now())],
                        trust_score=0.8,
                        timestamp=datetime.now(),
                        metadata={"interrupted": True}
                    ),
                    state_delta={"last_checkpoint": i},
                    events=[Event("interrupted", {"checkpoint": i}, datetime.now())]
                )
            
            # Simulate work
            await self.process_step(i)
            
            # Yield control periodically
            if i % 10 == 0:
                await asyncio.sleep(0)
        
        return NodeResult(
            value={
                "status": "completed",
                "checkpoint": total_steps,
                "progress": 1.0
            },
            context=ExecutionContext(
                provenance=["interruptible_node"],
                logs=[LogEntry("INFO", "Processing completed", datetime.now())],
                trust_score=1.0,
                timestamp=datetime.now(),
                metadata={"completed": True}
            ),
            state_delta={"completed": True},
            events=[Event("completed", {"total_steps": total_steps}, datetime.now())]
        )
    
    async def process_step(self, step: int):
        """Simulate processing a single step."""
        await asyncio.sleep(0.01)  # Simulate work
    
    def interrupt(self):
        """Signal the node to interrupt."""
        self.interruption_flag.set()
    
    def resume(self):
        """Clear the interruption flag."""
        self.interruption_flag.clear()
```

---

## Side Effect Modeling

### Effect Tracking

```python
class EffectTracker:
    """Utility for tracking and managing side effects."""
    
    def __init__(self):
        self.effects: List[Event] = []
    
    def record_effect(self, effect: Event):
        """Record a side effect."""
        self.effects.append(effect)
    
    def get_effects_by_type(self, effect_type: str) -> List[Event]:
        """Get all effects of a specific type."""
        return [e for e in self.effects if e.type == effect_type]
    
    def clear_effects(self):
        """Clear all recorded effects."""
        self.effects.clear()

class EffectAwareNode(Node[Any, Any]):
    """Base class for nodes that track side effects."""
    
    def __init__(self):
        self.effect_tracker = EffectTracker()
    
    async def run(self, input_data: Any) -> NodeResult[Any]:
        # Clear previous effects
        self.effect_tracker.clear_effects()
        
        # Execute node logic
        result = await self.execute_with_effects(input_data)
        
        # Add tracked effects to result
        if isinstance(result, Success):
            all_events = (result.events or []) + self.effect_tracker.effects
            return NodeResult(
                value=result.value,
                context=result.context,
                state_delta=result.state_delta,
                events=all_events
            )
        
        return result
    
    async def execute_with_effects(self, input_data: Any) -> NodeResult[Any]:
        """Override this method to implement node logic with effect tracking."""
        raise NotImplementedError
    
    def emit_effect(self, effect_type: str, payload: Dict[str, Any]):
        """Emit a side effect."""
        effect = Event(
            type=effect_type,
            payload=payload,
            timestamp=datetime.now(),
            source=self.__class__.__name__
        )
        self.effect_tracker.record_effect(effect)
```

### Deterministic Replay

```python
class ReplayableNode(Node[Any, Any]):
    """Node that supports deterministic replay."""
    
    def __init__(self, replay_mode: bool = False):
        self.replay_mode = replay_mode
        self.replay_cache: Dict[str, Any] = {}
        self.effect_log: List[Event] = []
    
    async def run(self, input_data: Any) -> NodeResult[Any]:
        cache_key = self.compute_cache_key(input_data)
        
        if self.replay_mode and cache_key in self.replay_cache:
            # Return cached result for deterministic replay
            cached_data = self.replay_cache[cache_key]
            return NodeResult(
                value=cached_data["value"],
                context=cached_data["context"],
                state_delta=cached_data["state_delta"],
                events=cached_data["events"] + [
                    Event("replay", {"cache_key": cache_key}, datetime.now())
                ]
            )
        
        # Execute normally
        result = await self.execute_logic(input_data)
        
        # Cache result for future replay
        if isinstance(result, Success) and not self.replay_mode:
            self.replay_cache[cache_key] = {
                "value": result.value,
                "context": result.context,
                "state_delta": result.state_delta,
                "events": result.events
            }
        
        return result
    
    def compute_cache_key(self, input_data: Any) -> str:
        """Compute cache key for input data."""
        import hashlib
        import json
        
        # Create deterministic hash of input
        input_str = json.dumps(input_data, sort_keys=True, default=str)
        return hashlib.sha256(input_str.encode()).hexdigest()
    
    async def execute_logic(self, input_data: Any) -> NodeResult[Any]:
        """Override this method with actual node logic."""
        raise NotImplementedError
    
    def enable_replay_mode(self):
        """Enable replay mode."""
        self.replay_mode = True
    
    def disable_replay_mode(self):
        """Disable replay mode."""
        self.replay_mode = False
    
    def clear_cache(self):
        """Clear replay cache."""
        self.replay_cache.clear()
```

---

## Advanced Composition Patterns

### Retry Pattern

```python
class RetryNode(Node[Any, Any]):
    """Node wrapper that adds retry logic."""
    
    def __init__(
        self,
        wrapped_node: Node,
        max_attempts: int = 3,
        backoff_strategy: str = "exponential",
        base_delay: float = 1.0
    ):
        self.wrapped_node = wrapped_node
        self.max_attempts = max_attempts
        self.backoff_strategy = backoff_strategy
        self.base_delay = base_delay
    
    async def run(self, input_data: Any) -> NodeResult[Any]:
        last_error = None
        
        for attempt in range(self.max_attempts):
            try:
                result = await self.wrapped_node.run(input_data)
                
                if isinstance(result, Success):
                    # Add retry metadata to context
                    enhanced_context = ContextEnhancer.add_log(
                        result.context,
                        LogEntry("INFO", f"Succeeded on attempt {attempt + 1}", datetime.now())
                    )
                    return NodeResult(
                        value=result.value,
                        context=enhanced_context,
                        state_delta=result.state_delta,
                        events=result.events
                    )
                elif isinstance(result, Failure) and result.error.retryable:
                    last_error = result.error
                    if attempt < self.max_attempts - 1:
                        delay = self.calculate_delay(attempt)
                        await asyncio.sleep(delay)
                        continue
                else:
                    # Non-retryable error
                    return result
                    
            except Exception as e:
                last_error = ErrorInfo(
                    error_type=ErrorType.INTERNAL,
                    message=str(e),
                    retryable=True
                )
                if attempt < self.max_attempts - 1:
                    delay = self.calculate_delay(attempt)
                    await asyncio.sleep(delay)
                    continue
        
        # All attempts failed
        return Failure(
            error=ErrorInfo(
                error_type=last_error.error_type if last_error else ErrorType.INTERNAL,
                message=f"Failed after {self.max_attempts} attempts: {last_error.message if last_error else 'Unknown error'}",
                retryable=False
            ),
            context=ExecutionContext(
                provenance=["retry_node"],
                logs=[LogEntry("ERROR", f"All {self.max_attempts} attempts failed", datetime.now())],
                trust_score=0.0,
                timestamp=datetime.now(),
                metadata={"max_attempts": self.max_attempts}
            )
        )
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for next retry attempt."""
        if self.backoff_strategy == "exponential":
            return self.base_delay * (2 ** attempt)
        elif self.backoff_strategy == "linear":
            return self.base_delay * (attempt + 1)
        else:
            return self.base_delay

# Usage
reliable_api_node = RetryNode(
    wrapped_node=ApiCallNode(),
    max_attempts=3,
    backoff_strategy="exponential",
    base_delay=1.0
)
```

### Circuit Breaker Pattern

```python
class CircuitBreakerNode(Node[Any, Any]):
    """Node wrapper that implements circuit breaker pattern."""
    
    def __init__(
        self,
        wrapped_node: Node,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 3
    ):
        self.wrapped_node = wrapped_node
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def run(self, input_data: Any) -> NodeResult[Any]:
        if self.state == "OPEN":
            if self.should_attempt_reset():
                self.state = "HALF_OPEN"
                self.success_count = 0
            else:
                return Failure(
                    error=ErrorInfo(
                        error_type=ErrorType.RESOURCE,
                        message="Circuit breaker is OPEN",
                        retryable=True
                    ),
                    context=ExecutionContext(
                        provenance=["circuit_breaker"],
                        logs=[LogEntry("WARN", "Circuit breaker prevented execution", datetime.now())],
                        trust_score=0.0,
                        timestamp=datetime.now(),
                        metadata={"circuit_state": "OPEN"}
                    )
                )
        
        try:
            result = await self.wrapped_node.run(input_data)
            
            if isinstance(result, Success):
                self.on_success()
            else:
                self.on_failure()
            
            return result
            
        except Exception as e:
            self.on_failure()
            return Failure(
                error=ErrorInfo(
                    error_type=ErrorType.INTERNAL,
                    message=str(e),
                    retryable=True
                ),
                context=ExecutionContext(
                    provenance=["circuit_breaker"],
                    logs=[LogEntry("ERROR", str(e), datetime.now())],
                    trust_score=0.0,
                    timestamp=datetime.now(),
                    metadata={"circuit_state": self.state}
                )
            )
    
    def on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        
        if self.state == "HALF_OPEN":
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = "CLOSED"
    
    def on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if self.last_failure_time is None:
            return False
        
        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.recovery_timeout
```

---

## See Also

- [Monadic Core Principles](architecture-node-monadic-core.md) - Core monadic principles and interfaces
- [Monadic Implementation Guide](guide-node-monadic-implementation.md) - Implementation examples and practical usage
- [Node Architecture Index](nodes/index.md) - Overview of node architecture series
- [State Reducers](nodes/state_reducers.md) - State management patterns
- [Sessions and Streaming](nodes/sessions_and_streaming.md) - Session lifecycle and streaming architecture
