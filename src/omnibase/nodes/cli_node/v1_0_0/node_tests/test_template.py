# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.829656'
# description: Stamped by PythonHandler
# entrypoint: python://test_template
# hash: d01aff69f4da696a31cdab7beb7b6328d0335932cc47b26a381be8c0404b2dc2
# last_modified_at: '2025-05-29T14:13:59.032553+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_template.py
# namespace: python://omnibase.nodes.cli_node.v1_0_0.node_tests.test_template
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 5cc80863-4f7f-4b7e-9dc8-89b1a31fb94e
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
TEMPLATE: Test suite for node_template.

Replace this docstring with a description of your node's test coverage.
Update the test cases to match your node's functionality.
"""

from unittest.mock import Mock

import pytest

from omnibase.core.core_error_codes import OnexError

from ..models.state import CLIInputState, CLIOutputState

# Updated imports for CLI node
from ..node import run_cli_node


class TestNodeTemplate:
    """
    TEMPLATE: Test class for node_template.

    Replace this with tests specific to your node's functionality.
    Update test method names and logic as needed.
    """

    def test_node_template_success(self) -> None:
        """
        TEMPLATE: Test successful execution of node_template.

        Replace this test with your node's success scenario.
        """
        # CLI node input for version command
        input_state = CLIInputState(
            version="1.0.0",
            command="version",
        )

        # Mock event bus to avoid side effects
        mock_event_bus = Mock()

        # CLI node function call
        result = run_cli_node(input_state, event_bus=mock_event_bus)

        # CLI node assertions
        assert isinstance(result, CLIOutputState)
        assert result.version == "1.0.0"
        assert result.status == "success"
        assert "CLI Node" in result.message

        # Verify events were emitted
        assert mock_event_bus.publish.call_count == 2  # START and SUCCESS

    def test_node_template_with_minimal_input(self) -> None:
        """
        TEMPLATE: Test node_template with minimal required input.

        Replace this test with your node's minimal input scenario.
        """
        # CLI node input with minimal required fields
        input_state = CLIInputState(
            version="1.0.0",
            command="info",
        )

        mock_event_bus = Mock()

        # CLI node function call
        result = run_cli_node(input_state, event_bus=mock_event_bus)

        # CLI node assertions for minimal input
        assert isinstance(result, CLIOutputState)
        assert result.status == "success"
        assert result.message is not None  # Should have output

    def test_node_template_error_handling(self) -> None:
        """
        TEMPLATE: Test error handling in node_template.

        Replace this test with your node's error scenarios.
        """
        # Test that empty required field raises validation error during creation
        with pytest.raises(OnexError):  # Validation error during model creation
            CLIInputState(
                version="1.0.0",
                command="",  # Empty command causes validation error
            )

    def test_node_template_state_validation(self) -> None:
        """
        TEMPLATE: Test input state validation.

        Replace this test with your node's validation scenarios.
        """
        # Test invalid version format
        with pytest.raises(OnexError):  # Validation error for invalid version
            CLIInputState(
                version="invalid-version",  # Invalid semantic version
                command="version",
            )

    def test_node_template_output_state_structure(self) -> None:
        """
        TEMPLATE: Test output state structure and validation.

        Replace this test with your node's output validation.
        """
        # Create valid input
        input_state = CLIInputState(version="1.0.0", command="version")

        mock_event_bus = Mock()

        # CLI node function call
        result = run_cli_node(input_state, event_bus=mock_event_bus)

        # Test output state structure
        assert hasattr(result, "version")
        assert hasattr(result, "status")
        assert hasattr(result, "message")
        assert hasattr(result, "command")

        # Test that output can be serialized
        json_output = result.model_dump_json()
        assert isinstance(json_output, str)
        assert len(json_output) > 0


# TEMPLATE: Add more test classes as needed for different aspects of your node
class TestNodeTemplateIntegration:
    """
    TEMPLATE: Integration tests for node_template.

    Replace this with integration tests that test your node
    with real dependencies or end-to-end scenarios.
    """

    def test_node_template_end_to_end(self) -> None:
        """
        TEMPLATE: End-to-end test for node_template.

        Replace this with a realistic end-to-end test scenario.
        """
        # TEMPLATE: This is a placeholder for integration testing
        # Replace with actual integration test logic
        pass


# TEMPLATE: Add fixtures if needed
@pytest.fixture
def template_input_state() -> CLIInputState:
    """
    TEMPLATE: Fixture for common input state.

    Replace this with fixtures specific to your node's testing needs.
    """
    return CLIInputState(
        version="1.0.0",
        command="version",
    )


@pytest.fixture
def mock_event_bus() -> Mock:
    """
    TEMPLATE: Fixture for mock event bus.

    Keep this fixture or replace with your preferred mocking approach.
    """
    return Mock()
