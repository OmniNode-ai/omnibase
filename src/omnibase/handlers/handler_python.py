# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: handler_python.py
# version: 1.0.0
# uuid: 937a05d5-6120-4e00-a9d7-6d68955336b0
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.164088
# last_modified_at: 2025-05-21T16:42:46.065605
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5cd7679bc2a6a7ee079a19f8be81af43da5b0e2b6f23803609f3c219bfc94e0d
# entrypoint: {'type': 'python', 'target': 'handler_python.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_python
# meta_type: tool
# === /OmniNode:Metadata ===

import logging
import re
from pathlib import Path
from typing import Any, Optional

from omnibase.handlers.block_placement_mixin import BlockPlacementMixin
from omnibase.handlers.metadata_block_mixin import MetadataBlockMixin
from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
from omnibase.model.model_node_metadata import (
    EntrypointType,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler

open_delim = PY_META_OPEN
close_delim = PY_META_CLOSE
logger = logging.getLogger(__name__)


class PythonHandler(ProtocolFileTypeHandler, MetadataBlockMixin, BlockPlacementMixin):
    """
    Handler for Python files (.py) for ONEX stamping.
    All block extraction, serialization, and idempotency logic is delegated to the canonical mixins.
    No custom or legacy logic is present; all protocol details are sourced from metadata_constants.
    """

    def __init__(
        self,
        default_author: str = "OmniNode Team",
        default_owner: str = "OmniNode Team",
        default_copyright: str = "OmniNode Team",
        default_description: str = "Stamped by PythonHandler",
        default_state_contract: str = "state_contract://default",
        default_lifecycle: Lifecycle = Lifecycle.ACTIVE,
        default_meta_type: MetaType = MetaType.TOOL,
        default_entrypoint_type: EntrypointType = EntrypointType.PYTHON,
        default_runtime_language_hint: str = "python>=3.11",
        default_namespace_prefix: str = "onex.stamped",
        can_handle_predicate: Optional[Any] = None,
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

    def can_handle(self, path: Path, content: str) -> bool:
        """
        Determine if this handler can process the given file.
        Uses an injected predicate or registry-driven check if provided.
        """
        if self.can_handle_predicate:
            result = self.can_handle_predicate(path)
            if isinstance(result, bool):
                return result
            return False
        return path.suffix.lower() == ".py"

    def extract_block(self, path: Path, content: str) -> tuple[Optional[Any], str]:
        logger = logging.getLogger("omnibase.handlers.handler_python")
        logger.debug(f"[START] extract_block for {path}")
        try:
            prev_meta, rest = self._extract_block_with_delimiters(
                path, content, PY_META_OPEN, PY_META_CLOSE
            )
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

        block_match = re.search(
            rf"(?s){re.escape(open_delim)}.*?{re.escape(close_delim)}", content
        )
        if not block_match:
            return None, content
        block_str = block_match.group(0)
        block_lines = [
            line.strip()
            for line in block_str.splitlines()
            if line.strip().startswith("#") and not line.strip().startswith(open_delim)
        ]
        block_lines = [
            line[1:].strip() for line in block_lines if line.startswith("#")
        ]  # Remove leading '#'
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
        Serialize the metadata model as a canonical Python comment block, wrapped in delimiters, using protocol constants.
        """
        lines = [f"{PY_META_OPEN}"]
        if isinstance(meta, dict):
            meta = NodeMetadataBlock(**meta)
        meta_dict = meta.model_dump()
        # Convert EntrypointBlock to dict for YAML compatibility
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
                lines.append(f"# {k}: {v}")
        lines.append(f"{PY_META_CLOSE}")
        return "\n".join(lines)

    def normalize_rest(self, rest: str) -> str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Use the centralized idempotency logic from MetadataBlockMixin for stamping.
        All protocol details are sourced from metadata_constants.
        Protocol: Must return only OnexResultModel, never the tuple from stamp_with_idempotency.
        """
        # Do not generate or pass 'now' here; let stamp_with_idempotency handle it only if needed
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
