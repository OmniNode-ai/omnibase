# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: __init__.py
# version: 1.0.0
# uuid: ed5ffb1c-3f06-4390-aba6-80c077c5374d
# author: OmniNode Team
# created_at: 2025-05-26T12:15:42.760715
# last_modified_at: 2025-05-26T16:53:38.725336
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 480a3860095b2c58d7c3b8d21ddbc5b64d49ce868ee374295742cae5e8aefade
# entrypoint: python@__init__.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.init
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
