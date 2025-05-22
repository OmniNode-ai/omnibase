<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: sessions_and_streaming.md
version: 1.0.0
uuid: 9b99bc68-bb93-4aa1-8337-788799e3d488
author: OmniNode Team
created_at: 2025-05-22T17:18:16.690029
last_modified_at: 2025-05-22T21:19:13.607029
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: ea7e97f51ae4c63d1d3eb3eee098fdb9bc26b69a5b20cdae1f3b24ba3cd51129
entrypoint: python@sessions_and_streaming.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.sessions_and_streaming
meta_type: tool
<!-- === /OmniNode:Metadata === -->


<file name=0 path=/Volumes/PRO-G40/Code/omnibase/docs/nodes/sessions_and_streaming.md># ONEX Node Architecture: Sessions and Streaming Architecture (for Function Execution)

> **Status:** Canonical  
> **Series:** Node Architecture  
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting documentation. 

## 04 – Sessions and Streaming Architecture

### Context & Origin

This document outlines the ONEX-native session and streaming layer, built on JetStream and optionally bridged via WebSocket or gRPC. This layer provides the asynchronous communication backbone for orchestrating and managing the execution of node "functions" and composed workflows, particularly for long-running, stateful, or interactive tasks. It emerged from the realization that:

> "We don't just need REST or SSE for simple request/response—we need structured, trust-aware sessions with persistent, multiplexed streams to manage the lifecycle and communication of **distributed function executions**."

---

### Goals

The session and streaming architecture aims to provide a robust environment for executing node functions beyond simple, synchronous calls:

* **Enable Multi-Node Session State:** Manage the overall context and shared state for a series of related **node function calls** within a single logical session.
* **Support Durable, Resumable, and Trusted Execution:** Ensure that **node function executions** can persist, be resumed after interruption, and are performed within a trusted context, with results recorded reliably.
* **Abstract Transport Complexity:** Provide a consistent interface for managing streams of **function call events** and data outputs, abstracting over underlying messaging technologies like JetStream, WebSocket, and gRPC.
* **Allow Nodes to Stream & Receive Updates:** Enable **node functions** (particularly long-running or stateful ones like agents or complex transformers) to stream partial outputs (`state_contract` updates), receive updates or "actions" (input state changes) during execution, or operate as long-lived workflow participants.

---

### Session Lifecycle

A session encapsulates the context and state of a specific **instance of a workflow or a long-running function execution**. Session lifecycle messages manage the state transitions of this execution instance.

#### ✅ Session Start

Initiates a new execution instance.

```yaml
# Example message on a session control channel
type: session.start
session_id: sess-abc123         # Unique ID for this execution instance
origin: agent.bundle-builder    # The entity initiating the execution
workflow_uri: workflow://my.process@1.0.0 # The workflow function to execute
initial_input_state: ...        # The initial input state (arguments) for the workflow function
caps: # Capabilities or constraints for this session/execution instance
  streaming: true             # Whether streaming is expected
  trust_level: provisional    # Trust context for the execution
  mode: sandbox               # Execution mode (e.g., sandbox, production)
```

#### ✅ Session Ack / Rejection

Confirmation or denial of the session initiation request.

```yaml
# Example acknowledgement message
type: session.ack
session_id: sess-abc123         # Acknowledging this execution instance
resolved_workflow_contract: ... # The state contract of the workflow function
trust_level: verified           # Verified trust level for the execution
```

```yaml
# Example rejection message
type: session.reject
session_id: sess-abc123
reason: contract_violation      # Reason for rejecting the execution request
details: ...
```

#### ✅ Session End

Marks the completion or termination of an execution instance.

```yaml
# Example end message
type: session.end
session_id: sess-abc123
reason: timeout                 # Reason for termination (e.g., timeout, completed, failed)
duration_ms: 302000             # Total duration of the execution instance
final_output_state: ...         # The final output state (return value) of the workflow function
status: success | failure       # Final status
```

---

### Streaming Channels

Streaming channels are the communication buses used to pass **messages about function calls** and **state/result streams** between nodes and orchestrators during a session. JetStream subjects provide the core pub/sub mechanism.

