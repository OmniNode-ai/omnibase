from typing import Protocol
from omnibase.model.model_uri import OnexUriModel

class ProtocolUriParser(Protocol):
    """
    Protocol for ONEX URI parser utilities.
    All implementations must provide a parse method that returns an OnexUriModel.

    Example:
        class MyUriParser(ProtocolUriParser):
            def parse(self, uri_string: str) -> OnexUriModel:
                ...
    """
    def parse(self, uri_string: str) -> OnexUriModel:
        """Parse a canonical ONEX URI string and return an OnexUriModel."""
        ...
