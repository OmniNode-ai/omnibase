# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.383597'
# description: Stamped by PythonHandler
# entrypoint: python://handler_metadata_yaml
# hash: 520f77269ddff758242d23b0e7a9c7c7b555b71e033527484fc6570f171e9e4a
# last_modified_at: '2025-05-29T14:14:00.447386+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: handler_metadata_yaml.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: f00c9bfe-e6e7-42e0-9302-76d48a65027c
# version: 1.0.0
# === /OmniNode:Metadata ===


import re
from pathlib import Path
from typing import Any, Optional

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.metadata.metadata_constants import (
    YAML_META_CLOSE,
    YAML_META_OPEN,
    get_namespace_prefix,
)
from omnibase.model.model_block_placement_policy import BlockPlacementPolicy
from omnibase.model.model_node_metadata import (
    EntrypointType,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataBlock,
    Namespace,
    EntrypointBlock,
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
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.nodes.stamper_node.v1_0_0.helpers.metadata_block_normalizer import (
    normalize_metadata_block,
)

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class MetadataYAMLHandler(
    ProtocolFileTypeHandler, MetadataBlockMixin, BlockPlacementMixin
):
    """
    Handler for YAML files (.yaml, .yml) for ONEX stamping.
    All block extraction, serialization, and idempotency logic is delegated to the canonical mixins.
    All block emission MUST use the canonical normalize_metadata_block from metadata_block_normalizer (protocol requirement).
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
        default_entrypoint_type: EntrypointType = EntrypointType.YAML,
        default_runtime_language_hint: str = None,
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
        # Use custom predicate if provided
        if self.can_handle_predicate:
            import inspect

            sig = inspect.signature(self.can_handle_predicate)
            if len(sig.parameters) == 1:
                return self.can_handle_predicate(path)
            else:
                return self.can_handle_predicate(path, content)
        # Support .yaml, .yml, and yaml-based templates
        return path.suffix.lower() in {".yaml", ".yml"}

    def extract_block(
        self, path: Path, content: str
    ) -> tuple[Optional[NodeMetadataBlock], Optional[str]]:
        """
        Extracts the ONEX metadata block from YAML content.
        - Uses canonical delimiter constants (YAML_META_OPEN, YAML_META_CLOSE) for all block operations.
        - Attempts to extract both canonical (YAML block with ---/...) and legacy (YAML block with # prefixes, or malformed) blocks.
        - Prefers canonical if both are found; upgrades legacy to canonical.
        - Removes all detected blocks before emitting the new one.
        - Logs warnings if multiple or malformed blocks are found.
        """
        import re
        import yaml
        from omnibase.metadata.metadata_constants import YAML_META_OPEN, YAML_META_CLOSE
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.core.core_structured_logging import emit_log_event
        from omnibase.enums import LogLevelEnum

        # 1. Try canonical block (YAML block with ---/...)
        canonical_pattern = (
            rf"{re.escape(YAML_META_OPEN)}\n(.*?)(?:\n)?{re.escape(YAML_META_CLOSE)}"
        )
        canonical_match = re.search(canonical_pattern, content, re.DOTALL)
        meta = None
        block_yaml = None
        if canonical_match:
            block_yaml = canonical_match.group(1)
            try:
                meta_dict = yaml.safe_load(block_yaml)
                meta = NodeMetadataBlock.model_validate(meta_dict)
            except Exception as e:
                emit_log_event(
                    LogLevelEnum.WARNING,
                    f"Malformed canonical metadata block in {path}: {e}",
                    node_id=_COMPONENT_NAME,
                )
                meta = None
        # 2. If not found, try legacy block (YAML block with # prefixes)
        if not meta:
            legacy_pattern = rf"{re.escape(YAML_META_OPEN)}\n((?:#.*?\n)+){re.escape(YAML_META_CLOSE)}"
            legacy_match = re.search(legacy_pattern, content, re.DOTALL)
            if legacy_match:
                block_legacy = legacy_match.group(1)
                # Remove # prefixes
                yaml_lines = []
                for line in block_legacy.splitlines():
                    if line.strip().startswith("# "):
                        yaml_lines.append(line.strip()[2:])
                    elif line.strip().startswith("#"):
                        yaml_lines.append(line.strip()[1:])
                    else:
                        yaml_lines.append(line)
                block_yaml = "\n".join(yaml_lines)
                try:
                    meta_dict = yaml.safe_load(block_yaml)
                    meta = NodeMetadataBlock.model_validate(meta_dict)
                except Exception as e:
                    emit_log_event(
                        LogLevelEnum.WARNING,
                        f"Malformed legacy metadata block in {path}: {e}",
                        node_id=_COMPONENT_NAME,
                    )
                    meta = None
        # 3. Remove all detected blocks using canonical delimiters
        all_block_pattern = (
            rf"{re.escape(YAML_META_OPEN)}[\s\S]+?{re.escape(YAML_META_CLOSE)}\n*"
        )
        body = re.sub(all_block_pattern, "", content, flags=re.MULTILINE)
        return meta, body

    def serialize_block(self, meta: object, event_bus=None) -> str:
        return serialize_metadata_block(
            meta, YAML_META_OPEN, YAML_META_CLOSE, comment_prefix="# ", event_bus=event_bus
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

    def stamp(self, path: Path, content: str, **kwargs: object) -> OnexResultModel:
        """
        Stamps the file by emitting a protocol-compliant metadata block using the canonical normalizer.
        All block emission must use normalize_metadata_block from metadata_block_normalizer.
        """
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.enums import OnexStatus
        from omnibase.model.model_onex_message_result import OnexResultModel
        # Remove all previous metadata blocks using shared mixin
        content_no_block = MetadataBlockMixin.remove_all_metadata_blocks(str(content) or "", "yaml")
        # Remove leading YAML document marker if present
        content_no_block = content_no_block.lstrip()
        if content_no_block.startswith("---"):
            content_no_block = content_no_block[3:]
            content_no_block = content_no_block.lstrip("\n ")
        # Extract previous metadata block if present
        prev_meta, _ = self.extract_block(path, content)
        prev_uuid = None
        prev_created_at = None
        if prev_meta is not None:
            try:
                valid_meta = NodeMetadataBlock.model_validate(prev_meta)
                prev_uuid = getattr(valid_meta, "uuid", None)
                prev_created_at = getattr(valid_meta, "created_at", None)
            except Exception:
                pass
        # Prepare metadata
        create_kwargs = dict(
            name=path.name,
            author=self.default_author or "OmniNode Team",
            entrypoint_type="yaml",
            entrypoint_target=path.stem,
            description=self.default_description or "Stamped by YAMLHandler",
            meta_type=(
                str(self.default_meta_type.value) if self.default_meta_type else "tool"
            ),
            owner=self.default_owner or "OmniNode Team",
            namespace=f"yaml://{path.stem}",
        )
        if prev_uuid is not None:
            create_kwargs["uuid"] = prev_uuid
        if prev_created_at is not None:
            create_kwargs["created_at"] = prev_created_at
        meta = NodeMetadataBlock.create_with_defaults(**create_kwargs)
        # Use canonical normalizer for emission
        stamped = normalize_metadata_block(content_no_block, "yaml", meta=meta)
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[],
            metadata={
                "content": stamped,
                "note": "Stamped (idempotent or updated)",
                "hash": meta.hash,
            },
        )

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None
