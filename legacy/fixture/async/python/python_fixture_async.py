# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_fixture_async"
# namespace: "omninode.tools.test_python_fixture_async"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:26+00:00"
# last_modified_at: "2025-05-05T13:00:26+00:00"
# entrypoint: "test_python_fixture_async.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTestFixture']
# base_class: ['BaseTestFixture']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Shared async/integration fixture for validator tests.
Fixtures are registry-registered, DI-compliant, and inherit from BaseTestFixture.
"""

import asyncio
from typing import Any

from foundation.script.validate.validate_registry import register_fixture
from foundation.fixture import BaseTestFixture
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture


class EventLoopFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for providing an event loop for async tests."""

    def get_fixture(self) -> asyncio.AbstractEventLoop:
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()


# Example async client fixture (replace with actual client as needed)
class AsyncClientFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for providing an async client (placeholder)."""

    def get_fixture(self) -> Any:
        class DummyAsyncClient:
            async def get(self, url):
                return {"status": "ok", "url": url}

        return DummyAsyncClient()


# Register fixture in the registry
register_fixture(
    name="event_loop_fixture",
    fixture=EventLoopFixture,
    description="Fixture for providing an event loop for async tests",
)
register_fixture(
    name="async_client_fixture",
    fixture=AsyncClientFixture,
    description="Fixture for providing an async client (placeholder)",
)