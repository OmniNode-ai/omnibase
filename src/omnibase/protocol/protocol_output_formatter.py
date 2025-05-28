# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_output_formatter.py
# version: 1.0.0
# uuid: 78bc5693-1149-46fe-a1f3-0cd7c48dcb65
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.255525
# last_modified_at: 2025-05-28T17:20:05.816543
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 472117c33fa0bee3d9a7a811bfe1fc20c6e3b1fe3a333ca02dc8d14076ffe950
# entrypoint: python@protocol_output_formatter.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_output_formatter
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Protocol

from omnibase.enums import OutputFormatEnum
from omnibase.model.model_output_data import OutputDataModel


class ProtocolOutputFormatter(Protocol):
    """
    Protocol for ONEX output formatting components.

    Example:
        class MyFormatter:
            def format(self, data: OutputDataModel, style: OutputFormatEnum = OutputFormatEnum.JSON) -> str:
                ...
    """

    def format(
        self, data: OutputDataModel, style: OutputFormatEnum = OutputFormatEnum.JSON
    ) -> str: ...
