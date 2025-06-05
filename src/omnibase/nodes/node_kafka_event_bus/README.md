# Kafka Event Bus Node (ONEX)

The **Kafka Event Bus Node** is a core component of the ONEX ecosystem, providing protocol-compliant, event-driven communication using Apache Kafka. It enables nodes to publish, subscribe, and process events asynchronously, supporting scalable workflows and robust integration patterns.

## What Does This Node Do?
- Implements the ONEX event bus contract using Kafka as the backend.
- Supports both direct (CLI) and event-driven (daemon/serve) operation modes.
- Provides standards-compliant introspection, health checks, and scenario-driven validation.
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

### Running the Node
- **Direct CLI Invocation:**
  ```bash
  poetry run onex run node_kafka_event_bus --args='{"args": ["--health-check"]}'
  ```
- **Event-Driven (Serve/Daemon) Mode:**
  ```bash
  poetry run onex run node_kafka_event_bus --args='["--serve"]'
  ```
  The node must be running in serve mode to process events from the event bus.

## Configuration & Integration
- Configuration is provided via the node's state or contract (see `contract.yaml` and config models).
- **Required fields:** `bootstrap_servers`, `topics`
- **Optional fields:** `security_protocol`, `sasl_mechanism`, `sasl_username`, `sasl_password`, `client_id`, `group_id`, `partitions`, `replication_factor`, `acks`, `enable_auto_commit`, `auto_offset_reset`
- See the versioned README and contract for full details.

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