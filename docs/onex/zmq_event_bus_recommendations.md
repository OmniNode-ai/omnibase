# ZMQ Event Bus: Design Recommendations and Roadmap

**Status:** Living design/roadmap document for ONEX event bus evolution
**Last Updated:** {{today}}

---

## Overview

The current ZMQ-based event bus in ONEX enables message-passing between nodes, supporting basic publish-subscribe and routing. However, several critical features are missing for production robustness, observability, and scale. This document captures the underspecified or missing components and provides detailed recommendations for improvement.

---

## 1. Port Management and Allocation
**Missing:**
- Lease lifecycle for dynamic port allocation
- Reaping of stale or orphaned port leases
- Handling of port conflicts and collision resolution

**Recommendations:**
- Define TTL (time-to-live) for port allocations
- Add reaper process or heartbeat mechanism to deregister stale leases
- Use atomic registry allocation with retry/backoff and conflict detection
- Allow range-based port allocation policies (e.g., per node type or purpose)
- Track `port_allocation_ts` and `last_heartbeat_ts` per lease to support expiry and diagnostics (Milestone 2).
- Include `allocated_by` metadata to trace node/requestor identity (Milestone 1).

---

## 2. Security and Access Control
**Missing:**
- No authentication, ACLs, or trust-based filtering for publishers/subscribers

**Recommendations:**
- Implement node identity signing and validation on publish/subscribe requests
- Allow per-bus access control lists (ACLs) or policies in the registry
- Add support for trusted_only subscriptions or bus-level flags
- Optionally support mutual TLS or key-based socket-level auth
- Add `trusted_only` flag per topic or subscriber in the registry schema (Milestone 2).
- Stub for signing ZMQ messages using shared secret or public key infrastructure (PKI) (Milestone 3+).

---

## 3. Observability and Debugging
**Missing:**
- No structured logs or metrics for publish, receive, drop, retry, or disconnect events
- No built-in tracing or event visualization

**Recommendations:**
- Emit structured EVENT_PUBLISHED, EVENT_RECEIVED, EVENT_DROPPED logs
- Include correlation IDs in all events
- Add Prometheus metrics: event count, size, latency, subscriber count, retry rate
- Add debug mode with full event payload dump (per-topic configurable)
- Add CLI command `onex event-monitor` to stream and inspect event logs in real-time (Milestone 2).
- Emit `EVENT_INVALID_SCHEMA` if incoming event fails validation (Milestone 1).
- Emit `EVENT_RETRY` and `EVENT_RETRY_LIMIT_EXCEEDED` for retried messages (Milestone 2+).

---

## 4. Backpressure and Queue Overflow
**Missing:**
- No flow control or handling of slow consumers

**Recommendations:**
- Add bounded queues per subscriber; log and/or drop on overflow
- Emit EVENT_BACKPRESSURE and EVENT_SUBSCRIBER_SLOW telemetry
- Optionally support durable buffering with disk-backed queues (future)

---

## 5. Fault Tolerance and Recovery
**Missing:**
- No handling of node reconnect, event replay, or missed messages

**Recommendations:**
- Add node registration TTL and automatic cleanup
- Include last-seen timestamp per node
- Support event replay buffer or limited history cache for critical topics
- Allow durable subscriber registration with cursor support (future)
- When reconnecting, emit `NODE_REJOINED` event and resubscribe to previous topics (Milestone 2).
- Maintain ephemeral vs. durable subscriber distinction and teardown policy.

---

## 6. Subscription Semantics
**Missing:**
- No formal subscription filtering beyond topic name

**Recommendations:**
- Support structured subscription filters (e.g., wildcard topic segments, metadata tags)
- Implement a policy engine for filtering messages per subscriber (e.g., topic + event_type + trust)
- Stub for topic affinity hints (e.g., node prefers telemetry only), allowing routing optimization later.

---

## 7. Developer Tooling and Simulation
**Missing:**
- No official CLI or simulation harness

**Recommendations:**
- Add CLI to inspect active buses, topics, ports; publish test messages; watch and decode incoming events
- Add local simulation harness that validates end-to-end routing logic and filters

---

## 8. Message Schema Enforcement
**Missing:**
- No formal schema validation for messages

**Recommendations:**
- All messages should conform to an OnexEvent schema or contract
- Runtime validation should emit structured errors on mismatch
- Add strict vs. permissive schema validation mode per bus or topic (Milestone 1).
- Validation errors should include topic, offending payload, and expected schema hash.

---

## 9. Multiplexing and Bus Segregation
**Missing:**
- All event types flow through the same bus by default

**Recommendations:**
- Support bus-level segregation (telemetry, control, user events, test buses)
- Each bus should be independently configurable (port, policy, logging)
- Registry should track which node is connected to which bus by name and topic scope.

## Registry Integration Enhancements

**Missing:**
- No unified index of active nodes, their ports, and subscriptions
- No typed metadata associated with bus registration

**Recommendations:**
- Maintain central registry map: `{ node_id → { buses: [...], topics: [...], port, trust, last_seen } }`
- Expose queryable introspection API for debugging and monitoring
- Support typed metadata block per bus (e.g., purpose, qos, debug flag)

