# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: __init__.py
# version: 1.0.0
# uuid: 87188bf6-ed94-4743-b625-09af91f3248a
# author: OmniNode Team
# created_at: 2025-05-25T07:57:38.539675
# last_modified_at: 2025-05-25T12:33:15.557246
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 51c79485952715d8901720c610e6e2668c0993618b264be36e9d137655ed1719
# entrypoint: python@__init__.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.init
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Shared mocks package for test fixtures.
Contains canonical mock implementations used across multiple nodes and tools.
"""

from .dummy_schema_loader import DummySchemaLoader

__all__ = [
    "DummySchemaLoader",
]
