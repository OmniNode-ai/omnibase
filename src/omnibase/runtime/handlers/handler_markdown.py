# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_markdown.py
# version: 1.0.0
# uuid: '2424bf07-f386-4bc9-9ac3-dc6669caa497'
# author: OmniNode Team
# created_at: '2025-05-22T14:05:24.999460'
# last_modified_at: '2025-05-22T18:43:36.762733'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 76dee61e50dccbb2bd2dcdf3656f65d025b1cecfa007ed609f6276ada36f29c7
# entrypoint:
#   type: python
#   target: handler_markdown.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_markdown
# meta_type: tool
# === /OmniNode:Metadata ===


import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from omnibase.metadata.metadata_constants import MD_META_CLOSE, MD_META_OPEN
from omnibase.model.model_node_metadata import NodeMetadataBlock

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock

from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.runtime.mixins.block_placement_mixin import BlockPlacementMixin
from omnibase.runtime.mixins.metadata_block_mixin import MetadataBlockMixin
from omnibase.runtime.protocol.protocol_file_type_handler import ProtocolFileTypeHandler


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

    def can_handle(self, path: Path, content: str) -> bool:
        return path.suffix.lower() == ".md"

    def extract_block(self, path: Path, content: str) -> tuple[Optional[Any], str]:
        logger = logging.getLogger("omnibase.runtime.handlers.handler_markdown")
        logger.debug(f"[START] extract_block for {path}")
        try:
            result = self._extract_block_with_delimiters(
                path, content, MD_META_OPEN, MD_META_CLOSE
            )
            prev_meta, rest = result
            # Canonicality check
            is_canonical, reasons = self.is_canonical_block(
                prev_meta, NodeMetadataBlock
            )
            if not is_canonical:
                logger.warning(
                    f"Restamping {path} due to non-canonical metadata block: {reasons}"
                )
                prev_meta = None  # Force restamp in idempotency logic
            logger.debug(f"[END] extract_block for {path}, result=({prev_meta}, rest)")
            return prev_meta, rest
        except Exception as e:
            logger.error(f"Exception in extract_block for {path}: {e}", exc_info=True)
            return None, content

    def _extract_block_with_delimiters(
        self, path: Path, content: str, open_delim: str, close_delim: str
    ) -> tuple[Optional[Any], str]:

        import yaml

        from omnibase.metadata.metadata_constants import MD_META_CLOSE, MD_META_OPEN

        # Find the block between the delimiters
        block_pattern = rf"(?s){re.escape(MD_META_OPEN)}(.*?){re.escape(MD_META_CLOSE)}"
        match = re.search(block_pattern, content)
        if not match:
            return None, content
        block_yaml = match.group(1).strip("\n ")
        prev_meta = None
        try:
            data = yaml.safe_load(block_yaml)
            if isinstance(data, dict):
                prev_meta = NodeMetadataBlock(**data)
            elif isinstance(data, NodeMetadataBlock):
                prev_meta = data
        except Exception:
            prev_meta = None
        # Remove the block from the content
        rest = re.sub(block_pattern + r"\n?", "", content, count=1)
        return prev_meta, rest

    def serialize_block(self, meta: object) -> str:
        """
        Serialize a complete NodeMetadataBlock model as a YAML block with Markdown comment delimiters.
        Expects a complete, validated NodeMetadataBlock model instance.
        All Enums are converted to strings. The block is round-trip parseable.
        """
        from enum import Enum

        import yaml

        from omnibase.metadata.metadata_constants import MD_META_CLOSE, MD_META_OPEN
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

        # Expect a complete NodeMetadataBlock model
        if not isinstance(meta, NodeMetadataBlock):
            raise ValueError(
                f"serialize_block expects NodeMetadataBlock, got {type(meta)}"
            )

        meta_dict = enum_to_str(meta.model_dump())

        # Filter out None values and empty collections to avoid clutter
        filtered_dict = {}
        for k, v in meta_dict.items():
            if v is not None and v != [] and v != {}:
                filtered_dict[k] = v

        # Custom YAML representer to force quoting of UUID and other string fields
        class QuotedStringDumper(yaml.SafeDumper):
            pass

        def quoted_string_representer(dumper, data):
            # Force quoting for UUID-like strings and other fields that need it
            if isinstance(data, str) and (
                len(data) == 36
                and data.count("-") == 4
                and all(c.isalnum() or c == "-" for c in data)
            ):
                return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")
            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        QuotedStringDumper.add_representer(str, quoted_string_representer)

        yaml_block = yaml.dump(
            filtered_dict,
            sort_keys=False,
            default_flow_style=False,
            Dumper=QuotedStringDumper,
        ).strip()
        # Ensure delimiters are on their own lines, no extra whitespace
        return f"{MD_META_OPEN}\n{yaml_block}\n{MD_META_CLOSE}\n"

    def normalize_rest(self, rest: str) -> str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        logger = logging.getLogger("omnibase.runtime.handlers.handler_markdown")
        logger.debug(f"[START] stamp for {path}")
        from datetime import datetime

        from omnibase.model.model_node_metadata import NodeMetadataBlock

        # Create a complete metadata model instead of a dictionary
        default_metadata = NodeMetadataBlock.create_with_defaults(
            name=path.name,
            author=self.default_author or "unknown",
            namespace=self.default_namespace_prefix + f".{path.stem}",
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
            logger.debug(f"[END] stamp for {path}, result={result}")
            return result
        except Exception as e:
            logger.error(f"Exception in stamp for {path}: {e}", exc_info=True)
            from omnibase.model.model_enum_log_level import LogLevelEnum
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
