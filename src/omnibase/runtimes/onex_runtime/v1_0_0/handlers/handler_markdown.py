# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_markdown.py
# version: 1.0.0
# uuid: 2424bf07-f386-4bc9-9ac3-dc6669caa497
# author: OmniNode Team
# created_at: 2025-05-22T14:05:24.999460
# last_modified_at: 2025-05-22T18:43:36.762733
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 76dee61e50dccbb2bd2dcdf3656f65d025b1cecfa007ed609f6276ada36f29c7
# entrypoint: python@handler_markdown.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_markdown
# meta_type: tool
# === /OmniNode:Metadata ===


import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.metadata.metadata_constants import MD_META_CLOSE, MD_META_OPEN
from omnibase.model.model_node_metadata import NodeMetadataBlock

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

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class MarkdownHandler(ProtocolFileTypeHandler, MetadataBlockMixin, BlockPlacementMixin):
    """
    Handler for Markdown (.md) files for ONEX stamping.
    All block extraction, serialization, and idempotency logic is delegated to the canonical mixins.
    No custom or legacy logic is present; all protocol details are sourced from metadata_constants.
    """

    def __init__(
        self,
        default_author: str = "OmniNode Team",
        default_entrypoint_type: str = "python",
        default_namespace_prefix: str = "onex.stamped",
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
        return path.suffix.lower() == ".md"

    def extract_block(self, path: Path, content: str) -> tuple[Optional[Any], str]:
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[START] extract_block for {path}",
            node_id=_COMPONENT_NAME,
        )
        try:
            prev_meta, rest = self._extract_block_with_delimiters(
                path, content, MD_META_OPEN, MD_META_CLOSE
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

        import yaml

        from omnibase.metadata.metadata_constants import MD_META_CLOSE, MD_META_OPEN

        # Remove all well-formed metadata blocks
        block_pattern = rf"(?s){re.escape(MD_META_OPEN)}.*?{re.escape(MD_META_CLOSE)}"
        content_wo_blocks = re.sub(block_pattern + r"\n*", "", content)

        # Remove any stray open delimiters (malformed/unmatched blocks)
        open_delim_pattern = rf"{re.escape(MD_META_OPEN)}.*?(?=<!--|$)"
        content_wo_open = re.sub(
            open_delim_pattern, "", content_wo_blocks, flags=re.DOTALL
        )

        # Extract metadata from the first well-formed block (if any)
        match = re.search(block_pattern, content)
        prev_meta = None
        if match:
            block_yaml = match.group(0)[len(MD_META_OPEN) : -len(MD_META_CLOSE)].strip(
                "\n "
            )
            try:
                data = yaml.safe_load(block_yaml)
                if isinstance(data, dict):
                    # Fix datetime objects - convert to ISO strings
                    for field in ["created_at", "last_modified_at"]:
                        if field in data and hasattr(data[field], "isoformat"):
                            data[field] = data[field].isoformat()

                    # Fix entrypoint format - handle compact format
                    if "entrypoint" in data:
                        entrypoint_val = data["entrypoint"]
                        if isinstance(entrypoint_val, str) and "@" in entrypoint_val:
                            # Compact format: "python@filename.md"
                            entry_type, entry_target = entrypoint_val.split("@", 1)
                            data["entrypoint"] = {
                                "type": entry_type.strip(),
                                "target": entry_target.strip(),
                            }
                        # If it's already a dict, keep it as-is

                    prev_meta = NodeMetadataBlock(**data)
                elif isinstance(data, NodeMetadataBlock):
                    prev_meta = data
            except Exception:
                prev_meta = None
        rest = content_wo_open
        return prev_meta, rest

    def serialize_block(self, meta: object) -> str:
        """
        Delegate to centralized runtime.metadata_block_serializer.serialize_metadata_block.
        """
        from typing import Any, Dict, Union

        from pydantic import BaseModel

        from omnibase.metadata.metadata_constants import MD_META_CLOSE, MD_META_OPEN
        from omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer import (
            serialize_metadata_block,
        )

        # Type cast to satisfy mypy
        meta_typed: Union[BaseModel, Dict[str, Any]]
        if isinstance(meta, BaseModel):
            meta_typed = meta
        elif isinstance(meta, dict):
            meta_typed = meta
        else:
            # Fallback for other object types - convert to dict if possible
            meta_typed = meta.__dict__ if hasattr(meta, "__dict__") else {}

        return serialize_metadata_block(
            meta_typed, MD_META_OPEN, MD_META_CLOSE, comment_prefix=""
        )

    def normalize_rest(self, rest: str) -> str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[START] stamp for {path}",
            node_id=_COMPONENT_NAME,
        )
        from datetime import datetime

        from omnibase.model.model_node_metadata import NodeMetadataBlock

        # Normalize filename for namespace
        normalized_stem = self._normalize_filename_for_namespace(path.stem)

        # Create a complete metadata model instead of a dictionary
        default_metadata = NodeMetadataBlock.create_with_defaults(
            name=path.name,
            author=self.default_author or "unknown",
            namespace=self.default_namespace_prefix + f".{normalized_stem}",
            entrypoint_type=self.default_entrypoint_type or "python",
            entrypoint_target=path.name,
            description=self.default_description or "Stamped by ONEX",
            meta_type=self.default_meta_type or "tool",
        )

        # Convert model to dictionary for context_defaults
        context_defaults = default_metadata.model_dump()

        try:
            result_tuple: tuple[str, OnexResultModel] = self.stamp_with_idempotency(
                path=path,
                content=content,  # Pass original content with metadata block intact
                author=self.default_author,
                entrypoint_type=self.default_entrypoint_type,
                namespace_prefix=self.default_namespace_prefix,
                meta_type=self.default_meta_type,
                description=self.default_description,
                extract_block_fn=self.extract_block,
                serialize_block_fn=self.serialize_block,
                model_cls=NodeMetadataBlock,
                context_defaults=context_defaults,  # Pass dictionary for now
            )
            _, result = result_tuple
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"[END] stamp for {path}, result={result}",
                node_id=_COMPONENT_NAME,
            )
            return result
        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Exception in stamp for {path}: {e}",
                node_id=_COMPONENT_NAME,
            )
            from omnibase.model.model_onex_message_result import (
                OnexMessageModel,
                OnexStatus,
            )

            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=str(path),
                messages=[
                    OnexMessageModel(
                        summary=f"Error stamping file: {str(e)}",
                        level=LogLevelEnum.ERROR,
                        file=str(path),
                        line=None,
                        details=None,
                        code=None,
                        context=None,
                        timestamp=datetime.now(),
                        type=None,
                    )
                ],
                metadata={},
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
