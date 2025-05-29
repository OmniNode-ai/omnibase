# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.633830'
# description: Stamped by PythonHandler
# entrypoint: python://test_event_schema_validator.py
# hash: 1400f537a56774ff178d987ab539314d1985f49d13ef82a2165670c16670585d
# last_modified_at: '2025-05-29T11:50:12.395355+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_event_schema_validator.py
# namespace: omnibase.test_event_schema_validator
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 5c505c5b-a78d-4469-9e40-654d107b46bd
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Tests for the ONEX event schema validator.

This module tests the OnexEventSchemaValidator to ensure it properly validates
events according to the canonical ONEX event schema.
"""

import uuid
from datetime import datetime

import pytest

from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry.event_schema_validator import (
    EventSchemaValidationError,
    OnexEventSchemaValidator,
    create_compliant_event,
    validate_event_schema,
)


class TestOnexEventSchemaValidator:
    """Test suite for OnexEventSchemaValidator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.validator = OnexEventSchemaValidator(strict_mode=False)
        self.strict_validator = OnexEventSchemaValidator(strict_mode=True)

    def test_valid_node_start_event(self) -> None:
        """Test validation of a valid NODE_START event."""
        event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="test_node",
            correlation_id="test-123",
            metadata={
                "input_state": {"file_path": "test.py", "author": "test"},
                "node_version": "1.0.0",
                "operation_type": "stamp_file",
            },
        )

        assert self.validator.validate_event(event)
        assert len(self.validator.get_validation_errors()) == 0

        # Verify metadata is present and has expected fields
        assert event.metadata is not None
        assert "input_state" in event.metadata

    def test_valid_node_success_event(self) -> None:
        """Test validation of a valid NODE_SUCCESS event."""
        event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_SUCCESS,
            node_id="test_node",
            correlation_id="test-123",
            metadata={
                "input_state": {"file_path": "test.py"},
                "output_state": {"status": "success", "message": "File stamped"},
                "execution_time_ms": 150.5,
                "result_summary": "Successfully stamped file",
            },
        )

        assert self.validator.validate_event(event)
        assert len(self.validator.get_validation_errors()) == 0

    def test_valid_node_failure_event(self) -> None:
        """Test validation of a valid NODE_FAILURE event."""
        event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_FAILURE,
            node_id="test_node",
            correlation_id="test-123",
            metadata={
                "input_state": {"file_path": "test.py"},
                "error": "File not found",
                "error_type": "FileNotFoundError",
                "execution_time_ms": 25.0,
            },
        )

        assert self.validator.validate_event(event)
        assert len(self.validator.get_validation_errors()) == 0

    def test_valid_telemetry_start_event(self) -> None:
        """Test validation of a valid TELEMETRY_OPERATION_START event."""
        event = OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            node_id="test_node",
            correlation_id="test-123",
            metadata={
                "operation": "process_file",
                "function": "run_test_node",
                "args_count": 2,
                "kwargs_keys": ["correlation_id", "event_bus"],
            },
        )

        assert self.validator.validate_event(event)
        assert len(self.validator.get_validation_errors()) == 0

    def test_valid_telemetry_success_event(self) -> None:
        """Test validation of a valid TELEMETRY_OPERATION_SUCCESS event."""
        event = OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
            node_id="test_node",
            correlation_id="test-123",
            metadata={
                "operation": "test_op",
                "function": "test_func",
                "execution_time_ms": 125.75,
                "result_type": "TestOutputState",
                "success": True,
            },
        )

        assert self.validator.validate_event(event)
        assert len(self.validator.get_validation_errors()) == 0

    def test_valid_telemetry_error_event(self) -> None:
        """Test validation of a valid TELEMETRY_OPERATION_ERROR event."""
        event = OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR,
            node_id="test_node",
            correlation_id="test-123",
            metadata={
                "operation": "process_file",
                "function": "run_test_node",
                "execution_time_ms": 50.0,
                "error_type": "OnexError",
                "error_message": "Invalid input parameter",
                "success": False,
                "recoverable": True,
            },
        )

        assert self.validator.validate_event(event)
        assert len(self.validator.get_validation_errors()) == 0

    def test_missing_required_fields(self) -> None:
        """Test validation failure for missing required fields."""
        # Event with missing node_id
        event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="",  # Empty node_id should fail
            metadata={"input_state": {"test": "data"}},
        )

        assert not self.validator.validate_event(event)
        errors = self.validator.get_validation_errors()
        assert any("node_id is required" in error for error in errors)

    def test_missing_required_metadata(self) -> None:
        """Test validation failure for missing required metadata fields."""
        # NODE_START event without required input_state
        event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="test_node",
            metadata={},  # Missing input_state
        )

        assert not self.validator.validate_event(event)
        errors = self.validator.get_validation_errors()
        assert any("metadata is required for event type" in error for error in errors)

    def test_invalid_metadata_types(self) -> None:
        """Test validation failure for invalid metadata field types."""
        event = OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
            node_id="test_node",
            metadata={
                "operation": "test_op",
                "function": "test_func",
                "execution_time_ms": "not_a_number",  # Should be float/int
                "success": "not_a_boolean",  # Should be boolean
            },
        )

        assert not self.validator.validate_event(event)
        errors = self.validator.get_validation_errors()
        assert any("execution_time_ms must be a number" in error for error in errors)
        assert any("success must be a boolean" in error for error in errors)

    def test_strict_mode_raises_exception(self) -> None:
        """Test that strict mode raises exceptions on validation failures."""
        event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="test_node",
            metadata={},  # Missing required input_state
        )

        with pytest.raises(EventSchemaValidationError):
            self.strict_validator.validate_event(event)

    def test_non_strict_mode_logs_warnings(self) -> None:
        """Test that non-strict mode logs warnings instead of raising exceptions."""
        event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="test_node",
            metadata={},  # Missing required input_state
        )

        # Should not raise exception in non-strict mode
        is_valid = self.validator.validate_event(event)
        assert not is_valid
        assert len(self.validator.get_validation_errors()) > 0

    def test_unknown_event_type_handling(self) -> None:
        """Test handling of unknown event types."""
        # Create event with unknown type (this would normally not be possible with enum)
        event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,  # Use valid type for creation
            node_id="test_node",
            metadata={"test": "data"},
        )
        # Manually change to unknown type for testing
        event.event_type = "UNKNOWN_EVENT_TYPE"  # type: ignore

        # Should handle gracefully and not fail validation due to unknown type
        self.validator.validate_event(event)
        # May fail for other reasons but not due to unknown event type handling
        errors = self.validator.get_validation_errors()
        assert any("not a valid OnexEventTypeEnum value" in error for error in errors)

    def test_large_metadata_size_validation(self) -> None:
        """Test validation of metadata size limits."""
        # Create event with very large metadata
        large_metadata = {
            "operation": "test",
            "function": "test",
            "large_data": "x" * (1024 * 1024 + 1),  # > 1MB
        }

        event = OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            node_id="test_node",
            metadata=large_metadata,
        )

        assert not self.validator.validate_event(event)
        errors = self.validator.get_validation_errors()
        assert any("exceeds recommended limit" in error for error in errors)


