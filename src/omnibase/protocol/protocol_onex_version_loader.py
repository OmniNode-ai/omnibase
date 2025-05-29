# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.233485'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_onex_version_loader.py
# hash: 60e34704237ec6a56041ce2cc941554dad18177776f0385356d790d700768181
# last_modified_at: '2025-05-29T11:50:12.151714+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_onex_version_loader.py
# namespace: omnibase.protocol_onex_version_loader
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 517b7eb6-e9ad-4683-924f-cae0ac93a64f
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Protocol

from omnibase.model.model_onex_version import OnexVersionInfo


class ProtocolOnexVersionLoader(Protocol):
    """
    Protocol for loading ONEX version information from .onexversion files.
    """

    def get_onex_versions(self) -> OnexVersionInfo: ...
