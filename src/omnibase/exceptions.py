# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:07.824534'
# description: Stamped by PythonHandler
# entrypoint: python://exceptions
# hash: 4dffa9678c1548407bf6a8d075706234b63d65b7f4a91709762961da081aaf7b
# last_modified_at: '2025-05-29T14:13:58.584965+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: exceptions.py
# namespace: python://omnibase.exceptions
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
