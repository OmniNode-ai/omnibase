# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_cli_dir_fixture_case.py
# version: 1.0.0
# uuid: '0c8579ca-0754-49a5-951d-4dcb5fed6c90'
# author: OmniNode Team
# created_at: '2025-05-22T12:17:04.450510'
# last_modified_at: '2025-05-22T18:05:26.862734'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: protocol_cli_dir_fixture_case.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_cli_dir_fixture_case
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


from typing import List, Optional, Protocol, Tuple


class ProtocolCLIDirFixtureCase(Protocol):
    id: str
    files: List[Tuple[str, str]]  # List of (relative_path, content)
    subdirs: Optional[List[Tuple[str, List[Tuple[str, str]]]]]  # (subdir, files)
