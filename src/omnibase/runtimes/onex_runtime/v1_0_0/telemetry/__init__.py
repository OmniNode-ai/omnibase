# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: __init__.py
# version: 1.0.0
# uuid: 81acbf71-7587-4ba4-9d63-097f7b233986
# author: OmniNode Team
# created_at: 2025-05-25T13:55:41.213762
# last_modified_at: 2025-05-25T17:58:01.578397
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 63ba8ab9c37f19df82b6605d5b1bd5b0d8b775e69653b480f833f664bdd011dc
# entrypoint: python@__init__.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.init
# meta_type: tool
# === /OmniNode:Metadata ===


"""
ONEX Runtime Telemetry Module.

This module provides telemetry and observability functionality for all ONEX nodes.
It includes decorators for automatic telemetry collection, event emission, and
real-time monitoring capabilities.
"""

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
]
