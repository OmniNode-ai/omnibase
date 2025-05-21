# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: utils.py
# version: 1.0.0
# uuid: 155814d5-4f24-4ffa-9871-20990e0507ec
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.163121
# last_modified_at: 2025-05-21T16:42:46.046137
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: e0c2a66af84135444bb001c5094c20279d038b3c43db5817cb34087bcb6c12df
# entrypoint: {'type': 'python', 'target': 'utils.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.utils
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Any

from .canonical_serialization import CanonicalYAMLSerializer


def canonicalize_metadata_block(*args: Any, **kwargs: Any) -> str:
    return CanonicalYAMLSerializer().canonicalize_metadata_block(*args, **kwargs)
