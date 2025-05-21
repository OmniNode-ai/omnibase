# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_stamper.py
# version: 1.0.0
# uuid: 97654a90-3f03-40bb-b4ee-5233590d650f
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167633
# last_modified_at: 2025-05-21T16:42:46.109471
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: eb71bac66c2097f9f0ef818a861ec43c13b13f338100ac37fcaf0c3984444fb2
# entrypoint: {'type': 'python', 'target': 'protocol_stamper.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_stamper
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
