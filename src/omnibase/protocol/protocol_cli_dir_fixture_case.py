# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.097025'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_cli_dir_fixture_case.py
# hash: 91320092f9aca797a405273512ce5c240d80df6a9ca887631c2c790609a42192
# last_modified_at: '2025-05-29T11:50:12.065015+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_cli_dir_fixture_case.py
# namespace: omnibase.protocol_cli_dir_fixture_case
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 78e37258-29cf-420f-aafd-7af0523cd1b6
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import List, Optional, Protocol, Tuple


class ProtocolCLIDirFixtureCase(Protocol):
    id: str
    files: List[Tuple[str, str]]  # List of (relative_path, content)
    subdirs: Optional[List[Tuple[str, List[Tuple[str, str]]]]]  # (subdir, files)
