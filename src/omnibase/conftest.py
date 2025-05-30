# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.407535'
# description: Stamped by PythonHandler
# entrypoint: python://conftest
# hash: e27d392c4180e8aef0f556fc207449fbb80f2f0fb98569e531153e8c4c8c5ad4
# last_modified_at: '2025-05-29T14:13:58.397492+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: conftest.py
# namespace: python://omnibase.conftest
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: e7d36e52-ede3-4f71-a0dd-aea07da0bdd9
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any, List, Optional

import pytest

from omnibase.core.core_error_codes import CoreErrorCode, OnexError

# Import fixture to make it available to tests
from omnibase.fixtures.cli_stamp_fixtures import cli_stamp_dir_fixture  # noqa: F401
from omnibase.fixtures.registry_adapter import MockRegistryAdapter, RegistryAdapter
from omnibase.protocol.protocol_registry import (
    ProtocolRegistry,
    RegistryArtifactInfo,
    RegistryArtifactType,
)
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.nodes.node_registry_node.v1_0_0.node import NodeRegistryNode
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum

UNIT_CONTEXT = 1
INTEGRATION_CONTEXT = 2


class RegistryLoaderContext:
    """
    Context wrapper for registry functionality using shared protocol.

    This provides registry functionality through the shared ProtocolRegistry
    interface without exposing node-specific implementation details.
    """

    def __init__(self, context_type: int, root_path: Optional[Path] = None):
        self.context_type = context_type
        self.root_path = root_path or Path.cwd() / "src" / "omnibase"

        if context_type == UNIT_CONTEXT:
            self._registry: ProtocolRegistry = MockRegistryAdapter()
        else:
            self._registry = RegistryAdapter(root_path=self.root_path, include_wip=True)

    def get_registry(self) -> ProtocolRegistry:
        """Get the registry protocol implementation."""
        return self._registry

    def get_node_by_name(self, name: str) -> RegistryArtifactInfo:
        """Get a node artifact by name."""
        try:
            return self._registry.get_artifact_by_name(name, RegistryArtifactType.NODES)
        except OnexError as e:
            # Convert "Artifact not found" to "Node not found" for backward compatibility
            if "Artifact not found:" in str(e):
                raise OnexError(
                    f"Node not found: {name}", CoreErrorCode.RESOURCE_NOT_FOUND
                ) from e
            raise

    def get_artifacts_by_type(
        self, artifact_type: RegistryArtifactType
    ) -> List[RegistryArtifactInfo]:
        """Get artifacts by type."""
        return self._registry.get_artifacts_by_type(artifact_type)


@pytest.fixture(
    params=[
        pytest.param(UNIT_CONTEXT, id="unit", marks=pytest.mark.mock),
        pytest.param(INTEGRATION_CONTEXT, id="integration", marks=pytest.mark.integration),
    ]
)
def handler_registry(request, event_driven_registry):
    """
    Canonical handler registry fixture for ONEX registry-driven tests.
    Provides the protocol-compliant registry instance for the requested context.
    Context mapping:
      UNIT_CONTEXT = 1 (unit/mock context; in-memory, isolated)
      INTEGRATION_CONTEXT = 2 (integration/real context; real registry, disk-backed, or service-backed)
    Returns:
        ProtocolFileTypeHandlerRegistry: The handler registry instance for the context.
    Raises:
        pytest.skip: If an unknown context is requested (future-proofing).
    """
    event_bus, registry_node = event_driven_registry
    registry = getattr(registry_node, "handler_registry", None)
    if registry is None:
        pytest.skip("NodeRegistryNode does not expose a handler_registry attribute.")
    if request.param == UNIT_CONTEXT:
        return registry  # In-memory, isolated
    elif request.param == INTEGRATION_CONTEXT:
        return registry  # Replace with integration context if available
    else:
        pytest.skip(f"Unknown registry context: {request.param}")


@pytest.fixture(scope="session")
def event_driven_registry():
    """
    Event-driven registry fixture for ONEX tests.
    Starts an in-memory event bus and a Registry Node (NodeRegistryNode) for event-driven handler/node registration.
    Yields (event_bus, registry_node) tuple for use in tests.
    """
    event_bus = InMemoryEventBus()
    registry_node = NodeRegistryNode(event_bus=event_bus)
    yield event_bus, registry_node
