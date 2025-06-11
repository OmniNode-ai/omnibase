"""
Protocol for maintenance tool for node_manager node.
Defines the interface for maintenance, regeneration, and cleanup operations.
"""
from typing import Protocol
from ..models.model_template_context import ModelRegenerationTarget

class ProtocolMaintenance(Protocol):
    """
    Protocol for maintenance tool for node_manager node.
    Implementations should provide methods for regenerating, cleaning, and maintaining node artifacts.
    """
    def regenerate(self, target: ModelRegenerationTarget) -> None:
        """
        Regenerate artifacts for the given target.
        Args:
            target (ModelRegenerationTarget): The target artifact or directory to regenerate.
        """
        ... 