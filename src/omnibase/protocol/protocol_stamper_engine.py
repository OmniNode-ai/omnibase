# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 27bfc2ec-f983-419e-a145-6d1de8dcaa6c
# name: protocol_stamper_engine.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:57.245507
# last_modified_at: 2025-05-19T16:19:57.245510
# description: Stamped Python file: protocol_stamper_engine.py
# state_contract: none
# lifecycle: active
# hash: 28685cc6bb44f902f282c5388e631653725a9b89500a8a2dda290998a7bc60e3
# entrypoint: {'type': 'python', 'target': 'protocol_stamper_engine.py'}
# namespace: onex.stamped.protocol_stamper_engine.py
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