**Milestone Scoping:**
- Milestone 1: Track node_id, port, topics, and timestamps in registry
- Milestone 2: Add trust and metadata indexing
- Milestone 3: Add full introspection API and GraphQL endpoint

---

## 10. Lifecycle and Teardown
**Missing:**
- No structured lifecycle hooks for bus startup/shutdown

**Recommendations:**
- Emit BUS_STARTED, BUS_STOPPED events with diagnostics
- Cleanly unregister all subscribers and flush queues on shutdown
- Fail fast if bus configuration is invalid or conflicting

---

## Leveraging Open Source Port Management: portpicker

To avoid re-implementing dynamic port allocation and management, ONEX will leverage the open source [portpicker](https://github.com/google/python_portpicker) library (also available on [PyPI](https://pypi.org/project/portpicker/)).

**portpicker** provides:
- Dynamic, race-free port allocation via a simple Python API (`pick_unused_port()`)
- An optional port server daemon for multi-process safety (prevents port collisions across processes)
- Production-grade reliability, used in large-scale test automation and distributed systems
- No changes required to ZMQ event bus logic; portpicker simply provides available ports for ZMQ sockets

**Recommendation:**
- Integrate portpicker into the registry node's port allocation logic
- Use the port server for robust, multi-process port management (set `PORTSERVER_ADDRESS` in the environment)
- Continue to use ZMQ for event transport; portpicker only manages port selection and lease

---

## Milestone Scoping (Updated)

**Milestone 1 (Immediate):**
- Integrate portpicker for all dynamic port allocation in registry node and event bus setup
- Document portpicker usage and configuration in developer docs
- Remove any custom port allocation logic in favor of portpicker

**Milestone 2:**
- ACLs and trusted subscriber filtering
- Replay buffer and node reconnect handling
- CLI tooling
- Filtered subscriptions

**Milestone 3+:**
- Durable subscribers
- Policy engine for filtering
- Multiplexed bus segregation
- Backing store for event persistence

---

## Summary and Next Steps (Updated)

- Adopt portpicker as the canonical solution for dynamic port management in ONEX
- Integrate into registry node and event bus setup
- Document usage and configuration for all developers
- Focus engineering effort on ONEX-specific registry, lease, and introspection logic, not low-level port management
- Expand registry to track per-node metadata and subscription map (Milestone 1).
- Add debug CLI to inspect buses, topics, and node status (stub for Milestone 2).

**Next Steps:**
- Review and ratify these recommendations as the canonical roadmap
- Integrate into ONEX event bus and registry design docs
- Begin implementation per milestone scoping
- Track progress and revisit priorities as the system evolves 

---

## Implementation Considerations and Open Questions

This section captures important design and implementation details that require further specification or are deferred to future milestones. It serves as a living checklist for maintainers and contributors.

### 1. ZMQ Socket Types/Patterns
- **Overview:** ZMQ supports multiple socket patterns: PUB/SUB (broadcast), REQ/REP (request/response), DEALER/ROUTER (async routing), PUSH/PULL (work queues).
- **ONEX Mapping Table:**
    | Event Type                  | ZMQ Pattern      | Notes                                  |
    |-----------------------------|------------------|----------------------------------------|
    | Telemetry, logs, announce   | PUB/SUB          | Broadcast to all subscribers           |
    | Tool proxy invocation       | REQ/REP or DEALER/ROUTER | For TOOL_PROXY_INVOKE/RESULT, request/response semantics |
    | Work/task distribution      | PUSH/PULL        | (Future) For distributed task queues   |
- **TODO:** Document actual socket usage per event type in implementation. Review and update as patterns evolve. (Milestone 2+)

### 2. Backpressure Strategy Details
- **Queue Size:** Define default per-subscriber queue size (e.g., 1000 messages, configurable).
- **Drop Policy:** Specify whether to drop oldest or newest messages on overflow (default: drop oldest). Make this configurable per topic/subscriber.
- **Publisher Behavior:** On EVENT_BACKPRESSURE, publisher may log, block, retry, or drop (configurable). Document default and alternatives.
- **Structured Events:** Emit EVENT_BACKPRESSURE and EVENT_DROPPED for observability.
- **TODO:** Decide and document concrete values and policies in registry/config. (Milestone 2)

### 3. Event Replay Buffer/History Cache
- **Critical Topics:** Define which topics require replay (e.g., control, audit).
- **Cache Parameters:** Recommend default size (e.g., last 1000 events), duration (e.g., 10 minutes), and storage (in-memory by default, disk-backed future).
- **Replay API:** Specify how subscribers request replay (e.g., by count or timestamp).
- **Trade-offs:** Note memory/disk usage vs. replay capability; document eviction policy (oldest-first).
- **Structured Events:** Emit EVENT_REPLAY_REQUESTED, EVENT_REPLAY_DELIVERED, EVENT_REPLAY_FAILED.
- **TODO:** Finalize replay API and cache policy in implementation. (Milestone 2+) 