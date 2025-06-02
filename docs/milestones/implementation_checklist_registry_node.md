# Implementation Checklist: Registry Node – Dynamic Event Bus Port Allocation and Tool Introspection

**Context:**
This checklist tracks the immediate, actionable tasks for implementing registry-driven event bus port allocation and tool discovery as part of Milestone 1. For high-level status and DoD, see [milestone_1_checklist.md](./milestone_1_checklist.md).

**See also:** [docs/onex/registry_node_introspection.md](../onex/registry_node_introspection.md) for the full introspection/query schema and milestone table.

---

## Immediate Tasks (Milestone 1)

### Port Allocation
- [x] Design protocol for requesting and releasing event bus ports from the registry node
  - [x] Define port lease lifecycle, including TTLs and lease renewal policy
  - [x] Validate port availability before lease grant; retry with backoff on conflict
- [x] Implement registry node logic for port allocation, tracking, and introspection
  - [x] Emit structured log and telemetry events for port allocations/releases
- [x] Update node and test harnesses to request ports from the registry instead of picking ad hoc
- [x] Update all nodes to register their tools and contracts with the registry node at startup

### Introspection & Tool Discovery (see design doc for schema)
- [x] Implement node metadata introspection API (Milestone 1)
- [x] Implement port & bus info introspection API (Milestone 1)
- [x] Implement trust/validation status API (Milestone 1)
- [~] Implement schema introspection API (Milestone 1)  # Partial: contract is loaded/validated, full endpoint deferred
- [x] Implement CLI handler for `onex describe` (Milestone 1)
- [x] Implement port metadata registration logic in registry node runtime (Milestone 1)
- [x] Expand registry node introspection to list all available event buses, ports, and exposed tools (with contracts)
- [ ] Implement registry APIs for tool discovery and (optionally) proxy invocation
---

## Additional Tasks from Design Documents

### Milestone 1 (Immediate)
- [ ] Implement ToolProxyInvocationRequest and ToolProxyInvocationResponse models using canonical enums.
- [ ] Implement proxy_invoke_tool method in the registry node (tool lookup, node selection, event emission, synchronous wait, error handling).
- [ ] Validate tool existence and argument contract (if available).
- [ ] Emit structured logs for all proxy request/response operations.
- [ ] Ensure correlation_id is propagated through all events.
- [ ] CLI: Add onex proxy-invoke command for tool invocation (with --dry-run and --verbose flags).
- [ ] Integrate portpicker for all dynamic port allocation in registry node and event bus setup.
- [ ] Document portpicker usage and configuration.
- [ ] Remove any custom port allocation logic in favor of portpicker.
- [ ] Track allocated_by metadata for each port lease.
- [ ] Registry: Track node_id, port, topics, and timestamps.
- [ ] Emit EVENT_INVALID_SCHEMA if incoming event fails validation.
- [ ] All messages must conform to OnexEvent schema; emit structured errors on mismatch.

### Milestone 2+ (Future/Stubbed)
- [ ] Implement trusted_only logic for proxy invocation (filter by node trust).
- [ ] Add support for tool versioning in proxy requests.
- [ ] Add ToolDescribeRequest API and CLI command (onex describe-tool).
- [ ] Support registration TTL and heartbeat for tool registrations.
- [ ] Purge expired/stale tool registrations and emit events.
- [ ] Add batch/streaming/async invocation support.
- [ ] Add test harness for proxy routing, timeouts, and failover.
- [ ] Add CLI support for batch and streaming invocations.
- [ ] Track port_allocation_ts and last_heartbeat_ts per lease (expiry/diagnostics).
- [ ] Add reaper/heartbeat for stale port leases.
- [ ] Add trusted_only flag per topic/subscriber in registry schema.
- [ ] Add CLI command onex event-monitor for real-time event log streaming.
- [ ] Emit EVENT_RETRY and EVENT_RETRY_LIMIT_EXCEEDED for retried messages.
- [ ] Emit NODE_REJOINED event and resubscribe on reconnect.
- [ ] Maintain ephemeral vs. durable subscriber distinction.
- [ ] Add structured subscription filters and policy engine.
- [ ] Add CLI to inspect buses, topics, ports, and node status.
- [ ] Add simulation harness for routing logic and filters.
- [ ] Add strict vs. permissive schema validation mode per bus/topic.
- [ ] Registry: Add trust and metadata indexing.
- [ ] Registry: Add full introspection API and GraphQL endpoint.
- [ ] Add BUS_STARTED, BUS_STOPPED events for lifecycle.
- [ ] Add debug CLI to inspect buses, topics, and node status.
- [ ] Document actual ZMQ socket usage per event type.
- [ ] Decide and document queue sizes, drop policy, and publisher behavior for backpressure.
- [ ] Finalize replay API and cache policy for event replay/history.

