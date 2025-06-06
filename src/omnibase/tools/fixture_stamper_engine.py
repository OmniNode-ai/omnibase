# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: fixture_stamper_engine.py
# version: 1.0.0
# uuid: 4b2aa2a2-0cc2-402b-8ed0-d66c61277b3b
# author: OmniNode Team
# created_at: 2025-05-21T13:18:56.573196
# last_modified_at: 2025-05-22T20:50:39.729182
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 83193040711ca5d5de14deab26fde731bcb2af2639308cde1befd296a2d02316
# entrypoint: python@fixture_stamper_engine.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.fixture_stamper_engine
# meta_type: tool
# === /OmniNode:Metadata ===


import json
from pathlib import Path
from typing import Any, List, Optional

import yaml

from omnibase.core.error_codes import CoreErrorCode, OnexError
from omnibase.enums import TemplateTypeEnum
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_stamper_engine import ProtocolStamperEngine


class FixtureStamperEngine(ProtocolStamperEngine):
    def __init__(self, fixture_path: Path, fixture_format: str = "json") -> None:
        self.fixture_path = fixture_path
        self.fixture_format = fixture_format
        self._load_fixtures()

    def _load_fixtures(self) -> None:
        if self.fixture_format == "json":
            with open(self.fixture_path, "r") as f:
                self.fixtures = json.load(f)
        elif self.fixture_format == "yaml":
            with open(self.fixture_path, "r") as f:
                self.fixtures = yaml.safe_load(f)
        else:
            raise OnexError(
                f"Unsupported fixture format: {self.fixture_format}",
                CoreErrorCode.INVALID_PARAMETER,
            )

    def stamp_file(
        self,
        path: Path,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
        author: str = "OmniNode Team",
        **kwargs: Any,
    ) -> OnexResultModel:
        # Use the file name as the key to look up the fixture result
        key = str(path)
        result_data = self.fixtures.get(key) or self.fixtures.get(path.name)
        if not result_data:
            raise OnexError(
                f"No fixture found for {key}", CoreErrorCode.RESOURCE_NOT_FOUND
            )
        # Assume result_data is a dict compatible with OnexResultModel
        return OnexResultModel.model_validate(result_data)

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
    ) -> OnexResultModel:
        # Use the directory name as the key to look up the fixture result
        key = str(directory)
        result_data = self.fixtures.get(key) or self.fixtures.get(directory.name)
        if not result_data:
            raise OnexError(
                f"No fixture found for {key}", CoreErrorCode.RESOURCE_NOT_FOUND
            )
        return OnexResultModel.model_validate(result_data)
