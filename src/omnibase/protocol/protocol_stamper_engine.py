# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_stamper_engine.py
# version: 1.0.0
# uuid: e2f209d1-3e49-47e0-9fd5-6732dd51d4e6
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.295679
# last_modified_at: 2025-05-28T17:20:05.142965
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: b261ebe45c56f394a398f2587b3690909f5cda68e46ae1d3a4a1884be1d5d750
# entrypoint: python@protocol_stamper_engine.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_stamper_engine
# meta_type: tool
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import List, Optional, Protocol

from omnibase.enums import TemplateTypeEnum
from omnibase.model.model_onex_message_result import OnexResultModel


class ProtocolStamperEngine(Protocol):
    """
    Protocol for stamping ONEX node metadata files and processing directories.
    All arguments must use Pydantic models and Enums as appropriate.
    No file I/O or CLI dependencies in the protocol.
    """

    def stamp_file(
        self,
        path: Path,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
        author: str = "OmniNode Team",
        **kwargs: object,
    ) -> OnexResultModel: ...

    def process_directory(
        self,
        directory: Path,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        recursive: bool = True,
        dry_run: bool = False,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        ignore_file: Optional[Path] = None,
        author: str = "OmniNode Team",
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
    ) -> OnexResultModel: ...
