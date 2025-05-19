# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 382ec701-2e46-4ea9-a225-59976980a00a
# name: protocol_naming_convention.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:53.344635
# last_modified_at: 2025-05-19T16:19:53.344637
# description: Stamped Python file: protocol_naming_convention.py
# state_contract: none
# lifecycle: active
# hash: 453f272a89159bb0619ece33fc91e39256d52f11cc6073293301cdcb63efed3c
# entrypoint: {'type': 'python', 'target': 'protocol_naming_convention.py'}
# namespace: onex.stamped.protocol_naming_convention.py
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
