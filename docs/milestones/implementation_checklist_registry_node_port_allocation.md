# Implementation Checklist: Registry Node – Dynamic Event Bus Port Allocation and Tool Introspection

**Context:**
This checklist tracks the immediate, actionable tasks for implementing registry-driven event bus port allocation and tool discovery as part of Milestone 1. For high-level status and DoD, see [milestone_1_checklist.md](./milestone_1_checklist.md).

---

## Immediate Tasks (Milestone 1)

### Port Allocation
- [ ] Design protocol for requesting and releasing event bus ports from the registry node
  - [ ] Define port lease lifecycle, including TTLs and lease renewal policy
  - [ ] Validate port availability before lease grant; retry with backoff on conflict
- [ ] Implement registry node logic for port allocation, tracking, and introspection
  - [ ] Emit structured log and telemetry events for port allocations/releases
- [ ] Update node and test harnesses to request ports from the registry instead of picking ad hoc

### Tool Registration and Introspection
- [ ] Expand registry node introspection to list all available event buses, ports, and exposed tools (with contracts)
- [ ] Update all nodes to register their tools and contracts with the registry node at startup
- [ ] Implement registry APIs for tool discovery and (optionally) proxy invocation

### Documentation and Testing
- [ ] Update developer docs and codegen tools to leverage registry-driven tool discovery
- [ ] Add tests for port allocation, tool registration, and introspection
  - [ ] Add collision detection strategy for duplicate tool contract IDs (document, not enforce)

---

## Future Milestone (Stubbed for M2+)
- [ ] Implement registry cleanup logic for orphaned ports
- [ ] Add metrics: current allocation count, available ports, failed requests
- [ ] Implement access controls for port allocation and tool registration
- [ ] Add audit log entries for all port and tool operations
- [ ] Define rebinding mechanism if node's port is no longer usable

---

## Design Notes & Open Questions
- Protocol sketch for port request/release
- Tool contract registration format
- Introspection response schema
- Open questions and blockers

---

**Assignees:** _(TBD)_
**Status:** _(Update as tasks are completed)_
**Notes:** _(Add implementation notes, PR links, etc.)_ 