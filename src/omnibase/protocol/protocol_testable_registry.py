# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_testable_registry.py
# version: 1.0.0
# uuid: 3e4b7bc4-55d5-4d6b-bb1e-6a82bcbac381
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167898
# last_modified_at: 2025-05-21T16:42:46.059758
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: b7001d88e096b5210933054cf16c9972df0eff5ae2a8c616bfb678738ee546ba
# entrypoint: python@protocol_testable_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_testable_registry
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
