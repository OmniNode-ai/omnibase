# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-01-27T00:00:00.000000'
# description: Discovery module for ONEX runtime handlers
# entrypoint: python://__init__
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# last_modified_at: '2025-01-27T00:00:00.000000'
# lifecycle: active
# meta_type: module
# metadata_version: 0.1.0
# name: __init__.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.discovery
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 00000000-0000-0000-0000-000000000000
# version: 1.0.0
# === /OmniNode:Metadata ===

"""
Discovery module for ONEX runtime handlers.

This module provides handler discovery implementations for the ONEX runtime,
enabling plugin-based handler registration without hardcoded imports.
"""

from .runtime_handler_discovery import RuntimeHandlerDiscovery

__all__ = ["RuntimeHandlerDiscovery"]
