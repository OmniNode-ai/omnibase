# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_struct_index_integration"
# namespace: "omninode.tools.test_struct_index_integration"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:30+00:00"
# last_modified_at: "2025-05-05T13:00:30+00:00"
# entrypoint: "test_struct_index_integration.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import pytest
import os
import sys
import subprocess
import logging
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
class TestStructIndexIntegration:
    def test_cli_invocation(self, struct_index_test_tree, tmp_path, struct_index_logger):
        import os
        repo_root = Path(__file__).resolve().parents[5]
        script = repo_root / "src" / "foundation" / "script" / "tool" / "struct" / "struct_tool_index_cli.py"
        result = subprocess.run([
            sys.executable, str(script),
            "--target", str(struct_index_test_tree),
            "--write", "--yaml", "--flat", "--with-metadata"
        ], capture_output=True, text=True)
        assert result.returncode == 0
        assert (struct_index_test_tree / ".tree").exists()
        assert (struct_index_test_tree / ".tree.yaml").exists()
        assert (struct_index_test_tree / ".tree.flat").exists()

    def test_directory_listing_failure(self, tmp_path, struct_index_logger):
        class FailingDirIter:
            def __call__(self, p):
                raise OSError("fail")
        indexer = StructIndex(struct_index_logger, dir_iter=FailingDirIter())
        node = indexer.build_tree(tmp_path, verbose=True)
        assert node.name == tmp_path.name

    def test_write_tree_files_dry_run_up_to_date(self, tmp_path, struct_index_logger):
        indexer = StructIndex(struct_index_logger)
        (tmp_path / "file.txt").write_text("hi")
        node = indexer.build_tree(tmp_path)
        indexer.write_tree_files(tmp_path, node, write=True)
        indexer.write_tree_files(tmp_path, node, write=False, verbose=True)

    def test_write_tree_files_dry_run_stale(self, tmp_path, struct_index_logger):
        indexer = StructIndex(struct_index_logger)
        (tmp_path / "file.txt").write_text("hi")
        node = indexer.build_tree(tmp_path)
        indexer.write_tree_files(tmp_path, node, write=True)
        with (tmp_path / ".tree").open("w") as f:
            f.write("corrupt\n")
        indexer.write_tree_files(tmp_path, node, write=False, verbose=True)

    def test_write_tree_files_dry_run_missing(self, tmp_path, struct_index_logger):
        indexer = StructIndex(struct_index_logger)
        (tmp_path / "file.txt").write_text("hi")
        node = indexer.build_tree(tmp_path)
        if (tmp_path / ".tree").exists():
            (tmp_path / ".tree").unlink()
        indexer.write_tree_files(tmp_path, node, write=False, verbose=True)

    def test_cli_main_valid(self, tmp_path):
        import subprocess, sys
        script = str((Path(__file__).parents[5] / "src/foundation/script/tool/struct/struct_tool_index_cli.py").resolve())
        (tmp_path / "afile.txt").write_text("hi")
        result = subprocess.run([
            sys.executable, script,
            "--target", str(tmp_path),
            "--write", "--yaml", "--flat", "--with-metadata"
        ], capture_output=True, text=True)
        assert result.returncode == 0
        assert (tmp_path / ".tree").exists()
        assert (tmp_path / ".tree.yaml").exists()
        assert (tmp_path / ".tree.flat").exists()

    def test_cli_main_invalid(self):
        import subprocess, sys
        script = str((Path(__file__).parents[5] / "src/foundation/script/tool/struct/struct_tool_index_cli.py").resolve())
        result = subprocess.run([
            sys.executable, script,
            "--target", "/nonexistent/path"
        ], capture_output=True, text=True)
        assert result.returncode != 0 