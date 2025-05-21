# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_stamper_engine.py
# version: 1.0.0
# uuid: 555d0ea2-daee-469a-bbff-b9d4cefa6d87
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167698
# last_modified_at: 2025-05-21T16:42:46.061579
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 1fa4bc55eb530d3bda451a6aa7b7bcd049e31bc2f49890273658b13e277726f7
# entrypoint: {'type': 'python', 'target': 'protocol_stamper_engine.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_stamper_engine
# meta_type: tool
# === /OmniNode:Metadata ===

from pathlib import Path
from typing import List, Optional, Protocol

from omnibase.model.model_enum_template_type import TemplateTypeEnum
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
