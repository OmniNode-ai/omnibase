# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 06f07e3f-d6c7-494a-9ac9-69dbb10e3be3
# name: protocol_testable_registry.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:55.749073
# last_modified_at: 2025-05-19T16:19:55.749074
# description: Stamped Python file: protocol_testable_registry.py
# state_contract: none
# lifecycle: active
# hash: 327953fe12ae6e51c70e69f7ad29cd0c47f893f5a99c387232d083b09522570e
# entrypoint: {'type': 'python', 'target': 'protocol_testable_registry.py'}
# namespace: onex.stamped.protocol_testable_registry.py
# meta_type: tool
# === /OmniNode:Metadata ===

"""
ProtocolTestableRegistry: Protocol for all testable ONEX registry interfaces.
Extends ProtocolTestable. Used for registry-driven tests and swappable registry fixtures.
"""

from typing import Any, Dict, Protocol, runtime_checkable

from omnibase.protocol.protocol_testable import ProtocolTestable


@runtime_checkable
class ProtocolTestableRegistry(ProtocolTestable, Protocol):
    """
    Protocol for testable ONEX registries (mock/real).
    Used for registry-driven tests and fixtures.
    """

    @classmethod
    def load_from_disk(cls) -> "ProtocolTestableRegistry": ...
    @classmethod
    def load_mock(cls) -> "ProtocolTestableRegistry": ...
    def get_node(self, node_id: str) -> Dict[str, Any]: ...
