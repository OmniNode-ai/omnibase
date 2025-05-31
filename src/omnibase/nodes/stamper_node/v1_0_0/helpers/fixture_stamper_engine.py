# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.629366'
# description: Stamped by PythonHandler
# entrypoint: python://fixture_stamper_engine
# hash: 3c63400a2fc5f90adadb411d3d1892d0e53231af7acc3a743e823e51ae4f3a30
# last_modified_at: '2025-05-29T14:13:59.809386+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: fixture_stamper_engine.py
# namespace: python://omnibase.nodes.stamper_node.v1_0_0.helpers.fixture_stamper_engine
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: b33911be-1b93-4ccf-92d1-cb047c1b7313
# version: 1.0.0
# === /OmniNode:Metadata ===


import json
from pathlib import Path
from typing import Any, List, Optional

import yaml

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import TemplateTypeEnum
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_stamper_engine import ProtocolStamperEngine


class FixtureStamperEngine(ProtocolStamperEngine):
    def __init__(self, fixture_path: Path, fixture_format: str = "json") -> None:
        super().__init__()
        self.fixture_path = fixture_path
        self.fixture_format = fixture_format
        self.fixtures = self._load_fixtures()
        # Always instantiate DirectoryTraverser with event_bus=None for fixture
        from omnibase.utils.directory_traverser import DirectoryTraverser
        self.directory_traverser = DirectoryTraverser(event_bus=None)

    def _load_fixtures(self) -> dict:
        if self.fixture_format == "json":
            with open(self.fixture_path, "r") as f:
                return json.load(f)
        elif self.fixture_format == "yaml":
            with open(self.fixture_path, "r") as f:
                return yaml.safe_load(f)
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
        event_bus: Optional[object] = None,
    ) -> OnexResultModel:
        # Use the directory name as the key to look up the fixture result
        key = str(directory)
        result_data = self.fixtures.get(key) or self.fixtures.get(directory.name)
        if not result_data:
            raise OnexError(
                f"No fixture found for {key}", CoreErrorCode.RESOURCE_NOT_FOUND
            )
        return OnexResultModel.model_validate(result_data)
