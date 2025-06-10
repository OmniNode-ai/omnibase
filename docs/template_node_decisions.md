<file name=0 path=/Volumes/PRO-G40/Code/omnibase/docs_private/milestones/template_node_decisions.md># ONEX Architecture: Template, Reducer, and Runtime Node Evolution  
*Date: 2025-06-03*

---

## 🔧 Summary

Today marks a key architectural refinement in ONEX. What began with exploratory work on the `tree_node` evolved into a foundational shift: defining a canonical `template_node`, reworking the role of `node.py` as a reducer, and consolidating all runtime functionality into a single, introspectable `runtime_node`.

This unified structure enables agents, orchestrators, and validators to treat all ONEX logic—no matter how simple or shared—as node-based, observable, and trust-compliant.

---

## 🧠 Key Concepts and Decisions

### ✅ Canonical `template_node`

- A minimal, clean node that follows the `.run().bind()` pattern
- Works with the ONEX runner, scenario runner, and updated test infrastructure
- Used as the pattern to clone from by the `manager_node`
- Serves as the source of truth for scaffolding and future node creation

### ✅ `node.py` as a Reducer

- Each node's `node.py` is now formally a **reducer**
- It accepts a `StateBlock`, selects a handler, and returns a `ResultBlock`
- Execution is composed using `.run().bind(...)`
- It does **not** contain behavior — it routes to inline state transformers

### ✅ Global Scenario Runner

- Orchestrates all node execution across the graph
- Nodes themselves do **not** have local scenario runners
- Reacts to `StateTransition` and `EventBlock` outputs
- Triggers new node executions or halts based on scenario state

### ✅ Runtime Functionality = `runtime_node`

- All shared helpers (e.g. `merge_state`, `emit_event`) are wrapped in a single `runtime_node`
- This node uses a dispatch table to expose helper functions to agents and runners
- Emits proper ONEX blocks and metadata
- Solves the introspection problem: agents can now discover and invoke all core functionality

---

## 📁 Directory Structure

```
    nodes/
        template_node/
            node.py
            metadata.yaml
            tests/
        runtime_node/
            node.py
            dispatch.yaml
            tests/
    runtime/
        state_utils.py
        event_utils.py
        contracts.py
```

---

## 🧪 Runtime Dispatch Logic

```
    DISPATCH_TABLE = {
        "merge_state": merge_state,
        "emit_event": emit_event,
        ...
    }

    from omnibase.core.errors import OnexError, CoreErrorCode

    def run(state):
        action = state.params["action"]
        handler = DISPATCH_TABLE.get(action)
        if not handler:
            raise OnexError(CoreErrorCode.UNSUPPORTED_OPERATION, f"Unknown runtime action: {action}")
        return handler(state)
```

---

## 📊 Strategic Benefits

```
    | Benefit                   | Description                                                 |
    |---------------------------|-------------------------------------------------------------|
    | Unified Model             | Everything is a node; helpers aren't special cases anymore  |
    | Agent-Aware               | Agents can reason about and invoke helper logic             |
    | Trustable & Observable    | All logic runs through ONEX protocols and logging           |
    | Composable                | Runtime helpers can be used in .bind() chains               |
    | Scenario-Compatible       | Can be orchestrated via external transitions or events      |
    | Future-Proof              | Runtime functions can evolve into standalone nodes if needed|
```

---

## ⏱ Timeline of Iteration

```
    | Time      | Key Shift                                                            |
    |-----------|----------------------------------------------------------------------|
    | Morning   | `tree_node` work began prematurely, without finalized infrastructure |
    | Midday    | Decision to build `template_node` as canonical pattern               |
    | Afternoon | Realized runtime helpers were opaque to agents                       |
    | Evening   | Decided to wrap all shared helpers in `runtime_node`                |
    | Late Day  | Locked in node.py = reducer, scenario runner = global orchestrator   |
```

---

## 🚀 Next Steps

```
    - [ ] Scaffold and finalize `template_node/` structure
    - [ ] Refactor `manager_node` to follow `.run().bind()` and clone from template
    - [ ] Create `runtime_node/` with dispatch table and schema exposure
    - [ ] Register helpers and emit metadata for agent introspection
    - [ ] Add GraphQL support for discoverability
    - [ ] Finalize e2e test coverage across runners
    - [ ] Update CLI `--scaffold` to default to `template_node`
```

---

## Scenario Exposure and Node-Specific Scenario Registry

> Inline handlers are scoped to a specific node's internal logic. Runtime helpers are global utilities wrapped in the `runtime_node` for shared access and dispatch-based execution.

- Scenarios are not globally registered in the ONEX registry. Instead, each node exposes its available scenarios via its introspection API.
- Each node maintains its own scenario registry/index (e.g., scenarios/index.yaml) listing all supported scenarios, their metadata, tags, and expected outcomes.
- Node introspection returns the list of available scenarios, their metadata, and how to invoke them.
- CI, agents, and UIs discover and run scenarios by querying node introspection, not by scanning the global registry.
- **Benefits:**
    - Keeps the global registry clean and focused on nodes, contracts, and tools.
    - Improves discoverability and organization of scenarios.
    - Allows node authors to add, deprecate, or version scenarios without polluting the global namespace.
    - Enables scalable, scenario-driven validation and regression testing.
    - CI systems can discover and validate scenarios per node without needing global registry awareness, simplifying testing and integration.

