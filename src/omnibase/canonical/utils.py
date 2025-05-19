# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 085a2335-1403-49fc-96f4-1fffbc2349ba
# name: utils.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:06.032498
# last_modified_at: 2025-05-19T16:20:06.032501
# description: Stamped Python file: utils.py
# state_contract: none
# lifecycle: active
# hash: a40dc29c69ad2b8cad4504c427a168f00e610fe42377a38026233f0d2f0bf5c9
# entrypoint: {'type': 'python', 'target': 'utils.py'}
# namespace: onex.stamped.utils.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Any

from .canonical_serialization import CanonicalYAMLSerializer


def canonicalize_metadata_block(*args: Any, **kwargs: Any) -> str:
    return CanonicalYAMLSerializer().canonicalize_metadata_block(*args, **kwargs)
