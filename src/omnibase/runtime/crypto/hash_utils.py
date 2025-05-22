# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: hash_utils.py
# version: 1.0.0
# uuid: '319e66d1-abee-487e-a37f-8acfc43bdf9d'
# author: OmniNode Team
# created_at: '2025-05-22T05:34:29.787636'
# last_modified_at: '2025-05-22T18:33:30.893768'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: hash_utils.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.hash_utils
# meta_type: tool
# trust_score: null
# tags: null
# capabilities: null
# protocols_supported: null
# base_class: null
# dependencies: null
# inputs: null
# outputs: null
# environment: null
# license: null
# signature_block: null
# x_extensions: {}
# testing: null
# os_requirements: null
# architectures: null
# container_image_reference: null
# compliance_profiles: []
# data_handling_declaration: null
# logging_config: null
# source_repository: null
# === /OmniNode:Metadata ===


import hashlib
from typing import Any, Tuple

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