### Example: `scenarios/index.yaml` for `validate_node`

    - id: validate_input_state
      description: Validates a node's input against contract schema
      tags: [validation, contract]
      entrypoint: scenarios/validate_input_state.yaml
      expected_result: success

---

## 💡 Closing Insight

> By unifying all execution under node-based structures, ONEX becomes a fully introspectable, agent-compatible, trust-traceable environment. No dual systems. No opaque helpers. Just nodes.

---

# Innovation Additions & Concerns

## Additions & Enhancements

1. **Metadata-Driven Node Discovery and Introspection**
    - Extend `metadata_block` to include introspection hooks and trust signals (e.g., `describe_extended`, `get_contract_schema`, `reviewed`, `coverage`, `provenance`).
2. **Dynamic Node Promotion and Demotion**
    - Allow nodes to be promoted/demoted between `internal`, `experimental`, and `public` via metadata and CI controls.
3. **Composable Node Graphs with Partial Bindings**
    - Support partial application and composition of nodes (e.g., `node_a.bind(param=value).run()`).
4. **Runtime Node as a Service**
    - Expose the `runtime_node` as a service endpoint (e.g., gRPC/GraphQL) for agent and external tool integration.
5. **Scenario-Driven Test and Validation**
    - All tests should be scenario-driven, using real node chains and state transitions, with snapshot and replay support.
6. **Contract-First Node Registration**
    - Require all nodes to declare input/output contract schemas in metadata, auto-generating validation and docs.
7. **Trust and Provenance Tracking**
    - Add fields to `metadata_block` for code review status, test coverage, and provenance.
8. **Live Node Reloading and Hot Swapping**
    - Support live reloading of node implementations in dev/test environments, with version pinning for scenarios.
9. **Registry-Driven Mocking and Overrides**
    - Allow the registry to provide mock or override implementations for any node, controlled via scenario or test config.
10. **GraphQL/Introspection API for All Nodes**
    - Expose a GraphQL endpoint for querying all registered nodes, their metadata, contracts, and trust signals.
11. **Inline Node Unit Test Harness**
    - Provide a lightweight test harness that can run inline node handlers in isolation, outside of full node execution. Useful for debugging, experimentation, and fast iteration on logic before embedding in a full `.run().bind()` chain.

## Concerns & Mitigations

1. **Metadata Drift and Boilerplate**
    - *Mitigation:* CLI tooling for scaffolding, validation, and updates; metadata inheritance/templates.
2. **Dispatch Table Complexity in Runtime Node**
    - *Mitigation:* Enforce contract/review for dispatch entries; group/document helpers by domain.
3. **Scenario Runner as a Bottleneck**
    - *Mitigation:* Allow sharding/parallel execution; ensure stateless, scalable runner.
4. **Versioning and Compatibility**
    - *Mitigation:* Enforce strict version pinning in scenario metadata; provide migration tools and compatibility checks.
5. **Security and Exposure**
    - *Mitigation:* Require explicit `exposed: true` and `scope: public` for external nodes; support access control and audit logging.
6. **Overhead of Treating All Helpers as Nodes**
    - *Mitigation:* Use a `runtime_node` dispatch strategy to group related helpers under a single node interface, reducing node sprawl while preserving introspection and testability.

---

# Future Milestones & Work Breakdown

## M2: Introspection, Trust, and Contract-First Nodes
- [ ] Extend `metadata_block` to support introspection hooks and trust signals
- [ ] Require contract schemas in node metadata; auto-generate validation/docs
- [ ] Add trust/provenance fields (reviewed, coverage, provenance)
- [ ] Implement CLI tooling for metadata management and validation
- [ ] Define schema and enforcement for per-node scenario registries (e.g., `scenarios/index.yaml`)

## M3: Runtime Node as a Service & GraphQL API
- [ ] Expose `runtime_node` as a service endpoint (gRPC/GraphQL)
- [ ] Implement GraphQL introspection API for all nodes and metadata
- [ ] Add access control and audit logging for public/exposed nodes

## M4: Scenario-Driven Testing, Mocking, and Live Reloading
- [ ] Refactor all tests to be scenario-driven, using real node chains
- [ ] Implement snapshot/replay support for scenarios
- [ ] Support registry-driven mocking and override injection for nodes
- [ ] Enable live reloading/hot swapping of node implementations in dev/test
- [ ] Add version pinning and compatibility checks for scenarios
- [ ] Add CLI support to run individual inline handlers or test runtime helpers independently via `onex test --handler foo`
- [ ] Extend `metadata_block` with `test_matrix` and `test_coverage` fields to expose quality signals to agents and dashboards

## M5: Composable Node Graphs & Partial Bindings
- [ ] Support partial application and composition of nodes in `.bind()` chains
- [ ] Document and test advanced node graph composition patterns