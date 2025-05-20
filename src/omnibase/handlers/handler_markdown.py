import datetime
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
        """
        Extract the metadata block and the rest of the file using canonical mixin logic and protocol constants.
        """
        return self._extract_block_with_delimiters(
            path, content, MD_META_OPEN, MD_META_CLOSE
        )

    def _extract_block_with_delimiters(
        self, path: Path, content: str, open_delim: str, close_delim: str
    ) -> tuple[Optional[Any], str]:

        import yaml

        block_match = re.search(
            rf"(?s){re.escape(open_delim)}.*?{re.escape(close_delim)}", content
        )
        if not block_match:
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
        except Exception:
            prev_meta = None
        rest = re.sub(
            rf"(?s){re.escape(open_delim)}.*?{re.escape(close_delim)}\n?",
            "",
            content,
            count=1,
        )
        return prev_meta, rest

    def serialize_block(self, meta: NodeMetadataBlock) -> str:
        """
        Serialize the metadata model as a canonical Markdown comment block, wrapped in delimiters, using protocol constants.
        """
        lines = [f"{MD_META_OPEN}"]
        if isinstance(meta, dict):
            print(
                "[DEBUG] Converting meta from dict to NodeMetadataBlock before model_dump (per typing_and_protocols rule)"
            )
            meta = NodeMetadataBlock(**meta)
        for k, v in meta.model_dump().items():
            if v is not None and v != {} and v != [] and v != set():
                lines.append(f"<!-- {k}: {v} -->")
        lines.append(f"{MD_META_CLOSE}")
        return "\n".join(lines)

    def normalize_rest(self, rest: str) -> str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Use the centralized idempotency logic from MetadataBlockMixin for stamping.
        All protocol details are sourced from metadata_constants.
        Protocol: Must return only OnexResultModel, never the tuple from stamp_with_idempotency.
        """
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
        return result

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
