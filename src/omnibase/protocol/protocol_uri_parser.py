# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.203337'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_uri_parser.py
# hash: 949d3cb489e47b23abcd23c487c6278f4f9173fa99ea5ef46bc826836e19f4fe
# last_modified_at: '2025-05-29T11:50:12.223289+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_uri_parser.py
# namespace: omnibase.protocol_uri_parser
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: b9a2444a-2347-44e1-853b-35ff2037b9b3
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Protocol

from omnibase.model.model_uri import OnexUriModel


class ProtocolUriParser(Protocol):
    """
    Protocol for ONEX URI parser utilities.
    All implementations must provide a parse method that returns an OnexUriModel.

    Example:
        class MyUriParser(ProtocolUriParser):
            def parse(self, uri_string: str) -> OnexUriModel:
                ...
    """

    def parse(self, uri_string: str) -> OnexUriModel:
        """Parse a canonical ONEX URI string and return an OnexUriModel."""
        ...
