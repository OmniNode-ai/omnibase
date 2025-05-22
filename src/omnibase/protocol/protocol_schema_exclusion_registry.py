# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_schema_exclusion_registry.py
# version: 1.0.0
# uuid: 44431874-4361-4823-a7e6-99cd0aecdde9
# author: OmniNode Team
# created_at: 2025-05-22T17:18:16.711876
# last_modified_at: 2025-05-22T21:19:13.487423
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 082a2451445d062e491c1f97eb503b5afc36d1acb00adbea5216a84b590a1385
# entrypoint: python@protocol_schema_exclusion_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_schema_exclusion_registry
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
