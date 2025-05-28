# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_schema_exclusion_registry.py
# version: 1.0.0
# uuid: 86967029-e106-4d65-9bd8-3f6e3614de44
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.285867
# last_modified_at: 2025-05-28T17:20:05.572374
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 73d006a656f8d2fb0fdb2cc095d645f782213ea8be28937e28011513d6a4670c
# entrypoint: python@protocol_schema_exclusion_registry.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_schema_exclusion_registry
# meta_type: tool
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
