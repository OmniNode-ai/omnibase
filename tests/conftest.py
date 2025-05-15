import pytest
from omnibase.core.core_registry import SchemaRegistry
from omnibase.protocol.protocol_registry import ProtocolRegistry

@pytest.fixture(params=["mock", "real"])
def registry(request) -> ProtocolRegistry:
    """
    Registry-swapping fixture for ONEX registry-driven tests.
    Returns a SchemaRegistry in either mock or real mode, typed as ProtocolRegistry.
    """
    if request.param == "mock":
        return SchemaRegistry.load_mock()
    return SchemaRegistry.load_from_disk() 