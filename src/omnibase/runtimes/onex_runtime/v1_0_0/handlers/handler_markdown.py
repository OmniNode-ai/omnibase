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
from omnibase.metadata.metadata_constants import MD_META_CLOSE, MD_META_OPEN, get_namespace_prefix
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

    def extract_block(self, path: Path, content: str) -> tuple[Optional[NodeMetadataBlock], Optional[str]]:
        import re
        import yaml
        from omnibase.metadata.metadata_constants import MD_META_OPEN, MD_META_CLOSE
        # Extract YAML block inside HTML comment delimiters
        block_match = re.search(rf"{re.escape(MD_META_OPEN)}\n(.*?)(?:\n)?{re.escape(MD_META_CLOSE)}", content, re.DOTALL)
        if not block_match:
            # Always return a string for the body, even if no block is found
            return None, content if content is not None else ""
        yaml_block = block_match.group(1)
        try:
            meta_dict = yaml.safe_load(yaml_block)
            meta = NodeMetadataBlock.model_validate(meta_dict)
        except Exception:
            meta = None
        # Remove the block from the content
        body = re.sub(rf"{re.escape(MD_META_OPEN)}[\s\S]+?{re.escape(MD_META_CLOSE)}\n*", "", content, flags=re.MULTILINE)
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

    def _remove_all_metadata_blocks(self, content: str) -> str:
        import re
        from omnibase.metadata.metadata_constants import MD_META_OPEN, MD_META_CLOSE
        block_pattern = rf"{re.escape(MD_META_OPEN)}[\s\S]+?{re.escape(MD_META_CLOSE)}\n*"
        return re.sub(block_pattern, "", content, flags=re.MULTILINE)

    def stamp(self, path: Path, content: str, **kwargs: object) -> OnexResultModel:
        import re
        from omnibase.metadata.metadata_constants import MD_META_OPEN, MD_META_CLOSE
        # Remove all previous metadata blocks
        content_no_block = self._remove_all_metadata_blocks(str(content) or "")
        # Extract previous metadata block if present
        prev_meta, _ = self.extract_block(path, content)
        prev_uuid = getattr(prev_meta, "uuid", None) if prev_meta else None
        prev_created_at = getattr(prev_meta, "created_at", None) if prev_meta else None
        # Prepare metadata
        create_kwargs = dict(
            name=path.name,
            author=self.default_author or "OmniNode Team",
            entrypoint_type="markdown",
            entrypoint_target=path.stem,
            description=self.default_description or "Stamped by MarkdownHandler",
            meta_type=str(self.default_meta_type.value) if self.default_meta_type else "tool",
            owner=getattr(self, "default_owner", None) or "OmniNode Team",
            namespace=f"markdown://{path.stem}",
        )
        if prev_uuid is not None:
            create_kwargs["uuid"] = prev_uuid
        if prev_created_at is not None:
            create_kwargs["created_at"] = prev_created_at
        meta = NodeMetadataBlock.create_with_defaults(**create_kwargs)
        serializer = CanonicalYAMLSerializer()
        yaml_block = serializer.canonicalize_metadata_block(meta, comment_prefix="")
        block = f"{MD_META_OPEN}\n{yaml_block}\n{MD_META_CLOSE}"
        # Normalize spacing: exactly one blank line after the block if content follows
        rest = content_no_block.lstrip("\n")
        if rest:
            stamped = block + "\n\n" + rest
        else:
            stamped = block + "\n"
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[],
            metadata={"content": stamped, "note": "Stamped (idempotent or updated)", "hash": meta.hash},
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
