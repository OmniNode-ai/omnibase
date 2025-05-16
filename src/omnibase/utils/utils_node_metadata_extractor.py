from typing import Any, Dict, Union
from pathlib import Path
from pydantic import ValidationError
from omnibase.model.model_node_metadata import NodeMetadataBlock
import yaml
import json
from omnibase.core.errors import OmniBaseError


def load_node_metadata_from_dict(data: Dict[str, Any]) -> NodeMetadataBlock:
    """
    Deserialize a dict into a NodeMetadataBlock, enforcing ONEX schema and type safety.
    Raises ValidationError on failure.
    See ONEX node_contracts.md for canonical field definitions.
    """
    try:
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