# Node Architecture Series

> **Status:** Canonical
> **Precedence:** The following documents are part of the Node Architecture Series and take precedence over any conflicting or legacy documentation. They define the core execution, planning, and trust model for OmniNode/ONEX.

---

## Introduction

The Node Architecture Series captures the canonical, foundational design and execution patterns for OmniNode (ONEX). These documents define the reducer/event-driven state model, contract-first node philosophy, graph resolution, caching, streaming, prompt/model integration, performance memory, and the architectural distinction from GraphQL. They are the authoritative reference for all node and execution-related behavior in the system.

---

## Table of Contents

1. **[State Reducers and Streams Architecture](./state_reducers.md)**  
   _Reducer/event-driven state, signals, and streaming as the foundation for node execution and session management._
2. **[Node Contracts and Metadata Structure](./node_contracts.md)**  
   _Contract-first, metadata-driven node design; input/output contracts, performance memory, and trust._
3. **[Graph Resolution and Execution Planning](./graph_resolution.md)**  
   _DAG-based execution planning, contract-driven topo sort, trust constraints, and streaming execution._
4. **[Caching and Composite Nodes](./caching_and_composite_nodes.md)**  
   _Composite nodes, subgraph encapsulation, cache keys, and advanced caching strategies._
5. **[Sessions and Streaming Architecture](./sessions_and_streaming.md)**  
   _Session lifecycle, JetStream/gRPC/WebSocket streaming, trust-aware multiplexed execution._
6. **[Prompt Blocks and Model Nodes](./prompt_blocks_and_model_nodes.md)**  
   _Prompts as first-class input blocks, model nodes as transformers, prompt contracts, and agent planning._
7. **[Performance Memory and Cost-Aware Execution](./performance_memory_and_cost.md)**  
   _Performance tracking, trace hashes, node evolution, trust/reputation, and cost-optimized planning._
8. **[GraphQL vs ONEX: Declarative Execution vs Declarative Query](./graphql_vs_onex.md)**  
   _Comparison of ONEX's contract-driven execution model with GraphQL's query paradigm._

---

> For any architectural, execution, or node-related question, these documents are the source of truth. If a conflict arises with other documentation, the Node Architecture Series prevails. 