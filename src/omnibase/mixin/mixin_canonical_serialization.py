# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: mixin_canonical_serialization.py
# version: 1.0.0
# uuid: 'e81e0d32-9125-419d-b4ca-169bb12ebff8'
# author: OmniNode Team
# created_at: '2025-05-22T14:05:24.971514'
# last_modified_at: '2025-05-22T18:05:26.846318'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: mixin_canonical_serialization.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.mixin_canonical_serialization
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


from typing import TYPE_CHECKING, Dict, Optional, Tuple, Union

import yaml

from omnibase.model.model_enum_metadata import NodeMetadataField
from omnibase.protocol.protocol_canonical_serializer import ProtocolCanonicalSerializer

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock


def _strip_comment_prefix(
    block: str, comment_prefixes: Tuple[str, ...] = ("# ", "#")
) -> str:
    """
    Remove leading comment prefixes from each line of a block.
    Args:
        block: Multiline string block to process.
        comment_prefixes: Tuple/list of prefix strings to remove from line starts.
    Returns:
        Block with comment prefixes removed from each line.
    """
    lines = block.splitlines()

    def _strip_line(line: str) -> str:
        for prefix in comment_prefixes:
            if line.lstrip().startswith(prefix):
                # Remove only one prefix per line, after optional leading whitespace
                i = line.find(prefix)
                return line[:i] + line[i + len(prefix) :]
        return line

    return "\n".join(_strip_line(line) for line in lines)


class CanonicalYAMLSerializer(ProtocolCanonicalSerializer):
    """
    Canonical YAML serializer implementing ProtocolCanonicalSerializer.
    Provides protocol-compliant, deterministic serialization and normalization for stamping, hashing, and idempotency.
    All field normalization and placeholder logic is schema-driven, using NodeMetadataBlock.model_fields.
    No hardcoded field names or types.
    """

    def canonicalize_metadata_block(
        self,
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
        **kwargs: object,
    ) -> str:
        """
        Canonicalize a metadata block for deterministic YAML serialization and hash computation.
        Args:
            block: A dict or NodeMetadataBlock instance (must implement model_dump(mode="json")).
            volatile_fields: Fields to replace with protocol placeholder values.
            placeholder: Placeholder value for volatile fields.
            sort_keys: Whether to sort keys in YAML output.
            explicit_start: Whether to include '---' at the start of YAML.
            explicit_end: Whether to include '...' at the end of YAML.
            default_flow_style: Use block style YAML.
            allow_unicode: Allow unicode in YAML output.
            comment_prefix: Prefix to add to each line (for comment blocks).
            **kwargs: Additional arguments for yaml.dump.
        Returns:
            Canonical YAML string (UTF-8, normalized line endings), with optional comment prefix.
        """
        import pydantic

        from omnibase.model.model_node_metadata import NodeMetadataBlock

        if isinstance(block, dict):
            # Convert dict to NodeMetadataBlock, handling type conversions
            try:
                block = NodeMetadataBlock(**block)  # type: ignore[arg-type]
            except (pydantic.ValidationError, TypeError):
                # If direct construction fails, try with model validation
                block = NodeMetadataBlock.model_validate(block)

        block_dict = block.model_dump(mode="json")
        # Protocol-compliant placeholders
        protocol_placeholders = {
            NodeMetadataField.HASH.value: "0" * 64,
            NodeMetadataField.LAST_MODIFIED_AT.value: "1970-01-01T00:00:00Z",
        }
        # Dynamically determine string and list fields from the model
        string_fields = set()
        list_fields = set()

        for name, field in NodeMetadataBlock.model_fields.items():
            annotation = field.annotation
            if annotation is None:
                continue
            origin = getattr(annotation, "__origin__", None)

            # Check for Union types
            if origin is Union and hasattr(annotation, "__args__"):
                args = annotation.__args__
                if str in args:
                    string_fields.add(name)
                if list in args:
                    list_fields.add(name)
            # Check for direct types
            elif annotation is str:
                string_fields.add(name)
            elif annotation is list:
                list_fields.add(name)

        normalized_dict: Dict[str, object] = {}
        for k, v in block_dict.items():
            # Replace volatile fields with protocol placeholder
            if k in protocol_placeholders:
                normalized_dict[k] = protocol_placeholders[k]
                continue
            # Convert NodeMetadataField to .value
            if isinstance(v, NodeMetadataField):
                v = v.value
            # Normalize string fields
            if k in string_fields and (v is None or v == "null"):
                normalized_dict[k] = ""
                continue
            # Normalize list fields
            if k in list_fields and (v is None or v == "null"):
                normalized_dict[k] = []
                continue
            normalized_dict[k] = v
        yaml_str = yaml.dump(
            normalized_dict,
            sort_keys=sort_keys,
            default_flow_style=default_flow_style,
            allow_unicode=allow_unicode,
            explicit_start=explicit_start,
            explicit_end=explicit_end,
        )
        yaml_str = yaml_str.replace("\xa0", " ")
        yaml_str = yaml_str.replace("\r\n", "\n").replace("\r", "\n")
        assert "\r" not in yaml_str, "Carriage return found in canonical YAML string"
        yaml_str.encode("utf-8")  # Explicitly check UTF-8 encoding
        if comment_prefix:
            yaml_str = "\n".join(
                f"{comment_prefix}{line}" if line.strip() else ""
                for line in yaml_str.splitlines()
            )
        return yaml_str

    def normalize_body(self, body: str) -> str:
        """
        Canonical normalization for file body content.
        Args:
            body: The file body content to normalize.
        Returns:
            Normalized file body as a string.
        """
        body = body.replace("\r\n", "\n").replace("\r", "\n")
        norm = body.rstrip(" \t\r\n") + "\n"
        assert "\r" not in norm, "Carriage return found after normalization"
        return norm

    def canonicalize_for_hash(
        self,
        block: Union[Dict[str, object], "NodeMetadataBlock"],
        body: str,
        volatile_fields: Tuple[NodeMetadataField, ...] = (
            NodeMetadataField.HASH,
            NodeMetadataField.LAST_MODIFIED_AT,
        ),
        placeholder: str = "<PLACEHOLDER>",
        comment_prefix: str = "",
        **kwargs: object,
    ) -> str:
        """
        Canonicalize a metadata block and file body for hash computation.
        Args:
            block: A dict or NodeMetadataBlock instance (must implement model_dump(mode="json")).
            body: The file body content to normalize and include in hash.
            volatile_fields: Fields to replace with protocol placeholder values.
            placeholder: Placeholder value for volatile fields.
            comment_prefix: Prefix to add to each line (for comment blocks).
            **kwargs: Additional arguments for canonicalization.
        Returns:
            Canonical string for hash computation.
        """
        meta_yaml = self.canonicalize_metadata_block(
            block,
            volatile_fields=volatile_fields,
            placeholder=placeholder,
            explicit_start=False,
            explicit_end=False,
            comment_prefix=comment_prefix,
        )
        norm_body = self.normalize_body(body)
        canonical = meta_yaml.rstrip("\n") + "\n\n" + norm_body.lstrip("\n")
        return canonical


