# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.449620'
# description: Stamped by PythonHandler
# entrypoint: python://utils_test_file_discovery_sources_cases.py
# hash: f51b7c6c7b45eb2c2d49cdb4e12e926d2eadfffdf9fb3f7ad4d941260df212ba
# last_modified_at: '2025-05-29T13:51:24.268240+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: utils_test_file_discovery_sources_cases.py
# namespace: py://omnibase.tests.utils.utils_test_file_discovery_sources_cases_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 8ae01cd5-e84c-4b8b-ba9a-28edef39653d
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Test case registry for file discovery sources (filesystem, .tree, hybrid).
Defines canonical test case classes and central registry for use in protocol-first tests.
"""

from pathlib import Path
from typing import Any, Callable, Dict, Set, Type

import pytest

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
        (tmp_path / "b.json").write_text('{"bar": 2}')
        (tmp_path / "ignore.txt").write_text("should be ignored")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git/hidden.yaml").write_text("should be ignored")
        return tmp_path

    def expected(self, tmp_path: Path) -> Set[Path]:
        return {tmp_path / "a.yaml", tmp_path / "b.json"}

    def run(self, discovery_source: Any, tmp_path: Path, protocol_event_bus=None) -> None:
        found = discovery_source.discover_files(tmp_path, event_bus=protocol_event_bus)
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
        (tmp_path / "b.json").write_text('{"bar": 2}')
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

    def run(self, discovery_source: Any, tmp_path: Path, protocol_event_bus=None) -> None:
        found = discovery_source.discover_files(tmp_path, event_bus=protocol_event_bus)
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
        (tmp_path / "b.json").write_text('{"bar": 2}')
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

    def run(self, discovery_source: Any, tmp_path: Path, protocol_event_bus=None) -> None:
        found = discovery_source.discover_files(tmp_path, event_bus=protocol_event_bus)
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
        (tmp_path / "b.json").write_text('{"bar": 2}')
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

    def run(self, discovery_source: Any, tmp_path: Path, protocol_event_bus=None) -> None:
        from omnibase.core.core_error_codes import OnexError

        with pytest.raises(OnexError):
            discovery_source.discover_files(tmp_path, event_bus=protocol_event_bus)
