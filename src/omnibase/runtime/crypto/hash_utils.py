import hashlib
from typing import Any, Optional, Tuple

import yaml


def canonicalize_metadata_block(
    meta: Any,
    volatile_fields: Tuple[str, ...] = ("hash", "last_modified_at"),
    placeholder: str = "<PLACEHOLDER>",
) -> str:
    """
    Canonicalize a metadata block for deterministic YAML serialization and hash computation.
    - Accepts a dict or model instance.
    - Replaces volatile fields (e.g., hash, last_modified_at) with a protocol placeholder.
    - Returns the canonical YAML string (UTF-8, normalized line endings).
    """
    if hasattr(meta, "model_dump"):
        meta_dict = meta.model_dump()
    else:
        meta_dict = dict(meta)
    for field in volatile_fields:
        if field in meta_dict:
            meta_dict[field] = placeholder
    yaml_str = yaml.dump(
        meta_dict, sort_keys=True, default_flow_style=False, allow_unicode=True
    )
    yaml_str = yaml_str.replace("\xa0", " ")
    yaml_str = yaml_str.replace("\r\n", "\n").replace("\r", "\n")
    assert "\r" not in yaml_str, "Carriage return found in canonical YAML string"
    yaml_str.encode("utf-8")
    return yaml_str


def normalize_body(body: str) -> str:
    """
    Canonical normalization for file body content.
    - Strips trailing spaces
    - Normalizes all line endings to '\n'
    - Ensures exactly one newline at EOF
    - Asserts only '\n' line endings are present
    """
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    norm = body.rstrip(" \t\r\n") + "\n"
    assert "\r" not in norm, "Carriage return found after normalization"
    return norm


def compute_canonical_hash(
    meta: Any,
    body: str,
    volatile_fields: Tuple[str, ...] = ("hash", "last_modified_at"),
    placeholder: str = "<PLACEHOLDER>",
) -> str:
    """
    Compute the hash for the normalized metadata block and file body.
    - Serializes the metadata block with volatile fields replaced by placeholders.
    - Concatenates the canonicalized metadata and normalized body.
    - Computes and returns the SHA-256 hash as a hex string.
    """
    meta_yaml = canonicalize_metadata_block(meta, volatile_fields, placeholder)
    norm_body = normalize_body(body)
    canonical = meta_yaml.rstrip("\n") + "\n\n" + norm_body.lstrip("\n")
    h = hashlib.sha256()
    h.update(canonical.encode("utf-8"))
    return h.hexdigest()
