# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_tree_generator.py
# version: 1.0.0
# uuid: 3f3d565e-11fe-4179-9fc1-180db9203367
# author: OmniNode Team
# created_at: 2025-05-24T09:36:56.350866
# last_modified_at: 2025-05-24T14:41:28.999909
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: b7f4d7dad1afd3bd5dd3621fbcf2cb8a38378474a17ee32368424b5a9b4dd7b9
# entrypoint: python@test_tree_generator.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_tree_generator
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Test suite for tree_generator_node.

Tests the functionality of generating .onextree manifest files from directory structure analysis.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from ..models.state import TreeGeneratorInputState, TreeGeneratorOutputState
from ..node import run_tree_generator_node


class TestTreeGeneratorNode:
    """Test class for tree_generator_node functionality."""

    def test_tree_generator_node_success(self) -> None:
        """Test successful execution of tree_generator_node."""
        # Create a temporary directory structure for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a simple directory structure
            (temp_path / "test_file.txt").write_text("test content")
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "nested_file.py").write_text("# test python file")

            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=str(temp_path),
                output_path=str(temp_path / ".onextree"),
            )

            mock_event_bus = Mock()

            result = run_tree_generator_node(input_state, event_bus=mock_event_bus)

            assert isinstance(result, TreeGeneratorOutputState)
            assert result.version == "1.0.0"
            assert result.status == "success"
            assert "Tree generation completed successfully" in result.message
            assert result.artifacts_discovered is not None
            assert result.validation_results is not None

            # Verify events were emitted
            assert mock_event_bus.publish.call_count == 2  # START and SUCCESS

    def test_tree_generator_node_with_nonexistent_directory(self) -> None:
        """Test tree_generator_node with nonexistent root directory."""
        input_state = TreeGeneratorInputState(
            version="1.0.0",
            root_directory="/nonexistent/path",
            output_path="/tmp/.onextree",
        )

        mock_event_bus = Mock()

        result = run_tree_generator_node(input_state, event_bus=mock_event_bus)

        # Should handle gracefully and return error status
        assert isinstance(result, TreeGeneratorOutputState)
        assert result.status == "error"
        assert "does not exist" in result.message.lower()

    def test_tree_generator_node_minimal_input(self) -> None:
        """Test tree_generator_node with minimal required input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=temp_dir,
                # output_path uses default value
            )

            mock_event_bus = Mock()

            result = run_tree_generator_node(input_state, event_bus=mock_event_bus)

            assert isinstance(result, TreeGeneratorOutputState)
            assert result.status in ["success", "error"]  # Depends on directory content
            assert result.artifacts_discovered is not None

    def test_tree_generator_node_state_validation(self) -> None:
        """Test input state validation."""
        # Test missing required field
        with pytest.raises(ValueError):  # Pydantic validation error
            TreeGeneratorInputState(
                version="1.0.0"
                # Missing required field: root_directory
            )

    def test_tree_generator_node_output_state_structure(self) -> None:
        """Test output state structure and validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = TreeGeneratorInputState(
                version="1.0.0", root_directory=temp_dir
            )

            mock_event_bus = Mock()

            result = run_tree_generator_node(input_state, event_bus=mock_event_bus)

            # Test output state structure
            assert hasattr(result, "version")
            assert hasattr(result, "status")
            assert hasattr(result, "message")
            assert hasattr(result, "artifacts_discovered")
            assert hasattr(result, "validation_results")

            # Test that output can be serialized
            json_output = result.model_dump_json()
            assert isinstance(json_output, str)
            assert len(json_output) > 0


class TestTreeGeneratorNodeIntegration:
    """Integration tests for tree_generator_node."""

    def test_tree_generator_node_with_real_structure(self) -> None:
        """Test tree_generator_node with a realistic directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a structure similar to ONEX nodes
            nodes_dir = temp_path / "nodes" / "test_node" / "v1_0_0"
            nodes_dir.mkdir(parents=True)

            # Create node metadata file
            (nodes_dir / "node.onex.yaml").write_text(
                """
schema_version: "0.1.0"
name: "test_node"
version: "1.0.0"
uuid: "test-uuid"
author: "Test Author"
created_at: "2025-01-24T00:00:00.000000"
last_modified_at: "2025-01-24T00:00:00.000000"
description: "Test node"
state_contract: "state_contract://test"
lifecycle: "active"
hash: "test-hash"
entrypoint:
  type: python
  target: node.py
namespace: "test.nodes.test_node"
meta_type: "tool"
"""
            )

            (nodes_dir / "node.py").write_text("# Test node implementation")

            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=str(temp_path),
                output_path=str(temp_path / ".onextree"),
            )

            mock_event_bus = Mock()

            result = run_tree_generator_node(input_state, event_bus=mock_event_bus)

            assert isinstance(result, TreeGeneratorOutputState)
            assert result.status == "success"
            # Should find at least the test node
            if result.artifacts_discovered:
                total_artifacts = sum(result.artifacts_discovered.values())
                assert total_artifacts >= 1

            # Verify .onextree file was created
            onextree_path = temp_path / ".onextree"
            assert onextree_path.exists()


# Test fixtures
@pytest.fixture
def tree_generator_input_state() -> TreeGeneratorInputState:
    """Fixture for common input state."""
    return TreeGeneratorInputState(
        version="1.0.0", root_directory="/tmp/test", output_path="/tmp/.onextree"
    )


@pytest.fixture
def mock_event_bus() -> Mock:
    """Fixture for mock event bus."""
    return Mock()
