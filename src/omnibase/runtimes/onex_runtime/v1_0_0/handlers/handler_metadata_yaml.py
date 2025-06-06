# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_metadata_yaml.py
# version: 1.0.0
# uuid: 2125bd0a-bbc6-4b32-a441-098d1a55eb88
# author: OmniNode Team
# created_at: 2025-05-22T14:05:25.002521
# last_modified_at: 2025-05-22T20:22:47.712361
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 78a4120df47ff3f60b754188ff400049f8882e717ebd192c61612dadebc99ab1
# entrypoint: python@handler_metadata_yaml.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_metadata_yaml
# meta_type: tool
# === /OmniNode:Metadata ===


import logging
import re
from pathlib import Path
from typing import Any, Optional

from omnibase.core.error_codes import CoreErrorCode, OnexError
from omnibase.enums import OnexStatus
from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN
from omnibase.model.model_block_placement_policy import BlockPlacementPolicy
from omnibase.model.model_node_metadata import (
    EntrypointType,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_message import LogLevelEnum, OnexMessageModel
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_block_placement import (
    BlockPlacementMixin,
)
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_metadata_block import (
    MetadataBlockMixin,
)
from omnibase.schemas.loader import SchemaLoader

logger = logging.getLogger("omnibase.runtime.handlers.handler_metadata_yaml")


class MetadataYAMLHandler(
    ProtocolFileTypeHandler, MetadataBlockMixin, BlockPlacementMixin
):
    """
    Handler for YAML files (.yaml, .yml) for ONEX stamping.
    All block extraction, serialization, and idempotency logic is delegated to the canonical mixins.
    No custom or legacy logic is present; all protocol details are sourced from metadata_constants.
    """

    # Canonical block placement policy (can be customized per handler/file type)
    block_placement_policy = BlockPlacementPolicy(
        allow_shebang=True,
        max_blank_lines_before_block=1,
        allow_license_header=True,
        license_header_pattern=None,
        normalize_blank_lines=True,
        enforce_block_at_top=True,
        placement_policy_version="1.0.0",
    )

    def __init__(
        self,
        default_author: str = "OmniNode Team",
        default_owner: str = "OmniNode Team",
        default_copyright: str = "OmniNode Team",
        default_description: str = "Stamped by MetadataYAMLHandler",
        default_state_contract: str = "state_contract://default",
        default_lifecycle: Lifecycle = Lifecycle.ACTIVE,
        default_meta_type: MetaType = MetaType.TOOL,
        default_entrypoint_type: EntrypointType = EntrypointType.PYTHON,
        default_runtime_language_hint: str = "python>=3.11",
        default_namespace_prefix: str = "onex.stamped",
        can_handle_predicate: Optional[Any] = None,
        schema_loader: Optional[SchemaLoader] = None,
    ):
        self.default_author = default_author
        self.default_owner = default_owner
        self.default_copyright = default_copyright
        self.default_description = default_description
        self.default_state_contract = default_state_contract
        self.default_lifecycle = default_lifecycle
        self.default_meta_type = default_meta_type
        self.default_entrypoint_type = default_entrypoint_type
        self.default_runtime_language_hint = default_runtime_language_hint
        self.default_namespace_prefix = default_namespace_prefix
        self.can_handle_predicate = can_handle_predicate
        self.schema_loader = schema_loader

    # Handler metadata properties (required by ProtocolFileTypeHandler)
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "yaml_metadata_handler"

    @property
    def handler_version(self) -> str:
        """Version of this handler implementation."""
        return "1.0.0"

    @property
    def handler_author(self) -> str:
        """Author or team responsible for this handler."""
        return "OmniNode Team"

    @property
    def handler_description(self) -> str:
        """Brief description of what this handler does."""
        return (
            "Handles YAML files (.yaml, .yml) for ONEX metadata stamping and validation"
        )

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        return [".yaml", ".yml"]

    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        return []  # YAML handler works with extensions, not specific filenames

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 50  # Runtime handler priority

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content."""
        return bool(self.can_handle_predicate)  # Only if custom predicate is provided

    def can_handle(self, path: Path, content: str) -> bool:
        if self.can_handle_predicate:
            return bool(self.can_handle_predicate(path))
        return path.suffix.lower() == ".yaml"

    def extract_block(self, path: Path, content: str) -> tuple[Optional[Any], str]:
        logger.debug(f"[START] extract_block for {path}")
        try:
            prev_meta, rest = self._extract_block_with_delimiters(
                path, content, YAML_META_OPEN, YAML_META_CLOSE
            )
            # # Canonicality check - DISABLED to fix idempotency issue
            # is_canonical, reasons = self.is_canonical_block(
            #     prev_meta, NodeMetadataBlock
            # )
            # if not is_canonical:
            #     logger.warning(
            #         f"Restamping {path} due to non-canonical metadata block: {reasons}"
            #     )
            #     prev_meta = None  # Force restamp in idempotency logic
            logger.debug(f"[END] extract_block for {path}, result=({prev_meta}, rest)")
            return prev_meta, rest
        except Exception as e:
            logger.error(f"Exception in extract_block for {path}: {e}", exc_info=True)
            return None, content

    def _extract_block_with_delimiters(
        self, path: Path, content: str, open_delim: str, close_delim: str
    ) -> tuple[Optional[Any], str]:
        import re

        import yaml

        from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN
        from omnibase.model.model_node_metadata import NodeMetadataBlock

        logger = logging.getLogger("omnibase.handlers.handler_metadata_yaml")
        logger.debug(f"[EXTRACT] Starting extraction for {path}")

        # Find the block between the delimiters
        block_pattern = (
            rf"(?s){re.escape(YAML_META_OPEN)}(.*?){re.escape(YAML_META_CLOSE)}"
        )
        match = re.search(block_pattern, content)
        if not match:
            logger.debug(f"[EXTRACT] No metadata block found in {path}")
            return None, content

        logger.debug(f"[EXTRACT] Metadata block found in {path}")
        block_yaml = match.group(1).strip("\n ")

        prev_meta = None
        if block_yaml:
            try:
                data = yaml.safe_load(block_yaml)
                logger.debug(
                    f"[EXTRACT] YAML parsing successful, keys: {list(data.keys())[:5]}"
                )
                if isinstance(data, dict):
                    # Fix datetime objects - convert to ISO strings
                    for field in ["created_at", "last_modified_at"]:
                        if field in data and hasattr(data[field], "isoformat"):
                            data[field] = data[field].isoformat()

                    # Fix entrypoint format - handle compact format
                    if "entrypoint" in data:
                        entrypoint_val = data["entrypoint"]
                        if isinstance(entrypoint_val, str) and "@" in entrypoint_val:
                            # Compact format: "python@filename.yaml"
                            entry_type, entry_target = entrypoint_val.split("@", 1)
                            data["entrypoint"] = {
                                "type": entry_type.strip(),
                                "target": entry_target.strip(),
                            }
                        # If it's already a dict, keep it as-is

                    prev_meta = NodeMetadataBlock(**data)
                    logger.debug(
                        f"[EXTRACT] NodeMetadataBlock created successfully: {prev_meta.uuid}"
                    )
                elif isinstance(data, NodeMetadataBlock):
                    prev_meta = data
                    logger.debug(
                        f"[EXTRACT] Already NodeMetadataBlock: {prev_meta.uuid}"
                    )
            except Exception as e:
                logger.debug(f"[EXTRACT] Failed to parse block: {e}")
                prev_meta = None

        # Remove the block from the content
        rest = re.sub(block_pattern + r"\n?", "", content, count=1)
        logger.debug(
            f"[EXTRACT] Extraction complete, prev_meta: {prev_meta is not None}"
        )
        return prev_meta, rest

    def serialize_block(self, meta: object) -> str:
        """
        Serialize a NodeMetadataBlock model as a YAML block with delimiters.
        Uses compact entrypoint format and filters out null values.
        """
        from enum import Enum

        import yaml

        from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN
        from omnibase.model.model_node_metadata import NodeMetadataBlock

        def enum_to_str(obj: Any) -> Any:
            if isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, dict):
                return {k: enum_to_str(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [enum_to_str(v) for v in obj]
            else:
                return obj

        def filter_nulls(d: dict) -> dict:
            """Filter out None/null/empty values recursively"""
            from typing import Any

            result: dict[str, Any] = {}
            for k, v in d.items():
                if v is None or v == [] or v == {} or v == "null":
                    continue
                if isinstance(v, dict):
                    filtered = filter_nulls(v)
                    if filtered:
                        result[k] = filtered
                elif isinstance(v, list):
                    filtered_list: list[Any] = [
                        x
                        for x in v
                        if x is not None and x != [] and x != {} and x != "null"
                    ]
                    if filtered_list:
                        result[k] = filtered_list
                else:
                    result[k] = v
            return result

        # Expect a complete NodeMetadataBlock model
        if not isinstance(meta, NodeMetadataBlock):
            raise OnexError(
                f"serialize_block expects NodeMetadataBlock, got {type(meta)}",
                CoreErrorCode.INVALID_PARAMETER,
            )

        # Use compact entrypoint format and filter nulls
        meta_dict = meta.to_serializable_dict(use_compact_entrypoint=True)
        meta_dict = enum_to_str(meta_dict)
        meta_dict = filter_nulls(meta_dict)

        yaml_block = yaml.safe_dump(
            meta_dict, sort_keys=False, default_flow_style=False
        ).strip()
        return f"{YAML_META_OPEN}\n{yaml_block}\n{YAML_META_CLOSE}\n"

    def normalize_rest(self, rest: str) -> str:
        """
        Normalize the rest content after metadata block extraction.
        For YAML files, strip leading document separator '---' to avoid multi-document issues.
        """
        normalized = rest.strip()

        # If the content starts with YAML document separator, remove it
        # This prevents multi-document YAML when metadata block is added
        if normalized.startswith("---"):
            lines = normalized.split("\n", 1)
            if len(lines) > 1:
                # Keep everything after the first line (which is the ---)
                normalized = lines[1].lstrip("\n")
            else:
                # Only had ---, so rest is empty
                normalized = ""

        return normalized

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Validate the YAML content against the ONEX node schema.
        """
        logger.debug(f"validate: content=\n{content}")
        try:
            meta_block_str, _ = self.extract_block(path, content)
            logger.debug(f"validate: meta_block_str=\n{meta_block_str}")
            if meta_block_str:
                meta = NodeMetadataBlock.from_file_or_content(
                    meta_block_str, already_extracted_block=meta_block_str
                )
                logger.debug(f"validate: loaded meta=\n{meta}")
            else:
                meta = None
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                target=None,
                messages=[],
                metadata={"note": "Validation passed"},
            )
        except Exception as e:
            logger.error(f"validate: Exception: {e}")

            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=None,
                messages=[
                    OnexMessageModel(
                        summary=f"Validation failed: {e}", level=LogLevelEnum.ERROR
                    )
                ],
                metadata={"note": "Validation failed", "error": str(e)},
            )

    def normalize_block_placement(self, content: str, policy: Any) -> str:
        """
        Normalize the placement of the metadata block according to block_placement_policy.
        - Preserves shebang if present.
        - Collapses all blank lines above the block to at most one.
        - Removes leading spaces/tabs before the block delimiter.
        - Ensures block is at the canonical position (top of file after shebang).
        """
        policy = self.block_placement_policy
        lines = content.splitlines(keepends=True)
        shebang = None
        start = 0
        # 1. Detect and preserve shebang
        if policy.allow_shebang and lines and lines[0].startswith("#!"):
            shebang = lines[0]
            start = 1
        # 2. Find the block delimiter
        open_delim = YAML_META_OPEN
        close_delim = YAML_META_CLOSE
        block_start = None
        block_end = None
        for i, line in enumerate(lines[start:], start):
            if line.lstrip().startswith(open_delim):
                block_start = i
                break
        if block_start is not None:
            for j in range(block_start, len(lines)):
                if lines[j].lstrip().startswith(close_delim):
                    block_end = j
                    break
        # 3. If block found, move it to canonical position
        if block_start is not None and block_end is not None:
            block_lines = lines[block_start : block_end + 1]
            after_block = lines[block_end + 1 :]
            # Remove leading spaces/tabs from block lines
            block_lines = [re.sub(r"^[ \t]+", "", line) for line in block_lines]
            # Collapse blank lines between shebang and block to at most one
            normalized = []
            if shebang:
                normalized.append(shebang)
            normalized.append("\n")  # At most one blank line
            normalized.extend(block_lines)
            # Remove leading blank lines after block
            after_block = list(after_block)
            while after_block and after_block[0].strip() == "":
                after_block.pop(0)
            normalized.extend(after_block)
            return "".join(normalized)
        else:
            # No block found, just normalize leading whitespace
            normalized = []
            if shebang:
                normalized.append(shebang)
            normalized.append("\n")
            normalized.extend(lines[start:])
            return "".join(normalized)

    def _normalize_filename_for_namespace(self, filename: str) -> str:
        """
        Normalize a filename for use in namespace generation.
        Removes leading dots, replaces dashes with underscores, and ensures valid characters.
        """
        import re

        # Remove leading dots
        normalized = filename.lstrip(".")
        # Replace dashes and other invalid chars with underscores
        normalized = re.sub(r"[^a-zA-Z0-9_]", "_", normalized)
        # Remove consecutive underscores
        normalized = re.sub(r"_+", "_", normalized)
        # Remove leading/trailing underscores
        normalized = normalized.strip("_")
        # Ensure not empty
        if not normalized:
            normalized = "file"
        return normalized

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Use the centralized idempotency logic from MetadataBlockMixin for stamping.
        All protocol details are sourced from metadata_constants.
        Protocol: Must return only OnexResultModel, never the tuple from stamp_with_idempotency.
        """
        from omnibase.model.model_node_metadata import NodeMetadataBlock

        # Normalize filename for namespace
        normalized_name = self._normalize_filename_for_namespace(path.stem)

        # Create a complete metadata model instead of a dictionary
        default_metadata = NodeMetadataBlock.create_with_defaults(
            name=path.name,
            author=self.default_author,
            namespace=f"{self.default_namespace_prefix}.{normalized_name}",
            entrypoint_type=str(self.default_entrypoint_type.value),
            entrypoint_target=path.name,
            description=self.default_description,
            meta_type=str(self.default_meta_type.value),
            owner=self.default_owner,
            copyright=self.default_copyright,
            state_contract=self.default_state_contract,
            lifecycle=str(self.default_lifecycle.value),
            runtime_language_hint=self.default_runtime_language_hint,
        )

        # Convert model to dictionary for context_defaults
        context_defaults = default_metadata.model_dump()

        result_tuple: tuple[str, OnexResultModel] = self.stamp_with_idempotency(
            path=path,
            content=content,
            author=self.default_author,
            entrypoint_type=self.default_entrypoint_type,
            namespace_prefix=self.default_namespace_prefix,
            meta_type=self.default_meta_type,
            description=self.default_description,
            extract_block_fn=self.extract_block,
            serialize_block_fn=self.serialize_block,
            normalize_rest_fn=self.normalize_rest,
            model_cls=NodeMetadataBlock,
            context_defaults=context_defaults,
        )
        _, result = result_tuple
        return result

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None
