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
    - Masks volatile fields in metadata with a constant placeholder.
    - Canonicalizes the body (if a canonicalizer is provided).
    - Serializes metadata (if a serializer is provided).
    Returns the concatenated canonicalized metadata and body as a string.
    """
    meta_for_hash = metadata.copy()
    for field in volatile_fields:
        if field in meta_for_hash:
            meta_for_hash[field] = "<PLACEHOLDER>"
    meta_str = (
        metadata_serializer(meta_for_hash)
        if metadata_serializer
        else str(meta_for_hash)
    )
    body_str = body_canonicalizer(body) if body_canonicalizer else body
    return meta_str + "\n" + body_str
