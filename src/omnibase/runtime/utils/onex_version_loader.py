# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: onex_version_loader.py
# version: 1.0.0
# uuid: '482f2a10-9232-4585-81b9-79bf439ac355'
# author: OmniNode Team
# created_at: '2025-05-22T05:34:29.793229'
# last_modified_at: '2025-05-22T18:33:30.854099'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: onex_version_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.onex_version_loader
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


"""
ONEX utility for loading version information from .onexversion files.
Implements ProtocolOnexVersionLoader and returns a strongly-typed OnexVersionInfo model.
"""


import os
from pathlib import Path

import yaml

from omnibase.model.model_onex_version import OnexVersionInfo
from omnibase.runtime.protocol.protocol_onex_version_loader import (
    ProtocolOnexVersionLoader,
)

_version_cache = None


class OnexVersionLoader(ProtocolOnexVersionLoader):
    """
    Canonical implementation of ProtocolOnexVersionLoader.
    Loads ONEX version info from .onexversion files and returns an OnexVersionInfo model.
    """

    def get_onex_versions(self) -> OnexVersionInfo:
        global _version_cache
        if _version_cache is not None:
            if not isinstance(_version_cache, OnexVersionInfo):
                raise TypeError("_version_cache must be an OnexVersionInfo instance")
            return _version_cache
        cwd = Path(os.getcwd())
        search_dirs = [cwd]
        search_dirs += list(cwd.parents)
        search_dirs.append(Path(__file__).parent.parent.parent.parent)
        for d in search_dirs:
            candidate = d / ".onexversion"
            if candidate.exists():
                with open(candidate, "r") as f:
                    data = yaml.safe_load(f)
                for key in ("metadata_version", "protocol_version", "schema_version"):
                    if key not in data:
                        raise ValueError(
                            f"Missing {key} in .onexversion at {candidate}"
                        )
                if not isinstance(data, dict):
                    raise TypeError(".onexversion must load as a dict")
                _version_cache = OnexVersionInfo(**data)
                return _version_cache
        raise FileNotFoundError(
            ".onexversion file not found in CWD or any parent directory"
        )
