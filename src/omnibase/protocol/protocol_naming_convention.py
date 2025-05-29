# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.132271'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_naming_convention.py
# hash: 65e7f6be912cf0243dc9343b87b6df68eed670374869f27d4ef302f507707574
# last_modified_at: '2025-05-29T11:50:12.135172+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_naming_convention.py
# namespace: omnibase.protocol_naming_convention
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: b403ea41-293d-4927-8dc8-e7208b8d28fa
# version: 1.0.0
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
