# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_directory_tree"
# namespace: "omninode.test.validate.directory_tree"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00Z"
# last_modified_at: "2025-05-07T12:00:00Z"
# entrypoint: "test_validate_directory_tree.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["ProtocolTestableCLI"]
# base_class: ["TestCase"]
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""Tests for directory tree structure validation (structure-only, no rules)."""

import pytest
import yaml
from foundation.script.validate.validate_directory_tree import ValidateDirectoryTree
from foundation.model.model_struct_index import TreeNode
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
import structlog
from foundation.fixture.fixture_registry import FIXTURE_REGISTRY
import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path
from foundation.script.validate import validate_directory_tree
from foundation.util.util_tree_file_utils import UtilTreeFileUtils
from foundation.const.metadata_tags import OMNINODE_METADATA_START, OMNINODE_METADATA_END
from foundation.fixture.fixture_tree_file_utils import TreeFileUtilsTestHelper
from foundation.model.model_unified_result import UnifiedStatus, UnifiedResultModel, UnifiedMessageModel


@pytest.fixture(autouse=True, scope="module")
def configure_structlog_for_tests():
    structlog.configure(
        processors=[structlog.processors.JSONRenderer()],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    import logging
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, force=True)

@pytest.fixture
def logger():
    return structlog.get_logger("test_logger")

@pytest.fixture
def validator(logger):
    tree_file_utils = FIXTURE_REGISTRY.get_fixture("tree_file_utils_fixture")
    return ValidateDirectoryTree(logger, tree_file_utils)

@pytest.fixture
def injected_template_path(tmp_path):
    template_path = TEST_CASE_REGISTRY.get_test_case("directory_tree", "template", "valid")
    test_template_path = tmp_path / "base_template.yaml"
    import shutil
    shutil.copy(template_path, test_template_path)
    return test_template_path

def test_validator_init(validator):
    assert validator is not None
    assert validator.template is None

def test_validator_configure(validator, logger):
    valid_keys = list(TEST_CASE_REGISTRY._cases['directory_tree']['valid'].keys())
    logger.debug(f"directory_tree valid keys: {valid_keys}")
    template_path = TEST_CASE_REGISTRY.get_test_case("directory_tree", "template", "valid")
    logger.debug(f"template_path: {template_path}")
    logger.debug(f"template_path exists: {os.path.exists(template_path) if template_path else 'None'}")
    validator.configure({"base_template_path": template_path})
    assert validator.template is not None

def test_valid_tree_structure(validator, logger):
    tree_path = TEST_CASE_REGISTRY.get_test_case("directory_tree", "tree", "valid")
    template_path = TEST_CASE_REGISTRY.get_test_case("directory_tree", "template", "valid")
    with open(tree_path) as f:
        tree_struct = yaml.safe_load(f)
    from foundation.model.model_struct_index import TreeNode
    tree_model = TreeNode.model_validate(tree_struct)
    tree_file_utils = validator.tree_file_utils
    canonical_tree_path = os.path.join(os.path.dirname(tree_path), ".tree")
    tree_file_utils.add_tree(canonical_tree_path, tree_model)
    root_dir = os.path.dirname(tree_path)
    validator.configure({"base_template_path": template_path})
    result = validator.validate(root_dir, {})
    assert isinstance(result, UnifiedResultModel)
    assert result.status == UnifiedStatus.success
    assert all(isinstance(msg, UnifiedMessageModel) for msg in result.messages)
    assert not [msg for msg in result.messages if msg.level == "error"]
    assert not [msg for msg in result.messages if msg.level == "warning"]

def test_invalid_tree_structure(validator, logger):
    tree_path = TEST_CASE_REGISTRY.get_test_case("directory_tree", "tree", "invalid")
    template_path = TEST_CASE_REGISTRY.get_test_case("directory_tree", "template", "invalid")
    with open(tree_path) as f:
        tree_struct = yaml.safe_load(f)
    from foundation.model.model_struct_index import TreeNode
    tree_model = TreeNode.model_validate(tree_struct)
    tree_file_utils = validator.tree_file_utils
    canonical_tree_path = os.path.join(os.path.dirname(tree_path), ".tree")
    tree_file_utils.add_tree(canonical_tree_path, tree_model)
    root_dir = os.path.dirname(tree_path)
    validator.configure({"base_template_path": template_path})
    result = validator.validate(root_dir, {})
    assert isinstance(result, UnifiedResultModel)
    assert result.status == UnifiedStatus.error
    assert any(msg.level == "error" for msg in result.messages)

def test_invalid_tree_with_metadata_block(logger):
    tree_utils = TreeFileUtilsTestHelper(logger)
    test_dir = os.path.dirname(__file__) + "/directory_tree/test_case/invalid"
    tree_file_name = "invalid_with_metadata_block.tree"
    try:
        tree_utils.read_tree_file_with_name(test_dir, tree_file_name)
    except ValueError as e:
        print("Validator error:", str(e))
        assert "metadata block" in str(e).lower()
    else:
        assert False, "Expected ValueError for metadata block, but none was raised."

def run_cli(args, cwd=None, env=None, input_data=None):
    cmd = [sys.executable, str(Path(__file__).parent.parent.parent / "script/validate/validate_directory_tree.py")] + args
    result = subprocess.run(
        cmd,
        input=input_data,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env or os.environ.copy(),
    )
    return result

def test_cli_json_output(tmp_path, logger, injected_template_path):
    from foundation.test.test_case_registry import TEST_CASE_REGISTRY
    import yaml
    template_tree_path = TEST_CASE_REGISTRY.get_test_case("directory_tree", "tree", "valid")
    test_tree_path = tmp_path / ".tree"
    import shutil
    shutil.copy(template_tree_path, test_tree_path)
    with open(template_tree_path, "r") as f:
        tree_struct = yaml.safe_load(f)
    def create_from_tree(node, base):
        if node["type"] == "directory":
            dir_path = base / node["name"]
            dir_path.mkdir(exist_ok=True)
            for child in node.get("children", []):
                create_from_tree(child, dir_path)
        elif node["type"] == "file":
            file_path = base / node["name"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("# test file\n")
    create_from_tree(tree_struct, tmp_path)
    if test_tree_path.exists():
        test_tree_path.unlink()
    from foundation.util.util_tree_file_utils import UtilTreeFileUtils
    tree_utils = UtilTreeFileUtils(logger)
    tree_node = tree_utils.directory_to_tree_node(str(tmp_path))
    tree_utils.write_tree_file(str(test_tree_path), tree_node, force=True)
    argv = ["--root", str(tmp_path), "--base-template", str(injected_template_path), "--output-format", "json"]
    result = run_cli(argv)
    import json
    if not result.stdout.strip():
        print("STDERR OUTPUT FROM CLI:\n", result.stderr)
    try:
        output = json.loads(result.stdout)
    except Exception as e:
        print("STDERR OUTPUT FROM CLI (on JSON decode error):\n", result.stderr)
        raise
    assert "status" in output
    assert output["status"] == UnifiedStatus.success.value
    assert "messages" in output
    assert not [msg for msg in output["messages"] if msg["level"] == "error"]
    assert not [msg for msg in output["messages"] if msg["level"] == "warning"]

def test_cli_text_output(tmp_path, logger, injected_template_path):
    from foundation.test.test_case_registry import TEST_CASE_REGISTRY
    import yaml
    template_tree_path = TEST_CASE_REGISTRY.get_test_case("directory_tree", "tree", "valid")
    test_tree_path = tmp_path / ".tree"
    import shutil
    shutil.copy(template_tree_path, test_tree_path)
    with open(template_tree_path, "r") as f:
        tree_struct = yaml.safe_load(f)
    def create_from_tree(node, base):
        if node["type"] == "directory":
            dir_path = base / node["name"]
            dir_path.mkdir(exist_ok=True)
            for child in node.get("children", []):
                create_from_tree(child, dir_path)
        elif node["type"] == "file":
            file_path = base / node["name"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("# test file\n")
    create_from_tree(tree_struct, tmp_path)
    if test_tree_path.exists():
        test_tree_path.unlink()
    from foundation.util.util_tree_file_utils import UtilTreeFileUtils
    tree_utils = UtilTreeFileUtils(logger)
    tree_node = tree_utils.directory_to_tree_node(str(tmp_path))
    tree_utils.write_tree_file(str(test_tree_path), tree_node, force=True)
    argv = ["--root", str(tmp_path), "--base-template", str(injected_template_path), "--output-format", "text"]
    result = run_cli(argv)
    assert "✅" in result.stdout or "❌" in result.stdout
    assert "Validation passed" in result.stdout or "Validation failed" in result.stdout

def test_missing_tree_file_standards_compliance(logger):
    from foundation.util.util_tree_file_utils import UtilTreeFileUtils
    from foundation.script.validate.validate_directory_tree import ValidateDirectoryTree
    from foundation.model.model_unified_result import UnifiedStatus, UnifiedResultModel, UnifiedMessageModel
    class InMemoryTreeFileUtils(UtilTreeFileUtils):
        def read_tree_file(self, path: str):
            raise ValueError("No .tree file found at path: " + path)
    tree_file_utils = InMemoryTreeFileUtils(logger)
    validator = ValidateDirectoryTree(logger, tree_file_utils)
    fake_dir = "/fake/dir/for/test"
    validator.configure({"base_template_path": "/fake/dir/for/test/.tree"})
    result = validator.validate(fake_dir, {})
    assert isinstance(result, UnifiedResultModel)
    assert result.status == UnifiedStatus.error
    assert isinstance(result.messages, list)
    assert any(isinstance(msg, UnifiedMessageModel) and msg.level == "error" and (".tree" in msg.summary.lower() or "not found" in msg.summary.lower()) for msg in result.messages)
    assert not hasattr(result, "is_valid")
    assert not hasattr(result, "errors")
    assert not hasattr(result, "warnings") 