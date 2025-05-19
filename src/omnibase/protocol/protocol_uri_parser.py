# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 24b1f587-3a7b-48ce-b553-b41b91a43021
# name: protocol_uri_parser.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:01.670479
# last_modified_at: 2025-05-19T16:20:01.670481
# description: Stamped Python file: protocol_uri_parser.py
# state_contract: none
# lifecycle: active
# hash: c2a8d2b6a5f0d085bb7dfaa059fc58603153873754e74a38e64ab72832633960
# entrypoint: {'type': 'python', 'target': 'protocol_uri_parser.py'}
# namespace: onex.stamped.protocol_uri_parser.py
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
