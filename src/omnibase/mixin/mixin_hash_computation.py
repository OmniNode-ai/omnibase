# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: mixin_hash_computation.py
# version: 1.0.0
# uuid: 71d2759f-d20a-438e-89f2-f45cdd20af79
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.598180
# last_modified_at: 2025-05-28T17:20:05.099893
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: da30c359eb927c53df6b33091e6ece6cacea2321b8c815f3233b32c79f9270f5
# entrypoint: python@mixin_hash_computation.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.mixin_hash_computation
# meta_type: tool
# === /OmniNode:Metadata ===


import hashlib
from typing import TYPE_CHECKING, Tuple

from omnibase.enums import NodeMetadataField
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer

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
