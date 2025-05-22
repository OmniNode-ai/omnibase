# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_cli_dir_fixture_registry.py
# version: 1.0.0
# uuid: 'dc24576d-de6c-487e-836a-473d1c129d01'
# author: OmniNode Team
# created_at: '2025-05-22T12:17:04.450919'
# last_modified_at: '2025-05-22T18:05:26.847673'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: protocol_cli_dir_fixture_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_cli_dir_fixture_registry
# meta_type: tool
# trust_score: null
# tags: null
# capabilities: null
# protocols_supported: null
# base_class: null
# dependencies: null
# inputs: null
# outputs: null
# environment: null
# license: null
# signature_block: null
# x_extensions: {}
# testing: null
# os_requirements: null
# architectures: null
# container_image_reference: null
# compliance_profiles: []
# data_handling_declaration: null
# logging_config: null
# source_repository: null
# === /OmniNode:Metadata ===


from typing import List, Protocol

from tests.fixtures.protocol_cli_dir_fixture_case import ProtocolCLIDirFixtureCase


class ProtocolCLIDirFixtureRegistry(Protocol):
    def all_cases(self) -> List[ProtocolCLIDirFixtureCase]: ...
    def get_case(self, case_id: str) -> ProtocolCLIDirFixtureCase: ...
    def filter_cases(self, predicate) -> List[ProtocolCLIDirFixtureCase]: ...