* **JetStream Subjects:** Canonical subjects follow a structured format:
    * `onex.session.{session_id}.events`: For session lifecycle messages and overall workflow events.
    * `onex.node.{node_uri_hash}.input`: For sending *input state updates* or *actions* to a specific instance of a long-running or stateful **node function** within a session.
    * `onex.node.{node_uri_hash}.result`: For receiving final or partial *output state* or *status updates* from a specific instance of a **node function** within a session.
* **Other Transports:** Provide bridges for clients or services not using JetStream natively:
    * gRPC stream (proto-based, supports contracted and signed messages)
    * WebSocket stream (used for CLI + browser clients)

---

### Streaming Message Types

Specific message types define the semantics of communication on streaming channels, primarily signaling events related to **node function calls**.

```yaml
# Example Dispatch Message
type: signal.node.dispatch
session_id: sess-abc123         # The execution instance this call belongs to
node_uri: tool://scaffold.validator@1.0.0 # The node function being called
input_state: ...                # The input state (arguments) for this function call
call_id: call-xyz789            # Unique ID for this specific function call instance
timestamp: ...
# Optional: parent_call_id (if part of a composite)
```

```yaml
# Example Result Message
type: signal.node.result
session_id: sess-abc123
node_uri: tool://scaffold.validator@1.0.0
call_id: call-xyz789            # Matches the dispatch call_id
output_state: ...               # The output state (return value) from the function call
status: success | failure       # Status of the function call
trace: ...                      # Execution trace data (latency, cost, etc.)
timestamp: ...
# Optional: error_details, reducer_state_update, signals_emitted
```

```yaml
# Example Heartbeat Message
type: signal.stream.heartbeat
session_id: sess-abc123
timestamp: ...
status: active # or idle, paused
# Indicates the session/stream is still active
```
Other messages could include `signal.session.state_update`, `signal.node.progress`, `action.node.dispatch` (for sending actions to stateful nodes), etc.

---

### Session Metadata + TTL

Session-level metadata governs the behavior of the execution instance itself.

```yaml
# Embedded in session.start message or managed externally
session_metadata:
  ttl: 300                      # Time-to-live in seconds before the session times out
  trust_scope: ephemeral        # Trust context scope for this session (e.g., ephemeral, persistent)
  replayable: true              # Whether the execution trace can be replayed
  cold_context_id: ctx-xyz      # Link to where session outputs are cached persistently
```

* Sessions can timeout, self-destruct upon completion/failure, or archive their outputs persistently.
* Session outputs (including intermediate node function results) can be cached in cold storage, linked via `cold_context_id`.

Composite nodes using `memoization_tier: deep` benefit from persistent subgraph execution caching during the session. When a session invokes a composite node with this setting, each child node's execution result may be cached independently using `trace_hash` keys. These cached results can be reused not only across retries within the session but also in future sessions that share equivalent subgraph structure.

---

### Fault Tolerance

The streaming architecture supports fault tolerance for **individual function calls** and the overall workflow execution.

* All messages can be marked with a `delivery_window` or require explicit acknowledgment.
* Messages not acknowledged in time can:
    * Be replayed (re-sending the function call request).
    * Escalate to trigger a fallback function call path.
    * Trigger a node rerun (a new instance of the failing function call).
    * Resume reducer-based nodes from their last cached snapshot if `reducer_snapshot` is enabled, rather than replaying the entire reducer action history.
* Durable streams (like JetStream) ensure messages are not lost even if services go down.

---

### Use Cases

The session and streaming layer enables complex execution patterns for node functions:

* **Live Streaming Execution:** Stream partial or final outputs from long-running node functions (like LLM generation nodes or agents) as they are produced.
* **Long-Lived Interactive Sessions:** Manage sessions involving repeated interaction and state updates with stateful node functions (e.g., agent conversations driven by reducer state).
* **Remote or Multi-Tenant Client Support:** Provides a robust, multiplexed channel for multiple clients or remote services to interact with ONEX workflows.
* **Hot-Swappable Stream-Based Workflows:** Allows dynamically updating the graph of node functions being executed within a session based on streaming events or external signals.

---

**Status:** Canonical foundation for ONEX-native session and stream layer. It provides the messaging infrastructure to manage the lifecycle, communication, and fault tolerance of distributed **node function executions**. Forms the basis for agent multiplexing, dashboard integration, and hybrid local-cloud execution flows.
