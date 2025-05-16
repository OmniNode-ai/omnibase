import pytest

from omnibase.core.core_registry import SchemaRegistry
from omnibase.protocol.protocol_registry import ProtocolRegistry

UNIT_CONTEXT = 1
INTEGRATION_CONTEXT = 2


@pytest.fixture(
    params=[
        pytest.param(UNIT_CONTEXT, id="unit", marks=pytest.mark.mock),
        pytest.param(
            INTEGRATION_CONTEXT, id="integration", marks=pytest.mark.integration
        ),
    ]
)
def registry(request) -> ProtocolRegistry:
    """
    Canonical registry-swapping fixture for ONEX registry-driven tests.

    Context mapping:
      UNIT_CONTEXT = 1 (unit/mock context; in-memory, isolated)
      INTEGRATION_CONTEXT = 2 (integration/real context; real registry, disk-backed, or service-backed)

    - "unit" is synonymous with "mock context" in this system.
    - "integration" is synonymous with "real context."
    - IDs are for human-readable test output; markers are for CI tier filtering.

    Returns:
        ProtocolRegistry: A SchemaRegistry instance in the appropriate context.

    Raises:
        ValueError: If an unknown context is requested (future-proofing).
    """
    if request.param == UNIT_CONTEXT:
        return SchemaRegistry.load_mock()
    elif request.param == INTEGRATION_CONTEXT:
        return SchemaRegistry.load_from_disk()
    else:
        raise ValueError(f"Unknown registry context: {request.param}")
