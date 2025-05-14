# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_fixture_struct_index"
# namespace: "omninode.tools.test_fixture_struct_index"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:24+00:00"
# last_modified_at: "2025-05-05T13:00:24+00:00"
# entrypoint: "test_fixture_struct_index.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import pytest
import tempfile
import shutil
from pathlib import Path
from foundation.script.validate.validate_registry import register_fixture

@pytest.fixture
def struct_index_test_tree(tmp_path):
    # Create a directory structure:
    # root/
    #   file1.txt
    #   file2.py
    #   subdir/
    #     file3.md
    #   .treeignore
    root = tmp_path
    (root / "file1.txt").write_text("hello")
    (root / "file2.py").write_text("print('hi')")
    subdir = root / "subdir"
    subdir.mkdir()
    (subdir / "file3.md").write_text("# doc")
    (root / ".treeignore").write_text("*.txt\nsubdir\n")
    return root

register_fixture(
    name="struct_index_test_tree",
    fixture=struct_index_test_tree,
    description="Test directory tree fixture for StructIndex tool tests."
) 