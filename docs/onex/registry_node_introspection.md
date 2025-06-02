# ONEX Registry Node: Introspection and Query Model

**Context:**
This document defines the complete introspection and query schema for the ONEX Registry Node. It is designed to support real-time inspection, routing, trust evaluation, and dynamic bus/subscriber coordination.

---

## 🎯 Goal
Enable agents, dashboards, and CLI tools to dynamically query:
- Node metadata and schema
- Execution history
- Port and subscriber information
- Trust scores and validation state
- Bus and message routing configuration

---

## 🔍 Introspection Query Categories

### 1. Node Metadata
- node_id
- version_hash
- node_type: tool | validator | test | adapter | agent
- description
- tags
- schema: input/output types, validation rules
- trust_score
- execution_count
- success/failure rate
- last_execution_timestamp

### 2. Execution Introspection
- last_inputs
- last_outputs
- execution_trace_log_id
- execution_duration_ms
- timestamp_created
- timestamp_updated
- state_snapshot_pointer
- Optional links:
    - execution_log_url
    - state_diff_url

### 3. Port & Bus Information
```yaml
inbound_ports:
  - name: registry_subscribe
    port: 12345
    protocol: JetStream | Redis | gRPC
    dynamic: true
    endpoint_uri: optional
    active: true
    subscriber_count: 5

outbound_ports:
  - name: registry_updates
    topic: onex.registry.updates
    protocol: JetStream
    subscribers:
      - node_id: node.processor.003
      - dynamic_client: session-7cf4a
    messages_per_sec: 25.3
    health_check_passed: true
```

### 4. Schema Introspection
```yaml
inputs:
  - name: input_text
    type: string
    required: true

outputs:
  - name: result
    type: object
    fields:
      - success: boolean
      - data: string

accepts_context: true
modifies_state: false
side_effects:
  - write_log
  - update_registry
```

### 5. Dynamic Capabilities
- supports_hot_reload: true
- available_models:
    - mixtral
    - deepseek
    - gpt-4
- versioned_templates:
    - template_id: validation_basic
      hash: 0xabcdef...
- override_flags:
    - log_level
    - dry_run
    - fallback_mode

### 6. Trust & Validation Status
- trust_score: 0.87
- validated: true
- validator_ids:
    - val_node_1
    - val_node_5
- failure_modes: []
- registry_lifecycle: canary | validated | frozen

---

## 🧠 Optional Enhancements

### Live Subscription API
Expose event streams for:
- node_changes
- execution_results
- bus_events
- port_state_changes

### Agent Relationships
```yaml
subscribed_by_agents:
  - agent.orbit.scheduler
owned_by_agent: agent.orbit.introspector
```

### Dependency Graph
```yaml
upstream_nodes:
  - validator.schema.checker

downstream_nodes:
  - validator.execution.monitor
```

---

## 🧪 CLI Introspection Example

```bash
onex describe --node validator.test.canary.001 --format yaml
```

Sample Output:
```yaml
node_id: validator.test.canary.001
version_hash: 0xf93d8a2...
node_type: validator
trust_score: 0.93
success_rate: 98.1%
inbound_ports:
  - name: registry_subscribe
    port: 48912
    protocol: JetStream
    dynamic: true
    active: true
    subscriber_count: 12
...
```

---

## ✅ Next Steps
- Define GraphQL schema (dynamic introspection query adapter)
- Scaffold CLI handler for onex describe
- Register port metadata in Registry Node runtime
- Add structured log traceback to execution_trace_log_id
- Integrate bus metrics from JetStream/Redis

---

## 📅 Milestone Table: What to Implement Now vs. Later

| Feature/Field                | Milestone 1 (Now) | Future (M2+) |
|------------------------------|:----------------:|:------------:|
| Node Metadata                |        ✅        |              |
| Port & Bus Info              |        ✅        |              |
| Schema Introspection         |        ✅        |              |
| Trust/Validation Status      |        ✅        |              |
| CLI Introspection Handler    |        ✅        |              |
| Port Metadata Registration   |        ✅        |              |
| Execution Introspection      |                  |      ✅      |
| Dynamic Capabilities         |                  |      ✅      |
| Live Subscription API        |                  |      ✅      |
| Agent Relationships/Graph    |                  |      ✅      |
| GraphQL Schema               |                  |      ✅      |
| Structured Log Traceback     |                  |      ✅      |
| Bus Metrics Integration      |                  |      ✅      | 

---

## 🔗 See Also: Tool Discovery and Proxy Invocation

The ONEX Registry Node now provides comprehensive, registry-driven tool discovery and proxy invocation APIs. All tool discovery, invocation, and contract metadata are accessible via the registry node's introspection and proxy APIs:

- **Tool Discovery:** The registry node exposes a canonical list of all registered tools, their contracts, and the nodes that provide them. This enables dynamic CLI, agent, and dashboard workflows to enumerate, filter, and select tools at runtime.
- **Proxy Invocation:** Clients can invoke any registered tool by name via the registry node, which routes the request to the appropriate node(s) and returns the result. This is documented in detail in the [Proxy Tool Invocation API](./registry_node_proxy_invocation.md).
- **Contract Metadata:** Tool contracts, argument schemas, and versioning information are available via the introspection and proxy APIs, supporting validation, codegen, and dynamic UI generation.

For full details, see:
- [Proxy Tool Invocation API](./registry_node_proxy_invocation.md)
- [Registry Architecture](../registry_architecture.md)
- [Plugin Discovery](../plugins/plugin_discovery.md)

**Status:** All tool discovery and invocation is now registry-driven and protocol-pure. Future enhancements will expand dynamic capabilities, trust evaluation, and batch/streaming invocation. 