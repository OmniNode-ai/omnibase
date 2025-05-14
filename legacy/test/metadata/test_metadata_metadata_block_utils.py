# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_metadata_metadata_block_utils"
# namespace: "omninode.tools.test_metadata_metadata_block_utils"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:28+00:00"
# last_modified_at: "2025-05-05T13:00:28+00:00"
# entrypoint: "test_metadata_metadata_block_utils.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Legacy monolithic test file for metadata_block_utils. This file is being split by subject for maintainability.
All fixtures are now injected via the fixture registry.
"""
import os
import tempfile
import logging
from pathlib import Path
from typing import List, Optional
import pytest

from foundation.script.metadata import metadata_block_utils as mbu
from foundation.script.validate.common.common_file_utils import FileUtils
from foundation.script.validate.common.common_yaml_utils import YamlUtils
from foundation.script.validate.common.common_error_utils import CommonErrorUtils
from foundation.script.validate.common.common_json_utils import safe_json_dumps

# Extraction-related tests have been moved to metadata_test_extraction.py

@pytest.fixture
def utility_registry():
    class Registry(dict):
        def register(self, name, obj):
            self[name] = obj
        def get(self, name):
            return self[name]
    reg = Registry()
    reg.register('file_utils', FileUtils())
    reg.register('yaml_utils', YamlUtils())
    reg.register('json_utils', {'safe_json_dumps': safe_json_dumps})
    reg.register('common_error_utils', CommonErrorUtils())
    return reg

def test_generate_metadata_block_minimal(fixture_registry) -> None:
    """Test generating a minimal metadata block."""
    logger = fixture_registry.get_fixture("logger").get_fixture()
    block = mbu.generate_metadata_block(
        name="test_tool",
        entrypoint="test_tool.py",
        template="minimal",
        logger=logger,
    )
    assert "name: test_tool" in block

def test_extract_metadata_block_not_found() -> None:
    """Test extracting a metadata block from text with no block (should return None)."""
    text = "no metadata here"
    block, start, end = mbu.extract_metadata_block(text)
    assert block is None and start is None and end is None

def test_validate_metadata_block_valid() -> None:
    """Test validating a correct metadata block."""
    block = """
"""
    status, msg = mbu.validate_metadata_block(block)
    assert status == "valid"
    assert msg == "OK"

def test_validate_metadata_block_missing_fields() -> None:
    """Test validating a metadata block with missing fields."""
    block = """
"""
    status, msg = mbu.validate_metadata_block(block)
    assert status == "partial"
    assert "Missing fields" in msg

def test_validate_metadata_block_corrupted() -> None:
    """Test validating a corrupted metadata block (bad version, bad name, bad namespace, bad entrypoint, bad protocols)."""
    block = """
"""
    status, msg = mbu.validate_metadata_block(block)
    assert status == "corrupted"
    assert "metadata_version must be '0.1'" in msg or "Invalid name" in msg or "Invalid namespace" in msg or "Invalid entrypoint" in msg or "protocols_supported must be a list" in msg

def test_strip_existing_header_and_place_metadata() -> None:
    """Test stripping and placing metadata block with/without shebang and existing block."""
    orig = """#!/usr/bin/env python3
# === OmniNode:Tool_Metadata ===
# name: old
# === /OmniNode:Tool_Metadata ===
print('hi')
"""
    new_block = "# === OmniNode:Tool_Metadata ===\n# name: new\n# === /OmniNode:Tool_Metadata ==="
    result = mbu.strip_existing_header_and_place_metadata(orig, new_block)
    assert result.startswith("#!/usr/bin/env python3")
    assert "# name: new" in result
    assert "print('hi')" in result
    # No shebang
    orig2 = "# === OmniNode:Tool_Metadata ===\n# name: old\n# === /OmniNode:Tool_Metadata ===\nprint('hi')"
    result2 = mbu.strip_existing_header_and_place_metadata(orig2, new_block)
    assert result2.startswith("# === OmniNode:Tool_Metadata ===")
    assert "# name: new" in result2
    assert "print('hi')" in result2

def test_load_stamperignore(tmp_path: Path) -> None:
    """Test loading .stamperignore patterns from a file."""
    ignore_file = tmp_path / ".stamperignore"
    ignore_file.write_text("foo.py\nbar/\n# comment\n\n")
    patterns = mbu.load_stamperignore(str(ignore_file))
    assert "foo.py" in patterns
    assert "bar/" in patterns
    assert "# comment" not in patterns

def test_should_ignore(tmp_path: Path) -> None:
    """Test should_ignore with and without pathspec."""
    patterns = ["foo.py", "bar/"]
    file1 = tmp_path / "foo.py"
    file2 = tmp_path / "bar" / "baz.py"
    file2.parent.mkdir()
    file2.write_text("print('hi')")
    assert mbu.should_ignore(file1, patterns)
    assert mbu.should_ignore(file2, patterns)
    file3 = tmp_path / "not_ignored.py"
    file3.write_text("print('no')")
    assert not mbu.should_ignore(file3, patterns)

def test_extract_base_classes_from_file_valid(fixture_registry):
    code = '''
class A:
    pass
class B(A):
    pass
class C(B):
    pass
'''
    logger = fixture_registry.get_fixture("logger").get_fixture()
    bases = mbu.extract_base_classes_from_file(code, logger=logger)
    assert set(bases) == {"A", "B"}

def test_extract_base_classes_from_file_invalid(fixture_registry):
    code = 'class A: bad syntax here'
    logger = fixture_registry.get_fixture("logger").get_fixture()
    bases = mbu.extract_base_classes_from_file(code, logger=logger)
    assert bases == []

def test_extract_base_classes_from_file_nonexistent(fixture_registry):
    logger = fixture_registry.get_fixture("logger").get_fixture()
    bases = mbu.extract_base_classes_from_file("", logger=logger)
    assert bases == [] 