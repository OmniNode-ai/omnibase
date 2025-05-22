<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: index.md
version: 1.0.0
uuid: c3a8365d-f812-4cc7-a858-e6dbda40909a
author: OmniNode Team
created_at: 2025-05-22T17:18:16.681352
last_modified_at: 2025-05-22T21:19:13.401268
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: b88da630f7502bbfd0bf17362381061c6f92c48ce78f01a6fdb50ad3262df3b5
entrypoint: python@index.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.index
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Error Handling Deep Dives Index

This directory contains deep-dive documentation for the OmniBase error handling system. For a high-level overview and canonical specification, see [../error_handling.md](../error_handling.md).

## Contents

- [Observability & Tracing](observability.md):
  - Advanced observability, OpenTelemetry integration, and error tracing details.
- [Retry & Circuit Breaker](retry.md):
  - In-depth discussion of retry logic, backoff, and circuit breaker patterns.

---

Return to [Error Handling Specification](../error_handling.md)
