# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.517511'
# description: Stamped by PythonHandler
# entrypoint: python://__init__.py
# hash: 4c7bcf2705db2a7b9e363d1c86c53f36a971af4236145343e01355dd456d34cd
# last_modified_at: '2025-05-29T11:50:10.814778+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: __init__.py
# namespace: omnibase.init
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: c7e92cfd-fa5c-4d63-b60f-f3bfdf60faec
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Shared mocks package for test fixtures.
Contains canonical mock implementations used across multiple nodes and tools.
"""

from .dummy_schema_loader import DummySchemaLoader

__all__ = [
    "DummySchemaLoader",
]
