<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: sessions_and_streaming.md
version: 1.0.0
uuid: 8eba2b3f-06e6-491c-8a12-e4e7d6f4bd64
author: OmniNode Team
created_at: 2025-05-27T08:15:15.090559
last_modified_at: 2025-05-27T17:26:51.917793
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 7ae3034d4ff237bf14867aec5dc1c7c8b695be17f1768fa5ec475c5e57f68795
entrypoint: python@sessions_and_streaming.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.sessions_and_streaming
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Architecture: Sessions and Streaming Architecture

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Define the session and streaming layer for orchestrating and managing distributed node function execution  
> **Audience:** System architects, node developers, infrastructure engineers  
> **Series:** Node Architecture  

---

## Overview

This document outlines the ONEX-native session and streaming layer, built on JetStream and optionally bridged via WebSocket or gRPC. This layer provides the asynchronous communication backbone for orchestrating and managing the execution of node functions and composed workflows, particularly for long-running, stateful, or interactive tasks.

The architecture emerged from the realization that simple REST or SSE patterns are insufficient for complex distributed function execution—we need structured, trust-aware sessions with persistent, multiplexed streams to manage the lifecycle and communication of distributed function executions.

---

## Goals

The session and streaming architecture aims to provide a robust environment for executing node functions beyond simple, synchronous calls:

* **Enable Multi-Node Session State**: Manage the overall context and shared state for a series of related node function calls within a single logical session
* **Support Durable, Resumable, and Trusted Execution**: Ensure that node function executions can persist, be resumed after interruption, and are performed within a trusted context
* **Abstract Transport Complexity**: Provide a consistent interface for managing streams of function call events and data outputs, abstracting over underlying messaging technologies
* **Allow Nodes to Stream & Receive Updates**: Enable node functions to stream partial outputs, receive updates during execution, or operate as long-lived workflow participants

---

## Session Lifecycle

A session encapsulates the context and state of a specific instance of a workflow or long-running function execution. Session lifecycle messages manage the state transitions of this execution instance.

### Session Start

Initiates a new execution instance:

```yaml
# Example message on a session control channel
type: session.start
session_id: sess-abc123         # Unique ID for this execution instance
origin: agent.bundle-builder    # The entity initiating the execution
workflow_uri: workflow://my.process@1.0.0 # The workflow function to execute
initial_input_state:            # The initial input state (arguments) for the workflow function
  data: "example input"
  options:
    timeout: 300
    retry_count: 3
capabilities:                   # Capabilities or constraints for this session/execution instance
  streaming: true               # Whether streaming is expected
  trust_level: provisional      # Trust context for the execution
  mode: sandbox                 # Execution mode (e.g., sandbox, production)
  max_duration: 3600           # Maximum session duration in seconds
```

### Session Acknowledgment / Rejection

Confirmation or denial of the session initiation request:

```yaml
# Example acknowledgement message
type: session.ack
session_id: sess-abc123         # Acknowledging this execution instance
resolved_workflow_contract:     # The state contract of the workflow function
  input_schema: "schema://workflow_input.json"
  output_schema: "schema://workflow_output.json"
trust_level: verified           # Verified trust level for the execution
estimated_duration: 1800        # Estimated execution time in seconds
allocated_resources:            # Resources allocated for this session
  cpu_cores: 2
  memory_mb: 4096
```

```yaml
# Example rejection message
type: session.reject
session_id: sess-abc123
reason: contract_violation      # Reason for rejecting the execution request
details:
  error_code: "INVALID_INPUT_SCHEMA"
  message: "Input state does not conform to required schema"
  validation_errors:
    - field: "data"
      error: "Required field missing"
```

### Session End

Marks the completion or termination of an execution instance:

```yaml
# Example end message
type: session.end
session_id: sess-abc123
reason: completed               # Reason for termination (completed, timeout, failed, cancelled)
duration_ms: 302000             # Total duration of the execution instance
final_output_state:             # The final output state (return value) of the workflow function
  result: "processing complete"
  metadata:
    nodes_executed: 15
    total_cost: 0.45
status: success                 # Final status (success, failure, timeout, cancelled)
execution_summary:              # Summary of execution
  nodes_called: 15
  cache_hits: 8
  errors_encountered: 0
  trust_score_final: 0.95
```

---

## Streaming Channels

Streaming channels are the communication buses used to pass messages about function calls and state/result streams between nodes and orchestrators during a session.

### JetStream Subjects

Canonical subjects follow a structured format:

* `onex.session.{session_id}.events`: For session lifecycle messages and overall workflow events
* `onex.node.{node_uri_hash}.input`: For sending input state updates or actions to a specific instance of a long-running or stateful node function within a session
* `onex.node.{node_uri_hash}.result`: For receiving final or partial output state or status updates from a specific instance of a node function within a session
* `onex.session.{session_id}.heartbeat`: For session health monitoring and keepalive messages

