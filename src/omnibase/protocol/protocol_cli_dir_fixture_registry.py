# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.107363'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_cli_dir_fixture_registry.py
# hash: b53ba62f6c1ca3bb9df76e3fcadaeb9183ae5c7db1100fd74fc0d9c7e4a4f4c3
# last_modified_at: '2025-05-29T11:50:12.070812+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_cli_dir_fixture_registry.py
# namespace: omnibase.protocol_cli_dir_fixture_registry
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 7d1d402a-1d9f-4beb-bd31-4675534a97fb
# version: 1.0.0
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
