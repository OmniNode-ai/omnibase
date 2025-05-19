# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 613ed16e-5e0d-4ba9-a0ed-794ff172db94
# name: __init__.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:55.791427
# last_modified_at: 2025-05-19T16:19:55.791429
# description: Stamped Python file: __init__.py
# state_contract: none
# lifecycle: active
# hash: 611ff111303ae45df061c402b1f19cb3d5a7f5069d457860a10d360f516c1eac
# entrypoint: {'type': 'python', 'target': '__init__.py'}
# namespace: onex.stamped.__init__.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Any

from .canonical_serialization import CanonicalYAMLSerializer


def canonicalize_metadata_block(*args: Any, **kwargs: Any) -> str:
    return CanonicalYAMLSerializer().canonicalize_metadata_block(*args, **kwargs)
