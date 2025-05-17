"""
Test case registry for file discovery sources (filesystem, .tree, hybrid).
Defines canonical test case classes and central registry for use in protocol-first tests.
"""
import pytest
from pathlib import Path
from typing import Dict, Type, Any, Callable, Set

# Central registry for test cases
FILE_DISCOVERY_TEST_CASES: Dict[str, Type] = {}

def register_file_discovery_test_case(name: str) -> Callable[[Type], Type]:
    """Decorator to register a test case class in the file discovery test case registry."""
    def decorator(cls: Type) -> Type:
        FILE_DISCOVERY_TEST_CASES[name] = cls
        return cls
    return decorator

# Example test case class for filesystem discovery
@register_file_discovery_test_case("filesystem_basic")
class FilesystemBasicCase:
    supported_sources: list[str] = ["filesystem"]
    """
    Test case: Filesystem discovery finds all eligible files, ignores as expected.
    """
    def setup(self, tmp_path: Path) -> Path:
        # Create files and directories
        (tmp_path / "a.yaml").write_text("foo: 1")
        (tmp_path / "b.json").write_text("{\"bar\": 2}")
        (tmp_path / "ignore.txt").write_text("should be ignored")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git/hidden.yaml").write_text("should be ignored")
        return tmp_path
    def expected(self, tmp_path: Path) -> Set[Path]:
        return {tmp_path / "a.yaml", tmp_path / "b.json"}
    def run(self, discovery_source: Any, tmp_path: Path) -> None:
        found = discovery_source.discover_files(tmp_path)
        assert found == self.expected(tmp_path)

# Example test case class for .tree discovery
@register_file_discovery_test_case("tree_basic")
class TreeBasicCase:
    supported_sources: list[str] = ["tree"]
    """
    Test case: .tree discovery returns only files listed in .tree.
    """
    def setup(self, tmp_path: Path) -> Path:
        (tmp_path / "a.yaml").write_text("foo: 1")
        (tmp_path / "b.json").write_text("{\"bar\": 2}")
        tree_data = {
            "type": "directory",
            "name": "",
            "children": [
                {"type": "file", "name": "a.yaml"},
                {"type": "file", "name": "b.json"},
            ],
        }
        import yaml
        (tmp_path / ".tree").write_text(yaml.safe_dump(tree_data))
        return tmp_path
    def expected(self, tmp_path: Path) -> Set[Path]:
        return {tmp_path / "a.yaml", tmp_path / "b.json"}
    def run(self, discovery_source: Any, tmp_path: Path) -> None:
        found = discovery_source.discover_files(tmp_path)
        assert found == self.expected(tmp_path)

# Example test case class for hybrid discovery (warn mode)
@register_file_discovery_test_case("hybrid_warn_drift")
class HybridWarnDriftCase:
    supported_sources: list[str] = ["hybrid_warn"]
    """
    Test case: Hybrid discovery warns on drift but returns all files in warn mode.
    """
    def setup(self, tmp_path: Path) -> Path:
        (tmp_path / "a.yaml").write_text("foo: 1")
        (tmp_path / "b.json").write_text("{\"bar\": 2}")
        (tmp_path / "extra.yaml").write_text("should warn as extra")
        tree_data = {
            "type": "directory",
            "name": "",
            "children": [
                {"type": "file", "name": "a.yaml"},
                {"type": "file", "name": "b.json"},
            ],
        }
        import yaml
        (tmp_path / ".tree").write_text(yaml.safe_dump(tree_data))
        return tmp_path
    def expected(self, tmp_path: Path) -> Set[Path]:
        # In warn mode, all eligible files are returned
        return {tmp_path / "a.yaml", tmp_path / "b.json", tmp_path / "extra.yaml"}
    def run(self, discovery_source: Any, tmp_path: Path) -> None:
        found = discovery_source.discover_files(tmp_path)
        assert found == self.expected(tmp_path)

# Example test case class for hybrid discovery (strict mode)
@register_file_discovery_test_case("hybrid_strict_drift")
class HybridStrictDriftCase:
    supported_sources: list[str] = ["hybrid_strict"]
    """
    Test case: Hybrid discovery errors on drift and returns only .tree files in strict mode.
    """
    def setup(self, tmp_path: Path) -> Path:
        (tmp_path / "a.yaml").write_text("foo: 1")
        (tmp_path / "b.json").write_text("{\"bar\": 2}")
        (tmp_path / "extra.yaml").write_text("should error as extra")
        tree_data = {
            "type": "directory",
            "name": "",
            "children": [
                {"type": "file", "name": "a.yaml"},
                {"type": "file", "name": "b.json"},
            ],
        }
        import yaml
        (tmp_path / ".tree").write_text(yaml.safe_dump(tree_data))
        return tmp_path
    def expected(self, tmp_path: Path) -> Set[Path]:
        # In strict mode, only .tree files are returned
        return {tmp_path / "a.yaml", tmp_path / "b.json"}
    def run(self, discovery_source: Any, tmp_path: Path) -> None:
        import pytest
        with pytest.raises(RuntimeError):
            discovery_source.discover_files(tmp_path) 