# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T14:41:41.684698'
# description: Stamped by PythonHandler
# entrypoint: python://hash_utils
# hash: 2beba3ce3d5dc7b0816dea5ed432e2c686df0397a40525e80011930e5955d3a8
# last_modified_at: '2025-05-29T14:13:59.817292+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: hash_utils.py
# namespace: python://omnibase.nodes.stamper_node.v1_0_0.helpers.hash_utils
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 33deb1b3-dcff-45e4-8508-c5dff7978e36
# version: 1.0.0
# === /OmniNode:Metadata ===


import hashlib
from typing import Any, List, Optional


def compute_canonical_hash(content: str) -> str:
    """
    Simple SHA256 hash computation for string content.
    This is the canonical hash function for the stamper node.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def compute_idempotency_hash(
    metadata_model: Any,  # NodeMetadataBlock
    body: str,
    volatile_fields: List[str] = ["hash", "last_modified_at"],
    metadata_serializer: Optional[Any] = None,
    body_canonicalizer: Optional[Any] = None,
) -> str:
    """
    Compute hash for idempotency checking using existing Pydantic model directly.
    This avoids reconstruction issues that cause hash mismatches.
    
    Args:
        metadata_model: Existing NodeMetadataBlock Pydantic model
        body: Body content to include in hash
        volatile_fields: Fields to mask during hash computation
        metadata_serializer: Function to serialize metadata to string
        body_canonicalizer: Function to canonicalize body content
        
    Returns:
        SHA256 hash as hex string
    """
    # Create a copy of the model and mask volatile fields directly
    # This avoids any reconstruction or validation issues
    model_copy = metadata_model.model_copy(deep=True)
    
    # Mask volatile fields with consistent placeholder values
    for field in volatile_fields:
        if hasattr(model_copy, field):
            if field == "hash":
                setattr(model_copy, field, "0" * 64)  # Use valid dummy hash
            elif field == "last_modified_at":
                setattr(model_copy, field, "1970-01-01T00:00:00Z")
            else:
                setattr(model_copy, field, None)
    
    # Serialize using the provided serializer (ensures exact same representation)
    meta_str = (
        metadata_serializer(model_copy)
        if metadata_serializer
        else str(model_copy.model_dump())
    )
    body_str = body_canonicalizer(body) if body_canonicalizer else body
    
    canonical_content = meta_str + "\n" + body_str
    return compute_canonical_hash(canonical_content)


def compute_metadata_hash_for_new_blocks(
    metadata_dict: dict[str, Any],
    body: str,
    volatile_fields: List[str] = ["hash", "last_modified_at"],
    metadata_serializer: Optional[Any] = None,
    body_canonicalizer: Optional[Any] = None,
) -> str:
    """
    Compute hash for NEW metadata blocks created from dictionaries.
    This is only used when creating new blocks, not for idempotency checking.
    
    For idempotency checking of existing blocks, use compute_idempotency_hash instead.
    
    Args:
        metadata_dict: Dictionary of metadata fields for new block
        body: Body content to include in hash
        volatile_fields: Fields to mask during hash computation
        metadata_serializer: Function to serialize metadata to string
        body_canonicalizer: Function to canonicalize body content
        
    Returns:
        SHA256 hash as hex string
    """
    from omnibase.model.model_node_metadata import NodeMetadataBlock

    # Extract key fields from metadata dict, use model defaults for missing fields
    name = metadata_dict.get("name", "unknown")
    author = metadata_dict.get("author", "unknown")
    namespace = metadata_dict.get("namespace", "omnibase.stamped.unknown")

    # Handle entrypoint - support both dict and string formats
    entrypoint = metadata_dict.get("entrypoint", {})
    if isinstance(entrypoint, dict):
        entrypoint_type = entrypoint.get("type", "python")
        if hasattr(entrypoint_type, "value"):
            entrypoint_type = entrypoint_type.value
        elif not isinstance(entrypoint_type, str):
            raise ValueError(f"entrypoint_type must be a string or enum with .value, got: {entrypoint_type}")
        entrypoint_target = entrypoint.get("target", "main.py")
    elif isinstance(entrypoint, str):
        # Accept any valid URI string (e.g., python://foo)
        from omnibase.model.model_node_metadata import EntrypointBlock
        try:
            ep_block = EntrypointBlock.from_uri(entrypoint)
            entrypoint_type = ep_block.type
            entrypoint_target = ep_block.target
        except Exception as e:
            raise ValueError(f"Entrypoint must be a valid URI string (e.g., python://foo), got: {entrypoint}") from e
    else:
        raise ValueError(f"Entrypoint must be a dict or URI string, got: {entrypoint}")

    # Create complete model using the canonical constructor
    model = NodeMetadataBlock.create_with_defaults(
        name=name,
        author=author,
        namespace=namespace,
        entrypoint_type=entrypoint_type,
        entrypoint_target=entrypoint_target,
        **{
            k: v
            for k, v in metadata_dict.items()
            if k not in ["name", "author", "namespace", "entrypoint"]
        },
    )

    # Now use the idempotency hash function with the constructed model
    return compute_idempotency_hash(
        metadata_model=model,
        body=body,
        volatile_fields=volatile_fields,
        metadata_serializer=metadata_serializer,
        body_canonicalizer=body_canonicalizer,
    )
