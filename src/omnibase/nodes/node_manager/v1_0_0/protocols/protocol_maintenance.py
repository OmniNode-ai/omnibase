"""
Protocol for maintenance tool for node_manager node.
Defines the interface for maintenance, regeneration, and cleanup operations.
"""
from typing import Protocol

class ProtocolMaintenance(Protocol):
    """
    Protocol for maintenance tool for node_manager node.
    Implementations should provide methods for regenerating, cleaning, and maintaining node artifacts.
    """
    def regenerate(self, target: str) -> None:
        """
        Regenerate artifacts for the given target.
        Args:
            target (str): The target artifact or directory to regenerate.
        """
        ... 