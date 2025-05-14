# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_struct_index_basic"
# namespace: "omninode.tools.test_struct_index_basic"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:30+00:00"
# last_modified_at: "2025-05-05T13:00:30+00:00"
# entrypoint: "test_struct_index_basic.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import pytest
import os
import logging
import uuid
from pathlib import Path
from foundation.script.tool.struct.struct_index import StructIndex
from foundation.model.model_struct_index import TreeNode
from foundation.fixture.fixture_struct_index import struct_index_test_tree

@pytest.fixture
def struct_index_logger():
    logger = logging.getLogger(f"StructIndexTest_{os.urandom(4).hex()}")
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

@pytest.mark.usefixtures("struct_index_test_tree")
class TestStructIndexBasic:
    def test_basic_scan(self, struct_index_test_tree, struct_index_logger, caplog):
        indexer = StructIndex(struct_index_logger)
        node = indexer.build_tree(struct_index_test_tree)
        assert node.name == struct_index_test_tree.name
        assert any(child.name == "file2.py" for child in node.children)
        assert all(child.name != "file1.txt" for child in node.children)
        assert all(child.name != "subdir" for child in node.children)

    def test_treeignore_exclusion(self, struct_index_test_tree, struct_index_logger):
        indexer = StructIndex(struct_index_logger)
        node = indexer.build_tree(struct_index_test_tree)
        names = [child.name for child in node.children]
        assert "file1.txt" not in names
        assert "subdir" not in names
        assert "file2.py" in names

    def test_output_formats(self, struct_index_test_tree, tmp_path, struct_index_logger):
        indexer = StructIndex(struct_index_logger)
        node = indexer.build_tree(struct_index_test_tree)
        indexer.write_tree_files(struct_index_test_tree, node, write=True, as_yaml=True, flat=True, with_metadata=True, verbose=False)
        assert (struct_index_test_tree / ".tree").exists()
        assert (struct_index_test_tree / ".tree.yaml").exists()
        assert (struct_index_test_tree / ".tree.flat").exists()
        with (struct_index_test_tree / ".tree").open() as f:
            lines = f.readlines()
        assert any("# hash:" in line for line in lines)
        assert any("# timestamp:" in line for line in lines)
        import yaml
        with (struct_index_test_tree / ".tree.yaml").open() as f:
            data = yaml.safe_load(f)
        assert data["name"] == struct_index_test_tree.name
        assert data["type"] == "directory"

    def test_flat_list_output(self, struct_index_test_tree, struct_index_logger):
        indexer = StructIndex(struct_index_logger)
        node = indexer.build_tree(struct_index_test_tree)
        flat_list = indexer.tree_format_utils.tree_to_flat(node)
        assert any("file2.py" in path for path in flat_list)
        assert all("file1.txt" not in path for path in flat_list)

    def test_dry_run_vs_write(self, struct_index_test_tree, struct_index_logger):
        indexer = StructIndex(struct_index_logger)
        node = indexer.build_tree(struct_index_test_tree)
        indexer.write_tree_files(struct_index_test_tree, node, write=False, as_yaml=True, flat=True, with_metadata=True, verbose=False)
        assert not (struct_index_test_tree / ".tree").exists() or (struct_index_test_tree / ".tree").stat().st_size == 0
        indexer.write_tree_files(struct_index_test_tree, node, write=True, as_yaml=True, flat=True, with_metadata=True, verbose=False)
        assert (struct_index_test_tree / ".tree").exists()

    def test_file_dir_count_metadata(self, struct_index_test_tree, struct_index_logger):
        indexer = StructIndex(struct_index_logger)
        node = indexer.build_tree(struct_index_test_tree, with_metadata=True, verbose=True)
        assert node.metadata["file_count"] == 2
        child_names = [child.name for child in node.children]
        assert "file2.py" in child_names
        assert ".treeignore" in child_names
        assert node.metadata["dir_count"] == 0

    def test_max_depth(self, struct_index_test_tree, struct_index_logger):
        indexer = StructIndex(struct_index_logger)
        node = indexer.build_tree(struct_index_test_tree, max_depth=0)
        assert all(child.type == "file" for child in node.children)

    def test_symlink_handling(self, tmp_path, struct_index_logger):
        (tmp_path / "file.txt").write_text("hi")
        (tmp_path / "dir").mkdir()
        (tmp_path / "dir" / "file2.txt").write_text("hi")
        (tmp_path / "link").symlink_to(tmp_path / "dir")
        indexer = StructIndex(struct_index_logger)
        node = indexer.build_tree(tmp_path, follow_symlinks=False)
        assert all(child.name != "link" for child in node.children)
        node2 = indexer.build_tree(tmp_path, follow_symlinks=True)
        def find_file2(node):
            if node.type == "file" and node.name == "file2.txt":
                return True
            if node.children:
                return any(find_file2(child) for child in node.children)
            return False
        assert find_file2(node2)

    def test_get_logger(self):
        import logging
        logger1 = logging.getLogger(f"StructIndexTest_{uuid.uuid4()}")
        logger1.setLevel(logging.INFO)
        logger2 = logging.getLogger(f"StructIndexTest_{uuid.uuid4()}")
        logger2.setLevel(logging.WARNING)
        assert logger1.level == logging.INFO
        assert logger2.level == logging.WARNING 