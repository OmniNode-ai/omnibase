# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.183974'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_testable_registry.py
# hash: 617ed73bc8fea1a526a09dc259cc71b6da8011bc492eb648028c34d2c6e74b60
# last_modified_at: '2025-05-29T11:50:12.206941+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_testable_registry.py
# namespace: omnibase.protocol_testable_registry
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: cea78984-9110-4bb6-8b2d-c208afa539b1
# version: 1.0.0
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
