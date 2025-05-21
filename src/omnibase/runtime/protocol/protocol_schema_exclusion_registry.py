from pathlib import Path
from typing import Protocol


class ProtocolSchemaExclusionRegistry(Protocol):
    """
    Canonical protocol for schema exclusion registries shared across nodes.
    Placed in runtime/ per OmniNode Runtime Structure Guidelines: use runtime/ for execution-layer components reused by multiple nodes.
    All schema exclusion logic must conform to this interface.
    """

    def is_schema_file(self, path: Path) -> bool:
        """Return True if the given path is a schema file to be excluded, else False."""
        ...
