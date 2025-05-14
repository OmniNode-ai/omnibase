from abc import ABC, abstractmethod
from typing import Any, Optional


class HTTPResponse:
    def __init__(self, status_code: int, content: Any, elapsed_ms: float):
        self.status_code = status_code
        self.content = content
        self.elapsed_ms = elapsed_ms


class HTTPClient(ABC):
    @abstractmethod
    def get(self, url: str, timeout: Optional[float] = None) -> HTTPResponse:
        """Perform a GET request and return a response object."""
        pass
