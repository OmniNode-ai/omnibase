# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_onex_version_loader.py
# version: 1.0.0
# uuid: 517b7eb6-e9ad-4683-924f-cae0ac93a64f
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.233485
# last_modified_at: 2025-05-28T17:20:04.308683
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 95953f37cbe0bdeb65676b791b33c57a19be124ca33f817b6c54ebf284ba7a85
# entrypoint: python@protocol_onex_version_loader.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_onex_version_loader
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Protocol

from omnibase.model.model_onex_version import OnexVersionInfo


class ProtocolOnexVersionLoader(Protocol):
    """
    Protocol for loading ONEX version information from .onexversion files.
    """

    def get_onex_versions(self) -> OnexVersionInfo: ...
