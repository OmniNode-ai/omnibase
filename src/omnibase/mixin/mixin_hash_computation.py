# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: mixin_hash_computation.py
# version: 1.0.0
# uuid: d1e5e882-7bc4-4c1f-ada8-79260cf45b2d
# author: OmniNode Team
# created_at: 2025-05-22T14:05:24.973939
# last_modified_at: 2025-05-22T20:26:29.274576
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a32c17c65ecb3e87fe165ed98f366c127611a046a407637490065fddaac20a4b
# entrypoint: python@mixin_hash_computation.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.mixin_hash_computation
# meta_type: tool
# === /OmniNode:Metadata ===


import hashlib
import logging
from typing import TYPE_CHECKING, Tuple

from omnibase.enums import NodeMetadataField
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass


class HashComputationMixin:
    """
    Pure mixin for protocol-compliant hash computation for node metadata blocks.
    - Requires self to be a NodeMetadataBlock (Pydantic model).
    - All field access and normalization is schema-driven using NodeMetadataBlock.model_fields and NodeMetadataField enum.
    - No hardcoded field names or types.
    - Compatible with Pydantic BaseModel inheritance.
    """

    def compute_hash(
        self,
        body: str,
        volatile_fields: Tuple[NodeMetadataField, ...] = (
            NodeMetadataField.HASH,
            NodeMetadataField.LAST_MODIFIED_AT,
        ),
        placeholder: str = "<PLACEHOLDER>",
        comment_prefix: str = "",
    ) -> str:
        canonical = CanonicalYAMLSerializer().canonicalize_for_hash(
            self,  # type: ignore[arg-type]
            body,
            volatile_fields=volatile_fields,
            placeholder=placeholder,
            comment_prefix=comment_prefix,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
