# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: metadata_utils
# version: 1.0.0
# uuid: edcd83de-67f4-400e-8e65-76581bc6911a
# author: OmniNode Team
# created_at: 2025-05-21T12:28:06.905362
# last_modified_at: 2025-05-21T12:28:06.905362
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 284b90a5bdfca8dca5a2a2df6aec1b5072e21f2c05b4ae063e04926be549c5c7
# entrypoint: {'type': 'python', 'target': 'metadata_utils.py'}
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
    - Masks volatile fields in metadata with a constant placeholder.
    - Canonicalizes the body (if a canonicalizer is provided).
    - Serializes metadata (if a serializer is provided).
    Returns the concatenated canonicalized metadata and body as a string.
    """
    meta_for_hash = metadata.copy()
    for field in volatile_fields:
        if field == "hash":
            meta_for_hash[field] = "0" * 64  # Use valid dummy hash
        elif field == "last_modified_at":
            meta_for_hash[field] = "1970-01-01T00:00:00Z"
        else:
            meta_for_hash[field] = None
    meta_str = (
        metadata_serializer(meta_for_hash)
        if metadata_serializer
        else str(meta_for_hash)
    )
    body_str = body_canonicalizer(body) if body_canonicalizer else body
    return meta_str + "\n" + body_str
