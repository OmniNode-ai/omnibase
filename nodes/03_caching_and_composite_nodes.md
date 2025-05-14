## 03 – Caching and Composite Nodes

### Context & Origin

This document describes the ONEX caching layer, including how reusable node subgraphs are encapsulated and memoized using composite nodes. This approach was born from the insight:

> "We can create arbitrary parent nodes that cache their subgraphs—caching is just context exploration."

---

### Composite Nodes

#### ✅ Purpose

* Wrap multiple child nodes into a single unit
* Enable reuse, substitution, and performance optimization
* Provide a single entry/exit point for complex subgraphs

#### ✅ Structure

```yaml
id: scaffold.pipeline
version: 0.2.4
type: composite
subgraph:
  - scaffold.validator
  - scaffold.name_checker
  - scaffold.tree_builder
```

#### ✅ Execution Flow

* Composite node resolved as part of graph
* Planner executes subgraph as an isolated unit
* Parent node may memoize output or emit global signal

---

### Caching Layer

#### ✅ Cache Between Nodes

* Cache stores:

  * Inputs
  * Node ID + version
  * Output + performance trace
* Cache key based on:

```yaml
cache_key:
  node_id: scaffold.tree_builder
  input_hash: sha256:aaa
  config_hash: sha256:bbb
  trace_hash: sha256:ccc
```

#### ✅ Cache Policy Block

```yaml
cache:
  enabled: true
  strategy: memoize
  scope: node | composite | global
  ttl_seconds: 3600
```

#### ✅ Cold Context as Long-Term Cache

* All cached outputs are stored as cold context
* Can be queried, inspected, replayed
* Versioned and TTL-governed

---

### Benefits of Caching

* Prevents recomputation of expensive nodes
* Enables deterministic subgraph testing
* Accelerates graph replay
* Reduces cloud/model cost

---

### Advanced Use Cases

#### 🔁 Tournament Caching

* Competing node variants cached with performance metadata
* Winning variant promoted based on hash + score

#### ♻️ Smart Cache Invalidation

* Invalidate on contract change
* Revalidate on schema upgrade or signal override

#### 🧠 Self-Aware Nodes

* Nodes can query their own cache history via registry
* Agents can review past performance to choose execution path

---

### Status

Canonical reference for the ONEX caching system. Composite nodes are the default boundary for cache reuse, test scaffolding, and latency optimization.
