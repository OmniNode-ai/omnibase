# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.824534'
# description: Stamped by PythonHandler
# entrypoint: python://exceptions.py
# hash: fabaa86e8bce2cdb31e4e3590545981ea9b9f9599dd74970d9140d64ecf1bf6c
# last_modified_at: '2025-05-29T11:50:10.787446+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: exceptions.py
# namespace: omnibase.exceptions
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: ae2b7601-b4fc-4ecd-8bfe-7bde02a696b6
# version: 1.0.0
# === /OmniNode:Metadata ===


class OmniBaseError(Exception):
    """
    Canonical base error for all ONEX/OmniBase exceptions.
    Extend for specific error types in core, tools, and schema modules.
    See docs/nodes/error_taxonomy.md for error taxonomy and codes.
    """

    pass
