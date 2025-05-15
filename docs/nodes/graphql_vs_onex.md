# ONEX Node Architecture: GraphQL vs ONEX - Declarative Query vs Declarative Execution

> **Status:** Canonical  
> **Series:** Node Architecture  
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting or legacy documentation. 

## 07 – GraphQL vs ONEX: Declarative Execution vs Declarative Query

### Context & Origin

This document explores the parallels—and fundamental differences—between ONEX and GraphQL, framing the comparison through their respective declarative natures. Both systems use declarative methods driven by schemas and contracts, but they apply them to fundamentally different problem spaces:

> "ONEX is like GraphQL—but focused on declarative **component execution** based on function contracts, rather than just declarative **data querying**."

ONEX describes and executes a graph of *functions* (nodes), while GraphQL describes and queries a graph of *data structures*.

---

### Key Similarities

| Aspect                 | GraphQL                                     | ONEX                                            | Relevance to Function Model                |
|------------------------|---------------------------------------------|-------------------------------------------------|--------------------------------------------|
| **Declarative Definition** | Describes data structure shapes             | Describes node functions and their composition  | Both define *what* is available declaratively. |
| **Schema Driven** | Uses schema to define data structure types  | Uses `.onex` schema + `state_contract` schema to define **function interfaces** and **properties** | Schemas define the *signature* and *metadata* of the declared unit. |
| **Contract-Based Interaction** | Client defines desired data shape via query | Node declares input/output `state_contract` to define **function signature**; graph defines **function call flow** | Contracts define the *interface* for data passing (function args/returns) and control. |
| **Dynamic Resolution** | Resolves data fetchers/resolvers at runtime | Resolves executable **node functions**, planners, and dispatchers at runtime | Both systems dynamically determine *how* to fulfill a request (query/execution). |

---

### Core Differences

Understanding these differences is crucial for appreciating ONEX's unique capabilities as a declarative *execution* environment compared to GraphQL as a declarative *query* language.

| Aspect            | GraphQL                             | ONEX                                                  | Link to Function Model                            |
| ----------------- | ----------------------------------- | ----------------------------------------------------- | ------------------------------------------------- |
| Purpose           | Query and manipulate data           | **Execute functions**, transform state, run workflows | **Execution** (ONEX) vs **Data Retrieval/Mutation** (GraphQL Resolvers). |
| Inputs            | Query / mutation arguments          | Input `state_contract` (function arguments), prompts, configuration | Defines the **function call's parameters**.       |
| Outputs           | Requested data                      | Output `state_contract` (function return value), side effects | Defines the **function's return value** and potential **side effects**. |
| Type Safety       | Strong via schema (Data Shape)      | Strong via input/output `state_contract` (Data Shape for **Function I/O**) | Ensures type-safe data passing between function calls. |
| Recursive Support | Limited (often shallow nesting)     | Full internal DAG traversal and **function composition** | Supports composing complex **recursive workflows of functions**. |
| Execution         | Predominantly Stateless Resolvers   | **Stateful, traceable, resumable execution** (via reducers and persistent context) | Supports **stateful functions** with managed internal state. |
| Trust + Metadata  | Minimal (data field properties)     | First-class, used for **orchestrating function calls**, routing, evolution, trustworthiness | Annotates **function properties** relevant to execution control. |
| Caching & Reuse     | Not applicable                        | Full subgraph memoization via `memoization_tier` and `trace_hash` | Enables deep caching of execution results and subgraph reuse. |

---

### GraphQL Limitations for ONEX (Why a Query Language Isn't Enough for Execution)

GraphQL's design as a declarative query language imposes limitations when the goal is declarative *execution* and *workflow* definition:

#### ❌ No Native Recursion for Execution Graphs

* GraphQL's query structure is primarily designed to traverse data trees, requiring manual depth definitions for nested data.
* ONEX must support recursive DAGs representing arbitrary **compositions of node functions** where the depth is determined by the workflow logic, not a query constraint.
* **Solution:** Recursion within the ONEX execution graph is managed internally. If exposing to a GraphQL interface, the graph structure is flattened into data blobs or subgraph references that GraphQL *can* query.

#### ❌ No Intrinsic Execution Engine

* GraphQL resolvers are typically focused on fetching or performing simple mutations on data; they don't constitute a general-purpose engine for executing arbitrary **transformation functions** or complex logic.
* ONEX nodes actively execute code (`entrypoint`), transform data, perform validation, or interact with external systems as **executable functions**.

#### ❌ No First-Class Performance or Trust Layer

* GraphQL schema fields carry data type information but don't intrinsically carry metadata about the performance or trustworthiness of the underlying resolver that fetches the data.
* ONEX nodes are annotated with metadata crucial for execution planning and trust: `success_rate`, `trace_hash`, `trust_score`, `cost_profile`, etc. This metadata allows the system to reason about **which node function implementation** to call or how to orchestrate calls reliably.

ONEX also supports subgraph-level memoization. Using `memoization_tier: deep`, the system caches execution traces across internal DAGs, allowing previously executed subgraphs to be reused across workflows. GraphQL has no equivalent mechanism for caching function execution trees or sharing computation history between requests.

---

### Declarative System Comparison: Analogies

> "GraphQL is a query language for *data*. ONEX is a queryable execution system for *behavior* defined by functions."

#### GraphQL Query Analogy:

```graphql
query GetUserView {
  user(id: "123") { # Calls a 'user' resolver (data fetcher function) with id arg
    name           # Selects specific fields from the returned data structure
    status
    avatar_url
  }
}
```
*Focus: Declaring the desired *shape* of data to retrieve.*

#### ONEX Execution Analogy:

```yaml
# Declaring a sequence of function calls (workflow)
workflow:
  - call:             # Declare a function call step
      node_uri: prompt.generator@1.0.0 # The function to call
      input_state:    # The input arguments (state_contract) for this call
        template_id: "avatar_prompt"
        user_id: "user-123"
      output_alias: generated_prompt # Alias for the output state
  - call:
      node_uri: image.generator.v1@2.0.0 # Another function to call
      input_state:    # Input arguments for this call, referencing previous output
        prompt: @generated_prompt.text # Use output from previous function call
      output_alias: avatar_image_result
```
*Focus: Declaring the sequence and connections of *function calls* to execute.*

---

### Learnings from Schema-Driven UI Workflows

* Just like GraphQL-driven UI views compose data fetched by resolvers:
    * ONEX can describe workflows as composable **graphs of node functions**.
    * Success depends on investment in creating reusable **node function components**.
    * Versioning and contract (`state_contract`) stability are critical for reliable **function interfaces**.

---

**Conclusion**

ONEX goes beyond GraphQL: it is a **declarative execution environment** where metadata and contracts govern not just data structure, but **runtime behavior, function composition, state management, evolution, and trust** of executable node functions.

> "GraphQL shows you what data looks like. ONEX tells you how to **execute** functions to make it, test it, and evolve the behavior."

---