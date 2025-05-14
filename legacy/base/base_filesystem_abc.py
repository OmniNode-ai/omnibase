from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class FileSystem(ABC):
    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Check if the file or directory exists."""
        pass

    @abstractmethod
    def read(self, path: Path, mode: str = "r", encoding: str = "utf-8") -> Any:
        """Read the contents of a file."""
        pass
