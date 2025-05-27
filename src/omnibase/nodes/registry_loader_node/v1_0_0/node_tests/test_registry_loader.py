# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_registry_loader.py
# version: 1.0.0
# uuid: 8b6c6b6e-4b4b-4b4b-8b6c-6b6e4b4b4b4b
# author: OmniNode Team
# created_at: 2025-05-23T10:29:04.625488
# last_modified_at: 2025-05-23T17:42:52.030520
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 8b6c6b6e4b4b4b4b8b6c6b6e4b4b4b4b8b6c6b6e4b4b4b4b8b6c6b6e4b4b4b4b
# entrypoint: python@test_registry_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_registry_loader
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Tests for Registry Loader Node.

Tests the registry loading functionality using canonical testing patterns:
- Registry-driven test case discovery
- Fixture injection for test environment setup
- Model-based assertions using Pydantic models and Enums
- Protocol-driven testing (tests public contracts only)
- Context-agnostic test logic (works with mock and integration contexts)

This module tests the registry loader node directly using its input/output
state models and validates the core functionality without external dependencies.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock

import pytest
import yaml

from omnibase.enums import OnexStatus

from ..helpers.registry_engine import RegistryEngine
from ..models.state import (
    ArtifactTypeEnum,
    RegistryLoaderInputState,
    RegistryLoaderOutputState,
)
from ..node import run_registry_loader_node


