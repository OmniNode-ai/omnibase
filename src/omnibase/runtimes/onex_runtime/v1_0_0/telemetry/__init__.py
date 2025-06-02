# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.680243'
# description: Stamped by PythonHandler
# entrypoint: python://__init__
# hash: a32ce106ef1cb3623e2723a7683292e6f30cdf0b9a40c41ea5ae327baa563ff0
# last_modified_at: '2025-05-29T14:14:00.823428+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: __init__.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.telemetry.__init__
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 51f38943-e284-47f1-9f74-4f4a35f8ec98
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
ONEX Runtime Telemetry Module.

This module provides telemetry and observability functionality for all ONEX nodes.
It includes decorators for automatic telemetry collection, event emission, and
real-time monitoring capabilities.
"""

from .event_schema_validator import (
    EventSchemaValidationError,
    OnexEventSchemaValidator,
    create_compliant_event,
    validate_event_schema,
)
from .telemetry import (
    _emit_event,
    add_correlation_id_to_state,
    clear_telemetry_handlers,
    get_correlation_id_from_state,
    register_telemetry_handler,
    telemetry,
    unregister_telemetry_handler,
)
from .telemetry_subscriber import (
    TelemetryOutputFormat,
    TelemetrySubscriber,
    create_cli_subscriber,
    monitor_telemetry_realtime,
)

__all__ = [
    # Telemetry decorator and event bus
    "telemetry",
    "register_telemetry_handler",
    "unregister_telemetry_handler",
    "clear_telemetry_handlers",
    "get_correlation_id_from_state",
    "add_correlation_id_to_state",
    "_emit_event",  # For testing purposes
    # Telemetry subscriber
    "TelemetrySubscriber",
    "TelemetryOutputFormat",
    "create_cli_subscriber",
    "monitor_telemetry_realtime",
    # Event schema validation
    "OnexEventSchemaValidator",
    "EventSchemaValidationError",
    "validate_event_schema",
    "create_compliant_event",
]
