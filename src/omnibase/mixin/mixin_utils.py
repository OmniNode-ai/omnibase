# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: mixin_utils.py
# version: 1.0.0
# uuid: e3b37250-8a08-4cf9-a81e-ac00912e5b9a
# author: OmniNode Team
# created_at: 2025-05-22T14:05:24.975516
# last_modified_at: 2025-05-22T20:31:11.354033
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 2ca1e237da124bc8baa1a8fad1fa069a468c714f6fa049f82be282b23b8efd7a
# entrypoint: python@mixin_utils.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.mixin_utils
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import TYPE_CHECKING, Any, Dict, Tuple, Union

from omnibase.enums import NodeMetadataField

from .mixin_canonical_serialization import CanonicalYAMLSerializer

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock


def canonicalize_metadata_block(
    block: Union[Dict[str, object], "NodeMetadataBlock"],
    volatile_fields: Tuple[NodeMetadataField, ...] = (
        NodeMetadataField.HASH,
        NodeMetadataField.LAST_MODIFIED_AT,
    ),
    placeholder: str = "<PLACEHOLDER>",
    sort_keys: bool = True,
    explicit_start: bool = True,
    explicit_end: bool = True,
    default_flow_style: bool = False,
    allow_unicode: bool = True,
    comment_prefix: str = "",
    **kwargs: Any,
) -> str:
    """
    Utility function to canonicalize a metadata block using CanonicalYAMLSerializer.
    Args:
        block: A dict or model instance (must implement model_dump(mode="json")).
        volatile_fields: Fields to replace with protocol placeholder values.
        placeholder: Placeholder value for volatile fields.
        sort_keys: Whether to sort keys in YAML output.
        explicit_start: Whether to include '---' at the start of YAML.
        explicit_end: Whether to include '...' at the end of YAML.
        default_flow_style: Use block style YAML.
        allow_unicode: Allow unicode in YAML output.
        comment_prefix: Prefix to add to each line (for comment blocks).
        **kwargs: Additional keyword arguments for CanonicalYAMLSerializer.canonicalize_metadata_block.
    Returns:
        Canonical YAML string for the metadata block.
    """
    return str(
        CanonicalYAMLSerializer().canonicalize_metadata_block(
            block,
            volatile_fields=volatile_fields,
            placeholder=placeholder,
            sort_keys=sort_keys,
            explicit_start=explicit_start,
            explicit_end=explicit_end,
            default_flow_style=default_flow_style,
            allow_unicode=allow_unicode,
            comment_prefix=comment_prefix,
            **kwargs,
        )
    )
