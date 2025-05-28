# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_cli_dir_fixture_registry.py
# version: 1.0.0
# uuid: 7d1d402a-1d9f-4beb-bd31-4675534a97fb
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.107363
# last_modified_at: 2025-05-28T17:20:04.241145
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: f82c5f84948bbafcf45e02415cfd37e03e12e137d5edb1d52d8e4ff3c0d2fe8f
# entrypoint: python@protocol_cli_dir_fixture_registry.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_cli_dir_fixture_registry
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Callable, List, Protocol
from unittest import mock

import pytest

from omnibase.protocol.protocol_cli_dir_fixture_case import ProtocolCLIDirFixtureCase


class ProtocolCLIDirFixtureRegistry(Protocol):
    def all_cases(self) -> List[ProtocolCLIDirFixtureCase]: ...
    def get_case(self, case_id: str) -> ProtocolCLIDirFixtureCase: ...
    def filter_cases(
        self, predicate: Callable[[ProtocolCLIDirFixtureCase], bool]
    ) -> List[ProtocolCLIDirFixtureCase]: ...


@pytest.fixture
def cli_fixture_registry() -> ProtocolCLIDirFixtureRegistry:
    # Implementation of the fixture
    return mock.MagicMock(spec=ProtocolCLIDirFixtureRegistry)
