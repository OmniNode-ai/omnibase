import io
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from pydantic import ValidationError

from omnibase.core.errors import OmniBaseError
from omnibase.model.model_node_metadata import NodeMetadataBlock

# Field type hints for normalization (top-level and common nested fields)
_STRING_FIELDS = {
    "description",
    "author",
    "created_at",
    "last_modified_at",
    "state_contract",
    "hash",
    "license",
    "runtime_language_hint",
    "namespace",
    "meta_type",
    "container_image_reference",
    "url",
    "commit_hash",
    "path",
    "signature",
    "algorithm",
    "signed_by",
    "issued_at",
    "data_residency_required",
    "data_classification",
    "level",
    "format",
    "binding",
    "protocol_required",
    "target",
    "name",
    "type",
}
_LIST_FIELDS = {
    "tags",
    "capabilities",
    "protocols_supported",
    "base_class",
    "dependencies",
    "inputs",
    "outputs",
    "environment",
    "os_requirements",
    "architectures",
    "compliance_profiles",
    "audit_events",
    "canonical_test_case_ids",
    "required_ci_tiers",
}


def _normalize_metadata_dict(obj: Any, parent_key: Optional[str] = None) -> Any:
    """
    Recursively normalize a metadata dict:
    - Convert datetime.datetime to ISO 8601 strings
    - Replace None with empty string for string fields
    - Replace None with [] for list fields
    - Recurse for dicts/lists
    """
    import datetime

    if isinstance(obj, dict):
        return {k: _normalize_metadata_dict(v, k) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_metadata_dict(v) for v in obj]
    elif obj is None:
        if parent_key in _STRING_FIELDS:
            return ""
        if parent_key in _LIST_FIELDS:
            return []
        return obj
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        return obj


def load_node_metadata_from_dict(data: Dict[str, Any]) -> NodeMetadataBlock:
    """
    Deserialize a dict into a NodeMetadataBlock, enforcing ONEX schema and type safety.
    Raises ValidationError on failure.
    See ONEX node_contracts.md for canonical field definitions.
    """
    try:
        # Normalize datetimes and None values
        data = _normalize_metadata_dict(data)
        # Use model_validate for Pydantic v2+
        return NodeMetadataBlock.model_validate(data)
    except ValidationError as e:
        raise OmniBaseError(f"Validation failed: {e}") from e


def load_node_metadata_from_yaml(path: Union[str, Path]) -> NodeMetadataBlock:
    """
    Load and deserialize a YAML file into a NodeMetadataBlock.
    Raises ValidationError or IOError on failure.
    See ONEX node_contracts.md for canonical field definitions.
    """
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return load_node_metadata_from_dict(data)
    except Exception as e:
        raise OmniBaseError(f"YAML load failed: {e}") from e


def load_node_metadata_from_json(path: Union[str, Path]) -> NodeMetadataBlock:
    """
    Load and deserialize a JSON file into a NodeMetadataBlock.
    Raises ValidationError or IOError on failure.
    See ONEX node_contracts.md for canonical field definitions.
    """
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return load_node_metadata_from_dict(data)
    except Exception as e:
        raise OmniBaseError(f"JSON load failed: {e}") from e


def node_metadata_to_json(metadata: NodeMetadataBlock, **kwargs: Any) -> str:
    """
    Serialize a NodeMetadataBlock to a JSON string.
    """
    return json.dumps(metadata.model_dump(), **kwargs)


def node_metadata_to_yaml(metadata: NodeMetadataBlock, **kwargs: Any) -> Any:
    """
    Serialize a NodeMetadataBlock to a YAML string.
    """
    return yaml.safe_dump(metadata.model_dump(), **kwargs)


def load_node_metadata_from_json_str(json_str: str) -> NodeMetadataBlock:
    """
    Load and deserialize a JSON string into a NodeMetadataBlock.
    """
    try:
        data = json.loads(json_str)
        return load_node_metadata_from_dict(data)
    except Exception as e:
        raise OmniBaseError(f"JSON string load failed: {e}") from e


def load_node_metadata_from_yaml_str(yaml_str: str) -> NodeMetadataBlock:
    """
    Load and deserialize a YAML string into a NodeMetadataBlock.
    """
    try:
        data = yaml.safe_load(io.StringIO(yaml_str))
        return load_node_metadata_from_dict(data)
    except Exception as e:
        raise OmniBaseError(f"YAML string load failed: {e}") from e


def extract_node_metadata_from_file(file_path: str) -> NodeMetadataBlock:
    raise NotImplementedError("extract_node_metadata_from_file is not implemented.")
