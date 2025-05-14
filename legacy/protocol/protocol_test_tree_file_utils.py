from typing import Any, Protocol
from foundation.protocol.protocol_tree_file_utils import ProtocolTreeFileUtils

class ProtocolTestTreeFileUtils(ProtocolTreeFileUtils, Protocol):
    """
    Test-only protocol extension for tree file utilities.
    Allows reading a tree file with an arbitrary file name (not just .tree).
    """
    def read_tree_file_with_name(self, directory: str, tree_file_name: str = ".tree") -> Any:
        ... 