# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_canonical_serializer.py
# version: 1.0.0
# uuid: 8a8460d1-fcbb-4353-812a-3ce95aa56b51
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.166804
# last_modified_at: 2025-05-21T16:42:46.076491
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d88107af8ee694e5ff8315d0749168d402082505c7a7e05a5b3535ec82840d21
# entrypoint: python@protocol_canonical_serializer.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_canonical_serializer
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import TYPE_CHECKING, Any, Protocol, Tuple, Union

from omnibase.enums import NodeMetadataField

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