### Transport Bridges

Provide bridges for clients or services not using JetStream natively:

* **gRPC Stream**: Protocol buffer-based, supports contracted and signed messages
* **WebSocket Stream**: Used for CLI and browser clients
* **HTTP/SSE**: Server-sent events for simple streaming scenarios

### Subject Naming Convention

```
onex.{domain}.{identifier}.{message_type}

Examples:
- onex.session.sess-abc123.events
- onex.node.tool-validator-v1-hash.input
- onex.node.tool-validator-v1-hash.result
- onex.session.sess-abc123.heartbeat
- onex.workflow.wf-xyz789.status
```

---

## Streaming Message Types

Specific message types define the semantics of communication on streaming channels, primarily signaling events related to node function calls.

### Node Dispatch Message

```yaml
# Example Dispatch Message
type: signal.node.dispatch
session_id: sess-abc123         # The execution instance this call belongs to
node_uri: tool://scaffold.validator@1.0.0 # The node function being called
input_state:                    # The input state (arguments) for this function call
  file_path: "src/example.py"
  validation_rules: ["syntax", "style"]
call_id: call-xyz789            # Unique ID for this specific function call instance
timestamp: "2025-05-27T10:00:00Z"
parent_call_id: call-parent123  # Optional: if part of a composite
execution_context:              # Context for this specific call
  trust_level: 0.9
  timeout_seconds: 60
  retry_policy:
    max_attempts: 3
    backoff_strategy: "exponential"
```

### Node Result Message

```yaml
# Example Result Message
type: signal.node.result
session_id: sess-abc123
node_uri: tool://scaffold.validator@1.0.0
call_id: call-xyz789            # Matches the dispatch call_id
output_state:                   # The output state (return value) from the function call
  validation_passed: true
  issues_found: []
  metadata:
    execution_time_ms: 1250
    lines_validated: 150
status: success                 # Status of the function call (success, failure, timeout)
trace:                          # Execution trace data
  start_time: "2025-05-27T10:00:00Z"
  end_time: "2025-05-27T10:00:01.250Z"
  cost_estimate: 0.001
  trust_score: 0.95
timestamp: "2025-05-27T10:00:01.250Z"
error_details: null             # Optional: error information if status is failure
reducer_state_update:           # Optional: state update for reducer-based nodes
  validation_count: 1
  last_validation: "2025-05-27T10:00:01.250Z"
signals_emitted:                # Optional: signals emitted during execution
  - type: "validation_complete"
    payload: {"file": "src/example.py"}
```

### Progress Message

```yaml
# Example Progress Message (for long-running nodes)
type: signal.node.progress
session_id: sess-abc123
node_uri: tool://data.processor@1.0.0
call_id: call-xyz789
progress:
  percentage: 45
  current_step: "processing_chunk_3"
  total_steps: 10
  estimated_remaining_ms: 30000
partial_output:                 # Optional: partial results
  processed_records: 4500
  errors_encountered: 2
timestamp: "2025-05-27T10:00:30Z"
```

### Heartbeat Message

```yaml
# Example Heartbeat Message
type: signal.stream.heartbeat
session_id: sess-abc123
timestamp: "2025-05-27T10:00:00Z"
status: active                  # active, idle, paused, terminating
resource_usage:                 # Optional: current resource usage
  cpu_percent: 25
  memory_mb: 1024
  active_nodes: 3
health_check:                   # Optional: health indicators
  all_systems_operational: true
  last_error: null
```

### Action Message

```yaml
# Example Action Message (for sending actions to stateful nodes)
type: action.node.dispatch
session_id: sess-abc123
node_uri: agent://conversation.manager@1.0.0
call_id: call-xyz789
action:
  type: "user_message"
  payload:
    message: "Please analyze the uploaded document"
    attachments: ["doc-123.pdf"]
timestamp: "2025-05-27T10:00:00Z"
```

---

## Session Metadata and TTL

Session-level metadata governs the behavior of the execution instance itself.

### Session Configuration

```yaml
# Embedded in session.start message or managed externally
session_metadata:
  ttl: 3600                     # Time-to-live in seconds before the session times out
  trust_scope: ephemeral        # Trust context scope (ephemeral, persistent, shared)
  replayable: true              # Whether the execution trace can be replayed
  cold_context_id: ctx-xyz      # Link to where session outputs are cached persistently
  execution_mode: production    # Execution mode (sandbox, staging, production)
  resource_limits:              # Resource constraints for the session
    max_cpu_cores: 4
    max_memory_mb: 8192
    max_duration_seconds: 7200
    max_cost_dollars: 10.0
  persistence_policy:           # How session data should be persisted
    save_intermediate_results: true
    compress_logs: true
    retention_days: 30
  notification_settings:        # How to notify about session events
    on_completion: ["email", "webhook"]
    on_error: ["slack", "pagerduty"]
    webhook_url: "https://api.example.com/webhooks/onex"
```

