from typing import Any, Protocol

class ProtocolTreeFileUtils(Protocol):
    """
    Protocol for tree file utility operations (read/write .tree files, represent directory trees).
    """
    def read_tree_file(self, path: str) -> Any:
        ...

    def write_tree_file(self, path: str, tree: Any) -> None:
        ...

    def add_tree(self, name: str, tree: Any) -> None:
        ...

    def get_tree(self, name: str) -> Any:
        ...

    def directory_to_tree_template(self, root_dir: str) -> Any:
        """
        Recursively walk a directory and return a tree_sync.TreeNode Pydantic model.
        Args:
            root_dir: Root directory path to scan.
        Returns:
            tree_sync.TreeNode representing the structure.
        """
        ... 