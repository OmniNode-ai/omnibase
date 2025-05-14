import os
import pytest
import yaml
import copy
from foundation.util.util_tree_file_utils import UtilTreeFileUtils
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.model.model_struct_index import TreeNode

"""
Registry-driven tests for UtilTreeFileUtils.
All file-based test cases are loaded via TEST_CASE_REGISTRY.
Test case files are named valid_*.tree or invalid_*.tree and registered in test_case_registry.py.
No inline YAML dicts are used; all test data is canonical and discoverable.
"""

def load_tree(path):
    with open(path, "r") as f:
        lines = f.readlines()
    # Extract metadata block
    in_block = False
    block_lines = []
    content_lines = []
    for line in lines:
        if line.strip() == "=== OmniNode:Metadata ===":
            in_block = True
            continue
        if line.strip() == "=== /OmniNode:Metadata ===" and in_block:
            in_block = False
            continue
        if in_block:
            block_lines.append(line)
        else:
            content_lines.append(line)
    metadata = yaml.safe_load("".join(block_lines)) if block_lines else None
    data = yaml.safe_load("".join(content_lines))
    if data is None:
        data = {}
    if metadata:
        data["metadata"] = metadata
    return data

def test_read_valid_tree_file(tmp_path):
    path = TEST_CASE_REGISTRY.get_test_case("tree_file", "valid_tree", "valid")
    print(f"DEBUG: test_read_valid_tree_file path={path} exists={os.path.exists(path)}")
    utils = UtilTreeFileUtils()
    data = utils.read_tree_file(path)
    assert data["name"] == "root"
    assert data["type"] == "directory"
    assert any(child["name"] == "foo.txt" for child in data["children"])
    assert data["metadata"]["name"] == "foundation_tree"

def test_read_tree_file_missing_metadata(tmp_path):
    path = TEST_CASE_REGISTRY.get_test_case("tree_file", "invalid_missing_metadata", "invalid")
    utils = UtilTreeFileUtils()
    with pytest.raises(ValueError) as exc:
        utils.read_tree_file(path)
    assert "missing required metadata block" in str(exc.value)

def test_read_tree_file_invalid_metadata(tmp_path):
    path = TEST_CASE_REGISTRY.get_test_case("tree_file", "invalid_invalid_metadata", "invalid")
    utils = UtilTreeFileUtils()
    with pytest.raises(ValueError) as exc:
        utils.read_tree_file(path)
    assert (
        "invalid metadata block" in str(exc.value)
        or "missing required metadata block at top of file" in str(exc.value)
    )

def test_read_invalid_tree_file(tmp_path):
    path = TEST_CASE_REGISTRY.get_test_case("tree_file", "invalid_tree", "invalid")
    utils = UtilTreeFileUtils()
    with pytest.raises(ValueError) as exc:
        utils.read_tree_file(path)
    assert (
        ".tree file schema validation failed" in str(exc.value)
        or "missing required metadata block at top of file" in str(exc.value)
    )

def test_write_valid_tree_file(tmp_path):
    src = TEST_CASE_REGISTRY.get_test_case("tree_file", "valid_tree", "valid")
    tree = load_tree(src)
    path = tmp_path / ".tree"
    utils = UtilTreeFileUtils()
    utils.write_tree_file(str(path), tree)
    data = utils.read_tree_file(str(path))
    assert data["name"] == "root"
    assert data["metadata"]["name"] == "foundation_tree"

def test_write_tree_file_missing_metadata(tmp_path):
    src = TEST_CASE_REGISTRY.get_test_case("tree_file", "invalid_missing_metadata", "invalid")
    tree = load_tree(src)
    path = tmp_path / ".tree"
    utils = UtilTreeFileUtils()
    with pytest.raises(ValueError) as exc:
        utils.write_tree_file(str(path), tree)
    assert "without required metadata block" in str(exc.value)

