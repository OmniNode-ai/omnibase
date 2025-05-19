# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 667369ef-3958-4e50-b1a1-849e4495891a
# name: protocol_canonical_serializer.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:03.567635
# last_modified_at: 2025-05-19T16:20:03.567639
# description: Stamped Python file: protocol_canonical_serializer.py
# state_contract: none
# lifecycle: active
# hash: 614f67266b15fe078d4924f76a76a00b27f6c8a0d25a5821c627f28933c8ee7f
# entrypoint: {'type': 'python', 'target': 'protocol_canonical_serializer.py'}
# namespace: onex.stamped.protocol_canonical_serializer.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import TYPE_CHECKING, Any, Protocol, Tuple, Union

from omnibase.model.model_enum_metadata import NodeMetadataField

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock


class ProtocolCanonicalSerializer(Protocol):
    """
    Protocol for canonical serialization and normalization of metadata blocks.
    Enforces protocol-compliant, deterministic serialization for stamping, hashing, and idempotency.
    All field references must use canonical Enums (e.g., NodeMetadataField), not string literals.
    Implementations may support YAML, JSON, or other formats.

    NOTE: This protocol uses TYPE_CHECKING and forward references for model types to avoid circular imports
    while maintaining strong typing. This is the canonical pattern for all ONEX protocol interfaces.
    """

    def canonicalize_metadata_block(
        self,
        block: Union[dict[str, Any], "NodeMetadataBlock"],
        volatile_fields: Tuple[NodeMetadataField, ...] = (
            NodeMetadataField.HASH,
            NodeMetadataField.LAST_MODIFIED_AT,
        ),
        placeholder: str = "<PLACEHOLDER>",
        **kwargs: Any,
    ) -> str:
        """
        Canonicalize a metadata block for deterministic serialization and hash computation.
        - Accepts a dict or model instance.
        - Replaces volatile fields (e.g., hash, last_modified_at) with a protocol placeholder.
        - Returns the canonical serialized string.
        """
        ...

    def normalize_body(self, body: str) -> str:
        """
        Canonical normalization for file body content.
        - Strips trailing spaces
        - Normalizes all line endings to '\n'
        - Ensures exactly one newline at EOF
        - Asserts only '\n' line endings are present
        """
        ...

    def canonicalize_for_hash(
        self,
        block: Union[dict[str, Any], "NodeMetadataBlock"],
        body: str,
        volatile_fields: Tuple[NodeMetadataField, ...] = (
            NodeMetadataField.HASH,
            NodeMetadataField.LAST_MODIFIED_AT,
        ),
        placeholder: str = "<PLACEHOLDER>",
        **kwargs: Any,
    ) -> str:
        """
        Canonicalize the full content (block + body) for hash computation.
        - Returns the canonical string to be hashed.
        """
        ...
