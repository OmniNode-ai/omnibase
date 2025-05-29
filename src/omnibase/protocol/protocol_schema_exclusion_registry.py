# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.285867'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_schema_exclusion_registry.py
# hash: 311b9a30cba07b6f7b14cd8b69023d8b5f3c080fb70d6c08b67250f1e372cf45
# last_modified_at: '2025-05-29T11:50:12.179059+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_schema_exclusion_registry.py
# namespace: omnibase.protocol_schema_exclusion_registry
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 86967029-e106-4d65-9bd8-3f6e3614de44
# version: 1.0.0
# === /OmniNode:Metadata ===


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
