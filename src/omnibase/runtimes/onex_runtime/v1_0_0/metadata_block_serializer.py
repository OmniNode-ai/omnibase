# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: metadata_block_serializer.py
# version: 1.0.0
# uuid: 61e8a105-29dc-410a-92c0-c18705fdc977
# author: OmniNode Team
# created_at: 2025-05-22T16:19:58.861708
# last_modified_at: 2025-05-22T20:22:47.711255
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 90798b9288035f72d06cf66b40ea0b8dd353c4ae95635411dbb9619159750497
# entrypoint: python@metadata_block_serializer.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.metadata_block_serializer
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Centralized logic for serializing ONEX metadata blocks for all file types.
- Filters out None/null/empty values recursively.
- Flattens nested dicts for flat key-value output.
- Parameterized by block delimiters and comment prefix.
- Used by all file handlers to ensure consistent, null-free metadata blocks.
"""

from enum import Enum
from typing import Any, Dict, Union

from pydantic import BaseModel


def _enum_to_str(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, dict):
        return {k: _enum_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_enum_to_str(v) for v in obj]
    else:
        return obj


def _filter_nulls(d: Dict[str, Any]) -> Dict[str, Any]:
    # Recursively filter out None/null/empty values
    # Special handling for semantic fields that should be preserved even when empty
    semantic_fields = {"tools"}  # Fields that have meaning even when empty

    result: Dict[str, Any] = {}
    for k, v in d.items():
        # Preserve semantic fields even when empty
        if k in semantic_fields and isinstance(v, dict):
            result[k] = v
            continue

        if v is None or v == [] or v == {} or v == "null":
            continue
        if isinstance(v, dict):
            filtered_dict = _filter_nulls(v)
            if filtered_dict:
                result[k] = filtered_dict
        elif isinstance(v, list):
            filtered_list = [
                x for x in v if x is not None and x != [] and x != {} and x != "null"
            ]
            if filtered_list:
                result[k] = filtered_list
        else:
            result[k] = v
    return result


def _flatten_dict(
    d: Dict[str, Any], parent_key: str = "", sep: str = "."
) -> Dict[str, Any]:
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)  # type: ignore[assignment]  # mypy false positive: items is list[tuple[str, Any]], return is dict[str, Any]; see review for rationale


def serialize_metadata_block(
    model: Union[BaseModel, Dict[str, Any]],
    open_delim: str,
    close_delim: str,
    comment_prefix: str = "# ",
) -> str:
    """
    Serialize a metadata model or dict as a flat, null-free, single-line comment block.
    Special handling for tools field: preserved as nested YAML structure.
    - open_delim: block opening delimiter (e.g., PY_META_OPEN)
    - close_delim: block closing delimiter (e.g., PY_META_CLOSE)
    - comment_prefix: prefix for each line (e.g., '# ')
    """
    import yaml

    if isinstance(model, BaseModel):
        # Use compact entrypoint format if supported
        if hasattr(model, "to_serializable_dict"):
            data = model.to_serializable_dict(use_compact_entrypoint=True)
        else:
            data = model.model_dump()
    else:
        data = dict(model)  # type: ignore[arg-type]
    data = _enum_to_str(data)
    filtered = _filter_nulls(data)
    # Guarantee type for mypy and runtime
    assert isinstance(filtered, dict), "Expected filtered to be a dict"
    from typing import cast

    # Special handling for tools field - preserve as nested YAML
    tools_data = filtered.pop("tools", None)

    # Flatten everything except tools
    flat = cast(
        dict[str, Any], _flatten_dict(filtered)
    )  # mypy: filtered is always a dict here

    lines = [open_delim]

    # Add flattened fields first
    for k, v in flat.items():
        lines.append(f"{comment_prefix}{k}: {v}")

    # Add tools field as nested YAML if present (including empty tools)
    if tools_data is not None:
        lines.append(f"{comment_prefix}tools:")
        if tools_data:  # Non-empty tools
            # Convert tools to YAML and add with proper indentation
            tools_yaml = yaml.dump(tools_data, default_flow_style=False, sort_keys=True)
            for line in tools_yaml.strip().split("\n"):
                if line.strip():  # Skip empty lines
                    lines.append(f"{comment_prefix}  {line}")
        else:  # Empty tools
            lines.append(f"{comment_prefix}  {{}}")  # Empty dict in YAML format

    lines.append(close_delim)
    lines.append("")

    return "\n".join(lines)
