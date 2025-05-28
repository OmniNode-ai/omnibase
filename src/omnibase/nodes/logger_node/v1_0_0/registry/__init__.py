# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: __init__.py
# version: 1.0.0
# uuid: d3295351-56ce-47e5-a805-b6c071febf28
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.160274
# last_modified_at: 2025-05-28T17:20:03.859140
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 062bd03c7ea7cd2d39b32b392c0d2e66f913538326edf2d29987828facf823ee
# entrypoint: python@__init__.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.init
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Registries for the logger node.

This package contains registry classes that manage the discovery,
registration, and selection of pluggable components.
"""

from .log_format_handler_registry import HandlerRegistration, LogFormatHandlerRegistry

__all__ = [
    "LogFormatHandlerRegistry",
    "HandlerRegistration",
]
