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
- [ ] Implement registry node logic for port allocation, tracking, and introspection
  - [ ] Emit structured log and telemetry events for port allocations/releases
- [ ] Update node and test harnesses to request ports from the registry instead of picking ad hoc

### Introspection & Tool Discovery (see design doc for schema)
- [ ] Implement node metadata introspection API (Milestone 1)
- [ ] Implement port & bus info introspection API (Milestone 1)
- [ ] Implement schema introspection API (Milestone 1)
- [ ] Implement trust/validation status API (Milestone 1)
- [ ] Implement CLI handler for `onex describe` (Milestone 1)
- [ ] Implement port metadata registration logic in registry node runtime (Milestone 1)
- [ ] Expand registry node introspection to list all available event buses, ports, and exposed tools (with contracts)
- [ ] Update all nodes to register their tools and contracts with the registry node at startup
- [ ] Implement registry APIs for tool discovery and (optionally) proxy invocation

### Documentation and Testing
- [ ] Update developer docs and codegen tools to leverage registry-driven tool discovery
- [ ] Add tests for port allocation, tool registration, and introspection
  - [ ] Add collision detection strategy for duplicate tool contract IDs (document, not enforce)

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

---

**Assignees:** _(TBD)_
**Status:** _(Update as tasks are completed)_
**Notes:** _(Add implementation notes, PR links, etc.)_ 