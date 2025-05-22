# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_onex_version_loader.py
# version: 1.0.0
# uuid: 0e8e62f1-17f8-4098-8f0d-f2b82300432b
# author: OmniNode Team
# created_at: 2025-05-22T05:34:29.795799
# last_modified_at: 2025-05-22T18:38:28.740782
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: e651bbfedef38109065f9d6b6c8ad975fddb45784cbf83e397a5170525f75ba4
# entrypoint: python@test_onex_version_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_onex_version_loader
# meta_type: tool
# === /OmniNode:Metadata ===


import os

import yaml

from omnibase.model.model_onex_version import OnexVersionInfo
from omnibase.runtime.utils.onex_version_loader import OnexVersionLoader


def test_onex_version_loader_reads_versions(tmp_path):
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
