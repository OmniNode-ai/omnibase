# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.493608'
# description: Stamped by PythonHandler
# entrypoint: python://cli_stamp_fixtures
# hash: b82cb96c6504ce0c23f6bfb64f99d65379c3c640fca015c3e1196246e15512de
# last_modified_at: '2025-05-29T14:13:58.606334+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: cli_stamp_fixtures.py
# namespace: python://omnibase.fixtures.cli_stamp_fixtures
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 5653b82b-74fa-452b-8ac0-03fda5dd7110
# version: 1.0.0
# === /OmniNode:Metadata ===


from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple

import pytest
from pydantic import BaseModel

from omnibase.protocol.protocol_cli_dir_fixture_case import ProtocolCLIDirFixtureCase
from omnibase.protocol.protocol_cli_dir_fixture_registry import (
    ProtocolCLIDirFixtureRegistry,
)


class FileEntryModel(BaseModel):
    relative_path: str
    content: str


class SubdirEntryModel(BaseModel):
    subdir: str
    files: List[FileEntryModel]


@dataclass
class CLIDirFixtureCase(ProtocolCLIDirFixtureCase):
    id: str
    files: List[FileEntryModel]  # List of FileEntryModel
    subdirs: Optional[List[SubdirEntryModel]] = None  # List of SubdirEntryModel


# Registry of protocol-compliant test directory/file structures
CLI_STAMP_DIR_FIXTURES: List[ProtocolCLIDirFixtureCase] = [
    CLIDirFixtureCase(
        id="basic_yaml_json",
        files=[
            FileEntryModel(relative_path="test.yaml", content="name: test"),
            FileEntryModel(relative_path="test.json", content='{"name": "test"}'),
            FileEntryModel(
                relative_path="test.txt", content="This is not YAML or JSON"
            ),
        ],
        subdirs=[
            SubdirEntryModel(
                subdir="subdir",
                files=[
                    FileEntryModel(
                        relative_path="sub_test.yaml", content="name: subtest"
                    ),
                    FileEntryModel(
                        relative_path="sub_test.json", content='{"name": "subtest"}'
                    ),
                ],
            )
        ],
    ),
    # Add more protocol-compliant cases as needed
]


class CLIStampDirFixtureRegistry(ProtocolCLIDirFixtureRegistry):
    def __init__(self, cases: List[ProtocolCLIDirFixtureCase]):
        self._cases = {case.id: case for case in cases}

    def all_cases(self) -> List[ProtocolCLIDirFixtureCase]:
        return list(self._cases.values())

    def get_case(self, case_id: str) -> ProtocolCLIDirFixtureCase:
        return self._cases[case_id]

    def filter_cases(
        self, predicate: Callable[[ProtocolCLIDirFixtureCase], bool]
    ) -> List[ProtocolCLIDirFixtureCase]:
        return [case for case in self._cases.values() if predicate(case)]


CLI_STAMP_DIR_FIXTURE_REGISTRY = CLIStampDirFixtureRegistry(CLI_STAMP_DIR_FIXTURES)


@pytest.fixture(params=CLI_STAMP_DIR_FIXTURES, ids=lambda c: c.id)
def cli_stamp_dir_fixture(
    request: Any, tmp_path: Path
) -> Tuple[Path, ProtocolCLIDirFixtureCase]:
    case: ProtocolCLIDirFixtureCase = request.param
    # Create files in tmp_path
    for file_entry in case.files:
        (tmp_path / file_entry.relative_path).write_text(file_entry.content)
    if case.subdirs:
        for subdir_entry in case.subdirs:
            subdir_path = tmp_path / subdir_entry.subdir
            subdir_path.mkdir()
            for file_entry in subdir_entry.files:
                (subdir_path / file_entry.relative_path).write_text(file_entry.content)
    return tmp_path, case


@pytest.fixture
def cli_stamp_fixtures() -> List[ProtocolCLIDirFixtureCase]:
    return CLI_STAMP_DIR_FIXTURES
