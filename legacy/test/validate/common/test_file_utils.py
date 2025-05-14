# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_file_utils"
# namespace: "omninode.tools.test_file_utils"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T17:01:19+00:00"
# last_modified_at: "2025-05-05T17:01:19+00:00"
# entrypoint: "test_file_utils.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import tempfile
from pathlib import Path
import pytest
from foundation.script.validate.common.common_file_utils import FileUtils

@pytest.fixture(autouse=True)
def register_file_utils(utility_registry):
    utility_registry.register('file_utils', FileUtils())

def test_check_file_extension(utility_registry):
    file_utils = utility_registry.get('file_utils')
    with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
        assert file_utils.check_file_extension(Path(tmp.name), {'.txt', '.md'})
        assert not file_utils.check_file_extension(Path(tmp.name), {'.md'})

def test_file_exists(utility_registry):
    file_utils = utility_registry.get('file_utils')
    with tempfile.NamedTemporaryFile() as tmp:
        assert file_utils.file_exists(Path(tmp.name))
    # After close, file should not exist
    assert not file_utils.file_exists(Path(tmp.name))

def test_read_file(utility_registry):
    file_utils = utility_registry.get('file_utils')
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write('hello world')
        tmp_path = Path(tmp.name)
    try:
        content = file_utils.read_file(tmp_path)
        assert content == 'hello world'
    finally:
        tmp_path.unlink() 