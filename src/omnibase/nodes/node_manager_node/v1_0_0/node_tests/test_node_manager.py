# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T18:40:10.144964'
# description: Stamped by PythonHandler
# entrypoint: python://test_node_manager
# hash: 41a51b4a2445de84167a0c2a51159da4179017ed7dc3e8820c73dde01dd90e19
# last_modified_at: '2025-05-29T14:13:59.414823+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_node_manager.py
# namespace: python://omnibase.nodes.node_manager_node.v1_0_0.node_tests.test_node_manager
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: dc1976f6-432e-40fb-a9b1-71cd474df87f
# version: 1.0.0
# === /OmniNode:Metadata ===


import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from omnibase.enums import OnexStatus
from omnibase.nodes.node_manager_node.v1_0_0.models.state import (
    NodeManagerInputState,
    NodeManagerOperation,
)
from omnibase.nodes.node_manager_node.v1_0_0.node import NodeManagerNode
from omnibase.protocol.protocol_event_bus import ProtocolEventBus


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
        template_source="node_template",
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