def test_write_tree_file_invalid_metadata(tmp_path):
    src = TEST_CASE_REGISTRY.get_test_case("tree_file", "invalid_invalid_metadata", "invalid")
    tree = load_tree(src)
    path = tmp_path / ".tree"
    utils = UtilTreeFileUtils()
    with pytest.raises(ValueError) as exc:
        utils.write_tree_file(str(path), tree)
    assert "invalid metadata block" in str(exc.value)

def test_write_tree_file_writes_hash(tmp_path):
    src = TEST_CASE_REGISTRY.get_test_case("tree_file", "valid_tree", "valid")
    tree = load_tree(src)
    path = tmp_path / ".tree"
    utils = UtilTreeFileUtils()
    utils.write_tree_file(str(path), tree, force=True)
    with open(path, "r") as f:
        lines = f.readlines()
    # Extract metadata block
    in_block = False
    block_lines = []
    for line in lines:
        if line.strip() == "=== OmniNode:Metadata ===":
            in_block = True
            continue
        if line.strip() == "=== /OmniNode:Metadata ===" and in_block:
            in_block = False
            continue
        if in_block:
            block_lines.append(line)
    metadata = yaml.safe_load("".join(block_lines))
    assert "tree_hash" in metadata
    computed = utils.compute_tree_hash(tree)
    assert metadata["tree_hash"] == computed

def test_is_tree_file_up_to_date_true_false(tmp_path):
    src = TEST_CASE_REGISTRY.get_test_case("tree_file", "valid_tree", "valid")
    tree = load_tree(src)
    path = tmp_path / ".tree"
    utils = UtilTreeFileUtils()
    utils.write_tree_file(str(path), tree, force=True)
    # Compute hash using validated/serialized structure
    validated = TreeNode.model_validate(tree)
    tree_dict = validated.model_dump(mode="python")
    with open(path, "r") as f:
        lines = f.readlines()
    # Extract metadata block
    in_block = False
    block_lines = []
    for line in lines:
        if line.strip() == "=== OmniNode:Metadata ===":
            in_block = True
            continue
        if line.strip() == "=== /OmniNode:Metadata ===" and in_block:
            in_block = False
            continue
        if in_block:
            block_lines.append(line)
    metadata = yaml.safe_load("".join(block_lines))
    file_hash = metadata.get("tree_hash")
    computed_hash = utils.compute_tree_hash(tree_dict)
    assert file_hash == computed_hash
    assert utils.is_tree_file_up_to_date(str(path), tree_dict)
    changed_tree = copy.deepcopy(tree_dict)
    changed_tree["children"].append({"name": "baz.txt", "type": "file"})
    assert not utils.is_tree_file_up_to_date(str(path), changed_tree)

def test_write_tree_file_idempotent(tmp_path):
    src = TEST_CASE_REGISTRY.get_test_case("tree_file", "valid_tree", "valid")
    tree = load_tree(src)
    path = tmp_path / ".tree"
    utils = UtilTreeFileUtils()
    utils.write_tree_file(str(path), tree, force=True)
    mtime1 = os.path.getmtime(path)
    utils.write_tree_file(str(path), tree, force=False)
    mtime2 = os.path.getmtime(path)
    assert mtime1 == mtime2
    utils.write_tree_file(str(path), tree, force=True)
    mtime3 = os.path.getmtime(path)
    assert mtime3 >= mtime2

def test_tree_hash_changes_on_tree_change(tmp_path):
    src = TEST_CASE_REGISTRY.get_test_case("tree_file", "valid_tree", "valid")
    tree = load_tree(src)
    utils = UtilTreeFileUtils()
    hash1 = utils.compute_tree_hash(tree)
    changed_tree = copy.deepcopy(tree)
    changed_tree["children"].append({"name": "baz.txt", "type": "file"})
    hash2 = utils.compute_tree_hash(changed_tree)
    assert hash1 != hash2 