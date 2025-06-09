"""
Protocol for file generation tool for node_manager node.
Defines the interface for file generation operations during node and artifact generation.
"""
from typing import Protocol
from pathlib import Path
from ..models.model_file_content import ModelFileContent

class ProtocolFileGenerator(Protocol):
    """
    Protocol for file generation tool for node_manager node.
    Implementations should provide methods for generating, writing, and managing files during node generation.
    """
    def generate_file(self, path: Path, content: ModelFileContent, overwrite: bool = False) -> None:
        """
        Generate or overwrite a file at the given path with the provided content.
        Args:
            path (Path): The file path to write to.
            content (ModelFileContent): The file content and metadata to write.
            overwrite (bool): Whether to overwrite if the file exists.
        """
        ... 