### Session State Management

* Sessions can timeout, self-destruct upon completion/failure, or archive their outputs persistently
* Session outputs (including intermediate node function results) can be cached in cold storage, linked via `cold_context_id`
* Composite nodes using `memoization_tier: deep` benefit from persistent subgraph execution caching during the session
* When a session invokes a composite node with deep memoization, each child node's execution result may be cached independently using `trace_hash` keys
* These cached results can be reused not only across retries within the session but also in future sessions that share equivalent subgraph structure

---

## Fault Tolerance

The streaming architecture supports fault tolerance for individual function calls and the overall workflow execution.

### Message Delivery Guarantees

* All messages can be marked with a `delivery_window` or require explicit acknowledgment
* Messages not acknowledged in time can trigger various recovery strategies:
  * **Replay**: Re-sending the function call request
  * **Escalation**: Trigger a fallback function call path
  * **Retry**: Trigger a node rerun (a new instance of the failing function call)
  * **Resume**: Resume reducer-based nodes from their last cached snapshot if `reducer_snapshot` is enabled

### Durability and Recovery

```yaml
# Example message with delivery guarantees
type: signal.node.dispatch
session_id: sess-abc123
node_uri: tool://critical.processor@1.0.0
call_id: call-xyz789
delivery_options:
  require_ack: true
  timeout_seconds: 30
  max_retries: 3
  retry_backoff: "exponential"
  fallback_node: "tool://simple.processor@1.0.0"
persistence:
  durable: true                 # Store in durable stream
  replicas: 3                   # Number of replicas
  retention_policy: "work_queue" # Message retention policy
```

### Circuit Breaker Pattern

```yaml
# Circuit breaker configuration for fault tolerance
circuit_breaker:
  failure_threshold: 5          # Number of failures before opening circuit
  timeout_seconds: 60           # How long to keep circuit open
  half_open_max_calls: 3        # Max calls to test if circuit should close
  success_threshold: 2          # Successes needed to close circuit
```

---

## Use Cases

The session and streaming layer enables complex execution patterns for node functions:

### Live Streaming Execution

Stream partial or final outputs from long-running node functions (like LLM generation nodes or agents) as they are produced:

```python
# Example: Streaming LLM generation
async def stream_llm_generation(session_id: str, prompt: str):
    """Stream LLM generation results in real-time."""
    
    # Start the generation node
    dispatch_message = {
        "type": "signal.node.dispatch",
        "session_id": session_id,
        "node_uri": "llm://text.generator@1.0.0",
        "call_id": f"call-{uuid.uuid4()}",
        "input_state": {"prompt": prompt, "stream": True}
    }
    
    await jetstream.publish("onex.node.llm-generator.input", dispatch_message)
    
    # Listen for streaming results
    async for message in jetstream.subscribe(f"onex.node.llm-generator.result"):
        if message["type"] == "signal.node.progress":
            # Partial result
            yield message["partial_output"]["text_chunk"]
        elif message["type"] == "signal.node.result":
            # Final result
            yield message["output_state"]["final_text"]
            break
```

### Long-Lived Interactive Sessions

Manage sessions involving repeated interaction and state updates with stateful node functions:

```python
# Example: Interactive agent conversation
class ConversationSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.agent_call_id = None
    
    async def start_agent(self):
        """Start a long-lived agent node."""
        self.agent_call_id = f"call-{uuid.uuid4()}"
        
        dispatch_message = {
            "type": "signal.node.dispatch",
            "session_id": self.session_id,
            "node_uri": "agent://conversation.manager@1.0.0",
            "call_id": self.agent_call_id,
            "input_state": {"mode": "interactive"}
        }
        
        await jetstream.publish("onex.node.agent-conversation.input", dispatch_message)
    
    async def send_user_message(self, message: str):
        """Send a message to the running agent."""
        action_message = {
            "type": "action.node.dispatch",
            "session_id": self.session_id,
            "call_id": self.agent_call_id,
            "action": {
                "type": "user_message",
                "payload": {"message": message}
            }
        }
        
        await jetstream.publish("onex.node.agent-conversation.input", action_message)
    
    async def listen_for_responses(self):
        """Listen for agent responses."""
        async for message in jetstream.subscribe(f"onex.node.agent-conversation.result"):
            if message["call_id"] == self.agent_call_id:
                if message["type"] == "signal.node.progress":
                    # Agent is thinking/processing
                    yield {"type": "thinking", "status": message["progress"]}
                elif message["type"] == "signal.node.result":
                    # Agent response
                    yield {"type": "response", "message": message["output_state"]["response"]}
```

