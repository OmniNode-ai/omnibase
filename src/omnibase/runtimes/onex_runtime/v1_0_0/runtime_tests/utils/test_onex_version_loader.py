# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.668901'
# description: Stamped by PythonHandler
# entrypoint: python://test_onex_version_loader.py
# hash: 89abf52e6fee7b5eaf22a10ec07428b609ce63e6fb19dea14c49bdc80599677f
# last_modified_at: '2025-05-29T11:50:12.422704+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_onex_version_loader.py
# namespace: omnibase.test_onex_version_loader
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 8b333a44-8470-4c43-8268-6f4a81129c5f
# version: 1.0.0
# === /OmniNode:Metadata ===


import os
from pathlib import Path

import yaml

from omnibase.model.model_onex_version import OnexVersionInfo
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)


def test_onex_version_loader_reads_versions(tmp_path: Path) -> None:
    # Create a temporary .onexversion file
    version_data = {
        "metadata_version": "1.2.3",
        "protocol_version": "4.5.6",
        "schema_version": "7.8.9",
    }
    version_file = tmp_path / ".onexversion"
    with open(version_file, "w") as f:
        yaml.safe_dump(version_data, f)
    # Change CWD to tmp_path for test isolation
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        loader = OnexVersionLoader()
        result = loader.get_onex_versions()
        assert isinstance(result, OnexVersionInfo)
        assert result.metadata_version == "1.2.3"
        assert result.protocol_version == "4.5.6"
        assert result.schema_version == "7.8.9"
    finally:
        os.chdir(old_cwd)
