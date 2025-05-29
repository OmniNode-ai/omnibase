# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.736231'
# description: Stamped by PythonHandler
# entrypoint: python://onex_version_loader
# hash: ab72f08c7bae67de01242c597054526dcb9f446f91a46321e2d4733234da37d1
# last_modified_at: '2025-05-29T14:14:00.914422+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: onex_version_loader.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: fcec67c6-dbac-434f-9f2b-e5077c96ceb2
# version: 1.0.0
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