### Remote or Multi-Tenant Client Support

Provides a robust, multiplexed channel for multiple clients or remote services to interact with ONEX workflows:

```python
# Example: Multi-tenant session management
class SessionManager:
    def __init__(self):
        self.active_sessions = {}
    
    async def create_session(self, tenant_id: str, workflow_uri: str) -> str:
        """Create a new session for a tenant."""
        session_id = f"sess-{tenant_id}-{uuid.uuid4()}"
        
        session_start = {
            "type": "session.start",
            "session_id": session_id,
            "origin": f"tenant.{tenant_id}",
            "workflow_uri": workflow_uri,
            "capabilities": {
                "streaming": True,
                "trust_level": "tenant_verified",
                "mode": "production"
            }
        }
        
        await jetstream.publish(f"onex.session.{session_id}.events", session_start)
        self.active_sessions[session_id] = {"tenant_id": tenant_id, "status": "starting"}
        
        return session_id
    
    async def route_message(self, session_id: str, message: dict):
        """Route a message to the appropriate session."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        # Add tenant context to message
        message["tenant_id"] = self.active_sessions[session_id]["tenant_id"]
        
        # Route based on message type
        if message["type"].startswith("signal.node"):
            await jetstream.publish(f"onex.node.{message['node_uri_hash']}.input", message)
        else:
            await jetstream.publish(f"onex.session.{session_id}.events", message)
```

### Hot-Swappable Stream-Based Workflows

Allows dynamically updating the graph of node functions being executed within a session based on streaming events or external signals:

```python
# Example: Dynamic workflow adaptation
class AdaptiveWorkflow:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_nodes = []
        self.workflow_state = "initial"
    
    async def adapt_workflow(self, trigger_event: dict):
        """Adapt the workflow based on streaming events."""
        
        if trigger_event["type"] == "signal.node.result":
            result = trigger_event["output_state"]
            
            # Decide next nodes based on result
            if result.get("confidence", 0) < 0.7:
                # Low confidence, add validation node
                await self.add_validation_node(result)
            elif result.get("complexity", "low") == "high":
                # High complexity, add specialized processing
                await self.add_specialized_processor(result)
            else:
                # Normal flow, continue with standard nodes
                await self.continue_standard_flow(result)
    
    async def add_validation_node(self, input_data: dict):
        """Dynamically add a validation node to the workflow."""
        validation_call_id = f"call-validation-{uuid.uuid4()}"
        
        dispatch_message = {
            "type": "signal.node.dispatch",
            "session_id": self.session_id,
            "node_uri": "validator://confidence.checker@1.0.0",
            "call_id": validation_call_id,
            "input_state": input_data
        }
        
        await jetstream.publish("onex.node.validator-confidence.input", dispatch_message)
        self.current_nodes.append(validation_call_id)
```

---

## Implementation Considerations

### Performance Optimization

* **Message Batching**: Batch multiple small messages to reduce overhead
* **Connection Pooling**: Reuse connections across multiple sessions
* **Compression**: Compress large message payloads
* **Partitioning**: Distribute sessions across multiple JetStream instances

### Security

* **Message Encryption**: Encrypt sensitive message payloads
* **Authentication**: Verify session and node identities
* **Authorization**: Enforce access controls on streaming channels
* **Audit Logging**: Log all session activities for compliance

### Monitoring and Observability

* **Metrics Collection**: Track session duration, message throughput, error rates
* **Distributed Tracing**: Correlate messages across the entire session lifecycle
* **Health Checks**: Monitor session and node health
* **Alerting**: Alert on session failures, timeouts, or resource exhaustion

---

## References

- [Node Architecture Index](./index.md) - Overview of node architecture series
- [State Reducers](./state_reducers.md) - State management and reducer patterns
- [Monadic Node Core](../architecture-node-monadic-core.md) - Core monadic principles and interfaces
- [Node Composition](../architecture-node-composition.md) - Composition patterns and execution models
- [Node Typology](./node_typology.md) - Node categorization and execution model
- [Protocol Definitions](./protocol_definitions.md) - Core protocol interfaces
- [Error Handling](../error_handling.md) - Error handling and retry patterns

---

**Note:** This document defines the canonical session and streaming architecture for ONEX. It provides the messaging infrastructure to manage the lifecycle, communication, and fault tolerance of distributed node function executions, forming the basis for agent multiplexing, dashboard integration, and hybrid local-cloud execution flows.
