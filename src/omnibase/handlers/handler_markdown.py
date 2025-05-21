# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: handler_markdown.py
# version: 1.0.0
# uuid: 26ac671a-6f97-447f-bb83-43eb3de83a36
# author: OmniNode Team
# created_at: 2025-05-21T12:56:10.596222
# last_modified_at: 2025-05-21T12:56:10.596222
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d43a9d774aed0a35f26872c85c88f1c5f0cc636d44be4b02cc504f655e7f0b21
# entrypoint: {'type': 'python', 'target': 'handler_markdown.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_markdown
# meta_type: tool
# === /OmniNode:Metadata ===
import datetime
import logging
import re
from pathlib import Path
from typing import Any, Optional

from omnibase.handlers.block_placement_mixin import BlockPlacementMixin
from omnibase.handlers.metadata_block_mixin import MetadataBlockMixin
from omnibase.metadata.metadata_constants import MD_META_CLOSE, MD_META_OPEN
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler


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
        logger = logging.getLogger("omnibase.handlers.handler_markdown")
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
        logger = logging.getLogger("omnibase.handlers.handler_markdown")
        logger.debug(f"[START] _extract_block_with_delimiters for {path}")
        import yaml

        try:
            block_match = re.search(
                rf"(?s){re.escape(open_delim)}.*?{re.escape(close_delim)}", content
            )
            if not block_match:
                logger.info(f"No metadata block found in {path}")
                return None, content
            block_str = block_match.group(0)
            block_lines = [
                line.strip()
                for line in block_str.splitlines()
                if line.strip().startswith("<!--")
                and not line.strip().startswith(open_delim)
            ]
            block_lines = [
                line[4:-3].strip() for line in block_lines if line.endswith("-->")
            ]
            block_yaml = "\n".join(block_lines)
            prev_meta = None
            try:
                data = yaml.safe_load(block_yaml)
                if isinstance(data, dict):
                    prev_meta = NodeMetadataBlock(**data)
                elif isinstance(data, NodeMetadataBlock):
                    prev_meta = data
                else:
                    prev_meta = None
            except Exception as e:
                logger.error(f"YAML parsing error in {path}: {e}", exc_info=True)
                prev_meta = None
            rest = re.sub(
                rf"(?s){re.escape(open_delim)}.*?{re.escape(close_delim)}\n?",
                "",
                content,
                count=1,
            )
            logger.debug(
                f"[END] _extract_block_with_delimiters for {path}, prev_meta={prev_meta}"
            )
            return prev_meta, rest
        except Exception as e:
            logger.error(
                f"Exception in _extract_block_with_delimiters for {path}: {e}",
                exc_info=True,
            )
            return None, content

    def serialize_block(self, meta: NodeMetadataBlock) -> str:
        """
        Serialize the metadata model as a canonical Markdown comment block, wrapped in delimiters, using protocol constants.
        """
        lines = [f"{MD_META_OPEN}"]
        if isinstance(meta, dict):
            meta = NodeMetadataBlock(**meta)
        meta_dict = meta.model_dump()
        # Convert EntrypointBlock to dict for YAML/Markdown compatibility
        if "entrypoint" in meta_dict:
            entrypoint = meta_dict["entrypoint"]
            if hasattr(entrypoint, "model_dump"):
                entrypoint = entrypoint.model_dump()
            if (
                isinstance(entrypoint, dict)
                and "type" in entrypoint
                and hasattr(entrypoint["type"], "value")
            ):
                entrypoint["type"] = str(entrypoint["type"].value)
            elif (
                isinstance(entrypoint, dict)
                and "type" in entrypoint
                and isinstance(entrypoint["type"], str)
            ):
                entrypoint["type"] = str(entrypoint["type"])
            meta_dict["entrypoint"] = entrypoint
        for k, v in meta_dict.items():
            if v is not None and v != {} and v != [] and v != set():
                lines.append(f"<!-- {k}: {v} -->")
        lines.append(f"{MD_META_CLOSE}")
        return "\n".join(lines)

    def normalize_rest(self, rest: str) -> str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        logger = logging.getLogger("omnibase.handlers.handler_markdown")
        logger.debug(f"[START] stamp for {path}")
        try:
            now = kwargs.get("now") or datetime.datetime.utcnow().isoformat()
            result_tuple: tuple[str, OnexResultModel] = self.stamp_with_idempotency(
                path=path,
                content=content,
                now=now,
                author=self.default_author,
                entrypoint_type=self.default_entrypoint_type,
                namespace_prefix=self.default_namespace_prefix,
                meta_type=self.default_meta_type,
                description=self.default_description,
                extract_block_fn=self.extract_block,
                serialize_block_fn=self.serialize_block,
                model_cls=NodeMetadataBlock,
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
                        timestamp=datetime.datetime.now(),
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
