# ONEX Node Model: Future Work and Roadmap

> **Status:** Canonical Draft
> **Last Updated:** 2025-05-18
> **Purpose:** Outline proposed future features, enhancements, and roadmap items for the ONEX node model beyond the initial bootstrap (M0) and core implementation (M1).
> **Audience:** Core developers, architects, roadmap planners
> **Series:** Node Architecture
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting or legacy documentation.

---

## 🧭 Future Work (Proposed Link Types)

Beyond the current M1 linking fields (`dependencies`, `base_class`, `protocols_supported`), future schema versions (M3+) may introduce richer link types to model node graphs, derivations, provenance, and compatibility.

| Proposed Field     | Purpose                                                                  |
|--------------------|--------------------------------------------------------------------------|
| `consumes`         | Declares what data types, state_contracts, or formats this node reads       |
| `produces`         | Declares what formats or data types this node emits                              |
| `compatible_with`  | Indicates safe chaining compatibility based on shared state_contracts       |
| `fork_of`          | Marks this node as a fork of another node (version, derivation, reuse)      |
| `generated_by`     | Points to the node or tool that scaffolded or generated this node            |

These fields are reserved and will be introduced in Milestone 3+ via schema version updates and enforcement logic. Nodes using these links will benefit from improved visualization and analysis in node graphs.

---

## 🛠️ Future Extensions (Planned - Reducer & Impurity)

The following enhancements are proposed for future versions of the ONEX Node Specification, primarily related to formalizing and enhancing impure and stateful node behaviors managed by reducers.

1.  **Reducer State Schema Definition (`reducer_contract`)**: Define a mechanism for reducers to declare the JSON Schema for their internal state.
    * *Rationale:* Aids testing (can validate reducer state transitions), introspection, and potential debugging tools.
    * *Suggested Milestone:* M2+ (following initial `reducer` field introduction).

2.  **Reducer Chaining within a Node**: Support composing multiple reducers or state transition functions within a single node.
    * *Rationale:* Allows breaking down complex internal state logic into smaller, testable units.
    * *Suggested Milestone:* M3+

3.  **Explicit Orchestration Chains between Reducer Nodes**: Define metadata or runtime patterns for orchestrating sequences of dispatches or interactions across multiple stateful/reducer nodes.
    * *Rationale:* Enables building stateful workflows spanning multiple nodes.
    * *Suggested Milestone:* M3+

4.  **Impure Node Policy Enforcement**: Define validation rules and runtime policies specifically for impure nodes (e.g., requiring documentation of side effects, sandboxing considerations).
    * *Rationale:* Ensures impure nodes are used responsibly and securely.
    * *Suggested Milestone:* M3+

---

## 🏗️ Future Extensions (Planned - Trust & Validation)

These enhancements focus on improving the trust model, validation, and security features of ONEX nodes.

1.  **Cryptographic Signatures**: Full support for cryptographic signing and verification of node metadata, including trust attestations from trusted entities.
    * *Rationale:* Enables secure distribution and verification of nodes from trusted sources.
    * *Suggested Milestone:* M2+

2.  **Runtime Trust Assessment**: Define runtime procedures for dynamically assessing trust scores based on execution history, output validation, and other measurable factors.
    * *Rationale:* Allows systems to learn which nodes are reliable and trustworthy based on actual usage.
    * *Suggested Milestone:* M3+

3.  **Graduated Trust Levels**: Formalize a graduated trust system where nodes can earn higher trust levels through successful execution, validation, and endorsement.
    * *Rationale:* Provides a more nuanced approach to trust than binary trusted/untrusted.
    * *Suggested Milestone:* M3+

---

## 🔄 Future Extensions (Planned - Versioning & Evolution)

These enhancements address the evolution and versioning of nodes over time.

1.  **Version Compatibility Declarations**: Explicit declarations of compatibility between node versions.
    * *Rationale:* Simplifies dependency management and updates.
    * *Suggested Milestone:* M2+

2.  **Deprecation Mechanisms**: Formal process and metadata for deprecating nodes or specific node versions.
    * *Rationale:* Ensures clear communication about lifecycle and encourages migration.
    * *Suggested Milestone:* M2+

3.  **Breaking Changes Protocol**: Standardized way to document and communicate breaking changes in node interfaces.
    * *Rationale:* Reduces friction during updates and version changes.
    * *Suggested Milestone:* M2+

---

## 💾 Future Extensions (Planned - Caching & Performance)

These enhancements focus on improving the performance and efficiency of node execution.

1.  **Fine-grained Cacheability Controls**: Allow nodes to specify caching behaviors and invalidation rules at a granular level.
    * *Rationale:* Enables more efficient caching strategies tailored to specific node behaviors.
    * *Suggested Milestone:* M2+

2.  **Performance Profiling Integration**: Build-in performance profiling and benchmarking capabilities.
    * *Rationale:* Provides data for optimization and comparison between node implementations.
    * *Suggested Milestone:* M3+

3.  **Resource Usage Declarations**: Allow nodes to declare expected resource usage (memory, CPU, network, etc.).
    * *Rationale:* Aids in resource planning and efficient node allocation.
    * *Suggested Milestone:* M3+

---

**Status:** This document outlines proposed future enhancements to the ONEX Node Model. These proposals are not binding commitments but represent the current thinking on directions for evolving the architecture.

--- 