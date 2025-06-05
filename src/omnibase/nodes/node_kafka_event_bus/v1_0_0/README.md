# Template Node (ONEX Canonical)

This node implements the canonical ONEX reducer pattern and serves as the reference for all new nodes.

## Key Features
- **Reducer Pattern:** Implements `.run()` and `.bind()` lifecycle. All business logic is delegated to inline handlers or runtime helpers.
- **Introspection:** Standards-compliant introspection via `introspection.py`, exposing node metadata, contract, CLI arguments, capabilities, and scenario registry.
- **Scenario-Driven Validation:** All validation and testing is scenario-driven. Scenarios are defined in `scenarios/index.yaml` and exposed via introspection.
- **Error Codes:** Canonical error codes are defined in `error_codes.py` and exposed via introspection.

## Usage

### CLI Introspection
```bash
python node.py --introspect
```
Prints full node contract, metadata, CLI arguments, and available scenarios as JSON.

### Scenario Discovery
```bash
python node.py --run-scenario <scenario_id>
```
Prints the scenario config for the given scenario ID from the node's scenario registry.

## Usage Modes

### 1. Direct CLI Invocation (Short-lived)

You can invoke the node directly for health checks, scenario runs, or direct input processing. In this mode, the node runs the requested operation and exits.

Example:

```bash
poetry run onex run node_kafka_event_bus --args='{"args": ["--health-check"]}'
```

### 2. Event-Driven (Serve/Daemon) Mode

For event-driven workflows (e.g., using the ONEX CLI to publish events), the node **must be running as a persistent process** that subscribes to the event bus and handles events as they arrive. This is called "serve" or "daemon" mode.

**Important:**
- The event-driven CLI (`poetry run onex run ...`) publishes events to the event bus and expects the node to be running and subscribed.
- If the node is not running in serve mode, CLI commands will hang or time out, as there is no subscriber to handle events.

#### Starting the Node in Serve Mode

```bash
poetry run python -m omnibase.nodes.node_kafka_event_bus.v1_0_0.node --serve
```

Or, if integrated with the ONEX CLI:

```bash
poetry run onex run node_kafka_event_bus --args='["--serve"]'
```

This will start the node as a persistent process, subscribing to the event bus and handling events as they arrive.

## Developer Notes
- Input/output state models are defined in `models/state.py` and must use canonical Pydantic models and Enums.
- All protocol and interface definitions must use the strongest possible typing (see project rules).
- Error codes must be referenced from `error_codes.py` and never hardcoded.
- All scenarios must be registered in `scenarios/index.yaml` and exposed via introspection.

## Naming Standards (Canonical)

All files (except for explicit exceptions below) must be prefixed with the name of their immediate parent directory, using all-lowercase and underscores. This ensures clarity, prevents import collisions, and enables automated enforcement.

**Examples:**
- `tools/input/input_validation_tool.py`
- `tools/output/output_field_tool.py`
- `protocols/input_validation_tool_protocol.py`
- `protocols/output_field_tool_protocol.py`

**Exceptions (do not require prefix):**
- `node.py` (main node entrypoint in versioned node directories)
- `contract.yaml` (canonical contract in versioned node directories)
- `node.onex.yaml` (node metadata in versioned node directories)
- `README.md`, `error_codes.py`, `pytest.ini` (standard project files)
- `state.py` (if always in a `models/` subdir and unambiguous)
- `test_*.py` (test files, by convention)

Any new exceptions must be justified and documented in the standards file.

For authoritative and up-to-date rules, see `.cursor/rules/standards.mdc`.

## References
- See `introspection.py` for the full introspection implementation.
- See `node_kafka_event_bus_milestone1_checklist.md` for milestone requirements.
- See project rules for interface, typing, and testing standards.

## Protocol Compliance and Edge Cases

### Protocol Compliance
- **Event Format & Models:**
  - All events use the canonical `OnexEvent` and `OnexEventMetadataModel` as defined in `model_onex_event.py`.
  - Event bus operations (`publish`, `subscribe`) accept and emit these models only.
- **Protocol Interface:**
  - Implements the `ProtocolEventBus` interface (`publish`, `subscribe`, `unsubscribe`, `clear`, `bus_id`).
  - All public methods and properties are protocol-compliant.
- **State Contract:**
  - Input/output state is defined in `contract.yaml` using canonical models and enums.
  - Required fields: `version`, `status`, `message`, and protocol-compliant output fields.
- **Error Handling:**
  - All errors use project-specific error codes and models.
  - Error events use the `error`, `error_type`, and `error_code` fields in metadata.
- **Event Schema Validation:**
  - All emitted events can be validated using the canonical ONEX event schema validator.

### Edge Cases
- **Degraded Mode:**
  - If the Kafka broker is unavailable, the node falls back to `InMemoryEventBus` for local event delivery.
  - All events remain protocol-compliant, but are not persisted or delivered cross-process.
