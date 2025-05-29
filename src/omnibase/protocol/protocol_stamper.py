# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.153817'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_stamper.py
# hash: 565aa6bd937914c9a1f8ae82d11cac665b1e856499aebb13a33c159a761c8674
# last_modified_at: '2025-05-29T11:50:12.195882+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_stamper.py
# namespace: omnibase.protocol_stamper
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 4b93002d-dee8-4272-a3b6-d17d4ce909d7
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Protocol

from omnibase.enums import TemplateTypeEnum
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
