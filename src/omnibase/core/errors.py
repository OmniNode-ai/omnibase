# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 9a9429ce-c6b7-4e80-a5bc-face0214e38f
# name: errors.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:38:47.568992
# last_modified_at: 2025-05-19T16:38:47.568994
# description: Stamped Python file: errors.py
# state_contract: none
# lifecycle: active
# hash: d6ad56549586f74bad620079032b7b0c45f45863f0603d9ba33e9c340ce7d143
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
