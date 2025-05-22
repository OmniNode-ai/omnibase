# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: errors.py
# version: 1.0.0
# uuid: 49d462c4-feda-4cfb-9677-f3a86c309dc1
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.163633
# last_modified_at: 2025-05-21T16:42:46.100096
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a92a1d6ffb92bf15e35121c7e05296ec363b8c5a20fa52697c39a0349682b7ab
# entrypoint: python@errors.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.errors
# meta_type: tool
# === /OmniNode:Metadata ===


class OmniBaseError(Exception):
    """
    Canonical base error for all ONEX/OmniBase exceptions.
    Extend for specific error types in core, tools, and schema modules.
    See docs/nodes/error_taxonomy.md for error taxonomy and codes.
    """

    pass
