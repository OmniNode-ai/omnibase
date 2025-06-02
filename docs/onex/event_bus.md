# ONEX Event Bus Subject Naming Convention

## Overview

ONEX event buses (ZMQ, JetStream/NATS, in-memory) use a protocol-pure event model. For JetStream/NATS, each event is published to a subject (topic) constructed from the event's type, following a canonical naming convention.

## Subject Naming Convention

- All events are published to subjects of the form:
  
  `onex.events.<event_type>`

- The subject prefix (`onex.events`) is configurable via environment variable `ONEX_EVENT_BUS_SUBJECT_PREFIX` or config dict.
- The `<event_type>` is taken from the `event_type` field of the `OnexEvent` model (e.g., `node_announce`, `log`, etc.).
- Example subjects:
  - `onex.events.node_announce`
  - `onex.events.log`
  - `onex.events.schema_update`

- Subscribers can use NATS wildcards, e.g.:
  - `onex.events.*` (all events)
  - `onex.events.node_announce` (only node announcements)

## Rationale

- This pattern is directly inspired by the ZMQ event bus, which used the `event_type` field for routing at the application level.
- JetStream/NATS requires explicit subject strings; this mapping preserves protocol-purity and enables fine-grained subscription.
- The convention is future-proof and allows for additional granularity (e.g., `onex.events.<event_type>.<node_id>`) if needed.

## Configuration

- Set the subject prefix via environment variable:
  
  ```bash
  export ONEX_EVENT_BUS_SUBJECT_PREFIX="onex.events"
  ```
- Or pass `{"subject_prefix": "onex.events"}` in the JetStreamEventBus config dict.

- Set the NATS server URL via environment variable:
  
  ```bash
  export ONEX_EVENT_BUS_NATS_URL="nats://localhost:4222"
  ```
Or pass `{"nats_url": "nats://localhost:4222"}` in the JetStreamEventBus config dict.

Or instantiate a config model explicitly:

```python
from omnibase.model.model_handler_config import JetStreamEventBusConfigModel

config = JetStreamEventBusConfigModel(
    subject_prefix="onex.events",
    nats_url="nats://localhost:4222"
)
```

## Example (Python)

```python
# Instantiating JetStreamEventBus with config model
from omnibase.model.model_handler_config import JetStreamEventBusConfigModel
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_jetstream import JetStreamEventBus

config = JetStreamEventBusConfigModel(
    subject_prefix="onex.events",
    nats_url="nats://localhost:4222"
)
event_bus = JetStreamEventBus(config=config)
await event_bus.connect()

# Publishing an event
subject = f"onex.events.{event.event_type}"
await event_bus._js.publish(subject, event.model_dump_json().encode())

# Subscribing to all events (not yet implemented)
# await event_bus.subscribe(callback, subject="onex.events.*")
```

## Migration from ZMQ

- ZMQ used a broadcast pattern; all events were sent to all subscribers, who filtered by `event_type`.
- JetStream/NATS uses subject-based routing, but the event_type-based pattern is preserved in the subject string.
- No application logic changes are required for event_type-based filtering; only the subject string is now explicit.

## See Also
- [src/omnibase/runtimes/onex_runtime/v1_0_0/events/event_bus_jetstream.py](../../src/omnibase/runtimes/onex_runtime/v1_0_0/events/event_bus_jetstream.py)
- [src/omnibase/runtimes/onex_runtime/v1_0_0/events/event_bus_zmq.py](../../src/omnibase/runtimes/onex_runtime/v1_0_0/events/event_bus_zmq.py) 