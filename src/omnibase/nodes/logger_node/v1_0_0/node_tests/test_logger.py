# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.116040'
# description: Stamped by PythonHandler
# entrypoint: python://test_logger
# hash: eeb630cc2b78a6e01cebd69b88bd834be7869e136e2662fb9ceffbfe80678592
# last_modified_at: '2025-05-29T14:13:59.261630+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_logger.py
# namespace: python://omnibase.nodes.logger_node.v1_0_0.node_tests.test_logger
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: af0c2cf0-4d26-4e6b-bd53-bbb1c8d721ba
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Test suite for logger_node.

Tests the logger node functionality including different output formats,
error handling, and state validation.
"""

from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from omnibase.enums import LogLevelEnum, OnexStatus, OutputFormatEnum

from ..models.state import LoggerInputState, LoggerOutputState

# Updated imports for logger node
from ..node import LoggerNode

# Use LogLevelEnum directly
# Use OutputFormatEnum directly


class TestLoggerNode:
    """
    Test class for logger_node.

    Tests the core logging functionality with different output formats.
    """

    def test_logger_node_success(self) -> None:
        """
        Test successful execution of logger_node.
        """
        # Create valid input for logger node
        input_state = LoggerInputState(
            version="1.0.0",
            log_level=LogLevelEnum.INFO,
            message="Test log message",
            output_format=OutputFormatEnum.JSON,
        )

        # Mock event bus to avoid side effects
        mock_event_bus = Mock()

        # Call the logger node using the class directly
        node = LoggerNode(event_bus=mock_event_bus)
        result = node.run(input_state, event_bus=mock_event_bus)

        # Verify the output
        assert isinstance(result, LoggerOutputState)
        assert result.version == "1.0.0"
        assert result.status == OnexStatus.SUCCESS
        assert "Successfully formatted log entry" in result.message
        assert result.formatted_log is not None
        assert "Test log message" in result.formatted_log

        # Verify events were emitted
        # Check that NODE_START and NODE_SUCCESS events were emitted in order
        event_types = [
            call_args[0][0].event_type
            for call_args in mock_event_bus.publish.call_args_list
            if hasattr(call_args[0][0], "event_type")
        ]
        # There may be extra events (e.g., telemetry), but these two must be present and ordered
        try:
            start_idx = event_types.index("NODE_START")
            success_idx = event_types.index("NODE_SUCCESS")
            assert start_idx < success_idx
        except ValueError:
            assert (
                False
            ), f"NODE_START and NODE_SUCCESS events not found in emitted events: {event_types}"

    def test_logger_node_with_minimal_input(self) -> None:
        """
        Test logger_node with minimal required input.
        """
        # Create minimal input for logger node
        input_state = LoggerInputState(
            version="1.0.0",
            log_level=LogLevelEnum.INFO,
            message="Minimal test message",
            # output_format uses default value (json)
        )

        mock_event_bus = Mock()

        # Call the logger node using the class directly
        node = LoggerNode(event_bus=mock_event_bus)
        result = node.run(input_state, event_bus=mock_event_bus)

        # Verify minimal input scenario
        assert isinstance(result, LoggerOutputState)
        assert result.status == OnexStatus.SUCCESS
        assert result.formatted_log is not None  # Should have output

    def test_logger_node_error_handling(self) -> None:
        """
        Test error handling in logger_node.
        """
        # Test error handling for invalid log level during state creation
        with pytest.raises(ValidationError):  # Pydantic validation error
            LoggerInputState(
                version="1.0.0",
                log_level="invalid_level",  # type: ignore # Invalid log level - string instead of enum
                message="Test message",
                output_format=OutputFormatEnum.JSON,
            )

    def test_logger_node_state_validation(self) -> None:
        """
        Test input state validation.
        """
        # Test invalid input state - missing required message field
        with pytest.raises(ValidationError):  # Pydantic validation error
            LoggerInputState(  # type: ignore # Missing required field: message
                version="1.0.0",
                log_level=LogLevelEnum.INFO,
                # Missing required field: message
            )

    def test_logger_node_output_state_structure(self) -> None:
        """
        Test output state structure and validation.
        """
        # Create valid input
        input_state = LoggerInputState(
            version="1.0.0",
            log_level=LogLevelEnum.INFO,
            message="Structure test message",
            output_format=OutputFormatEnum.JSON,
        )

        mock_event_bus = Mock()

        # Call the logger node using the class directly
        node = LoggerNode(event_bus=mock_event_bus)
        result = node.run(input_state, event_bus=mock_event_bus)

        # Test output state structure
        assert hasattr(result, "version")
        assert hasattr(result, "status")
        assert hasattr(result, "message")
        assert hasattr(result, "formatted_log")

        # Test that output can be serialized
        json_output = result.model_dump_json()
        assert isinstance(json_output, str)
        assert len(json_output) > 0


class TestLoggerNodeIntegration:
    """
    Integration tests for logger_node.

    Tests the logger node with different output formats and
    end-to-end scenarios.
    """

    def test_logger_node_different_formats(self) -> None:
        """
        Test logger_node with different output formats.
        """
        formats = [
            OutputFormatEnum.JSON,
            OutputFormatEnum.YAML,
            OutputFormatEnum.MARKDOWN,
            OutputFormatEnum.TEXT,
            OutputFormatEnum.CSV,
        ]

        for output_format in formats:
            input_state = LoggerInputState(
                version="1.0.0",
                log_level=LogLevelEnum.INFO,
                message=f"Test message for {output_format.value} format",
                output_format=output_format,
            )

            mock_event_bus = Mock()
            node = LoggerNode(event_bus=mock_event_bus)
            result = node.run(input_state, event_bus=mock_event_bus)

            assert isinstance(result, LoggerOutputState)
            assert result.status == OnexStatus.SUCCESS
            assert result.formatted_log is not None
            assert (
                f"Test message for {output_format.value} format" in result.formatted_log
            )


@pytest.fixture
def logger_input_state() -> LoggerInputState:
    """
    Fixture for common logger input state.
    """
    return LoggerInputState(
        version="1.0.0",
        log_level=LogLevelEnum.INFO,
        message="Fixture test message",
        output_format=OutputFormatEnum.JSON,
        context={"test": "fixture"},
        tags=["test", "fixture"],
    )


@pytest.fixture
def mock_event_bus() -> Mock:
    """
    Fixture for mock event bus.
    """
    return Mock()
