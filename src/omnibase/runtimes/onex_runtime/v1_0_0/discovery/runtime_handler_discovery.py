# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-01-27T00:00:00.000000'
# description: Runtime handler discovery for ONEX runtime handlers
# entrypoint: python://runtime_handler_discovery
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# last_modified_at: '2025-01-27T00:00:00.000000'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: runtime_handler_discovery.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.discovery.runtime_handler_discovery
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
Runtime handler discovery for ONEX runtime handlers.

This module provides discovery of the standard ONEX runtime handlers without
requiring hardcoded imports in the core registry. It implements the
ProtocolHandlerDiscovery interface to enable plugin-based handler registration.
"""

from typing import List

from omnibase.protocol.protocol_handler_discovery import (
    HandlerInfo,
    ProtocolHandlerDiscovery,
)
from omnibase.enums import HandlerSourceEnum, HandlerPriorityEnum


class RuntimeHandlerDiscovery(ProtocolHandlerDiscovery):
    """
    Discovery implementation for ONEX runtime handlers.
    
    This class provides the standard set of ONEX runtime handlers for file processing
    without requiring hardcoded imports in the core registry.
    """
    
    def discover_handlers(self) -> List[HandlerInfo]:
        """
        Discover ONEX runtime handlers.
        
        Returns:
            List of HandlerInfo objects for runtime handlers
        """
        handlers = []
        
        # Python handler
        try:
            from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_python import PythonHandler
            handlers.append(HandlerInfo(
                handler_class=PythonHandler,
                name="python_handler",
                source=HandlerSourceEnum.RUNTIME,
                priority=HandlerPriorityEnum.RUNTIME,
                extensions=[".py"],
                metadata={"description": "Python file handler with metadata block support"}
            ))
        except ImportError:
            pass
        
        # Markdown handler
        try:
            from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_markdown import MarkdownHandler
            handlers.append(HandlerInfo(
                handler_class=MarkdownHandler,
                name="markdown_handler",
                source=HandlerSourceEnum.RUNTIME,
                priority=HandlerPriorityEnum.RUNTIME,
                extensions=[".md", ".markdown", ".mdx"],
                metadata={"description": "Markdown file handler with metadata block support"}
            ))
        except ImportError:
            pass
        
        # YAML metadata handler
        try:
            from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import MetadataYAMLHandler
            handlers.append(HandlerInfo(
                handler_class=MetadataYAMLHandler,
                name="metadata_yaml_handler",
                source=HandlerSourceEnum.RUNTIME,
                priority=HandlerPriorityEnum.RUNTIME,
                extensions=[".yaml", ".yml"],
                metadata={"description": "YAML metadata file handler"}
            ))
        except ImportError:
            pass
        
        # Node contract handler
        try:
            from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_node_contract import NodeContractHandler
            handlers.append(HandlerInfo(
                handler_class=NodeContractHandler,
                name="node_contract_handler",
                source=HandlerSourceEnum.RUNTIME,
                priority=HandlerPriorityEnum.CONTRACT,
                special_files=["node.onex.yaml"],
                metadata={"description": "Node contract YAML handler"}
            ))
        except ImportError:
            pass
        
        # State contract handler
        try:
            from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_state_contract import StateContractHandler
            handlers.append(HandlerInfo(
                handler_class=StateContractHandler,
                name="state_contract_handler",
                source=HandlerSourceEnum.RUNTIME,
                priority=HandlerPriorityEnum.CONTRACT,
                special_files=["contract.yaml"],
                metadata={"description": "State contract YAML handler"}
            ))
        except ImportError:
            pass
        
        # Project metadata handler
        try:
            from omnibase.runtimes.onex_runtime.v1_0_0.handlers.project_metadata_handler import ProjectMetadataHandler
            handlers.append(HandlerInfo(
                handler_class=ProjectMetadataHandler,
                name="project_metadata_handler",
                source=HandlerSourceEnum.RUNTIME,
                priority=HandlerPriorityEnum.CONTRACT,
                special_files=["project.onex.yaml"],
                metadata={"description": "Project metadata YAML handler"}
            ))
        except ImportError:
            pass
        
        return handlers
    
    def get_source_name(self) -> str:
        """
        Get the name of this discovery source.
        
        Returns:
            Human-readable name for this discovery source
        """
        return "ONEX Runtime Handlers" 