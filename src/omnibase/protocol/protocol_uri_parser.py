# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_uri_parser.py
# version: 1.0.0
# uuid: 5c494b83-9310-4f10-a230-189d3de20453
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.168021
# last_modified_at: 2025-05-21T16:42:46.051186
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 8e9c9f1a066c2e65a123a4667c44f45c12d2dcf75b756742425ce9038a2c7477
# entrypoint: python@protocol_uri_parser.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_uri_parser
# meta_type: tool
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
