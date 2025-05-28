# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: event_schema_validator.py
# version: 1.0.0
# uuid: 625e8987-0ac3-4bb7-930f-86e870c645e0
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.691415
# last_modified_at: 2025-05-28T17:20:03.841150
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9e8a5476a58b4b52f78ca09d8213f85eff57726e4e0469b7eb0eb46dc1a1f729
# entrypoint: python@event_schema_validator.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.event_schema_validator
# meta_type: tool
# === /OmniNode:Metadata ===


"""
ONEX Event Schema Validator.

This module provides validation utilities to ensure all events conform to the
canonical ONEX event schema as defined in docs/protocol/onex_event_schema.md.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from omnibase.core.core_error_codes import OnexError
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class EventSchemaValidationError(Exception):
    """Raised when an event does not conform to the ONEX event schema."""

    pass


class OnexEventSchemaValidator:
    """
    Validator for ONEX event schema compliance.

    Validates events against the canonical schema defined in the protocol documentation.
    """

    # Required metadata fields for each event type
    REQUIRED_METADATA_FIELDS: Dict[OnexEventTypeEnum, Set[str]] = {
        OnexEventTypeEnum.NODE_START: {"input_state"},
        OnexEventTypeEnum.NODE_SUCCESS: {"input_state", "output_state"},
        OnexEventTypeEnum.NODE_FAILURE: {"input_state", "error"},
        OnexEventTypeEnum.TELEMETRY_OPERATION_START: {"operation", "function"},
        OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS: {
            "operation",
            "function",
            "execution_time_ms",
        },
        OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR: {
            "operation",
            "function",
            "execution_time_ms",
            "error_type",
            "error_message",
        },
    }

    # Optional but recommended metadata fields
    RECOMMENDED_METADATA_FIELDS: Dict[OnexEventTypeEnum, Set[str]] = {
        OnexEventTypeEnum.NODE_START: {"node_version", "operation_type"},
        OnexEventTypeEnum.NODE_SUCCESS: {"execution_time_ms", "result_summary"},
        OnexEventTypeEnum.NODE_FAILURE: {"error_type", "execution_time_ms"},
        OnexEventTypeEnum.TELEMETRY_OPERATION_START: {"args_count", "kwargs_keys"},
        OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS: {"result_type", "success"},
        OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR: {"success", "recoverable"},
    }

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, raise exceptions on validation failures.
                        If False, log warnings instead.
        """
        self.strict_mode = strict_mode
        self.validation_errors: List[str] = []

    def validate_event(self, event: OnexEvent) -> bool:
        """
        Validate an event against the ONEX event schema.

        Args:
            event: The event to validate

        Returns:
            True if the event is valid, False otherwise

        Raises:
            EventSchemaValidationError: If strict_mode is True and validation fails
        """
        self.validation_errors.clear()

        # Validate required fields
        self._validate_required_fields(event)

        # Validate metadata schema
        self._validate_metadata_schema(event)

        # Validate field types and constraints
        self._validate_field_constraints(event)

        # Handle validation results
        if self.validation_errors:
            error_message = (
                f"Event schema validation failed: {'; '.join(self.validation_errors)}"
            )
            if self.strict_mode:
                raise EventSchemaValidationError(error_message)
            else:
                emit_log_event(
                    LogLevelEnum.WARNING,
                    error_message,
                    node_id=_COMPONENT_NAME,
                )
            return False

        return True

    def _validate_required_fields(self, event: OnexEvent) -> None:
        """Validate that all required fields are present and non-empty."""
        if not event.event_id:
            self.validation_errors.append("event_id is required")

        if not event.timestamp:
            self.validation_errors.append("timestamp is required")

        if not event.node_id:
            self.validation_errors.append("node_id is required and must be non-empty")

        if not event.event_type:
            self.validation_errors.append("event_type is required")

        # Validate event_type is a valid enum value
        try:
            # Check if the event_type is a valid enum member
            if event.event_type not in [e.value for e in OnexEventTypeEnum]:
                self.validation_errors.append(
                    f"event_type '{event.event_type}' is not a valid OnexEventTypeEnum value"
                )
        except (TypeError, AttributeError):
            # Handle cases where event_type is not a string or enum
            self.validation_errors.append(
                f"event_type '{event.event_type}' is not a valid OnexEventTypeEnum value"
            )

    def _validate_metadata_schema(self, event: OnexEvent) -> None:
        """Validate metadata schema based on event type."""
        if event.event_type not in self.REQUIRED_METADATA_FIELDS:
            # Unknown event type - log warning but don't fail validation
            emit_log_event(
                LogLevelEnum.WARNING,
                f"Unknown event type: {event.event_type}",
                node_id=_COMPONENT_NAME,
            )
            return

        required_fields = self.REQUIRED_METADATA_FIELDS[event.event_type]
        recommended_fields = self.RECOMMENDED_METADATA_FIELDS.get(
            event.event_type, set()
        )

        if not event.metadata:
            if required_fields:
                self.validation_errors.append(
                    f"metadata is required for event type {event.event_type}"
                )
            return

        # Check required metadata fields
        missing_required = required_fields - set(event.metadata.keys())
        if missing_required:
            self.validation_errors.append(
                f"Missing required metadata fields for {event.event_type}: {missing_required}"
            )

        # Check recommended metadata fields (warning only)
        missing_recommended = recommended_fields - set(event.metadata.keys())
        if missing_recommended:
            emit_log_event(
                LogLevelEnum.INFO,
                f"Missing recommended metadata fields for {event.event_type}: {missing_recommended}",
                node_id=_COMPONENT_NAME,
            )

    def _validate_field_constraints(self, event: OnexEvent) -> None:
        """Validate field type constraints and business rules."""
        # Validate timestamp is UTC (basic check)
        if event.timestamp and event.timestamp.tzinfo is not None:
            emit_log_event(
                LogLevelEnum.WARNING,
                "Timestamp should be in UTC (timezone-naive)",
                node_id=_COMPONENT_NAME,
            )

        # Validate metadata size (recommend < 1MB)
        if event.metadata:
            try:
                import json

                metadata_size = len(json.dumps(event.metadata, default=str))
                if metadata_size > 1024 * 1024:  # 1MB
                    self.validation_errors.append(
                        f"Metadata size ({metadata_size} bytes) exceeds recommended limit (1MB)"
                    )
            except (TypeError, OnexError) as e:
                self.validation_errors.append(f"Metadata is not JSON-serializable: {e}")

        # Validate specific field types in metadata
        self._validate_metadata_field_types(event)

    def _validate_metadata_field_types(self, event: OnexEvent) -> None:
        """Validate specific metadata field types."""
        metadata = event.metadata

        if metadata is None:
            return

        # Validate execution_time_ms is a number
        if "execution_time_ms" in metadata:
            if not isinstance(metadata["execution_time_ms"], (int, float)):
                self.validation_errors.append(
                    "execution_time_ms must be a number (int or float)"
                )

        # Validate success is a boolean
        if "success" in metadata:
            if not isinstance(metadata["success"], bool):
                self.validation_errors.append("success must be a boolean")

        # Validate args_count is an integer
        if "args_count" in metadata:
            if not isinstance(metadata["args_count"], int):
                self.validation_errors.append("args_count must be an integer")

        # Validate kwargs_keys is a list
        if "kwargs_keys" in metadata:
            if not isinstance(metadata["kwargs_keys"], list):
                self.validation_errors.append("kwargs_keys must be a list")

    def get_validation_errors(self) -> List[str]:
        """Get the list of validation errors from the last validation."""
        return self.validation_errors.copy()


def validate_event_schema(event: OnexEvent, strict_mode: bool = False) -> bool:
    """
    Convenience function to validate a single event.

    Args:
        event: The event to validate
        strict_mode: If True, raise exceptions on validation failures

    Returns:
        True if the event is valid, False otherwise

    Raises:
        EventSchemaValidationError: If strict_mode is True and validation fails
    """
    validator = OnexEventSchemaValidator(strict_mode=strict_mode)
    return validator.validate_event(event)


def create_compliant_event(
    event_type: OnexEventTypeEnum,
    node_id: str,
    correlation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> OnexEvent:
    """
    Create an event that is guaranteed to be schema-compliant.

    Args:
        event_type: Type of event to create
        node_id: ID of the node emitting the event
        correlation_id: Optional correlation ID
        metadata: Event metadata

    Returns:
        A schema-compliant OnexEvent

    Raises:
        EventSchemaValidationError: If the created event is not schema-compliant
    """
    event = OnexEvent(
        event_type=event_type,
        node_id=node_id,
        correlation_id=correlation_id,
        metadata=metadata or {},
    )

    # Validate the created event
    if not validate_event_schema(event, strict_mode=True):
        raise EventSchemaValidationError("Failed to create schema-compliant event")

    return event
