# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.160274'
# description: Stamped by PythonHandler
# entrypoint: python://__init__
# hash: c275f0b9b38fb50d0ad598bd48b4441446d18216ce6a9205619926eeecb41d31
# last_modified_at: '2025-05-29T14:13:59.302904+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: __init__.py
# namespace: python://omnibase.nodes.logger_node.v1_0_0.registry.__init__
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: d3295351-56ce-47e5-a805-b6c071febf28
# version: 1.0.0
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
