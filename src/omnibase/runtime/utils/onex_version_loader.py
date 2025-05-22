# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: onex_version_loader.py
# version: 1.0.0
# uuid: 482f2a10-9232-4585-81b9-79bf439ac355
# author: OmniNode Team
# created_at: 2025-05-22T05:34:29.793229
# last_modified_at: 2025-05-22T20:50:39.711500
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 26c707fec6d82d4570e0038e285b454ac442ab3e24b39d4585e2ff367253972b
# entrypoint: python@onex_version_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.onex_version_loader
# meta_type: tool
# === /OmniNode:Metadata ===


"""
ONEX utility for loading version information from .onexversion files.
Implements ProtocolOnexVersionLoader and returns a strongly-typed OnexVersionInfo model.
"""


import os
from pathlib import Path

import yaml

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
