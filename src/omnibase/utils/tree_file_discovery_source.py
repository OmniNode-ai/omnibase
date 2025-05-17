"""
.tree-based file discovery source for stamping/validation tools.
Implements ProtocolFileDiscoverySource.
"""
from pathlib import Path
from typing import Set, Optional, List
import yaml
from omnibase.protocol.protocol_file_discovery_source import ProtocolFileDiscoverySource
from omnibase.model.model_tree_sync_result import TreeSyncResultModel, TreeSyncStatusEnum
from omnibase.model.model_onex_message_result import OnexMessageModel

class TreeFileDiscoverySource(ProtocolFileDiscoverySource):
    """
    File discovery source that uses a .tree file as the canonical source of truth.
    """
    def discover_files(
        self,
        directory: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        ignore_file: Optional[Path] = None,
    ) -> Set[Path]:
        """
        Discover files listed in the .tree file in the given directory.
        Ignores include/exclude patterns; only files in .tree are returned.
        """
        tree_file = directory / ".tree"
        return self.get_canonical_files_from_tree(tree_file)

    def validate_tree_sync(
        self,
        directory: Path,
        tree_file: Path,
    ) -> TreeSyncResultModel:
        """
        Validate that the .tree file and filesystem are in sync.
        """
        canonical_files = self.get_canonical_files_from_tree(tree_file)
        files_on_disk = set(p for p in directory.rglob("*") if p.is_file())
        extra_files = files_on_disk - canonical_files
        missing_files = canonical_files - files_on_disk
        status = TreeSyncStatusEnum.OK if not extra_files and not missing_files else TreeSyncStatusEnum.DRIFT
        messages = []
        if extra_files:
            messages.append(OnexMessageModel(summary=f"Extra files on disk: {sorted(str(f) for f in extra_files)}", level="warning"))
        if missing_files:
            messages.append(OnexMessageModel(summary=f"Missing files in .tree: {sorted(str(f) for f in missing_files)}", level="warning"))
        return TreeSyncResultModel(
            extra_files_on_disk=extra_files,
            missing_files_in_tree=missing_files,
            status=status,
            messages=messages,
        )

    def get_canonical_files_from_tree(self, tree_file: Path) -> Set[Path]:
        """
        Parse the .tree file and return the set of canonical files.
        """
        if not tree_file.exists():
            return set()
        with open(tree_file, "r") as f:
            data = yaml.safe_load(f)
        return set(self._extract_files_from_tree_data(tree_file.parent, data))

    def _extract_files_from_tree_data(self, base_dir: Path, data) -> List[Path]:
        """
        Recursively extract file paths from .tree data structure.
        """
        files = []
        if isinstance(data, dict):
            if data.get("type") == "file" and "name" in data:
                files.append(base_dir / data["name"])
            elif data.get("type") == "directory" and "children" in data:
                dir_path = base_dir / data.get("name", "")
                for child in data["children"]:
                    files.extend(self._extract_files_from_tree_data(dir_path, child))
        elif isinstance(data, list):
            for item in data:
                files.extend(self._extract_files_from_tree_data(base_dir, item))
        return files 