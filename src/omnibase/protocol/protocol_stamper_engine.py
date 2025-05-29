# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.295679'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_stamper_engine.py
# hash: 6473cfef1a48dfd636ac2e2e0e5c0642743cf4a0829676bac9d1981515e36428
# last_modified_at: '2025-05-29T11:50:12.190332+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_stamper_engine.py
# namespace: omnibase.protocol_stamper_engine
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: e2f209d1-3e49-47e0-9fd5-6732dd51d4e6
# version: 1.0.0
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
