from pathlib import Path
from typing import Dict, Any, Protocol


class ProtocolTreeGenerator(Protocol):
    """
    Protocol for tree generator engines.
    All implementations must scan directory structures and return tree data.
    """

    def scan_directory_structure(self, root_directory: Path) -> Dict[str, Any]:
        """
        Scan directory structure and return tree data.
        
        Args:
            root_directory: Path to the root directory to scan
            
        Returns:
            Dictionary containing the tree structure data
            
        Raises:
            FileNotFoundError: If the root directory doesn't exist
        """
        ... 