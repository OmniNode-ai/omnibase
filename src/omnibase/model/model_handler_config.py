# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: model_handler_config.py
# version: 1.0.0
# uuid: c6cae84d-f423-4d9b-a85c-12377cc25bcc
# author: OmniNode Team
# created_at: 2025-05-28T08:55:22.046606
# last_modified_at: 2025-05-28T15:55:26.258109
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d67d48ed58edf6092fe946565d0997329b35461bb85c8168bab9a9025c248e5b
# entrypoint: python@model_handler_config.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.model_handler_config
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Pydantic model for file type handler configuration.

This module provides structured configuration for file type handlers,
including processing categories, patterns, and priority settings.
"""

from typing import List
from pydantic import BaseModel, Field, ConfigDict


class HandlerConfig(BaseModel):
    """
    Configuration model for file type handlers.
    
    This model defines the configuration structure for file type handlers,
    including their processing capabilities, supported patterns, and priority.
    """
    
    handler_name: str = Field(
        description="Unique name identifier for the handler"
    )
    processing_category: str = Field(
        description="Category of processing this handler performs"
    )
    force_processing_patterns: List[str] = Field(
        default_factory=list,
        description="File patterns this handler should process despite ignore rules"
    )
    supported_extensions: List[str] = Field(
        default_factory=list,
        description="File extensions this handler can process"
    )
    supported_filenames: List[str] = Field(
        default_factory=list,
        description="Specific filenames this handler can process"
    )
    priority: int = Field(
        default=50,
        description="Handler priority for conflict resolution (higher wins)"
    )
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "handler_name": "node_contract_handler",
                "processing_category": "contract_processing",
                "force_processing_patterns": ["node.onex.yaml", "*_contract.yaml"],
                "supported_extensions": [".yaml"],
                "supported_filenames": ["node.onex.yaml"],
                "priority": 75
            }
        }
    )