normalize_body = CanonicalYAMLSerializer().normalize_body


def extract_metadata_block_and_body(
    content: str, open_delim: str, close_delim: str
) -> tuple[Optional[str], str]:
    """
    Canonical utility: Extract the metadata block (if present) and the rest of the file content.
    Returns (block_str or None, rest_of_content).
    """
    import logging
    import re

    logger = logging.getLogger("omnibase.canonical.canonical_serialization")

    # Accept both commented (# === ... ===) and non-commented (=== ... ===) delimiter forms for robust round-trip idempotency.
    # Allow every line between the delimiters to be optionally prefixed with a comment (e.g., '# '),
    # so it matches fully commented, non-commented, and mixed forms.
    # The block may be at the very start of the file, after a shebang, or after blank lines.
    pattern = (
        rf"(?ms)"  # multiline, dotall
        rf"^(?:[ \t\r\f\v]*\n)*"  # any number of leading blank lines/whitespace
        rf"[ \t\r\f\v]*(?:#\s*)?{re.escape(open_delim)}[ \t]*\n"  # open delimiter
        rf"((?:[ \t\r\f\v]*(?:#\s*)?.*\n)*?)"  # block content: any number of lines, each optionally commented
        rf"[ \t\r\f\v]*(?:#\s*)?{re.escape(close_delim)}[ \t]*\n?"  # close delimiter
    )

    match = re.search(pattern, content)
    if match:
        # Re-extract the full block, including delimiters
        block_start = match.start()
        block_end = match.end()
        block_str = content[block_start:block_end]
        rest = content[block_end:]
        # Strip comment prefixes from all lines (including delimiters) for downstream detection
        block_lines = block_str.splitlines()
        block_str_stripped = "\n".join(
            _strip_comment_prefix(line) for line in block_lines
        )
        logger.debug(
            f"extract_metadata_block_and_body: block_str=\n{block_str}\nrest=\n{rest}"
        )
        # Return the prefix-stripped block_str for downstream usage
        return block_str_stripped, rest
    else:
        logger.debug("extract_metadata_block_and_body: No block found")
        return None, content


def strip_block_delimiters_and_assert(
    lines: list[str], delimiters: set[str], context: str = ""
) -> str:
    """
    Canonical utility: Remove all lines that exactly match any delimiter. Assert none remain after filtering.
    Args:
        lines: List of lines (after comment prefix stripping)
        delimiters: Set of delimiter strings (imported from canonical constants)
        context: Optional context string for error messages
    Returns:
        Cleaned YAML string (no delimiters)
    Raises:
        AssertionError if any delimiter lines remain after filtering.
    """
    cleaned = [line for line in lines if line.strip() not in delimiters]
    remaining = [line for line in cleaned if line.strip() in delimiters]
    if remaining:
        raise AssertionError(
            f"Delimiter(s) still present after filtering in {context}: {remaining}"
        )
    return "\n".join(cleaned).strip()
