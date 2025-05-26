# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: utils_uri_parser.py
# version: 1.0.0
# uuid: fcd19706-1a89-4caa-8306-49813221a6c2
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.169767
# last_modified_at: 2025-05-21T16:42:46.094836
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 41dd118694932001e42d4e0c2f7944c94abaad79d3670c7120238e2c39570715
# entrypoint: python@utils_uri_parser.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.utils_uri_parser
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Canonical ONEX URI parser utility.
See docs/nodes/node_contracts.md and docs/nodes/structural_conventions.md for URI format and usage.
# TODO: M1+ add dereferencing, registry lookup, and version resolution.
"""

import re

from omnibase.enums import UriTypeEnum
from omnibase.exceptions import OmniBaseError
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
