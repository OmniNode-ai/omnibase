# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: fbb0e0bf-71c8-43e1-b74a-c6262d2713fa
# name: hash_computation_mixin.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:01.704580
# last_modified_at: 2025-05-19T16:20:01.704581
# description: Stamped Python file: hash_computation_mixin.py
# state_contract: none
# lifecycle: active
# hash: 3c792496bf0888ad8867b6b0e6fa952567bdbbcfd75b0e80d0b1cb5379c3c954
# entrypoint: {'type': 'python', 'target': 'hash_computation_mixin.py'}
# namespace: onex.stamped.hash_computation_mixin.py
# meta_type: tool
# === /OmniNode:Metadata ===

import hashlib
import logging
from typing import Any, Optional, Tuple

from omnibase.canonical.canonical_serialization import CanonicalYAMLSerializer
from omnibase.model.model_enum_metadata import NodeMetadataField

logger = logging.getLogger(__name__)


class HashComputationMixin:
    """
    Mixin for protocol-compliant hash computation for node metadata blocks.
    Provides compute_hash for stamping and idempotency.
    Uses CanonicalYAMLSerializer and NodeMetadataField Enum for protocol compliance.
    """

    def compute_hash(
        self: Any,
        body: str,
        comment_prefix: str,
        last_modified_at_override: Optional[str] = None,
        volatile_fields: Tuple[NodeMetadataField, ...] = (
            NodeMetadataField.HASH,
            NodeMetadataField.LAST_MODIFIED_AT,
        ),
        placeholder: str = "<PLACEHOLDER>",
    ) -> str:
        """
        Compute the hash for the normalized metadata block and file body.
        - Serializes the metadata block with 'hash' and 'last_modified_at' replaced by protocol placeholders.
        - Concatenates the canonicalized metadata and normalized body.
        - Computes and returns the SHA-256 hash as a hex string.
        """
        meta_copy = self.model_copy()
        for field in volatile_fields:
            field_name = (
                field.value if isinstance(field, NodeMetadataField) else str(field)
            )
            if hasattr(meta_copy, field_name):
                setattr(meta_copy, field_name, placeholder)
        if last_modified_at_override is not None:
            meta_copy.last_modified_at = last_modified_at_override
        else:
            meta_copy.last_modified_at = "1970-01-01T00:00:00Z"  # Protocol placeholder
        serializer = CanonicalYAMLSerializer()
        meta_yaml = serializer.canonicalize_metadata_block(
            meta_copy,
            volatile_fields=volatile_fields,
            placeholder=placeholder,
            explicit_start=False,
            explicit_end=False,
        )
        norm_body = serializer.normalize_body(body)
        canonical = meta_yaml.rstrip("\n") + "\n\n" + norm_body.lstrip("\n")
        logger.debug(f"compute_hash: canonical string before hash=\n{canonical}")
        h = hashlib.sha256()
        h.update(canonical.encode("utf-8"))
        return h.hexdigest()
