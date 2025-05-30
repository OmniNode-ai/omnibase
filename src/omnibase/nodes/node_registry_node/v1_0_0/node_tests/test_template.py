# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.948741'
# description: Stamped by PythonHandler
# entrypoint: python://test_node_registry
# hash: fcf5f232ebff9487aba6d8469e30c6198f1526170c3d752fa7042eb839feb997
# last_modified_at: '2025-05-29T14:14:00.057658+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_node_registry.py
# namespace: python://omnibase.nodes.node_registry_node.v1_0_0.node_tests.test_node_registry
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 0c5dc3d1-0b79-4105-a622-087fd7e6ee7b
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
NODE_REGISTRY: Test suite for node_registry_node.

Replace this docstring with a description of your node's test coverage.
Update the test cases to match your node's functionality.
"""

from unittest.mock import Mock

import pytest

from omnibase.core.core_error_codes import OnexError

from ..models.state import NodeRegistryInputState, NodeRegistryOutputState, NodeRegistryEntry

# NODE_REGISTRY: Update these imports to match your node's structure
from ..node import run_node_registry_node

from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from uuid import uuid4


class TestNodeRegistryNode:
    """
    NODE_REGISTRY: Test class for node_registry_node.

    Replace this with tests specific to your node's functionality.
    Update test method names and logic as needed.
    """

    def test_node_registry_node_success(self) -> None:
        """
        NODE_REGISTRY: Test successful execution of node_registry_node.

        Replace this test with your node's success scenario.
        """
        input_state = NodeRegistryInputState(
            version="1.0.0",
            action="get_active_nodes",
        )
        mock_event_bus = Mock()
        result = run_node_registry_node(input_state, event_bus=mock_event_bus)
        assert isinstance(result, NodeRegistryOutputState)
        assert result.version == "1.0.0"
        assert result.status == "success"
        assert "Registry state returned" in result.message
        assert result.registry_json is not None

    def test_node_registry_node_with_node_id(self) -> None:
        """
        NODE_REGISTRY: Test node_registry_node with node_id.

        Replace this test with your node's node_id scenario.
        """
        input_state = NodeRegistryInputState(
            version="1.0.0",
            action="get_node",
            node_id="test_node_id",
        )
        mock_event_bus = Mock()
        result = run_node_registry_node(input_state, event_bus=mock_event_bus)
        assert isinstance(result, NodeRegistryOutputState)
        assert result.status in {"success", "failure"}
        # If registry is empty, should fail
        if result.status == "failure":
            assert "not found" in result.message

    def test_node_registry_node_error_handling(self) -> None:
        """
        NODE_REGISTRY: Test error handling in node_registry_node.

        Replace this test with your node's error scenarios.
        """
        with pytest.raises(OnexError):
            NodeRegistryInputState(
                version="1.0.0",
                action="invalid_action",
            )

    def test_node_registry_node_state_validation(self) -> None:
        """
        NODE_REGISTRY: Test input state validation.

        Replace this test with your node's validation scenarios.
        """
        with pytest.raises(OnexError):
            NodeRegistryInputState(
                version="invalid-version",
                action="get_active_nodes",
            )

    def test_node_registry_node_output_state_structure(self) -> None:
        """
        NODE_REGISTRY: Test output state structure and validation.

        Replace this test with your node's output validation.
        """
        input_state = NodeRegistryInputState(
            version="1.0.0", action="get_active_nodes"
        )
        mock_event_bus = Mock()
        result = run_node_registry_node(input_state, event_bus=mock_event_bus)
        assert hasattr(result, "version")
        assert hasattr(result, "status")
        assert hasattr(result, "message")
        assert hasattr(result, "registry_json")
        json_output = result.model_dump_json()
        assert isinstance(json_output, str)
        assert len(json_output) > 0


# NODE_REGISTRY: Add more test classes as needed for different aspects of your node
class TestNodeRegistryNodeIntegration:
    """
    NODE_REGISTRY: Integration tests for node_registry_node.

    Replace this with integration tests that test your node
    with real dependencies or end-to-end scenarios.
    """

    def test_node_registry_node_end_to_end(self) -> None:
        """
        NODE_REGISTRY: End-to-end test for node_registry_node.

        Replace this with a realistic end-to-end test scenario.
        """
        # NODE_REGISTRY: This is a placeholder for integration testing
        # Replace with actual integration test logic
        pass


# NODE_REGISTRY: Add fixtures if needed
@pytest.fixture
def node_registry_input_state() -> NodeRegistryInputState:
    """
    NODE_REGISTRY: Fixture for common input state.

    Replace this with fixtures specific to your node's testing needs.
    """
    return NodeRegistryInputState(
        version="1.0.0",
        action="get_active_nodes",
    )


@pytest.fixture
def mock_event_bus() -> Mock:
    """
    NODE_REGISTRY: Fixture for mock event bus.

    Keep this fixture or replace with your preferred mocking approach.
    """
    return Mock()


class TestNodeRegistryNodeEventDriven:
    def test_node_announce_event_updates_registry_and_emits_accept(self):
        event_bus = InMemoryEventBus()
        node = run_node_registry_node.__globals__["NodeRegistryNode"](event_bus=event_bus)
        node_id = str(uuid4())
        from omnibase.model.model_node_metadata import NodeMetadataBlock, IOBlock
        announce_event = OnexEvent(
            node_id=node_id,
            event_type=OnexEventTypeEnum.NODE_ANNOUNCE,
            metadata={
                "node_id": node_id,
                "metadata_block": NodeMetadataBlock(
                    name="test_node",
                    version="1.0.0",
                    uuid=node_id,
                    author="Test Author",
                    created_at="2025-01-01T00:00:00Z",
                    last_modified_at="2025-01-01T00:00:00Z",
                    entrypoint="python://main",
                    namespace="test.namespace",
                    hash="0"*64,
                ).model_dump(),
                "status": "ephemeral",
                "execution_mode": "memory",
                "inputs": [IOBlock(name="input1", schema_ref="str").model_dump()],
                "outputs": [IOBlock(name="output1", schema_ref="str").model_dump()],
            },
        )
        events = []
        event_bus.subscribe(lambda e: events.append(e))
        event_bus.publish(announce_event)
        assert node_id in node.registry_state.registry
        assert node.registry_state.registry[node_id].metadata_block.name == "test_node"
        event_types = [e.event_type for e in events]
        assert OnexEventTypeEnum.NODE_ANNOUNCE_ACCEPTED in event_types

    def test_registry_query_protocol_returns_active_nodes(self):
        event_bus = InMemoryEventBus()
        node = run_node_registry_node.__globals__["NodeRegistryNode"](event_bus=event_bus)
        node_id = str(uuid4())
        from omnibase.model.model_node_metadata import NodeMetadataBlock, IOBlock
        node.registry_state.registry[node_id] = NodeRegistryEntry(
            node_id=node_id,
            metadata_block=NodeMetadataBlock(
                name="test_node",
                version="1.0.0",
                uuid=node_id,
                author="Test Author",
                created_at="2025-01-01T00:00:00Z",
                last_modified_at="2025-01-01T00:00:00Z",
                entrypoint="python://main",
                namespace="test.namespace",
                hash="0"*64,
            ),
            status="ephemeral",
            execution_mode="memory",
            inputs=[IOBlock(name="input1", schema_ref="str")],
            outputs=[IOBlock(name="output1", schema_ref="str")],
        )
        input_state = NodeRegistryInputState(
            version="1.0.0",
            action="get_node",
            node_id=node_id,
        )
        result = node.run(input_state)
        assert node_id in node.registry_state.registry
        assert result.status == "success"
        assert "info returned" in result.message
        assert result.registry_json is not None
