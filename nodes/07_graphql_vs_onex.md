## 07 – GraphQL vs ONEX: Declarative Execution vs Declarative Query

### Context & Origin

This document explores the parallels—and fundamental differences—between ONEX and GraphQL, stemming from this insight:

> "OmniNode is like GraphQL—but with component-driven contracts, and the means to execute them."

---

### Key Similarities

#### ✅ Declarative Schema

* Both GraphQL and ONEX use schemas to describe:

  * Structure
  * Capabilities
  * Required/optional fields

#### ✅ Contract-Based Query / Execution

* In GraphQL: client defines desired data shape
* In ONEX: node declares input/output contracts to shape execution flow

#### ✅ Dynamic Resolution

* GraphQL resolves resolvers at runtime
* ONEX resolves executable nodes, planners, and dispatchers at runtime

---

### Core Differences

| Aspect            | GraphQL                   | ONEX                                        |
| ----------------- | ------------------------- | ------------------------------------------- |
| Purpose           | Query data                | Execute transformations                     |
| Inputs            | Query / mutation schema   | Input contracts / prompts / config          |
| Outputs           | Data                      | Mutated state / code / transformed output   |
| Type Safety       | Strong via schema         | Strong via input/output contracts           |
| Recursive Support | Limited (shallow nesting) | Full internal DAG traversal and composition |
| Execution         | Stateless                 | Stateful, traceable, resumable              |
| Trust + Metadata  | Minimal                   | First-class, used for routing and evolution |

---

### GraphQL Limitations for ONEX

#### ❌ No Native Recursion

* GraphQL requires manual depth definitions
* ONEX must support recursive DAGs of unlimited depth
* Solution: flatten recursion in GraphQL layer via JSON blobs or subgraph references

#### ❌ No Execution Engine

* GraphQL cannot mutate state or run code
* ONEX nodes actively execute, transform, or validate input

#### ❌ No Performance/Trust Layer

* GraphQL fields don’t carry reputation
* ONEX nodes carry:

  * `success_rate`
  * `trace_hash`
  * `trust_score`
  * `cost_profile`

---

### Declarative System Comparison

> "GraphQL is a query language for *data*. ONEX is a queryable execution system for *behavior*."

#### GraphQL Analogy:

```graphql
query GetUserView {
  user(id: "123") {
    name
    status
    avatar_url
  }
}
```

#### ONEX Analogy:

```yaml
- prompt: "Generate avatar image for user ID 123"
- transformer.node: image.generator.v1
- input_contract:
    user.id: str
- output_contract:
    image.url: str
```

---

### Learnings from Schema-Driven UI Workflows

* Just like GraphQL-driven views:

  * ONEX can describe workflows as composable graphs
  * You must invest in reusable components
  * Versioning and contract stability are critical

---

**Conclusion**
ONEX goes beyond GraphQL: it is a **declarative execution environment** where contracts govern not just structure, but **runtime behavior, evolution, and trust**.

> "GraphQL shows you what something looks like. ONEX tells you how to make it, test it, and evolve it."
