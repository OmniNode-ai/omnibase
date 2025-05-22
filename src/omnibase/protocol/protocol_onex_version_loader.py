# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_onex_version_loader.py
# version: 1.0.0
# uuid: acecc006-5c00-4c7b-8c00-7aafdb662626
# author: OmniNode Team
# created_at: 2025-05-22T17:18:16.711596
# last_modified_at: 2025-05-22T21:19:13.521017
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a04409fe458a3f225998f769c970709bd5dbf8df57e2dcb29625096dd6fad4c3
# entrypoint: python@protocol_onex_version_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_onex_version_loader
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Protocol

from omnibase.model.model_onex_version import OnexVersionInfo


class ProtocolOnexVersionLoader(Protocol):
    """
    Protocol for loading ONEX version information from .onexversion files.
    """

    def get_onex_versions(self) -> OnexVersionInfo: ...
