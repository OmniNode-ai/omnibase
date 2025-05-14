## 04 – Sessions and Streaming Architecture

### Context & Origin

This document outlines the OmniNode-native session and streaming layer, built on JetStream and optionally bridged via WebSocket or gRPC. It emerged from the realization that:

> "We don’t just need REST or SSE—we need structured, trust-aware sessions with persistent, multiplexed streams."

---

### Goals

* Enable multi-node session state
* Support durable, resumable, and trusted execution
* Abstract over JetStream, WebSocket, and gRPC
* Allow nodes to stream outputs, receive updates, or operate long-lived workflows

---

### Session Lifecycle

#### ✅ Session Start

```yaml
type: session.start
session_id: sess-abc123
origin: agent.bundle-builder
caps:
  streaming: true
  trust_level: provisional
  mode: sandbox
```

#### ✅ Session Ack / Rejection

```yaml
type: session.ack
session_id: sess-abc123
node_contract: base_node_contract_v1
trust_level: verified
```

```yaml
type: session.reject
reason: contract_violation
```

#### ✅ Session End

```yaml
type: session.end
session_id: sess-abc123
reason: timeout
duration: 302
```

---

### Streaming Channels

* JetStream subjects follow:

  * `onex.session.{session_id}.events`
  * `onex.node.{node_id}.input`
  * `onex.node.{node_id}.result`
* Other transports:

  * gRPC stream (proto-based, supports contract signatures)
  * WebSocket stream (used for CLI + browser clients)

---

### Streaming Message Types

```yaml
type: signal.node.dispatch
node: scaffold.validator
session_id: sess-abc123
input: ...
```

```yaml
type: signal.node.result
node: scaffold.validator
session_id: sess-abc123
output: ...
trace: ...
```

```yaml
type: signal.stream.heartbeat
```

---

### Session Metadata + TTL

```yaml
session_metadata:
  ttl: 300
  trust_scope: ephemeral
  replayable: true
  cold_context_id: ctx-xyz
```

* Sessions can timeout, self-destruct, or archive
* Session outputs can be cached in cold storage

---

### Fault Tolerance

* All messages can be marked with a `delivery_window`
* Messages not acknowledged in time can:

  * Be replayed
  * Escalate fallback path
  * Trigger node rerun

---

### Use Cases

* Live streaming node execution (LLMs, agents, tools)
* Long-lived patch sessions
* Remote or multi-tenant client support
* Hot-swappable stream-based workflows

---

**Status:** Canonical foundation for ONEX-native session and stream layer. Forms the basis for agent multiplexing, dashboard integration, and hybrid local-cloud execution flows.
