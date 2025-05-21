# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_output_formatter.py
# version: 1.0.0
# uuid: 26a883c2-e2a3-4253-8f4f-080634814a59
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167385
# last_modified_at: 2025-05-21T16:42:46.053884
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: e9b9c1d5eb90bace4dba07db6c6e272bca97ddba274735310616d5db0bdf5ad2
# entrypoint: {'type': 'python', 'target': 'protocol_output_formatter.py'}
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
