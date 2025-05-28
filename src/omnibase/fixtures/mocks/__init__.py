# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: __init__.py
# version: 1.0.0
# uuid: c7e92cfd-fa5c-4d63-b60f-f3bfdf60faec
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.517511
# last_modified_at: 2025-05-28T17:20:04.573490
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: b9bcb171ff521b212dce98ac47862f9623d5fe42d57bd82fe07cc78ebabf9482
# entrypoint: python@__init__.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.init
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
