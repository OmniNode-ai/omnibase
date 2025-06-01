# ONEX Event Bus Expansion: Architecture, Protocols, and Registry-Driven Discovery

**Status:** Living document – design, implementation, and reference for all ONEX event bus backends and registry-driven management.

---

## Table of Contents
1. Overview: Event Bus Architecture
2. Motivation: Dynamic Port Allocation & Registry-Driven Management
3. Supported Event Bus Backends
4. Protocols
    - 4.1 Port Request/Lease
    - 4.2 Event Bus Registration
    - 4.3 Introspection & Discovery
    - 4.4 Tool Registration & Discovery
5. Example Message Contracts
6. Best Practices for Test & CI Isolation
7. Developer Guidance
8. Future Enhancements
9. References

---

## 1. Overview: Event Bus Architecture
- In-memory, ZMQ (TCP/IPC), IPC, JetStream/NATS (future)
- Registry node as central broker for port allocation, event bus discovery, and tool contracts

## 2. Motivation: Dynamic Port Allocation & Registry-Driven Management
- Prevent port collisions, enable robust test/CI, support distributed orchestration
- Centralize event bus and tool discovery for extensibility and observability

## 3. Supported Event Bus Backends
- InMemoryEventBus: for local, single-process use
- ZmqEventBus: for cross-process, TCP/IPC
- IpcEventBus: for Unix domain socket IPC (future)
- JetStream/NATS: for distributed/cloud-native (future)

## 4. Protocols
### 4.1 Port Request/Lease
- Request/response pattern for port allocation
- Lease lifecycle, TTL, renewal, and release
### 4.2 Event Bus Registration
- Nodes register event bus endpoints with the registry
- Registry tracks and introspects all active buses
### 4.3 Introspection & Discovery
- Registry exposes all event buses, endpoints, and status
- Introspection API for clients, agents, and tools
### 4.4 Tool Registration & Discovery
- Nodes register tool contracts (input/output schemas, error codes)
- Registry exposes all available tools and contracts

## 5. Example Message Contracts
- PortRequest, PortLease, EventBusRegistration, ToolContractRegistration, IntrospectionResponse (with JSON schema snippets)

## 6. Best Practices for Test & CI Isolation
- Always request ports from registry in tests
- Use per-test event bus instances
- Clean up ports and registrations after use

## 7. Developer Guidance
- How to request a port from the registry
- How to register an event bus and tools
- How to use introspection for dynamic discovery

## 8. Future Enhancements
- Metrics, access control, multi-tenant support, health checks

## 9. References
- [milestone_1_checklist.md](../milestones/milestone_1_checklist.md)
- [implementation_checklist_registry_node_port_allocation.md](../milestones/implementation_checklist_registry_node_port_allocation.md)

---

_This document is updated as the event bus and registry node evolve. Please contribute improvements and corrections as needed._ 