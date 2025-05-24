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
import sys
from pathlib import Path
from typing import Any, List, Optional

import pytest

# Add registry loader node to path for importing
sys.path.insert(
    0, str(Path(__file__).parent / "nodes" / "registry_loader_node" / "v1_0_0")
)

# Import fixture to make it available to tests
from omnibase.fixtures.cli_stamp_fixtures import cli_stamp_dir_fixture  # noqa: F401
from omnibase.model.enum_onex_status import OnexStatus

# Import registry loader node components
from omnibase.nodes.registry_loader_node.v1_0_0.models.state import (
    ArtifactTypeEnum,
    RegistryArtifact,
    RegistryLoaderInputState,
    RegistryLoaderOutputState,
)
from omnibase.nodes.registry_loader_node.v1_0_0.node import run_registry_loader_node

logging.basicConfig(level=logging.DEBUG)

MOCK_CONTEXT = 1
INTEGRATION_CONTEXT = 2


class RegistryLoaderContext:
    """
    Context wrapper for registry loader node functionality.

    This replaces the old ProtocolRegistry interface with direct usage
    of the registry loader node input/output state models.
    """

    def __init__(self, context_type: int, root_path: Optional[Path] = None):
        self.context_type = context_type
        self.root_path = root_path or Path.cwd() / "src" / "omnibase"
        self._output_state: Optional[RegistryLoaderOutputState] = None

        if context_type == MOCK_CONTEXT:
            self._create_mock_output()
        else:
            self._load_real_registry()

    def _create_mock_output(self) -> None:
        """Create mock registry output for testing."""
        # Create mock artifacts
        mock_artifacts = [
            RegistryArtifact(
                name="stamper_node",
                version="v1_0_0",
                artifact_type=ArtifactTypeEnum.NODES,
                path="/mock/path/stamper_node",
                metadata={
                    "name": "stamper_node",
                    "version": "v1_0_0",
                    "description": "Mock stamper node for testing",
                },
                is_wip=False,
            ),
            RegistryArtifact(
                name="example_node_id",
                version="v1_0_0",
                artifact_type=ArtifactTypeEnum.NODES,
                path="/mock/path/example_node_id",
                metadata={
                    "name": "example_node_id",
                    "version": "v1_0_0",
                    "description": "Mock example node for testing",
                },
                is_wip=False,
            ),
        ]

        self._output_state = RegistryLoaderOutputState(
            version="1.0.0",
            status=OnexStatus.SUCCESS,
            message="Mock registry loaded successfully",
            root_directory=str(self.root_path),
            artifacts=mock_artifacts,
            artifact_count=len(mock_artifacts),
            valid_artifact_count=len(mock_artifacts),
            invalid_artifact_count=0,
            wip_artifact_count=0,
            artifact_types_found=[ArtifactTypeEnum.NODES],
            errors=[],
        )

    def _load_real_registry(self) -> None:
        """Load real registry using registry loader node."""
        input_state = RegistryLoaderInputState(
            version="1.0.0", root_directory=str(self.root_path), include_wip=True
        )

        self._output_state = run_registry_loader_node(input_state)

    def get_output_state(self) -> RegistryLoaderOutputState:
        """Get the registry loader output state."""
        assert self._output_state is not None, "Output state not initialized"
        return self._output_state

    def get_node_by_name(self, name: str) -> RegistryArtifact:
        """Get a node artifact by name."""
        assert self._output_state is not None, "Output state not initialized"
        for artifact in self._output_state.artifacts:
            if (
                artifact.name == name
                and artifact.artifact_type == ArtifactTypeEnum.NODES
            ):
                return artifact
        raise ValueError(f"Node not found: {name}")

    def get_artifacts_by_type(
        self, artifact_type: ArtifactTypeEnum
    ) -> List[RegistryArtifact]:
        """Get artifacts by type."""
        assert self._output_state is not None, "Output state not initialized"
        return [
            a for a in self._output_state.artifacts if a.artifact_type == artifact_type
        ]


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
    Modern registry loader context fixture for ONEX registry-driven tests.

    This fixture provides direct access to registry loader node functionality
    without the old ProtocolRegistry interface layer.

    Context mapping:
      MOCK_CONTEXT = 1 (mock context; in-memory, isolated)
      INTEGRATION_CONTEXT = 2 (integration context; real registry, disk-backed)

    Returns:
        RegistryLoaderContext: A context wrapper with registry loader functionality.

    Raises:
        ValueError: If an unknown context is requested.
    """
    if request.param == MOCK_CONTEXT:
        return RegistryLoaderContext(MOCK_CONTEXT)
    elif request.param == INTEGRATION_CONTEXT:
        return RegistryLoaderContext(INTEGRATION_CONTEXT)
    else:
        raise ValueError(f"Unknown registry context: {request.param}")


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
