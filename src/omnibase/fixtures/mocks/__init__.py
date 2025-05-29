# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.517511'
# description: Stamped by PythonHandler
# entrypoint: python://__init__
# hash: 3677e02d7715a8b21bfd8053d23407b2677197c54599ce42a26224395ad700a3
# last_modified_at: '2025-05-29T14:13:58.620118+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: __init__.py
# namespace: python://omnibase.fixtures.mocks.__init__
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
