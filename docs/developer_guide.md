<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: developer_guide.md
version: 1.0.0
uuid: a94bdb94-71fe-4705-9b70-376db84448c9
author: OmniNode Team
created_at: '2025-05-28T12:40:26.240949'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://developer_guide
namespace: markdown://developer_guide
meta_type: tool

<!-- === /OmniNode:Metadata === -->
# Canonical Rule: Protocols vs Abstract Base Classes (ABCs)

> **Status:** Canonical Draft  
> **Last Updated:** 2025-05-18  
> **Audience:** Contributors implementing core interfaces, validators, tools, plugins, and infrastructure nodes  
> **Applies To:** `omnibase.protocol.*`, validator/test/tool interfaces, `Protocol*` patterns in ONEX

---

## 🧭 Purpose

This document outlines the canonical rules for when to use **`Protocol`** vs **Abstract Base Classes (`ABC`)** when designing interfaces in the ONEX ecosystem. Consistent usage is critical for extensibility, plugin boundary clarity, and type-safe collaboration across tools, agents, and validators.

---

## 🔍 Summary Table

| Use Case | Protocol | ABC |
|----------|----------|-----|
| Third-party plugin interfaces | ✅ Yes | ❌ No |
| Internal base class with shared logic | ❌ No | ✅ Yes |
| Interface contract based on method shape only | ✅ Yes | ❌ No |
| Requires subclassing enforcement or `super()` logic | ❌ No | ✅ Yes |
| Behavior-first pattern, runtime agnostic | ✅ Yes | ❌ No |
| Static typing + duck-typed implementation | ✅ Yes | ❌ No |
| Cross-boundary usage (tools, agents, plugins) | ✅ Yes | ❌ No |
| Tight control over subclass lifecycle | ❌ No | ✅ Yes |

---

## ✅ Use `Protocol` When…

### 1. Defining Interfaces Across Plugin or Tool Boundaries

Use `Protocol` when you want to define *capabilities* or *contracts* that third-party code or tools will implement **without requiring inheritance**.

```python
from typing import Protocol

class ProtocolValidate(Protocol):
    def validate(self, path: str) -> bool: ...
```

This allows:
- Structural typing (`hasattr()`-style compatibility)
- Lightweight contracts
- Flexible mocking and test fakes

### 2. You Don't Control All Implementations

Use protocols when the implementations may live:
- In user-injected agents
- In external packages
- In plugin discovery registries

---

## ✅ Use `ABC` When…

### 1. You Require Subclassing with Shared Behavior

Use `ABC` when:
- You need to share logic across subclasses.
- You want to enforce inheritance (e.g., internal base node scaffolds).
- You need `@abstractmethod` enforcement and `super()` semantics.

```python
from abc import ABC, abstractmethod

class OmniBaseNode(ABC):
    @abstractmethod
    def execute(self): ...

    def log_metadata(self):
        print(self.__class__.__name__)
```

---

## 👷 Concrete Guidelines

### Tooling Interfaces (e.g., CLI, Stamp, Validate)
→ Use `Protocol`

### Validator and Registry APIs
→ Use `Protocol` for registration, plugin loading, and schema access  
→ Use `ABC` only if subclassing internally (e.g., default error-handling behavior)

### Reducer Interfaces
→ Use `Protocol` unless base classes will provide concrete reducer logic  
→ ABCs allowed for stateful node types later in ONEX

## Protocol-Driven Engines and Registry/Test Harness Exposure

- When implementing a new tool or validator (e.g., the ONEX Metadata Stamper), define all core logic as a Python Protocol (see [docs/protocols.md](./protocols.md)).
- Register protocol-driven engines in the protocol registry to enable dynamic discovery and selection at runtime or via CLI.
- Expose all dependencies (file I/O, ignore pattern sources, etc.) via constructor or fixture injection—never hardcode or use global state.
- Ensure all test harnesses use fixture-injectable engines, supporting both real and in-memory/mock contexts for context-agnostic testing.
- See [docs/testing.md](./testing.md) and [docs/structured_testing.md](./structured_testing.md) for canonical registry and fixture-injection patterns.

---

## 📌 Final Rule of Thumb

> Use `Protocol` for any interface that could be implemented outside the core, and `ABC` when you're implementing a concrete subclass pattern inside it.

---

## 📚 References

- [PEP 544 – Structural Subtyping via Protocols](https://peps.python.org/pep-0544/)
- [Typing Extensions: Protocols](https://typing.readthedocs.io/en/latest/source/protocol.html)
- [abc — Abstract Base Classes](https://docs.python.org/3/library/abc.html)

## Pull Request Template and Enforcement

All contributors must use the canonical pull request template located at `.github/pull_request_template.md` for every PR. This template enforces:
- A summary of the change and its milestone/checklist context
- Explicit type of change (feature, bugfix, docs, refactor, CI)
- Details of changes, testing, and documentation
- Reviewer guidance and issue linkage

**Enforcement:**
- The PR template is auto-populated by GitHub for all new PRs.
- CI and/or pre-commit hooks will check that all PRs use the required headings and structure.
- Any deviation or omission must be justified in the PR and may block merge until resolved.

**Reference:**
- See `.github/pull_request_template.md` for the canonical template.
- See `docs/testing.md#amendment-and-feedback-process` for how to propose changes to the template or enforcement process.

---

## IPC Event Bus Usage and Configuration

The ONEX IPC Event Bus enables protocol-pure, cross-process event-driven communication using Unix domain sockets. This section documents how to configure, use, and troubleshoot the IPC event bus implementation.

### Selecting the Event Bus Implementation

- Use the environment variable `ONEX_EVENT_BUS_TYPE` to select the event bus implementation:
  - `ONEX_EVENT_BUS_TYPE=ipc` — Use the IPC (Unix domain socket) event bus
  - `ONEX_EVENT_BUS_TYPE=inmemory` — Use the in-memory event bus (default)
- The event bus can also be selected programmatically via the `get_event_bus()` factory in `omnibase.protocol.protocol_event_bus`.

### IPC Socket Path Configuration

- The IPC event bus uses a Unix domain socket for inter-process communication.
- The socket path is configured via the `ONEX_IPC_SOCKET` environment variable (default: `/tmp/onex_eventbus.sock`).
- Example:
  ```bash
  export ONEX_EVENT_BUS_TYPE=ipc
  export ONEX_IPC_SOCKET=/tmp/onex_eventbus.sock
  ```

### Error Handling and Reconnection

- The IPC event bus implementation automatically attempts to rebind the socket if it is closed or encounters errors.
- All errors and reconnection attempts are logged as protocol-pure log events (see logs for details).
- If the socket file is stale or cannot be unlinked, a warning is emitted and the bus will retry.
- The event bus uses a thread pool for subscriber dispatch to avoid blocking the main event loop.

### Usage Example

```python
from omnibase.protocol.protocol_event_bus import get_event_bus

# Select IPC event bus via environment variable or explicitly
bus = get_event_bus()

# Publish an event
bus.publish(my_event)

# Subscribe to events
bus.subscribe(my_callback)
```

### Limitations and Notes

- The IPC event bus currently supports only Unix domain sockets (Linux/macOS). Windows support is not implemented.
- For high-throughput or async scenarios, consider extending the implementation to use asyncio or a message queue.
- The event bus interface is future-proofed for JetStream/NATS and other distributed backends.

---
