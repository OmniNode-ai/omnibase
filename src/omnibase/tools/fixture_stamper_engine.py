from pathlib import Path
from typing import Optional, List, Dict, Any
from omnibase.protocol.protocol_stamper_engine import ProtocolStamperEngine
from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.model.model_onex_message_result import OnexResultModel
import json
import yaml

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
            raise ValueError(f"Unsupported fixture format: {self.fixture_format}")

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
            raise FileNotFoundError(f"No fixture found for {key}")
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
            raise FileNotFoundError(f"No fixture found for {key}")
        return OnexResultModel.model_validate(result_data) 