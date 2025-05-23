# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_output_formatter.py
# version: 1.0.0
# uuid: f3184427-0c36-42cd-ad98-6bfa25f16e18
# author: OmniNode Team
# created_at: 2025-05-21T13:18:56.569533
# last_modified_at: 2025-05-22T20:50:39.740370
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: c08c6e55cda9a1472e7b2e171fd514cb4ed3144e9c77b48e71dbb854e2d75195
# entrypoint: python@protocol_output_formatter.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_output_formatter
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
