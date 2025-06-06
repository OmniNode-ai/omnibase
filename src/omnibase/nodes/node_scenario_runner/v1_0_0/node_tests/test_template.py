# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.948741'
# description: Stamped by PythonHandler
# entrypoint: python://test_node_scenario_runner
# hash: fcf5f232ebff9487aba6d8469e30c6198f1526170c3d752fa7042eb839feb997
# last_modified_at: '2025-05-29T14:14:00.057658+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_node_scenario_runner.py
# namespace: python://omnibase.nodes.node_scenario_runner_node.v1_0_0.node_tests.test_node_scenario_runner
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
NODE_SCENARIO_RUNNER: Test suite for node_scenario_runner_node.

Replace this docstring with a description of your node's test coverage.
Update the test cases to match your node's functionality.
"""

from unittest.mock import Mock

import pytest

from omnibase.core.core_error_codes import OnexError

from ..models.state import NodeScenarioRunnerInputState, NodeScenarioRunnerOutputState

# NODE_SCENARIO_RUNNER: Update these imports to match your node's structure
from ..node import run_node_scenario_runner_node


class TestNodeScenarioRunnerNode:
    """
    NODE_SCENARIO_RUNNER: Test class for node_scenario_runner_node.

    Replace this with tests specific to your node's functionality.
    Update test method names and logic as needed.
    """

    def test_node_scenario_runner_node_success(self) -> None:
        """
        NODE_SCENARIO_RUNNER: Test successful execution of node_scenario_runner_node.

        Replace this test with your node's success scenario.
        """
        # NODE_SCENARIO_RUNNER: Update this input to match your node's requirements
        input_state = NodeScenarioRunnerInputState(
            version="1.0.0",
            node_scenario_runner_required_field="test_value",
            node_scenario_runner_optional_field="optional_test_value",
        )

        # Mock event bus to avoid side effects
        mock_event_bus = Mock()

        # NODE_SCENARIO_RUNNER: Update this function call to match your node
        result = run_node_scenario_runner_node(input_state, event_bus=mock_event_bus)

        # NODE_SCENARIO_RUNNER: Update these assertions to match your expected output
        assert isinstance(result, NodeScenarioRunnerOutputState)
        assert result.version == "1.0.0"
        assert result.status == "success"
        assert "NODE_SCENARIO_RUNNER: Processed test_value" in result.message
        assert (
            result.node_scenario_runner_output_field
            == "NODE_SCENARIO_RUNNER_RESULT_test_value"
        )

        # Verify events were emitted
        # Check that NODE_START and NODE_SUCCESS events were emitted in order (robust to extra events)
        event_types = [
            call_args[0][0].event_type
            for call_args in mock_event_bus.publish.call_args_list
            if hasattr(call_args[0][0], "event_type")
        ]
        try:
            start_idx = event_types.index("NODE_START")
            success_idx = event_types.index("NODE_SUCCESS")
            assert start_idx < success_idx
        except ValueError:
            assert (
                False
            ), f"NODE_START and NODE_SUCCESS events not found in emitted events: {event_types}"

    def test_node_scenario_runner_node_with_minimal_input(self) -> None:
        """
        NODE_SCENARIO_RUNNER: Test node_scenario_runner_node with minimal required input.

        Replace this test with your node's minimal input scenario.
        """
        # NODE_SCENARIO_RUNNER: Update this input to use only required fields
        input_state = NodeScenarioRunnerInputState(
            version="1.0.0",
            node_scenario_runner_required_field="minimal_test",
            # node_scenario_runner_optional_field uses default value
        )

        mock_event_bus = Mock()

        # NODE_SCENARIO_RUNNER: Update this function call to match your node
        result = run_node_scenario_runner_node(input_state, event_bus=mock_event_bus)

        # NODE_SCENARIO_RUNNER: Update these assertions for minimal input scenario
        assert isinstance(result, NodeScenarioRunnerOutputState)
        assert result.status == "success"
        assert (
            result.node_scenario_runner_output_field is not None
        )  # Should have output

    def test_node_scenario_runner_node_error_handling(self) -> None:
        """
        NODE_SCENARIO_RUNNER: Test error handling in node_scenario_runner_node.

        Replace this test with your node's error scenarios.
        """
        # NODE_SCENARIO_RUNNER: Test that empty required field raises validation error during creation
        with pytest.raises(OnexError):  # Validation error during model creation
            NodeScenarioRunnerInputState(
                version="1.0.0",
                node_scenario_runner_required_field="",  # Empty value causes validation error
            )

    def test_node_scenario_runner_node_state_validation(self) -> None:
        """
        NODE_SCENARIO_RUNNER: Test input state validation.

        Replace this test with your node's validation scenarios.
        """
        # NODE_SCENARIO_RUNNER: Test invalid version format
        with pytest.raises(OnexError):  # Validation error for invalid version
            NodeScenarioRunnerInputState(
                version="invalid-version",  # Invalid semantic version
                node_scenario_runner_required_field="valid_field",
            )

    def test_node_scenario_runner_node_output_state_structure(self) -> None:
        """
        NODE_SCENARIO_RUNNER: Test output state structure and validation.

        Replace this test with your node's output validation.
        """
        # NODE_SCENARIO_RUNNER: Create valid input
        input_state = NodeScenarioRunnerInputState(
            version="1.0.0", node_scenario_runner_required_field="structure_test"
        )

        mock_event_bus = Mock()

        # NODE_SCENARIO_RUNNER: Update this function call
        result = run_node_scenario_runner_node(input_state, event_bus=mock_event_bus)

        # NODE_SCENARIO_RUNNER: Test output state structure
        assert hasattr(result, "version")
        assert hasattr(result, "status")
        assert hasattr(result, "message")
        assert hasattr(result, "node_scenario_runner_output_field")

        # Test that output can be serialized
        json_output = result.model_dump_json()
        assert isinstance(json_output, str)
        assert len(json_output) > 0


# NODE_SCENARIO_RUNNER: Add more test classes as needed for different aspects of your node
class TestNodeScenarioRunnerNodeIntegration:
    """
    NODE_SCENARIO_RUNNER: Integration tests for node_scenario_runner_node.

    Replace this with integration tests that test your node
    with real dependencies or end-to-end scenarios.
    """

    def test_node_scenario_runner_node_end_to_end(self) -> None:
        """
        NODE_SCENARIO_RUNNER: End-to-end test for node_scenario_runner_node.

        Replace this with a realistic end-to-end test scenario.
        """
        # NODE_SCENARIO_RUNNER: This is a placeholder for integration testing
        # Replace with actual integration test logic
        pass


# NODE_SCENARIO_RUNNER: Add fixtures if needed
@pytest.fixture
def node_scenario_runner_input_state() -> NodeScenarioRunnerInputState:
    """
    NODE_SCENARIO_RUNNER: Fixture for common input state.

    Replace this with fixtures specific to your node's testing needs.
    """
    return NodeScenarioRunnerInputState(
        version="1.0.0",
        node_scenario_runner_required_field="fixture_test_value",
        node_scenario_runner_optional_field="fixture_optional_value",
    )


@pytest.fixture
def mock_event_bus() -> Mock:
    """
    NODE_SCENARIO_RUNNER: Fixture for mock event bus.

    Keep this fixture or replace with your preferred mocking approach.
    """
    return Mock()
