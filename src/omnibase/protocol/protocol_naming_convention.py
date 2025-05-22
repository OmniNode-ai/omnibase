# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_naming_convention.py
# version: 1.0.0
# uuid: 1df03540-fa8d-4665-9d4e-3dd03c9cbeeb
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167260
# last_modified_at: 2025-05-21T16:42:46.057611
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: bb05ded7c0f0def5ffcf8119b4b5b6ed790de6fca399024bfb505aaf23148cdc
# entrypoint: python@protocol_naming_convention.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_naming_convention
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Protocol

from omnibase.model.model_naming_convention import NamingConventionResultModel


class ProtocolNamingConvention(Protocol):
    """
    Protocol for ONEX naming convention enforcement.

    Example:
        class MyNamingConvention:
            def validate_name(self, name: str) -> NamingConventionResultModel:
                ...
    """

    def validate_name(self, name: str) -> NamingConventionResultModel: ...
