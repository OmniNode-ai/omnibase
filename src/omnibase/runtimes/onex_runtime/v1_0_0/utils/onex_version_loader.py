# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: onex_version_loader.py
# version: 1.0.0
# uuid: fcec67c6-dbac-434f-9f2b-e5077c96ceb2
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.736231
# last_modified_at: 2025-05-28T17:20:04.392471
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: b664b204be30b363d09be5ebf221e7b2a73191b1b73b00c114d79b4f9a6e3a7c
# entrypoint: python@onex_version_loader.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.onex_version_loader
# meta_type: tool
# === /OmniNode:Metadata ===


"""
ONEX utility for loading version information from .onexversion files.
Implements ProtocolOnexVersionLoader and returns a strongly-typed OnexVersionInfo model.
"""


import os
from pathlib import Path

import yaml

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.model.model_onex_version import OnexVersionInfo
from omnibase.protocol.protocol_onex_version_loader import ProtocolOnexVersionLoader

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
                raise OnexError(
                    "_version_cache must be an OnexVersionInfo instance",
                    CoreErrorCode.INVALID_PARAMETER,
                )
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
                        raise OnexError(
                            f"Missing {key} in .onexversion at {candidate}",
                            CoreErrorCode.MISSING_REQUIRED_PARAMETER,
                        )
                if not isinstance(data, dict):
                    raise OnexError(
                        ".onexversion must load as a dict",
                        CoreErrorCode.INVALID_PARAMETER,
                    )
                _version_cache = OnexVersionInfo(**data)
                return _version_cache
        raise OnexError(
            ".onexversion file not found in CWD or any parent directory",
            CoreErrorCode.FILE_NOT_FOUND,
        )
