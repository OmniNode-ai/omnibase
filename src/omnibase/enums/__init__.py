# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.465484'
# description: Stamped by PythonHandler
# entrypoint: python://__init__
# hash: 029849e9f0e628f0ad4135568d595059b98812ecd141ff76fac9ae14ce9f2cff
# last_modified_at: '2025-05-29T14:13:58.521683+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: __init__.py
# namespace: python://omnibase.enums.__init__
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 5b27ab08-8f57-4122-8699-214e381b8e89
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Centralized enums package for ONEX.

This file is the canonical source for all enums used throughout the ONEX ecosystem, including:
- ArtifactTypeEnum (protocol artifact types for all nodes/tools)
- Status, handler, file, and template enums

All enums here are intended for import by any ONEX tool, node, or test that needs protocol enum values.
Version: 1.0.0 (increment with any breaking/additive changes)
"""

from enum import Enum

from .enum_node_status import NodeStatusEnum
from .enum_registry_action import RegistryActionEnum
from .enum_registry_entry_status import RegistryEntryStatusEnum
from .enum_registry_execution_mode import RegistryExecutionModeEnum
from .enum_registry_output_status import RegistryOutputStatusEnum
from .enum_trust_state import TrustStateEnum

# File and metadata enums
from .file_status import FileStatusEnum
from .file_type import FileTypeEnum
from .handler_priority import HandlerPriorityEnum
from .handler_source import HandlerSourceEnum
from .handler_type import HandlerTypeEnum
from .ignore_pattern_source import IgnorePatternSourceEnum, TraversalModeEnum
from .log_level import LogLevelEnum, SeverityLevelEnum
from .metadata import (
    EntrypointType,
    FunctionLanguageEnum,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataField,
    ProtocolVersionEnum,
    RuntimeLanguageEnum,
    UriTypeEnum,
)

# New Enum
from .node_name import NodeNameEnum

# Core status enum
from .onex_status import OnexStatus

# Output and formatting enums
from .output_format import OutputFormatEnum

# Template and pattern enums
from .template_type import TemplateTypeEnum

# Validation result enum
from .enum_validation_result import EnumValidationResult


# Protocol artifact type enum (used for all artifact type references in config, models, and protocol logic)
class ArtifactTypeEnum(str, Enum):
    NODES = "nodes"
    CLI_TOOLS = "cli_tools"
    RUNTIMES = "runtimes"
    ADAPTERS = "adapters"
    CONTRACTS = "contracts"
    PACKAGES = "packages"


class NamespaceStrategyEnum(str, Enum):
    ONEX_DEFAULT = "onex_default"
    NONE = "none"
    CUSTOM = "custom"


__all__ = [
    # Core status
    "OnexStatus",
    "NodeStatusEnum",
    "RegistryOutputStatusEnum",
    "RegistryEntryStatusEnum",
    "RegistryActionEnum",
    "RegistryExecutionModeEnum",
    # File and metadata
    "EntrypointType",
    "FileStatusEnum",
    "FileTypeEnum",
    "FunctionLanguageEnum",
    "Lifecycle",
    "MetaTypeEnum",
    "NodeMetadataField",
    "ProtocolVersionEnum",
    "RuntimeLanguageEnum",
    "UriTypeEnum",
    # Output and formatting
    "OutputFormatEnum",
    "LogLevelEnum",
    "SeverityLevelEnum",
    # Template and pattern
    "TemplateTypeEnum",
    "IgnorePatternSourceEnum",
    "TraversalModeEnum",
    "HandlerPriorityEnum",
    "HandlerSourceEnum",
    "HandlerTypeEnum",
    "TrustStateEnum",
    "NodeNameEnum",
    "ArtifactTypeEnum",
    "NamespaceStrategyEnum",
    "EnumValidationResult",
]
