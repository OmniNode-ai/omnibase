import pytest
from pathlib import Path
from typing import Any, List, Optional

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.fixtures.registry_adapter import MockRegistryAdapter, RegistryAdapter
from omnibase.protocol.protocol_registry import (
    ProtocolRegistry,
    RegistryArtifactInfo,
    RegistryArtifactType,
)

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
def registry_loader_context(request):
    """
    Canonical registry loader context fixture for ONEX registry-driven tests.
    Provides the RegistryLoaderContext instance for the requested context.
    Context mapping:
      UNIT_CONTEXT = 1 (unit/mock context; in-memory, isolated)
      INTEGRATION_CONTEXT = 2 (integration/real context; real registry, disk-backed)
    Returns:
        RegistryLoaderContext: The registry loader context instance for the context.
    """
    return RegistryLoaderContext(request.param)


@pytest.fixture(scope="session")
def protocol_event_bus():
    """
    Canonical protocol-pure event bus fixture for all tests requiring emit_log_event.
    Use this fixture in any test that calls emit_log_event or requires protocol-pure logging.
    """
    from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
    yield InMemoryEventBus() 