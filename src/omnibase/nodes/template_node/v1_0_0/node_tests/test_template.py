# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.948741'
# description: Stamped by PythonHandler
# entrypoint: python://test_template.py
# hash: 4fd33c6828fb69ce3d4a76eea692e3e6ac171a1c12598615ccd22efcbd22a6ed
# last_modified_at: '2025-05-29T11:50:11.923524+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_template.py
# namespace: omnibase.test_template
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
TEMPLATE: Test suite for template_node.

Replace this docstring with a description of your node's test coverage.
Update the test cases to match your node's functionality.
"""

from unittest.mock import Mock

import pytest

from omnibase.core.core_error_codes import OnexError

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
        # Check that NODE_START and NODE_SUCCESS events were emitted in order (robust to extra events)
        event_types = [call_args[0][0].event_type if call_args[0] else None for call_args in mock_event_bus.publish.call_args_list]
        try:
            start_idx = event_types.index("NODE_START")
            success_idx = event_types.index("NODE_SUCCESS")
            assert start_idx < success_idx
        except ValueError:
            assert False, f"NODE_START and NODE_SUCCESS events not found in emitted events: {event_types}"

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
        # TEMPLATE: Test that empty required field raises validation error during creation
        with pytest.raises(OnexError):  # Validation error during model creation
            TemplateInputState(
                version="1.0.0",
                template_required_field="",  # Empty value causes validation error
            )

    def test_template_node_state_validation(self) -> None:
        """
        TEMPLATE: Test input state validation.

        Replace this test with your node's validation scenarios.
        """
        # TEMPLATE: Test invalid version format
        with pytest.raises(OnexError):  # Validation error for invalid version
            TemplateInputState(
                version="invalid-version",  # Invalid semantic version
                template_required_field="valid_field",
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
