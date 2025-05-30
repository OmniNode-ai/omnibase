# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.374558'
# description: Stamped by PythonHandler
# entrypoint: python://handler_markdown
# hash: 1d8b135a331c8c31b642913d31790250086f0893349761ee2119e8fc347cc4ec
# last_modified_at: '2025-05-29T14:14:00.440055+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: handler_markdown.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_markdown
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: dbb0cf44-e3d6-40f0-a6f9-944b9cd3e3f7
# version: 1.0.0
# === /OmniNode:Metadata ===


import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.metadata.metadata_constants import (
    MD_META_CLOSE,
    MD_META_OPEN,
    get_namespace_prefix,
)
from omnibase.model.model_node_metadata import NodeMetadataBlock, Namespace

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock

from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_block_placement import (
    BlockPlacementMixin,
)
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_metadata_block import (
    MetadataBlockMixin,
)
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class MarkdownHandler(ProtocolFileTypeHandler, MetadataBlockMixin, BlockPlacementMixin):
    """
    Handler for Markdown (.md) files for ONEX stamping.
    All block extraction, serialization, and idempotency logic is delegated to the canonical mixins.
    All block emission MUST use the canonical normalize_metadata_block from metadata_block_normalizer (protocol requirement).
    No custom or legacy logic is present; all protocol details are sourced from metadata_constants.
    All extracted metadata blocks must be validated and normalized using the canonical Pydantic model (NodeMetadataBlock) before further processing.
    """

    def __init__(
        self,
        default_author: str = "OmniNode Team",
        default_entrypoint_type: str = "markdown",
        default_namespace_prefix: str = f"{get_namespace_prefix()}.stamped",
        default_meta_type: Optional[Any] = None,
        default_description: Optional[str] = None,
    ) -> None:
        self.default_author = default_author
        self.default_entrypoint_type = default_entrypoint_type
        self.default_namespace_prefix = default_namespace_prefix
        self.default_meta_type = default_meta_type
        self.default_description = default_description

    # Handler metadata properties (required by ProtocolFileTypeHandler)
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "markdown_handler"

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
        return "Handles Markdown files (.md) for ONEX metadata stamping and validation"

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        return [".md", ".markdown"]

    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        return []  # Markdown handler works with extensions, not specific filenames

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 50  # Runtime handler priority

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content."""
        return False  # Markdown handler uses extension-based detection

    def can_handle(self, path: Path, content: str) -> bool:
        # Support .md, .markdown, .mdx, and markdown-based templates
        return path.suffix.lower() in {".md", ".markdown", ".mdx"}

    def extract_block(
        self, path: Path, content: str
    ) -> tuple[Optional[NodeMetadataBlock], Optional[str]]:
        """
        Extracts the ONEX metadata block from Markdown content.
        - Uses canonical delimiter constants (MD_META_OPEN, MD_META_CLOSE) for all block operations.
        - Attempts to extract canonical (YAML in HTML comment), legacy (YAML in HTML comment with # prefixes), and legacy field-per-comment (<!-- field: value -->) blocks.
        - Prefers canonical if both are found; upgrades legacy to canonical.
        - Removes all detected blocks before emitting the new one.
        - Logs warnings if multiple or malformed blocks are found.
        """
        import re
        import yaml
        from omnibase.metadata.metadata_constants import MD_META_OPEN, MD_META_CLOSE
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.core.core_structured_logging import emit_log_event
        from omnibase.enums import LogLevelEnum

        # 1. Try canonical block (YAML in HTML comment)
        canonical_pattern = (
            rf"{re.escape(MD_META_OPEN)}\n(.*?)(?:\n)?{re.escape(MD_META_CLOSE)}"
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
        # 2. If not found, try legacy block (YAML in HTML comment with # prefixes)
        if not meta:
            legacy_pattern = (
                rf"{re.escape(MD_META_OPEN)}\n((?:#.*?\n)+){re.escape(MD_META_CLOSE)}"
            )
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
        # 3. If still not found, try legacy field-per-comment block
        if not meta:
            # Look for a block of consecutive <!-- field: value --> lines between the delimiters
            field_comment_pattern = rf"{re.escape(MD_META_OPEN)}\n((?:<!--.*?-->\n?)+){re.escape(MD_META_CLOSE)}"
            field_comment_match = re.search(field_comment_pattern, content, re.DOTALL)
            if field_comment_match:
                block_fields = field_comment_match.group(1)
                # Parse each line: <!-- field: value -->
                field_pattern = r"<!--\s*([a-zA-Z0-9_]+):\s*(.*?)\s*-->"
                meta_dict = {}
                for line in block_fields.splitlines():
                    m = re.match(field_pattern, line.strip())
                    if m:
                        key, value = m.group(1), m.group(2)
                        meta_dict[key] = value
                if meta_dict:
                    try:
                        meta = NodeMetadataBlock.model_validate(meta_dict)
                        emit_log_event(
                            LogLevelEnum.WARNING,
                            f"Upgraded legacy field-per-comment metadata block to canonical in {path}",
                            node_id=_COMPONENT_NAME,
                        )
                    except Exception as e:
                        emit_log_event(
                            LogLevelEnum.WARNING,
                            f"Malformed field-per-comment metadata block in {path}: {e}",
                            node_id=_COMPONENT_NAME,
                        )
                        meta = None
        # 4. Remove all detected blocks using canonical delimiters
        all_block_pattern = (
            rf"{re.escape(MD_META_OPEN)}[\s\S]+?{re.escape(MD_META_CLOSE)}\n*"
        )
        body = re.sub(all_block_pattern, "", content, flags=re.MULTILINE)
        return meta, body

    def serialize_block(self, meta: object) -> str:
        from omnibase.metadata.metadata_constants import MD_META_CLOSE, MD_META_OPEN
        from omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer import (
            serialize_metadata_block,
        )

        return serialize_metadata_block(
            meta, MD_META_OPEN, MD_META_CLOSE, comment_prefix=""
        )

    def normalize_rest(self, rest: str) -> str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: object) -> OnexResultModel:
        """
        Stamps the file by emitting a protocol-compliant metadata block using the canonical normalizer.
        All block emission must use normalize_metadata_block from metadata_block_normalizer.
        """
        from omnibase.nodes.stamper_node.v1_0_0.helpers.metadata_block_normalizer import (
            normalize_metadata_block,
        )
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.enums import OnexStatus
        from omnibase.model.model_onex_message_result import OnexResultModel
        # Remove all previous metadata blocks using shared mixin
        content_no_block = MetadataBlockMixin.remove_all_metadata_blocks(str(content) or "", "markdown")
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
            entrypoint_type="markdown",
            entrypoint_target=path.stem,
            description=self.default_description or "Stamped by MarkdownHandler",
            meta_type=(
                str(self.default_meta_type.value) if self.default_meta_type else "tool"
            ),
            owner=getattr(self, "default_owner", None) or "OmniNode Team",
            namespace=f"markdown://{path.stem}",
        )
        if prev_uuid is not None:
            create_kwargs["uuid"] = prev_uuid
        if prev_created_at is not None:
            create_kwargs["created_at"] = prev_created_at
        meta = NodeMetadataBlock.create_with_defaults(**create_kwargs)
        # Use canonical normalizer for emission
        stamped = normalize_metadata_block(content_no_block, "markdown", meta=meta)
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

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        return OnexResultModel(status=None, target=str(path), messages=[], metadata={})
