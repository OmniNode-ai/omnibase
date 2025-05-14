---

version: v0.1
status: Draft
last\_updated: 2024-06-09
-------------------------

# O.N.E. Protocol Specification — v0.1 (Draft)

> **O.N.E. Framing:**
> This protocol specification defines the foundational standards for all O.N.E. (OmniNode Environment) deployments—local, hosted, federated, or hybrid. All registry, discovery, addressing, and trust models described herein are canonical for O.N.E. environments.

> **O.N.E. Context Note:**
> All protocol standards and registry/discovery practices described here are standardized across any O.N.E. (OmniNode Environment)—local, hosted, or federated.

---

## O.M.N.I. — Metadata & Network Identity  
*A sub-protocol for trust, addressing, and identity within O.N.E.*

## Mission Statement

OmniNode is the open protocol for distributed, intelligent systems—built to power the next generation of AI agents, developer tools, and decentralized compute.

We're creating more than messaging between nodes. We're creating a self-organizing ecosystem where agents, models, and resources flow freely between trusted peers—secured by cryptographic identity, coordinated by intelligent routing, and fueled by a shared commitment to openness.

## Terminology

* **O.N.E. (OmniNode Environment):** The unified environment for orchestrating, managing, and scaling OmniNode agents, tools, and services—local, hosted, or federated.
* **O.M.N.I.:** OmniNode Metadata & Network Identity protocol for trust, identity, and addressing.
* **Entity:** Any addressable component (node, agent, tool, validator, model) in an O.N.E.
* **Node:** A runtime unit (containerized or virtualized) registered in an O.N.E.
* **Agent:** An autonomous process or service that acts on behalf of users or workflows.
* **Registry:** The canonical service for entity discovery, metadata, and health (e.g., Consul, etcd).
* **Trust Zone:** Logical boundary for access control and compliance (e.g., zone.local, zone.org).

---

# O.M.N.I. — OmniNode Metadata & Network Identity

*The secure backbone for agent identity, access control, and trust enforcement.*

O.M.N.I. is the security and trust protocol for the OmniNode ecosystem. It governs identity registration, authentication, authorization, trust zones, signature validation, and network integrity for all addressable entities (nodes, agents, tools, validators, models).

---

## Protocol Layers

| Layer            | Purpose                                            |
| ---------------- | -------------------------------------------------- |
| Control Plane    | Messaging, orchestration, task routing (JetStream) |
| Data Plane       | Model & data distribution (BitTorrent-style P2P)   |
| Addressing       | Logical routing using node IDs, types, and zones   |
| Trust & Security | Trust-aware message validation and node reputation |

---

## Registry & Discovery

OmniNode assumes a shared registry for all addressable entities (nodes, agents, tools, validators, models). This registry is the canonical approach for all O.N.E. deployments and must support:

* Canonical address resolution
* Health check metadata
* Trust zone assignment
* Signature key verification

### Default Implementation: Consul

In the MVP, we use Consul to manage entity discovery, health checks, and metadata.

Alternate implementations may include etcd, Redis-backed service directories, or decentralized DHTs.

---

## Messaging Semantics

O.N.E. messaging is event-based, using JetStream for distributed, reliable message passing. Message types include:

### Message Types

| Type                   | Description                         |
| ---------------------- | ----------------------------------- |
| `event.node.register`  | New node joins the registry         |
| `event.agent.started`  | Agent instance activated            |
| `event.node.failed`    | Node reported unhealthy             |
| `signal.task.dispatch` | Task routing or execution signal    |
| `signal.result.ready`  | Output produced by a node           |
| `signal.state.update`  | Update to node or system-wide state |

### Stream Protocol

All O.N.E. environments must support:

* **Durable subscription**
* **Backpressure handling**
* **Dead-letter queueing**
* **Replay from sequence**

### Namespacing

```
jetstream.onex.zone.{zone_id}.{entity_type}.{entity_id}.events
```

---

## Security and Trust Model

All O.N.E. messages and nodes must support trust metadata and signature enforcement.

### Trust Metadata

```yaml
trust:
  signer: omninode.root
  level: verified
  signature: sha256:abcdef...
  zone: zone.trusted.org
  expires_at: 2025-12-31T00:00:00Z
```

### Trust Policies

| Policy Type    | Scope          | Enforcement Level |
| -------------- | -------------- | ----------------- |
| `signature`    | node, agent    | strict            |
| `zone_match`   | session        | advisory          |
| `token_valid`  | message        | strict            |
| `origin_check` | distributed ID | advisory          |

---

## Version Negotiation

O.N.E. must support versioned schema and protocol negotiation across federated deployments.

```yaml
protocol:
  version: 0.1
  compatible_with: ["0.1", "0.0.9"]
  declared_by: registry.omninode.org
  schema_manifest_url: https://.../schemas/v0.1/index.json
```

Federated deployments must:

* Support schema version probing
* Support fallback negotiation (e.g. transform between `v0.2` and `v0.1` if needed)
* Reject incompatible agents with clear error codes

---

## Execution Trust Chain

A full trust chain includes:

1. **Agent Keypair** – issued at onboarding or self-generated with O.M.N.I. attestation
2. **Node Identity** – cryptographic ID tied to fingerprinted build and zone
3. **Signed Registry Entry** – stored in canonical registry with proof of signature
4. **Session Grant** – time-bound, revocable contract authorizing node or agent
5. **Execution Attestation** – log of outcome, signature, cost, and trust delta

### Example:

```yaml
execution_attestation:
  node: scaffold.uuid_checker
  trace_hash: sha256:abc123...
  signer: registry.omninode.org
  trust_delta: +0.02
  verified: true
  execution_time: 92ms
```

Trust chains allow OmniNode to:

* Trace provenance of results
* Rate agents by performance and consistency
* Enforce zone-aware policy
* Select fallback or alternate nodes with proof context

---

\[Restored full content from docs.bak/protocol/O.N.E.\_protocol\_spec\_v0.1.md and extended with v0.1.1 streaming, trust, negotiation, and trust chain clauses]
