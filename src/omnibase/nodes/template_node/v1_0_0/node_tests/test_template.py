# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_template.py
# version: 1.0.0
# uuid: 3f3d565e-11fe-4179-9fc1-180db9203367
# author: OmniNode Team
# created_at: 2025-05-24T09:36:56.350866
# last_modified_at: 2025-05-24T13:39:57.892470
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 1837633bc3baba3af3d99ef7f1a63e7c47f6d67a8cb844a479bbcf2932b4724f
# entrypoint: python@test_template.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_template
# meta_type: tool
# === /OmniNode:Metadata ===


"""
TEMPLATE: Test suite for template_node.

Replace this docstring with a description of your node's test coverage.
Update the test cases to match your node's functionality.
"""

from unittest.mock import Mock

import pytest

from ..models.state import TemplateInputState, TemplateOutputState

# TEMPLATE: Update these imports to match your node's structure
from ..node import run_template_node


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
        # TEMPLATE: Update this input to match your node's requirements
        input_state = TemplateInputState(
            version="1.0.0",
            template_required_field="test_value",
            template_optional_field="optional_test_value",
        )

        # Mock event bus to avoid side effects
        mock_event_bus = Mock()

        # TEMPLATE: Update this function call to match your node
        result = run_template_node(input_state, event_bus=mock_event_bus)

        # TEMPLATE: Update these assertions to match your expected output
        assert isinstance(result, TemplateOutputState)
        assert result.version == "1.0.0"
        assert result.status == "success"
        assert "TEMPLATE: Processed test_value" in result.message
        assert result.template_output_field == "TEMPLATE_RESULT_test_value"

        # Verify events were emitted
        assert mock_event_bus.publish.call_count == 2  # START and SUCCESS

    def test_template_node_with_minimal_input(self) -> None:
        """
        TEMPLATE: Test template_node with minimal required input.

        Replace this test with your node's minimal input scenario.
        """
        # TEMPLATE: Update this input to use only required fields
        input_state = TemplateInputState(
            version="1.0.0",
            template_required_field="minimal_test",
            # template_optional_field uses default value
        )

        mock_event_bus = Mock()

        # TEMPLATE: Update this function call to match your node
        result = run_template_node(input_state, event_bus=mock_event_bus)

        # TEMPLATE: Update these assertions for minimal input scenario
        assert isinstance(result, TemplateOutputState)
        assert result.status == "success"
        assert result.template_output_field is not None  # Should have output

    def test_template_node_error_handling(self) -> None:
        """
        TEMPLATE: Test error handling in template_node.

        Replace this test with your node's error scenarios.
        """
        # TEMPLATE: Create an input that would cause an error in your node
        input_state = TemplateInputState(
            version="1.0.0",
            template_required_field="",  # Empty value might cause error
        )

        mock_event_bus = Mock()

        # TEMPLATE: Update this to test your node's error handling
        # This example assumes empty required field causes an error
        # Replace with actual error conditions for your node
        with pytest.raises(ValueError):  # Or whatever exception your node raises
            run_template_node(input_state, event_bus=mock_event_bus)

        # Verify failure event was emitted
        # Note: This assumes the error is caught and event is emitted before re-raising
        # Update based on your node's error handling strategy

    def test_template_node_state_validation(self) -> None:
        """
        TEMPLATE: Test input state validation.

        Replace this test with your node's validation scenarios.
        """
        # TEMPLATE: Test invalid input state
        with pytest.raises(ValueError):  # Pydantic validation error
            TemplateInputState(
                version="1.0.0",
                template_required_field="missing_field_test",
                # Missing required field: template_required_field
            )

    def test_template_node_output_state_structure(self) -> None:
        """
        TEMPLATE: Test output state structure and validation.

        Replace this test with your node's output validation.
        """
        # TEMPLATE: Create valid input
        input_state = TemplateInputState(
            version="1.0.0", template_required_field="structure_test"
        )

        mock_event_bus = Mock()

        # TEMPLATE: Update this function call
        result = run_template_node(input_state, event_bus=mock_event_bus)

        # TEMPLATE: Test output state structure
        assert hasattr(result, "version")
        assert hasattr(result, "status")
        assert hasattr(result, "message")
        assert hasattr(result, "template_output_field")

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
def template_input_state() -> TemplateInputState:
    """
    TEMPLATE: Fixture for common input state.

    Replace this with fixtures specific to your node's testing needs.
    """
    return TemplateInputState(
        version="1.0.0",
        template_required_field="fixture_test_value",
        template_optional_field="fixture_optional_value",
    )


@pytest.fixture
def mock_event_bus() -> Mock:
    """
    TEMPLATE: Fixture for mock event bus.

    Keep this fixture or replace with your preferred mocking approach.
    """
    return Mock()