class TestRegistryLoaderNode:
    """
    Test class for registry_loader_node.

    Tests core functionality using direct state model testing
    following canonical testing patterns.
    """

    def test_registry_loader_basic_functionality(
        self, registry_test_environment: Any
    ) -> None:
        """
        Test basic registry loader functionality with a simple registry.
        """
        # Create simple test data
        test_registry = {
            "nodes": [
                {
                    "name": "test_node",
                    "version": "v1_0_0",
                    "path": "nodes/test_node/v1_0_0",
                }
            ]
        }

        temp_path = registry_test_environment(test_registry)

        input_state = RegistryLoaderInputState(
            version="1.0.0",
            root_directory=str(temp_path / "src" / "omnibase"),
            include_wip=True,
        )

        mock_event_bus = Mock()
        result = run_registry_loader_node(input_state, event_bus=mock_event_bus)

        # Verify the result using model-based assertions
        assert isinstance(result, RegistryLoaderOutputState)
        assert result.version == "1.0.0"
        assert result.status in [OnexStatus.SUCCESS, OnexStatus.WARNING]
        assert result.artifact_count >= 0
        assert len(result.artifacts) == result.artifact_count

        # Verify events were emitted
        assert (
            mock_event_bus.publish.call_count >= 2
        )  # At least START and SUCCESS/FAILURE

    def test_registry_loader_artifact_type_filtering(
        self, registry_test_environment: Any
    ) -> None:
        """
        Test artifact type filtering functionality using enum-based filtering.
        """
        # Create test data with multiple artifact types
        test_registry = {
            "nodes": [
                {
                    "name": "test_node",
                    "version": "v1_0_0",
                    "path": "nodes/test_node/v1_0_0",
                }
            ],
            "cli_tools": [
                {
                    "name": "test_cli",
                    "version": "v1_0_0",
                    "path": "cli_tools/test_cli/v1_0_0",
                }
            ],
        }

        temp_path = registry_test_environment(test_registry)

        # Test filtering to only nodes using enum
        input_state = RegistryLoaderInputState(
            version="1.0.0",
            root_directory=str(temp_path / "src" / "omnibase"),
            artifact_types=[ArtifactTypeEnum.NODES],
        )

        mock_event_bus = Mock()
        result = run_registry_loader_node(input_state, event_bus=mock_event_bus)

        # Should only include nodes - verify using enum comparison
        if result.artifacts:
            # Verify no other types are included
            non_node_artifacts = [
                a for a in result.artifacts if a.artifact_type != ArtifactTypeEnum.NODES
            ]
            assert len(non_node_artifacts) == 0

    def test_registry_loader_wip_handling(self, registry_test_environment: Any) -> None:
        """
        Test WIP artifact handling with include/exclude scenarios.
        """
        # Create test data with WIP artifacts
        test_registry = {
            "nodes": [
                {
                    "name": "test_node",
                    "version": "v1_0_0",
                    "path": "nodes/test_node/v1_0_0",
                }
            ]
        }

        temp_path = registry_test_environment(test_registry)

        # Test excluding WIP artifacts
        input_state = RegistryLoaderInputState(
            version="1.0.0",
            root_directory=str(temp_path / "src" / "omnibase"),
            include_wip=False,
        )

        mock_event_bus = Mock()
        result = run_registry_loader_node(input_state, event_bus=mock_event_bus)

        # Should exclude WIP artifacts
        wip_artifacts = [a for a in result.artifacts if a.is_wip]
        assert len(wip_artifacts) == 0
        assert result.wip_artifact_count == 0

        # Test including WIP artifacts
        input_state.include_wip = True
        result = run_registry_loader_node(input_state, event_bus=mock_event_bus)

        # WIP count should be consistent
        wip_artifacts = [a for a in result.artifacts if a.is_wip]
        assert len(wip_artifacts) == result.wip_artifact_count

    def test_registry_loader_error_scenarios(self) -> None:
        """
        Test various error scenarios and error handling.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test 1: Missing .onextree
            input_state = RegistryLoaderInputState(
                version="1.0.0",
                root_directory=str(temp_path),
            )

            mock_event_bus = Mock()
            result = run_registry_loader_node(input_state, event_bus=mock_event_bus)

            # Verify error status using enum
            assert result.status == OnexStatus.ERROR
            assert "Failed to find .onextree file" in result.message
            assert result.artifact_count == 0

    def test_registry_engine_directly(self) -> None:
        """
        Test the registry engine directly for more granular testing.
        """
        engine = RegistryEngine()

        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = RegistryLoaderInputState(
                version="1.0.0",
                root_directory=str(temp_dir),
            )

            result = engine.load_registry(input_state)

            # Should handle missing registry gracefully
            assert isinstance(result, RegistryLoaderOutputState)
            assert result.status == OnexStatus.ERROR

    def test_registry_loader_state_validation(self) -> None:
        """
        Test input and output state validation.
        """
        # Test valid input state
        input_state = RegistryLoaderInputState(
            version="1.0.0",
            root_directory="/tmp",
        )
        assert input_state.version == "1.0.0"
        assert input_state.include_wip is False  # Default value

        # Test input state with custom values
        input_state = RegistryLoaderInputState(
            version="1.0.0",
            root_directory="/tmp",
            include_wip=True,
            artifact_types=[ArtifactTypeEnum.NODES],
        )
        assert input_state.include_wip is True
        assert input_state.artifact_types is not None
        assert ArtifactTypeEnum.NODES in input_state.artifact_types


@pytest.fixture
def registry_loader_input_state() -> RegistryLoaderInputState:
    """Fixture providing a basic input state for testing."""
    return RegistryLoaderInputState(
        version="1.0.0",
        root_directory="/tmp",
    )


@pytest.fixture
def mock_event_bus() -> Mock:
    """Fixture providing a mock event bus for testing."""
    return Mock()


@pytest.fixture
def registry_test_environment() -> Any:
    """
    Fixture for setting up test registry environments.

    Returns a function that creates a temporary directory with a .onextree
    file and proper directory structure for testing.
    """

    def _setup_environment(registry_data: dict) -> Path:
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)

        # Create the src/omnibase directory structure
        src_dir = temp_path / "src" / "omnibase"
        src_dir.mkdir(parents=True, exist_ok=True)

        # Create artifact directories and metadata files based on registry_data
        for artifact_type, artifacts in registry_data.items():
            if artifact_type in ["nodes", "cli_tools", "runtimes"]:
                type_dir = src_dir / artifact_type
                type_dir.mkdir(parents=True, exist_ok=True)

                for artifact in artifacts:
                    name = artifact["name"]
                    version = artifact["version"]

                    # Create artifact directory
                    artifact_dir = type_dir / name / version
                    artifact_dir.mkdir(parents=True, exist_ok=True)

                    # Create appropriate metadata file
                    if artifact_type == "nodes":
                        metadata_file = artifact_dir / "node.onex.yaml"
                        metadata_content = {
                            "name": name,
                            "version": version,
                            "schema_version": "1.0.0",
                            "description": f"Test {name} node",
                        }
                    elif artifact_type == "cli_tools":
                        metadata_file = artifact_dir / "cli_tool.yaml"
                        metadata_content = {
                            "name": name,
                            "version": version,
                            "schema_version": "1.0.0",
                            "description": f"Test {name} CLI tool",
                        }
                    elif artifact_type == "runtimes":
                        metadata_file = artifact_dir / "runtime.yaml"
                        metadata_content = {
                            "name": name,
                            "version": version,
                            "schema_version": "1.0.0",
                            "description": f"Test {name} runtime",
                        }

                    with open(metadata_file, "w") as f:
                        yaml.dump(metadata_content, f)

        # Create a simple .onextree file
        onextree_content: Dict[str, Any] = {
            "name": "omnibase",
            "type": "directory",
            "children": [],
        }

        # Add artifact type directories to onextree
        for artifact_type, artifacts in registry_data.items():
            if artifact_type in ["nodes", "cli_tools", "runtimes"]:
                type_children = []
                for artifact in artifacts:
                    name = artifact["name"]
                    version = artifact["version"]

                    # Add artifact directory structure
                    artifact_node = {
                        "name": name,
                        "type": "directory",
                        "children": [
                            {
                                "name": version,
                                "type": "directory",
                                "children": [
                                    {
                                        "name": (
                                            f"{artifact_type[:-1]}.onex.yaml"
                                            if artifact_type == "nodes"
                                            else f"{artifact_type[:-1]}.yaml"
                                        ),
                                        "type": "file",
                                        "children": None,
                                    }
                                ],
                            }
                        ],
                    }
                    type_children.append(artifact_node)

                if type_children:
                    type_node = {
                        "name": artifact_type,
                        "type": "directory",
                        "children": type_children,
                    }
                    onextree_content["children"].append(type_node)

        # Write .onextree file in the parent of src/omnibase (so it's found by the resolver)
        # The resolver looks for .onextree in parent directory of root_path
        onextree_file = temp_path / "src" / ".onextree"
        with open(onextree_file, "w") as f:
            yaml.dump(onextree_content, f)

        return temp_path

    return _setup_environment
