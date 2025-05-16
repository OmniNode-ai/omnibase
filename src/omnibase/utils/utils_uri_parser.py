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
