# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.429498'
# description: Stamped by PythonHandler
# entrypoint: python://metadata_block_serializer
# hash: 56fabbfdd1673046340ffe2c69ec88fdaa226b821e2ffc04605a9227c23c7166
# last_modified_at: '2025-05-29T14:14:00.526742+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: metadata_block_serializer.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: ef026ffb-eb3e-467a-b62f-7452baef2ba6
# version: 1.0.0
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
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.enums import LogLevelEnum


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
        # Always include semantic fields if present, even if empty (protocol: tools must be present if discovery enabled)
        if k in semantic_fields:
            value = v
            # Always include, even if empty dict
            if value is not None:
                result[k] = value if isinstance(value, dict) else {}
        elif v is None or v == [] or v == {} or v == "null":
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
    comment_prefix: str = None,
    event_bus=None,
) -> str:
    """
    Canonical, deterministic serialization for ONEX metadata blocks.
    Delegates to CanonicalYAMLSerializer with protocol-compliant options.
    Sets comment_prefix to "# " for YAML and ignore files, "" for Markdown.
    """
    # Determine comment prefix if not explicitly set
    if comment_prefix is None:
        if open_delim.strip().startswith("<!--"):  # Markdown
            comment_prefix = ""
        else:  # YAML, ignore, Python
            comment_prefix = "# "
    # Convert model to dict if needed
    if isinstance(model, BaseModel):
        if hasattr(model, "to_serializable_dict"):
            data = model.to_serializable_dict(use_compact_entrypoint=True)
        else:
            data = model.model_dump()
    else:
        data = dict(model)
    # Log tools field before serialization
    try:
        from omnibase.core.core_structured_logging import emit_log_event

        emit_log_event(
            None,
            f"[TRACE] serialize_metadata_block: tools field before serialization: {data.get('tools', 'NOT_SET')}, type: {type(data.get('tools', None))}",
            node_id="metadata_block_serializer",
            event_bus=event_bus,
        )
    except Exception:
        print(
            f"[TRACE] serialize_metadata_block: tools field before serialization: {data.get('tools', 'NOT_SET')}, type: {type(data.get('tools', None))}"
        )
    # Canonical serialization
    yaml_str = CanonicalYAMLSerializer().canonicalize_metadata_block(
        data,
        volatile_fields=(),  # Do not mask any fields for file output
        sort_keys=True,
        explicit_start=False,
        explicit_end=False,
        default_flow_style=False,
        allow_unicode=True,
        comment_prefix=comment_prefix,
    )
    # Log YAML output after serialization
    try:
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[TRACE] serialize_metadata_block: YAML output after serialization:\n{yaml_str}",
            node_id="metadata_block_serializer",
            event_bus=event_bus,
        )
    except Exception:
        print(
            f"[TRACE] serialize_metadata_block: YAML output after serialization:\n{yaml_str}"
        )
    # Add delimiters
    return f"{open_delim}\n{yaml_str}\n{close_delim}\n"


def serialize_python_metadata_block(model: Union[BaseModel, Dict[str, Any]]) -> str:
    """
    Utility for tests: serialize a metadata block as a Python comment block.
    Ensures all lines are prefixed with '# ' and delimiters are correct.
    """
    from omnibase.metadata.metadata_constants import PY_META_OPEN, PY_META_CLOSE

    return serialize_metadata_block(
        model, PY_META_OPEN, PY_META_CLOSE, comment_prefix="# "
    )