class TestValidateEventSchemaFunction:
    """Test suite for the validate_event_schema convenience function."""

    def test_valid_event_returns_true(self) -> None:
        """Test that valid events return True."""
        event = OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            node_id="test_node",
            metadata={"operation": "test", "function": "test"},
        )

        assert validate_event_schema(event, strict_mode=False)

    def test_invalid_event_returns_false(self) -> None:
        """Test that invalid events return False in non-strict mode."""
        event = OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            node_id="test_node",
            metadata={},  # Missing required fields
        )

        assert not validate_event_schema(event, strict_mode=False)

    def test_invalid_event_raises_exception_strict(self) -> None:
        """Test that invalid events raise exceptions in strict mode."""
        event = OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            node_id="test_node",
            metadata={},  # Missing required fields
        )

        with pytest.raises(EventSchemaValidationError):
            validate_event_schema(event, strict_mode=True)


class TestCreateCompliantEvent:
    """Test suite for the create_compliant_event function."""

    def test_create_valid_node_start_event(self) -> None:
        """Test creating a valid NODE_START event."""
        event = create_compliant_event(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="test_node",
            correlation_id="test-123",
            metadata={"input_state": {"test": "data"}},
        )

        assert event.event_type == OnexEventTypeEnum.NODE_START
        assert event.node_id == "test_node"
        assert event.correlation_id == "test-123"
        assert event.metadata is not None
        assert "input_state" in event.metadata

    def test_create_valid_telemetry_event(self) -> None:
        """Test creating a valid telemetry event."""
        event = create_compliant_event(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
            node_id="test_node",
            metadata={
                "operation": "test_op",
                "function": "test_func",
                "execution_time_ms": 100.0,
            },
        )

        assert event.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS
        assert event.node_id == "test_node"
        assert event.metadata is not None
        assert event.metadata["operation"] == "test_op"

    def test_create_invalid_event_raises_exception(self) -> None:
        """Test that creating an invalid event raises an exception."""
        with pytest.raises(EventSchemaValidationError):
            create_compliant_event(
                event_type=OnexEventTypeEnum.NODE_START,
                node_id="test_node",
                metadata={},  # Missing required input_state
            )

    def test_auto_generated_fields(self) -> None:
        """Test that auto-generated fields are properly set."""
        event = create_compliant_event(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            node_id="test_node",
            metadata={"operation": "test", "function": "test"},
        )

        assert event.event_id is not None
        assert event.timestamp is not None
        assert isinstance(event.event_id, uuid.UUID)
        assert isinstance(event.timestamp, datetime)

    def test_create_valid_node_start_event_no_exceptions(self) -> None:
        """Test creating a valid NODE_START event without raising exceptions."""
        # Should not raise any exceptions
        create_compliant_event(
            OnexEventTypeEnum.NODE_START,
            "test_node",
            correlation_id="test-123",
            metadata={"test": "data"},
        )
