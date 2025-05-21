# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: __init__.py
# version: 1.0.0
# uuid: 7ef2922f-643b-4b40-a6e3-b94a438e3f2d
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.162894
# last_modified_at: 2025-05-21T16:42:46.060724
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5e51024f2ac4d65106923139b5b16b8e38c068ca95d5b90214b1874517e1f142
# entrypoint: {'type': 'python', 'target': '__init__.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.___init__
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Any

from .canonical_serialization import CanonicalYAMLSerializer


def canonicalize_metadata_block(*args: Any, **kwargs: Any) -> str:
    return CanonicalYAMLSerializer().canonicalize_metadata_block(*args, **kwargs)
