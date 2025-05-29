# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.493608'
# description: Stamped by PythonHandler
# entrypoint: python://cli_stamp_fixtures.py
# hash: 71a1664d711fccd5d2194a917fd75c93580be7d4c082162470256327f55d4527
# last_modified_at: '2025-05-29T11:50:10.803982+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: cli_stamp_fixtures.py
# namespace: omnibase.cli_stamp_fixtures
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

from omnibase.protocol.protocol_cli_dir_fixture_case import ProtocolCLIDirFixtureCase
from omnibase.protocol.protocol_cli_dir_fixture_registry import (
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
    for rel_path, content in case.files:
        (tmp_path / rel_path).write_text(content)
    if case.subdirs:
        for subdir, files in case.subdirs:
            subdir_path = tmp_path / subdir
            subdir_path.mkdir()
            for rel_path, content in files:
                (subdir_path / rel_path).write_text(content)
    return tmp_path, case


@pytest.fixture
def cli_stamp_fixtures() -> List[ProtocolCLIDirFixtureCase]:
    return CLI_STAMP_DIR_FIXTURES
