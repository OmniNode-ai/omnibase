# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.255525'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_output_formatter.py
# hash: ab6b1c9831a860e6a998510225788dff5328156db6de9a642677d0887cc54343
# last_modified_at: '2025-05-29T11:50:12.162465+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_output_formatter.py
# namespace: omnibase.protocol_output_formatter
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 78bc5693-1149-46fe-a1f3-0cd7c48dcb65
# version: 1.0.0
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
