# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: conftest.py
# version: 1.0.0
# uuid: dc826cdb-2382-497b-9f59-75bbf0a099b5
# author: OmniNode Team
# created_at: 2025-05-22T15:06:55.021877
# last_modified_at: 2025-05-22T20:03:53.602626
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 6748481d882ad291660959388529702450c8c82a337ab4034aa80ef494cb2945
# entrypoint: python@conftest.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.conftest
# meta_type: tool
# === /OmniNode:Metadata ===


import logging
from typing import Any

import pytest

from omnibase.core.core_registry import SchemaRegistry  # type: ignore[import-untyped]
from omnibase.protocol.protocol_registry import (
    ProtocolRegistry,  # type: ignore[import-untyped]
)

# Import fixture to make it available to tests
from tests.fixtures.cli_stamp_fixtures import cli_stamp_dir_fixture  # noqa: F401

logging.basicConfig(level=logging.DEBUG)

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
def registry(request: Any) -> ProtocolRegistry:
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
