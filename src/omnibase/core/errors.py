# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 6563c0a6-6c0c-42e7-99fb-58596a225f4d
# name: errors.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:56.573085
# last_modified_at: 2025-05-19T16:19:56.573088
# description: Stamped Python file: errors.py
# state_contract: none
# lifecycle: active
# hash: 6d3575dd59ddcc27a82a95cc16ba20ef26ed5f01855b87175c56b0e9e8a25223
# entrypoint: {'type': 'python', 'target': 'errors.py'}
# namespace: onex.stamped.errors.py
# meta_type: tool
# === /OmniNode:Metadata ===


class OmniBaseError(Exception):
    """
    Canonical base error for all ONEX/OmniBase exceptions.
    Extend for specific error types in core, tools, and schema modules.
    See docs/nodes/error_taxonomy.md for error taxonomy and codes.
    """

    pass
