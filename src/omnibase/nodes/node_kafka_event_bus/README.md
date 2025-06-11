# Kafka Event Bus Node (ONEX)

> **⚠️ WARNING:**
> The Kafka node must be run in daemon/service mode using `--serve` for all Kafka I/O. Direct CLI invocation is not supported for Kafka-backed operation. See the daemonization checklist and versioned README for migration and implementation details.

The **Kafka Event Bus Node** is a core component of the ONEX ecosystem, providing protocol-compliant, event-driven communication using Apache Kafka. It enables nodes to publish, subscribe, and process events asynchronously, supporting scalable workflows and robust integration patterns.

## What Does This Node Do?
- Implements the ONEX event bus contract using Kafka as the backend.
- **Must be run in daemon/service mode (`--serve`) for all Kafka I/O.**
- Supports standards-compliant introspection, health checks, and scenario-driven validation.
- Falls back to in-memory event bus for degraded operation if Kafka is unavailable.

## How to Use & Introspect

### Discover and Introspect with ONEX CLI
```bash
# List all available nodes
poetry run onex list-nodes

# Get detailed info about the Kafka node
poetry run onex node-info node_kafka_event_bus

# Introspect the node (shows contract, CLI args, scenarios, etc.)
poetry run onex run node_kafka_event_bus --introspect
```

### Running the Node (Daemon/Service Mode Required)
- **Daemon/Service Mode (REQUIRED):**
  ```bash
  poetry run onex run node_kafka_event_bus --args='["--serve"]'
  ```
  The node must be running in serve mode to process events from the event bus. Direct CLI invocation is not supported for Kafka I/O.

- **Event-Driven CLI Usage:**
  - All CLI and tool commands must emit events to the event bus; they must not instantiate Kafka clients directly.
  - See the daemonization checklist for migration and implementation details.

## Configuration & Integration
- Configuration is provided via the node's state or contract (see `contract.yaml` and config models).
- **Required fields:** `bootstrap_servers`, `topics`
- **Optional fields:** `security_protocol`, `sasl_mechanism`, `sasl_username`, `sasl_password`, `client_id`, `group_id`, `partitions`, `replication_factor`, `acks`, `enable_auto_commit`, `auto_offset_reset`
- See the versioned README and contract for full details.

## Async Context Manager: Design & Usage

### KafkaEventBusContextManager

#### Rationale
The KafkaEventBusContextManager provides a robust, canonical async context manager for all Kafka I/O in the ONEX Kafka node. It ensures:
- Proper initialization and shutdown of Kafka producers/consumers
- Structured lifecycle logging
- No resource leaks or unclosed warnings
- All Kafka I/O is managed by the node, never by CLI/tools
- Protocol abstraction for extensibility and testability

#### Lifecycle
- `__init__`: Logs initialization of the context manager (producer/consumer not yet connected)
- `__aenter__`: Logs connection start, successful connection, and current state of producer/consumer
- `__aexit__`: Logs shutdown start, successful shutdown, and post-cleanup state
- All log events use canonical log levels and context fields for observability

#### Logging & Observability
- Every lifecycle transition (init, connect, message send/receive, shutdown, cleanup) is logged using `emit_log_event_sync`
- Log levels follow ONEX standards (`INFO` for transitions, `DEBUG` for state details)
- All logs include canonical context fields (e.g., node_id)
- This enables full traceability and troubleshooting for all Kafka resource management

#### Protocol Abstraction
- The context manager implements the `ProtocolEventBusContextManager` protocol
- This allows for type-safe, extensible, and testable event bus context management
- All usage should depend on the protocol, not the concrete class, for maximum flexibility

#### Usage Example
```python
async with KafkaEventBusContextManager(config) as bus:
    await bus.publish(...)
    # ... consume, process, etc. ...
```

#### Checklist Compliance
- All requirements for daemonization, CLI/tool refactor, async context management, and lifecycle logging are now complete and documented
- See `node_kafka_event_bus_daemonization_checklist.md` for full migration status

#### Integration Notes
- Only the Kafka node should instantiate this context manager
- CLI/tools must use the event bus protocol, never direct Kafka clients
- All lifecycle events are logged for observability
- See `tool_kafka_event_bus.py` and `kafka_event_bus_context_manager.py` for implementation

#### Maintenance
- Update this doc if the context manager interface, protocol, or logging changes
- Ensure all new Kafka I/O logic uses this pattern

## Protocol & Standards Compliance
- Fully implements the ONEX event bus protocol and contract.
- All public interfaces use strong typing and canonical models/enums.
- Compliance can be validated using the parity validator node:
  ```bash
  poetry run onex run parity_validator_node --args='["--nodes-directory", "src/omnibase/nodes/node_kafka_event_bus"]'
  ```

## Versioning & Directory Structure
- Each version of the node lives in its own subdirectory (e.g., `v1_0_0/`).
- This root README provides a high-level overview; see the versioned README(s) for implementation details, developer notes, and version-specific configuration.
- To select a specific version, use the ONEX CLI with the `--version` flag:
  ```bash
  poetry run onex run node_kafka_event_bus --version v1_0_0
  ```

## Migration & Upgrade Notes
- This node supersedes previous event bus implementations (e.g., JetStream, ZMQ).
- All event payloads and types are protocol-agnostic and compatible with ONEX consumers.

## Further Reading & References
- [Versioned README](./v1_0_0/README.md) – Implementation and developer details for v1.0.0
- [Contract](./v1_0_0/contract.yaml) – Canonical state and config contract
- [Introspection](./v1_0_0/introspection.py) – Standards-compliant introspection implementation
- [ONEX Project Standards](../../../docs/standards.md)
- [ONEX CLI Guide](../../../docs/guides/cli/)

## Support & Contribution
- Maintained by the OmniNode/ONEX team. For issues or contributions, see the main project [README](../../../README.md) and contribution guidelines.

---

*For implementation details, advanced configuration, and developer notes, always refer to the versioned README in the appropriate subdirectory.* 