--- 

### Documentation and Testing
- [ ] Update developer docs and codegen tools to leverage registry-driven tool discovery
- [x] Add tests for port allocation, tool registration, and introspection
  - [x] Add collision detection strategy for duplicate tool contract IDs (document, not enforce)

---

## Future Milestone (Stubbed for M2+)
- [ ] Implement execution introspection API (see design doc)
- [ ] Implement dynamic capabilities API (see design doc)
- [ ] Implement live subscription API (see design doc)
- [ ] Implement agent relationships/dependency graph API (see design doc)
- [ ] Implement GraphQL schema for dynamic introspection (see design doc)
- [ ] Add structured log traceback to execution_trace_log_id (see design doc)
- [ ] Integrate bus metrics from JetStream/Redis (see design doc)
- [ ] Implement registry cleanup logic for orphaned ports
- [ ] Add metrics: current allocation count, available ports, failed requests
- [ ] Implement access controls for port allocation and tool registration
- [ ] Add audit log entries for all port and tool operations
- [ ] Define rebinding mechanism if node's port is no longer usable

---

## Design Notes & Open Questions
- PortRequestModel now enforces UUID for requester_id, per protocol standards.
- Protocol sketch for port request/release
- Tool contract registration format
- Introspection response schema
- Open questions and blockers
- PortManager fixture is now shared and lives in src/omnibase/fixtures/port_manager_fixtures.py, per standards.

---

**Assignees:** _(TBD)_
**Status:** _(Update as tasks are completed)_
**Notes:** _(Add implementation notes, PR links, etc.)_

**Progress Note:**
- Port allocation, tracking, and introspection logic is complete and fully tested.
- Node metadata, port/bus info, and trust/validation status introspection APIs are implemented and validated.
- Schema introspection is partially covered (contract is loaded/validated, but a dedicated schema endpoint may be deferred).
- Next: Implement CLI handler for `onex describe`, port metadata registration logic, and expand tool discovery APIs.

**Note:**
- The CLI handler for `onex describe` is now implemented, supports table/json/yaml output, and passes all tests.
- Port metadata registration logic is now implemented, protocol-pure, and validated by tests. The registry node's state and introspection expose all active port leases for tool discovery and audit.
- Registry node introspection now exposes all event buses, ports, and a canonical tools registry (ToolCollection) in a protocol-pure, standards-compliant way. All tests pass and coverage is confirmed.

**Assignees:** _(TBD)_
**Status:** _(Update as tasks are completed)_
**Notes:** _(Add implementation notes, PR links, etc.)_

**Progress Note:**
- Port allocation, tracking, and introspection logic is complete and fully tested.
- Node metadata, port/bus info, and trust/validation status introspection APIs are implemented and validated.
- Schema introspection is partially covered (contract is loaded/validated, but a dedicated schema endpoint may be deferred).
- Next: Implement CLI handler for `onex describe`, port metadata registration logic, and expand tool discovery APIs.

**Note:**
- The CLI handler for `onex describe` is now implemented, supports table/json/yaml output, and passes all tests.
- Port metadata registration logic is now implemented, protocol-pure, and validated by tests. The registry node's state and introspection expose all active port leases for tool discovery and audit. 