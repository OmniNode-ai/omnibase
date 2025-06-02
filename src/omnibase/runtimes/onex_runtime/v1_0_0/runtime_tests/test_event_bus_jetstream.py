# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-06-03T00:00:00.000000'
# description: Protocol compliance tests for JetStreamEventBus (integration only)
# entrypoint: python://test_event_bus_jetstream
# hash: <to-be-stamped>
# last_modified_at: '2025-06-03T00:00:00.000000+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_event_bus_jetstream.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.runtime_tests.test_event_bus_jetstream
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: <to-be-generated>
# version: 1.0.0
# === /OmniNode:Metadata ===

"""
Protocol compliance tests for JetStreamEventBus (integration only).
- Tests connect and publish only (subscribe/unsubscribe not yet implemented).
- Requires a running JetStream server at nats://localhost:4222.
- Skips if nats-py is not installed or server is unavailable.
- Follows ONEX canonical test standards (protocol-pure, fixture-injected, strong typing).
"""

import asyncio
import pytest

from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum, OnexEventMetadataModel
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_jetstream import JetStreamEventBus

pytestmark = pytest.mark.integration

JETSTREAM_SERVER = "nats://localhost:4222"


async def is_jetstream_available() -> bool:
    try:
        import nats
        try:
            nc = await nats.connect(JETSTREAM_SERVER, connect_timeout=0.5)
            await nc.close()
            return True
        except Exception:
            return False
    except ImportError:
        return False
    except Exception:
        return False


def make_event(event_type: OnexEventTypeEnum, node_id: str = "test_node") -> OnexEvent:
    return OnexEvent(event_type=event_type, node_id=node_id, metadata=OnexEventMetadataModel())


@pytest.mark.asyncio
async def test_jetstream_event_bus_connect_and_publish():
    if not await is_jetstream_available():
        pytest.skip("JetStream server not available or nats-py not installed.")
    bus = JetStreamEventBus()
    await bus.connect(JETSTREAM_SERVER)
    event = make_event(OnexEventTypeEnum.NODE_START)
    # Should not raise
    await bus.publish(event)
    # No subscribe/unsubscribe tests yet (not implemented) 