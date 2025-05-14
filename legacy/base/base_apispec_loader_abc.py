from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class APISpecLoader(ABC):
    @abstractmethod
    def load_spec(self, path: Path) -> Dict[str, Any]:
        """Load and parse an OpenAPI/Swagger spec from the given path."""
        pass
