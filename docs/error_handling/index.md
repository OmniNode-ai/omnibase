<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: index.md
version: 1.0.0
uuid: b7ec0d3e-2f06-4c8c-b90a-f6b9515493e5
author: OmniNode Team
created_at: 2025-05-27T07:23:25.853385
last_modified_at: 2025-05-27T17:26:52.019866
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: c89bef4f39058e4e5123e5ccc0ac41628f42fef98cead912aaead25679bbc0eb
entrypoint: python@index.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.index
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Error Handling Deep Dives Index

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Index for detailed error handling documentation  
> **Audience:** Developers, system architects, platform engineers  
> **Companion:** [Error Handling Specification](../error_handling.md)

---

## Overview

This directory contains deep-dive documentation for the ONEX error handling system. For a high-level overview and canonical specification, see [Error Handling Specification](../error_handling.md).

---

## Contents

### [Observability & Tracing](observability.md)
Advanced observability, OpenTelemetry integration, and error tracing details including:
- Observability hooks and span tracing
- Structured logging and correlation IDs
- CLI output modes and formatting
- Design requirements and constraints

### [Retry & Circuit Breaker](retry.md)
In-depth discussion of retry logic, backoff, and circuit breaker patterns including:
- Retryable vs non-retryable error classification
- Exponential backoff and retry decorators
- Circuit breaker implementation patterns
- Observability integration for retry operations

---

## Quick Reference

### Error Classification
- **RetryableError**: Transient failures (I/O, network, auth)
- **NonRetryableError**: Logic errors, invalid input
- **SecurityError**: Capability denied, authorization failures

### Observability Features
- OpenTelemetry span tracing
- Structured JSON logging
- Error correlation IDs
- Retry count tracking
- Circuit breaker state monitoring

### CLI Output Formats
- **human**: Developer-friendly CLI usage
- **json**: CI/CD pipeline integration
- **yaml**: Agent and automation inspection

---

## Design Principles

1. **No Silent Failures**: All errors must be explicitly handled and reported
2. **Structured Output**: No `print()` statements; use loggers or CLI emitters
3. **Observable Operations**: Every error emits traces and structured logs
4. **Graceful Degradation**: Circuit breakers prevent cascade failures
5. **Actionable Feedback**: Errors include suggestions for resolution

---

## References

- [Error Handling Specification](../error_handling.md)
- [Error Taxonomy](../error_taxonomy.md)
- [Monitoring Specification](../monitoring.md)
- [CLI Interface](../cli_interface.md)

---

**Note:** This directory provides detailed implementation guidance for the ONEX error handling system. All error handling components should follow these patterns to ensure consistency and reliability.
