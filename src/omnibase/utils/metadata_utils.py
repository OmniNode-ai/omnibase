# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: metadata_utils.py
# version: 1.0.0
# uuid: c59268b5-88b9-433f-9df5-7e4dc7037691
# author: OmniNode Team
# created_at: 2025-05-22T14:05:21.449308
# last_modified_at: 2025-05-22T20:50:39.712639
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: be4418331d4279b7e59df0688a615ec5e912ad9601cafcf173520381ecc226f4
# entrypoint: python@metadata_utils.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.metadata_utils
# meta_type: tool
# === /OmniNode:Metadata ===


import hashlib
import uuid
from typing import Any, Dict, List


def generate_uuid() -> str:
    return str(uuid.uuid4())


def compute_canonical_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def canonicalize_for_hash(
    metadata: Dict[str, Any],
    body: str,
    volatile_fields: List[str] = ["hash", "last_modified_at"],
    metadata_serializer: Any = None,
    body_canonicalizer: Any = None,
) -> str:
    """
    Canonicalize metadata and body for hash computation.
    - Constructs a complete NodeMetadataBlock model from metadata dict
    - Masks volatile fields in metadata with a constant placeholder.
    - Canonicalizes the body (if a canonicalizer is provided).
    - Serializes metadata (if a serializer is provided).
    Returns the concatenated canonicalized metadata and body as a string.
    """
    from omnibase.model.model_node_metadata import NodeMetadataBlock

    # Extract key fields from metadata dict, use model defaults for missing fields
    name = metadata.get("name", "unknown")
    author = metadata.get("author", "unknown")
    namespace = metadata.get("namespace", "onex.stamped.unknown")

    # Handle entrypoint - support both dict and string formats
    entrypoint = metadata.get("entrypoint", {})
    if isinstance(entrypoint, dict):
        entrypoint_type = entrypoint.get("type", "python")
        entrypoint_target = entrypoint.get("target", "main.py")
    elif isinstance(entrypoint, str) and "@" in entrypoint:
        # Parse string format like "python@filename.py"
        parts = entrypoint.split("@", 1)
        entrypoint_type = parts[0]
        entrypoint_target = parts[1]
    else:
        entrypoint_type = "python"
        entrypoint_target = "main.py"

    # Create complete model using the canonical constructor
    model = NodeMetadataBlock.create_with_defaults(
        name=name,
        author=author,
        namespace=namespace,
        entrypoint_type=entrypoint_type,
        entrypoint_target=entrypoint_target,
        **{
            k: v
            for k, v in metadata.items()
            if k not in ["name", "author", "namespace", "entrypoint"]
        },
    )

    # Now mask volatile fields for hash computation
    model_dict = model.model_dump()
    for field in volatile_fields:
        if field == "hash":
            model_dict[field] = "0" * 64  # Use valid dummy hash
        elif field == "last_modified_at":
            model_dict[field] = "1970-01-01T00:00:00Z"
        else:
            model_dict[field] = None

    # Reconstruct model with masked fields
    meta_for_hash = NodeMetadataBlock(**model_dict)

    meta_str = (
        metadata_serializer(meta_for_hash)
        if metadata_serializer
        else str(meta_for_hash.model_dump())
    )
    body_str = body_canonicalizer(body) if body_canonicalizer else body
    return meta_str + "\n" + body_str
