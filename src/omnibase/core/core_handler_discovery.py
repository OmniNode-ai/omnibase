# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-01-27T00:00:00.000000'
# description: Core handler discovery for ONEX core handlers
# entrypoint: python://core_handler_discovery
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# last_modified_at: '2025-01-27T00:00:00.000000'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: core_handler_discovery.py
# namespace: python://omnibase.core.core_handler_discovery
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
Core handler discovery for ONEX core handlers.

This module provides discovery of the core ONEX handlers without
requiring hardcoded imports in the core registry. It implements the
ProtocolHandlerDiscovery interface to enable plugin-based handler registration.
"""

from typing import List

from omnibase.protocol.protocol_handler_discovery import (
    HandlerInfo,
    ProtocolHandlerDiscovery,
)


class CoreHandlerDiscovery(ProtocolHandlerDiscovery):
    """
    Discovery implementation for ONEX core handlers.
    
    This class provides the core set of ONEX handlers that are part of the
    core framework, such as ignore file handlers.
    Protocol purity: No direct imports from handlers/ or nodes/ allowed.
    Handlers must be injected or discovered via plugin/entry-point.
    """
    
    def __init__(self, injected_handlers: list = None):
        self._injected_handlers = injected_handlers or []

    def discover_handlers(self) -> List[HandlerInfo]:
        """
        Discover ONEX core handlers (protocol-pure: only injected or plugin-based).
        
        Returns:
            List of HandlerInfo objects for core handlers
        """
        return self._injected_handlers
    
    def get_source_name(self) -> str:
        """
        Get the name of this discovery source.
        
        Returns:
            Human-readable name for this discovery source
        """
        return "ONEX Core Handlers" 