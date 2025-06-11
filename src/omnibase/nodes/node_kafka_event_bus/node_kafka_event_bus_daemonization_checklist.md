# Kafka Node Daemonization & Async Context Manager Migration Checklist

> This checklist tracks all work required to ensure the Kafka node operates as a long-running daemon/service, with all Kafka I/O managed by a dedicated async context manager. The CLI and other tools must only emit events to the event bus, never instantiate Kafka clients directly. All steps must be completed for full standards compliance and maintainability.

---

## 1. Serve/Daemon Mode as Canonical Pattern
- [x] Ensure the Kafka node is always run in `--serve` (daemon/service) mode for all Kafka I/O.
- [x] Document serve/daemon mode as the canonical pattern in the README and developer docs.
- [x] Remove or deprecate any direct CLI invocation patterns that instantiate Kafka clients.

> **Batch One Complete:** All tasks in Step 1 are now enforced in code and documentation.

## 2. CLI/Tool Refactor & Dedicated Async Context Manager
- [x] Audit all CLI and tool code for any direct instantiation of Kafka clients (`AIOKafkaProducer`, `AIOKafkaConsumer`).
- [x] Refactor any such code to emit events to the event bus protocol instead.
- [x] Ensure all CLI/tools use the event bus abstraction and never touch Kafka directly.
- [x] Implement a dedicated async context manager in the Kafka node for all Kafka I/O.
- [x] Ensure the context manager handles full lifecycle: initialization, active state, shutdown, and cleanup.
- [x] Expose safe, protocol-driven request/response interfaces for other components (e.g., CLI, other nodes).
- [x] Optionally, provide health checks, metrics, and error reporting from the context manager.

> **Step 2 Complete:** KafkaEventBusContextManager is protocol-abstracted and in its own file. All CLI/tools are event bus protocol-only.

## 3. Lifecycle Logging
- [x] Add detailed logging for the full lifecycle of producer and consumer objects:
    - Initialization
    - Connection
    - Message send/receive
    - Shutdown/cleanup
- [x] Ensure all log events use canonical log levels and context fields
- [x] Use structured log events for all lifecycle transitions.

> **Step 3 Complete:** All lifecycle transitions for producer/consumer are now logged with canonical log levels and context fields.

## 4. Documentation
- [x] Update the root and versioned README(s) to document:
    - Daemon/service operation as canonical
    - Async context manager responsibilities
    - Protocol-pure event bus usage for all CLI/tools
    - Any known edge cases or shutdown quirks

## 5. Scenario/Test Coverage
- [x] Add or update scenarios to cover:
    - Daemon/serve mode operation
    - Async context manager lifecycle (explicit scenario now present and passing)
    - CLI/tool event bus protocol compliance
    - Error handling (malformed events, missing fields, invalid config)
    - Registry integration and backend selection
    - Multi-subscriber and async handler edge cases
- [x] Ensure all tests use the event bus protocol and never instantiate Kafka clients directly.

> **Step 5 Complete:** All scenario-driven tests, including explicit coverage for the async context manager lifecycle and logging, are present and passing. Coverage is now comprehensive for daemonization, async context management, and protocol compliance.

## 6. Migration & Validation
- [ ] Run and pass all tests (mock, integration, regression) in daemon/serve mode.
- [ ] Validate protocol compliance and standards using the parity validator node.
- [ ] Document any deviations or open questions in the README and migration checklist.

---

**All items must be checked and justified before the Kafka node is considered fully daemonized and context-managed.** 