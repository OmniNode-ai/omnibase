# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 084678be-eaf3-480f-bb4a-f13617de17b4
# name: protocol_stamper.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:54.618826
# last_modified_at: 2025-05-19T16:19:54.618830
# description: Stamped Python file: protocol_stamper.py
# state_contract: none
# lifecycle: active
# hash: 284cd00eb9fac36d6d3ecb3d8a226d8b99675e57abe33dd5b175d87b5f7a1b6b
# entrypoint: {'type': 'python', 'target': 'protocol_stamper.py'}
# namespace: onex.stamped.protocol_stamper.py
# meta_type: tool
# === /OmniNode:Metadata ===

from pathlib import Path
from typing import Protocol

from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.model.model_onex_message_result import OnexResultModel


class ProtocolStamper(Protocol):
    """
    Protocol for stamping ONEX node metadata with hashes, signatures, or trace data.

    Example:
        class MyStamper:
            def stamp(self, path: str) -> OnexResultModel:
                ...
    """

    def stamp(self, path: str) -> OnexResultModel:
        """Stamp an ONEX metadata file at the given path."""
        ...

    def stamp_file(
        self,
        path: Path,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
        author: str = "OmniNode Team",
        **kwargs: object,
    ) -> OnexResultModel:
        """
        Stamp the file with a metadata block, replacing any existing block.
        :return: OnexResultModel describing the operation result.
        """
        ...
