import hashlib
from typing import Any, List, Optional


def compute_canonical_hash(content: str) -> str:
    """
    Simple SHA256 hash computation for string content.
    This is the canonical hash function for ONEX runtime.
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
    Args:
        metadata_model: Existing NodeMetadataBlock Pydantic model
        body: Body content to include in hash
        volatile_fields: Fields to mask during hash computation
        metadata_serializer: Function to serialize metadata to string
        body_canonicalizer: Function to canonicalize body content
    Returns:
        SHA256 hash as hex string
    """
    model_copy = metadata_model.model_copy(deep=True)
    for field in volatile_fields:
        if hasattr(model_copy, field):
            if field == "hash":
                setattr(model_copy, field, "0" * 64)
            elif field == "last_modified_at":
                setattr(model_copy, field, "1970-01-01T00:00:00Z")
            else:
                setattr(model_copy, field, None)
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

    name = metadata_dict.get("name", "unknown")
    author = metadata_dict.get("author", "unknown")
    namespace = metadata_dict.get("namespace", "omnibase.stamped.unknown")
    entrypoint = metadata_dict.get("entrypoint", {})
    if isinstance(entrypoint, dict):
        entrypoint_type = entrypoint.get("type", "python")
        if hasattr(entrypoint_type, "value"):
            entrypoint_type = entrypoint_type.value
        elif not isinstance(entrypoint_type, str):
            raise ValueError(
                f"entrypoint_type must be a string or enum with .value, got: {entrypoint_type}"
            )
        entrypoint_target = entrypoint.get("target", "main.py")
    elif isinstance(entrypoint, str):
        from omnibase.model.model_node_metadata import EntrypointBlock

        try:
            ep_block = EntrypointBlock.from_uri(entrypoint)
            entrypoint_type = ep_block.type
            entrypoint_target = ep_block.target
        except Exception as e:
            raise ValueError(
                f"Entrypoint must be a valid URI string (e.g., python://foo), got: {entrypoint}"
            ) from e
    else:
        raise ValueError(f"Entrypoint must be a dict or URI string, got: {entrypoint}")
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
    return compute_idempotency_hash(
        metadata_model=model,
        body=body,
        volatile_fields=volatile_fields,
        metadata_serializer=metadata_serializer,
        body_canonicalizer=body_canonicalizer,
    )
