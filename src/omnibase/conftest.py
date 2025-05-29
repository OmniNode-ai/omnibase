# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.407535'
# description: Stamped by PythonHandler
# entrypoint: python://conftest.py
# hash: 215abc5372cd2aa70e7b6e398d380c5344e897b03176f7901379d735d4c72b77
# last_modified_at: '2025-05-29T11:50:10.694480+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: conftest.py
# namespace: omnibase.conftest
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

MOCK_CONTEXT = 1
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

        if context_type == MOCK_CONTEXT:
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
        pytest.param(MOCK_CONTEXT, id="mock", marks=pytest.mark.mock),
        pytest.param(
            INTEGRATION_CONTEXT, id="integration", marks=pytest.mark.integration
        ),
    ]
)
def registry_loader_context(request: Any) -> RegistryLoaderContext:
    """
    Modern registry context fixture for ONEX registry-driven tests.

    This fixture provides registry functionality through the shared ProtocolRegistry
    interface, abstracting away node-specific implementation details while enabling
    both mock and integration testing patterns.

    Context mapping:
      MOCK_CONTEXT = 1 (mock context; in-memory, isolated)
      INTEGRATION_CONTEXT = 2 (integration context; real registry, disk-backed)

    Returns:
        RegistryLoaderContext: A context wrapper with shared registry protocol functionality.

    Raises:
        OnexError: If an unknown context is requested.
    """
    if request.param == MOCK_CONTEXT:
        return RegistryLoaderContext(MOCK_CONTEXT)
    elif request.param == INTEGRATION_CONTEXT:
        return RegistryLoaderContext(INTEGRATION_CONTEXT)
    else:
        raise OnexError(
            f"Unknown registry context: {request.param}",
            CoreErrorCode.INVALID_PARAMETER,
        )


# Legacy fixture for backward compatibility during transition
@pytest.fixture(
    params=[
        pytest.param(MOCK_CONTEXT, id="mock", marks=pytest.mark.mock),
        pytest.param(
            INTEGRATION_CONTEXT, id="integration", marks=pytest.mark.integration
        ),
    ]
)
def registry(request: Any) -> RegistryLoaderContext:
    """
    Legacy registry fixture for backward compatibility.

    DEPRECATED: Use registry_loader_context instead.
    This fixture will be removed after all tests are migrated.
    """
    return registry_loader_context(request)
