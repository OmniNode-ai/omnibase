# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_cli_dir_fixture_case.py
# version: 1.0.0
# uuid: 78e37258-29cf-420f-aafd-7af0523cd1b6
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.097025
# last_modified_at: 2025-05-28T17:20:05.991216
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 1095e0fc2275f3b5e75414c8310ca6464cb52a67b03f2377ddcfef3a7946aaf5
# entrypoint: python@protocol_cli_dir_fixture_case.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_cli_dir_fixture_case
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import List, Optional, Protocol, Tuple


class ProtocolCLIDirFixtureCase(Protocol):
    id: str
    files: List[Tuple[str, str]]  # List of (relative_path, content)
    subdirs: Optional[List[Tuple[str, List[Tuple[str, str]]]]]  # (subdir, files)
