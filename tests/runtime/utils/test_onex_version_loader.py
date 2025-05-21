import os
import tempfile
from pathlib import Path

import pytest
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
