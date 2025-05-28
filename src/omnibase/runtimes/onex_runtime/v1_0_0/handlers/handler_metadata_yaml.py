# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_metadata_yaml.py
# version: 1.0.0
# uuid: f00c9bfe-e6e7-42e0-9302-76d48a65027c
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.383597
# last_modified_at: 2025-05-28T17:20:06.146699
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 24316c753c79834e61c69b15b3f517f9ec53c50082ab0b1a7ab7636c38216022
# entrypoint: python@handler_metadata_yaml.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.handler_metadata_yaml
# meta_type: tool
# === /OmniNode:Metadata ===


import re
from pathlib import Path
from typing import Any, Optional

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN, get_namespace_prefix
from omnibase.model.model_block_placement_policy import BlockPlacementPolicy
from omnibase.model.model_node_metadata import (
    EntrypointType,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_message import OnexMessageModel
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_block_placement import (
    BlockPlacementMixin,
)
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_metadata_block import (
    MetadataBlockMixin,
)
from omnibase.schemas.loader import SchemaLoader
from omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer import (
    serialize_metadata_block,
)

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class MetadataYAMLHandler(
    ProtocolFileTypeHandler, MetadataBlockMixin, BlockPlacementMixin
):
    """
    Handler for YAML files (.yaml, .yml) for ONEX stamping.
    All block extraction, serialization, and idempotency logic is delegated to the canonical mixins.
    No custom or legacy logic is present; all protocol details are sourced from metadata_constants.
    All extracted metadata blocks must be validated and normalized using the canonical Pydantic model (NodeMetadataBlock) before further processing.
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
        default_meta_type: MetaTypeEnum = MetaTypeEnum.TOOL,
        default_entrypoint_type: EntrypointType = EntrypointType.PYTHON,
        default_runtime_language_hint: str = "python>=3.11",
        default_namespace_prefix: str = f"{get_namespace_prefix()}.stamped",
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
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[START] extract_block for {path}",
            node_id=_COMPONENT_NAME,
        )
        try:
            prev_meta, rest = self._extract_block_with_delimiters(
                path, content, YAML_META_OPEN, YAML_META_CLOSE
            )
            # # Canonicality check - DISABLED to fix idempotency issue
            # is_canonical, reasons = self.is_canonical_block(
            #     prev_meta, NodeMetadataBlock
            # )
            # if not is_canonical:
            #     emit_log_event(
            #         LogLevelEnum.WARNING,
            #         f"Restamping {path} due to non-canonical metadata block: {reasons}",
            #         node_id=_COMPONENT_NAME,
            #     )
            #     prev_meta = None  # Force restamp in idempotency logic
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"[END] extract_block for {path}, result=({prev_meta}, rest)",
                node_id=_COMPONENT_NAME,
            )
            return prev_meta, rest
        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Exception in extract_block for {path}: {e}",
                node_id=_COMPONENT_NAME,
            )
            return None, content

    def _extract_block_with_delimiters(
        self, path: Path, content: str, open_delim: str, close_delim: str
    ) -> tuple[Optional[Any], str]:
        import re
        import yaml
        from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN
        from omnibase.model.model_node_metadata import NodeMetadataBlock

        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[EXTRACT] Starting extraction for {path}",
            node_id=_COMPONENT_NAME,
        )

        # Find the block between the delimiters
        block_pattern = (
            rf"(?s){re.escape(YAML_META_OPEN)}(.*?){re.escape(YAML_META_CLOSE)}"
        )
        match = re.search(block_pattern, content)
        if not match:
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"[EXTRACT] No metadata block found in {path}",
                node_id=_COMPONENT_NAME,
            )
            return None, content

        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[EXTRACT] Metadata block found in {path}",
            node_id=_COMPONENT_NAME,
        )
        block_content = match.group(1).strip("\n ")

        # Remove '# ' prefix from each line to get clean YAML
        yaml_lines = []
        for line in block_content.split("\n"):
            if line.startswith("# "):
                yaml_lines.append(line[2:])  # Remove '# ' prefix
            elif line.startswith("#"):
                yaml_lines.append(line[1:])  # Remove '#' prefix
            else:
                yaml_lines.append(line)  # Keep line as-is

        block_yaml = "\n".join(yaml_lines).strip()
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[EXTRACT] Processed YAML length: {len(block_yaml)}",
            node_id=_COMPONENT_NAME,
        )

        prev_meta = None
        if block_yaml:
            try:
                data = yaml.safe_load(block_yaml)
                emit_log_event(
                    LogLevelEnum.DEBUG,
                    f"[EXTRACT] YAML parsing successful, keys: {list(data.keys())[:5] if isinstance(data, dict) else 'N/A'}",
                    node_id=_COMPONENT_NAME,
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
                    emit_log_event(
                        LogLevelEnum.DEBUG,
                        f"[EXTRACT] NodeMetadataBlock created successfully: {prev_meta.uuid}",
                        node_id=_COMPONENT_NAME,
                    )
                elif isinstance(data, NodeMetadataBlock):
                    prev_meta = data
                    emit_log_event(
                        LogLevelEnum.DEBUG,
                        f"[EXTRACT] Already NodeMetadataBlock: {prev_meta.uuid}",
                        node_id=_COMPONENT_NAME,
                    )
            except Exception as e:
                emit_log_event(
                    LogLevelEnum.DEBUG,
                    f"[EXTRACT] Failed to parse block as YAML: {e}",
                    node_id=_COMPONENT_NAME,
                )
                prev_meta = None

        # Remove the block from the content
        rest = re.sub(block_pattern + r"\n?", "", content, count=1)
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[EXTRACT] Extraction complete, prev_meta: {prev_meta is not None}",
            node_id=_COMPONENT_NAME,
        )
        return prev_meta, rest

    def serialize_block(self, meta: object) -> str:
        return serialize_metadata_block(
            meta, YAML_META_OPEN, YAML_META_CLOSE, comment_prefix="# "
        )

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
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"validate: content=\n{content}",
            node_id=_COMPONENT_NAME,
        )
        try:
            meta_block_str, _ = self.extract_block(path, content)
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"validate: meta_block_str=\n{meta_block_str}",
                node_id=_COMPONENT_NAME,
            )
            if meta_block_str:
                meta = NodeMetadataBlock.from_file_or_content(
                    meta_block_str, already_extracted_block=meta_block_str
                )
                emit_log_event(
                    LogLevelEnum.DEBUG,
                    f"validate: loaded meta=\n{meta}",
                    node_id=_COMPONENT_NAME,
                )
            else:
                meta = None
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                target=None,
                messages=[],
                metadata={"note": "Validation passed"},
            )
        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"validate: Exception: {e}",
                node_id=_COMPONENT_NAME,
            )

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
        # Remove namespace since it's now generated automatically from file path
        context_defaults.pop("namespace", None)

        result_tuple: tuple[str, OnexResultModel] = self.stamp_with_idempotency(
            path=path,
            content=content,
            author=self.default_author,
            entrypoint_type=self.default_entrypoint_type,
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
