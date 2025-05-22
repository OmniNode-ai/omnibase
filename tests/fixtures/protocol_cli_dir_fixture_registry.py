# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_cli_dir_fixture_registry.py
# version: 1.0.0
# uuid: dc24576d-de6c-487e-836a-473d1c129d01
# author: OmniNode Team
# created_at: 2025-05-22T12:17:04.450919
# last_modified_at: 2025-05-22T20:50:39.710754
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 468d2163eceded4ddc84ebf8457ce4e070ae0325a6b16ace553d93d0ca06095d
# entrypoint: python@protocol_cli_dir_fixture_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_cli_dir_fixture_registry
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import List, Protocol

from tests.fixtures.protocol_cli_dir_fixture_case import ProtocolCLIDirFixtureCase


class ProtocolCLIDirFixtureRegistry(Protocol):
    def all_cases(self) -> List[ProtocolCLIDirFixtureCase]: ...
    def get_case(self, case_id: str) -> ProtocolCLIDirFixtureCase: ...
    def filter_cases(self, predicate) -> List[ProtocolCLIDirFixtureCase]: ...
