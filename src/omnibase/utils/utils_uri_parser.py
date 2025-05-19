# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: b517c6b2-0d11-437d-ab45-49b37e5de3e5
# name: utils_uri_parser.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:55.922990
# last_modified_at: 2025-05-19T16:19:55.922991
# description: Stamped Python file: utils_uri_parser.py
# state_contract: none
# lifecycle: active
# hash: 2a5b7e18271b7c07c21d7f6440d9db302aeb00935df1c53e62aa5dc8a13576e3
# entrypoint: {'type': 'python', 'target': 'utils_uri_parser.py'}
# namespace: onex.stamped.utils_uri_parser.py
# meta_type: tool
# === /OmniNode:Metadata ===

"""
Canonical ONEX URI parser utility.
See docs/nodes/node_contracts.md and docs/nodes/structural_conventions.md for URI format and usage.
# TODO: M1+ add dereferencing, registry lookup, and version resolution.
"""

import re

from omnibase.core.errors import OmniBaseError
from omnibase.model.model_enum_metadata import UriTypeEnum
from omnibase.model.model_uri import OnexUriModel
from omnibase.protocol.protocol_uri_parser import ProtocolUriParser

# Build the allowed types pattern from the Enum
ALLOWED_TYPES = [e.value for e in UriTypeEnum if e != UriTypeEnum.UNKNOWN]
URI_PATTERN = re.compile(rf"^({'|'.join(ALLOWED_TYPES)})://([^@]+)@(.+)$")


class CanonicalUriParser(ProtocolUriParser):
    """
    Canonical implementation of ProtocolUriParser for ONEX URIs.
    Instantiate and inject this class; do not use as a singleton or global.
    """

    def parse(self, uri_string: str) -> OnexUriModel:
        """
        Parse a canonical ONEX URI of the form <type>://<namespace>@<version_spec>.
        Raises OmniBaseError if the format is invalid.
        Returns an OnexUriModel.
        """
        print(f"Parsing ONEX URI: {uri_string}")
        match = URI_PATTERN.match(uri_string)
        if not match:
            raise OmniBaseError(f"URI parsing failed: Invalid format for {uri_string}")
        uri_type, namespace, version_spec = match.groups()
        print(f"Parsed: Type={uri_type}, Namespace={namespace}, Version={version_spec}")
        return OnexUriModel(
            type=UriTypeEnum(uri_type),
            namespace=namespace,
            version_spec=version_spec,
            original=uri_string,
        )
