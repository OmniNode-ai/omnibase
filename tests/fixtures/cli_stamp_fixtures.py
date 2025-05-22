# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: cli_stamp_fixtures.py
# version: 1.0.0
# uuid: 5c094657-c28d-4c09-831f-c277f50931d7
# author: OmniNode Team
# created_at: 2025-05-22T14:03:21.906752
# last_modified_at: 2025-05-22T20:50:39.737232
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 8fce3b51134cfe8982cdb221060fa0e8d58b458f7da50fe03072b90735697ffa
# entrypoint: python@cli_stamp_fixtures.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.cli_stamp_fixtures
# meta_type: tool
# === /OmniNode:Metadata ===


from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import pytest

from tests.fixtures.protocol_cli_dir_fixture_case import ProtocolCLIDirFixtureCase
from tests.fixtures.protocol_cli_dir_fixture_registry import (
    ProtocolCLIDirFixtureRegistry,
)


@dataclass
class CLIDirFixtureCase(ProtocolCLIDirFixtureCase):
    id: str
    files: List[Tuple[str, str]]  # List of (relative_path, content)
    subdirs: Optional[List[Tuple[str, List[Tuple[str, str]]]]] = None  # (subdir, files)


# Registry of protocol-compliant test directory/file structures
CLI_STAMP_DIR_FIXTURES: List[ProtocolCLIDirFixtureCase] = [
    CLIDirFixtureCase(
        id="basic_yaml_json",
        files=[
            ("test.yaml", "name: test"),
            ("test.json", '{"name": "test"}'),
            ("test.txt", "This is not YAML or JSON"),
        ],
        subdirs=[
            (
                "subdir",
                [
                    ("sub_test.yaml", "name: subtest"),
                    ("sub_test.json", '{"name": "subtest"}'),
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

    def filter_cases(self, predicate) -> List[ProtocolCLIDirFixtureCase]:
        return [case for case in self._cases.values() if predicate(case)]


CLI_STAMP_DIR_FIXTURE_REGISTRY = CLIStampDirFixtureRegistry(CLI_STAMP_DIR_FIXTURES)


@pytest.fixture(params=CLI_STAMP_DIR_FIXTURES, ids=lambda c: c.id)
def cli_stamp_dir_fixture(
    request, tmp_path: Path
) -> Tuple[Path, ProtocolCLIDirFixtureCase]:
    case: ProtocolCLIDirFixtureCase = request.param
    # Create files in tmp_path
    for rel_path, content in case.files:
        (tmp_path / rel_path).write_text(content)
    if case.subdirs:
        for subdir, files in case.subdirs:
            subdir_path = tmp_path / subdir
            subdir_path.mkdir()
            for rel_path, content in files:
                (subdir_path / rel_path).write_text(content)
    return tmp_path, case