- **Async/Sync Bridging:**
  - The Kafka event bus currently wraps synchronous Kafka client calls in async methods as a temporary bridge until full async support is implemented.
- **Health Check, Bootstrap, and Introspection:**
  - All emit events/results using canonical models and are protocol-compliant.

### Notes
- All protocol compliance and edge case handling is covered by automated tests and schema validation.
- Any future changes to protocol or event schema should be reflected in this documentation and validated by the test suite.

## Configuration

- Configure the node by providing a `KafkaEventBusConfigModel` via state or contract.
- Required fields: `bootstrap_servers`, `topics`.
- Optional fields: `security_protocol`, `sasl_mechanism`, `sasl_username`, `sasl_password`, `client_id`, `group_id`, `partitions`, `replication_factor`, `acks`, `enable_auto_commit`, `auto_offset_reset`.

## Event Replay Policy

The Kafka Event Bus Node implements a clear policy for handling missed or lost messages and reconnection scenarios:

- **Offset Management:**
  - The node uses the `auto_offset_reset` configuration (default: `earliest`) to determine where to start consuming if no committed offset is found for the group.
  - If `enable_auto_commit` is enabled (default: true), offsets are committed automatically after message processing. This provides at-least-once delivery semantics.
  - If the node is restarted or reconnects, it will resume from the last committed offset. If no offset is committed, it will use the `auto_offset_reset` policy.

- **Missed/Lost Messages:**
  - If the node is offline or disconnected, any messages published to the topic during that time will be delivered upon reconnection, subject to broker retention policies and committed offsets.
  - If messages are deleted from the topic due to retention before the node reconnects, those messages are lost and cannot be replayed.

- **Replay Limitations:**
  - In-memory (degraded) mode does not support replay or persistence. All events are ephemeral and lost on process exit.
  - The node does not implement custom replay logic; replay is managed by Kafka offsets and broker retention.

- **User Responsibilities:**
  - Users are responsible for configuring appropriate `retention.ms` and `auto_offset_reset` values in Kafka to ensure desired replay behavior.
  - For strict delivery guarantees, ensure `enable_auto_commit` is set appropriately and monitor consumer group lag.

- **Caveats:**
  - The node does not currently support explicit replay commands or manual offset management via the CLI.
  - For advanced replay or recovery scenarios, use Kafka tooling or extend the node as needed.

**Summary:**
The node provides at-least-once delivery semantics by default, with replay governed by Kafka's offset and retention configuration. No replay is possible in in-memory mode. See the contract and config model for all relevant options.

## Running with a Real Kafka Broker (Local/CI)

To validate the Kafka Event Bus Node in non-degraded mode, you must run it against a real Kafka broker. The following guide provides a canonical setup for both local development and CI environments.

### 1. Start a Local Kafka Broker (Docker Compose)

Create a file named `docker-compose.kafka.yml` in your project root with the following contents:

```yaml
version: '3.7'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"
  kafka:
    image: confluentinc/cp-kafka:7.4.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
```

Start the broker:

```bash
docker-compose -f docker-compose.kafka.yml up -d
```

### 2. Run the Node and CLI in Real-Broker Mode

Set the required environment variable or CLI flag to use Kafka:

```bash
export ONEX_EVENT_BUS_TYPE=kafka
# or use --event-bus-type kafka with the CLI
```

Run the node in serve mode (persistent process):

```bash
poetry run onex run node_kafka_event_bus --args='["--serve"]' --event-bus-type kafka
```

In a separate terminal, publish an event or run a scenario via the CLI:

```bash
poetry run onex run node_kafka_event_bus --args='{"args": ["--health-check"]}' --event-bus-type kafka
```

### 3. Verify End-to-End Event Flow

- The node should log successful connection to Kafka and process events as expected.
- CLI output should show event-driven results (not fallback/in-memory warnings).
- You can inspect Kafka topics and consumer groups using standard Kafka CLI tools if needed.

### 4. Troubleshooting

- **Port Conflicts:** Ensure ports 2181 (ZooKeeper) and 9092 (Kafka) are free.
- **Dependency Issues:** If you see errors about missing Kafka dependencies, ensure `confluent-kafka` or `aiokafka` is installed in your environment.
- **Connection Errors:** Check Docker logs (`docker-compose logs kafka`) for broker startup issues.
- **Fallback Warnings:** If the CLI or node falls back to in-memory mode, check that `ONEX_EVENT_BUS_TYPE` is set and Kafka is reachable at `localhost:9092`.

### 5. CI Integration

- Add the above Docker Compose service to your CI pipeline before running integration tests.
- Use the same environment variable or CLI flag to ensure tests run against the real broker.

---

This process ensures the node is validated in a real Kafka environment, as required by the milestone checklist. For advanced broker configuration, see the Kafka documentation or extend the Docker Compose file as needed.

## Migration Notes

- This node replaces JetStream/ZMQ event bus implementations.
- All event payloads and types are protocol-agnostic and compatible with existing ONEX event consumers.
