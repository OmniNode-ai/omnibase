# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_cli_dir_fixture_case.py
# version: 1.0.0
# uuid: 0c8579ca-0754-49a5-951d-4dcb5fed6c90
# author: OmniNode Team
# created_at: 2025-05-22T12:17:04.450510
# last_modified_at: 2025-05-22T20:50:39.727546
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 3f206ad9a2064503ebc9bd71b598179e474621c33405b8585683b1dd64cc8c4e
# entrypoint: python@protocol_cli_dir_fixture_case.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_cli_dir_fixture_case
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import List, Optional, Protocol, Tuple


class ProtocolCLIDirFixtureCase(Protocol):
    id: str
    files: List[Tuple[str, str]]  # List of (relative_path, content)
    subdirs: Optional[List[Tuple[str, List[Tuple[str, str]]]]]  # (subdir, files)
