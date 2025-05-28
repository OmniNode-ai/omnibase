# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_template.py
# version: 1.0.0
# uuid: 5cc80863-4f7f-4b7e-9dc8-89b1a31fb94e
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.829656
# last_modified_at: 2025-05-28T17:20:04.710365
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a43e364fe8913d6760bd5c10d9fc90397bac94dc96498530f78f68182ac5ef55
# entrypoint: python@test_template.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.test_template
# meta_type: tool
# === /OmniNode:Metadata ===


"""
TEMPLATE: Test suite for template_node.

Replace this docstring with a description of your node's test coverage.
Update the test cases to match your node's functionality.
"""

from unittest.mock import Mock

import pytest

from omnibase.core.core_error_codes import OnexError

from ..models.state import CLIInputState, CLIOutputState

# Updated imports for CLI node
from ..node import run_cli_node


class TestTemplateNode:
    """
    TEMPLATE: Test class for template_node.

    Replace this with tests specific to your node's functionality.
    Update test method names and logic as needed.
    """

    def test_template_node_success(self) -> None:
        """
        TEMPLATE: Test successful execution of template_node.

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

    def test_template_node_with_minimal_input(self) -> None:
        """
        TEMPLATE: Test template_node with minimal required input.

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

    def test_template_node_error_handling(self) -> None:
        """
        TEMPLATE: Test error handling in template_node.

        Replace this test with your node's error scenarios.
        """
        # Test that empty required field raises validation error during creation
        with pytest.raises(OnexError):  # Validation error during model creation
            CLIInputState(
                version="1.0.0",
                command="",  # Empty command causes validation error
            )

    def test_template_node_state_validation(self) -> None:
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

    def test_template_node_output_state_structure(self) -> None:
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
class TestTemplateNodeIntegration:
    """
    TEMPLATE: Integration tests for template_node.

    Replace this with integration tests that test your node
    with real dependencies or end-to-end scenarios.
    """

    def test_template_node_end_to_end(self) -> None:
        """
        TEMPLATE: End-to-end test for template_node.

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
