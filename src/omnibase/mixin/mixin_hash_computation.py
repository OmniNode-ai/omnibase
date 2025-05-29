# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.598180'
# description: Stamped by PythonHandler
# entrypoint: python://mixin_hash_computation.py
# hash: d145f269d82aa2543ab86d589e750cc4dd9a1d682bcf59e95f087c521207f485
# last_modified_at: '2025-05-29T11:50:10.868842+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: mixin_hash_computation.py
# namespace: omnibase.mixin_hash_computation
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 71d2759f-d20a-438e-89f2-f45cdd20af79
# version: 1.0.0
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
