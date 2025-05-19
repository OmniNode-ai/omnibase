# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: e42d8e7a-aaa7-493a-aacf-cc0c8b2dd38d
# name: protocol_output_formatter.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:53.636066
# last_modified_at: 2025-05-19T16:19:53.636068
# description: Stamped Python file: protocol_output_formatter.py
# state_contract: none
# lifecycle: active
# hash: 29e2a209ad9612795ea4d1d2b985c6fbc3bcd0ae55729c347814122357ca7563
# entrypoint: {'type': 'python', 'target': 'protocol_output_formatter.py'}
# namespace: onex.stamped.protocol_output_formatter.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Protocol

from omnibase.model.model_enum_output_format import OutputFormatEnum
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
