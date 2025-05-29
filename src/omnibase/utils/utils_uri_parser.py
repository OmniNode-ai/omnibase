# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.257653'
# description: Stamped by PythonHandler
# entrypoint: python://utils_uri_parser
# hash: 93e5007ba344a2eb922e1163b93290a8d23ab4aa70bc990dd787084b7a98cf10
# last_modified_at: '2025-05-29T14:14:00.989431+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: utils_uri_parser.py
# namespace: python://omnibase.utils.utils_uri_parser
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 249f5d3d-20f0-4932-9b2f-43406aedee32
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Canonical ONEX URI parser utility.
See docs/nodes/node_contracts.md and docs/nodes/structural_conventions.md for URI format and usage.
# TODO: M1+ add dereferencing, registry lookup, and version resolution.
"""

import re
from pathlib import Path

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, UriTypeEnum
from omnibase.exceptions import OmniBaseError
from omnibase.model.model_uri import OnexUriModel
from omnibase.protocol.protocol_uri_parser import ProtocolUriParser

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem

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
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"Parsing ONEX URI: {uri_string}",
            node_id=_COMPONENT_NAME,
        )
        match = URI_PATTERN.match(uri_string)
        if not match:
            raise OmniBaseError(f"URI parsing failed: Invalid format for {uri_string}")
        uri_type, namespace, version_spec = match.groups()
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"Parsed: Type={uri_type}, Namespace={namespace}, Version={version_spec}",
            node_id=_COMPONENT_NAME,
        )
        return OnexUriModel(
            type=UriTypeEnum(uri_type),
            namespace=namespace,
            version_spec=version_spec,
            original=uri_string,
        )
