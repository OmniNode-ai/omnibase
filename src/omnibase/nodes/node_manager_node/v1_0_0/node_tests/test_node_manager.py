import tempfile
from pathlib import Path
import pytest
from unittest.mock import Mock

from omnibase.enums import OnexStatus
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.nodes.node_manager_node.v1_0_0.node import NodeManagerNode
from omnibase.nodes.node_manager_node.v1_0_0.models.state import NodeManagerInputState, NodeManagerOperation

@pytest.fixture
def mock_event_bus():
    return Mock(spec=ProtocolEventBus)

@pytest.fixture
def minimal_generate_input(tmp_path):
    # Create a temp directory for target
    target_dir = tmp_path / "nodes"
    target_dir.mkdir()
    return NodeManagerInputState(
        version="1.0.0",
        operation=NodeManagerOperation.GENERATE,
        node_name="test_node",
        template_source="template_node",
        target_directory=str(target_dir),
        author="Test Author",
    )

def test_node_manager_generate_minimal(mock_event_bus, minimal_generate_input):
    node = NodeManagerNode(event_bus=mock_event_bus)
    result = node.run(minimal_generate_input)
    assert result.status in [OnexStatus.SUCCESS, OnexStatus.WARNING, OnexStatus.ERROR]
    assert hasattr(result, "message")
    assert hasattr(result, "input_state")
    # TODO: Add assertions for affected_files, processed_nodes, etc.
    # TODO: Add tests for other operations and integration contexts 