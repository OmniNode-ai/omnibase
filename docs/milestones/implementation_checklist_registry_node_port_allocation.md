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