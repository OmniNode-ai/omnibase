# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: handler_ignore.py
# version: 1.0.0
# uuid: 4b351bbf-50f7-4ff7-877e-8953067e14a4
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.163871
# last_modified_at: 2025-05-21T16:42:46.119330
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 6150d2b37613395577be6339ef87bdf5eb64113706c74c9bb17978e761196329
# entrypoint: {'type': 'python', 'target': 'handler_ignore.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_ignore
# meta_type: tool
# === /OmniNode:Metadata ===

import logging
from pathlib import Path
from typing import Any, Optional

from omnibase.handlers.metadata_block_mixin import MetadataBlockMixin
from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN
from omnibase.model.model_enum_metadata import MetaTypeEnum
from omnibase.model.model_node_metadata import EntrypointType, NodeMetadataBlock
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler

logger = logging.getLogger(__name__)


class IgnoreFileHandler(ProtocolFileTypeHandler, MetadataBlockMixin):
    """
    Handler for ignore files (.onexignore, .stamperignore, .gitignore) for ONEX stamping.
    Uses the canonical model and outputs a valid YAML metadata block.
    """

    def __init__(self, default_author: str = "OmniNode Team"):
        self.default_author = default_author
        self.default_entrypoint_type = EntrypointType.CLI
        self.default_namespace_prefix = "onex.ignore"
        self.default_meta_type = MetaTypeEnum.IGNORE_CONFIG
        self.default_description = "Ignore file stamped for provenance"

    def can_handle(self, path: Path, content: str) -> bool:
        return path.suffix in {".onexignore", ".stamperignore", ".gitignore"}

    def extract_block(self, path: Path, content: str) -> tuple[Optional[Any], str]:
        import yaml

        block_match = None
        try:
            import re

            block_match = re.search(
                rf"(?s){YAML_META_OPEN}.*?{YAML_META_CLOSE}", content
            )
            if not block_match:
                return None, content
            block_str = block_match.group(0)
            block_lines = [
                line.strip()
                for line in block_str.splitlines()
                if line.strip().startswith("#")
                and not line.strip().startswith(YAML_META_OPEN)
            ]
            block_lines = [
                line[1:].strip() for line in block_lines if line.startswith("#")
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
                rf"(?s){YAML_META_OPEN}.*?{YAML_META_CLOSE}\n?",
                "",
                content,
                count=1,
            )
            return prev_meta, rest
        except Exception as e:
            logger.error(f"Exception in extract_block for {path}: {e}", exc_info=True)
            return None, content

    def serialize_block(self, meta: NodeMetadataBlock) -> str:
        lines = [f"{YAML_META_OPEN}"]
        if isinstance(meta, dict):
            meta = NodeMetadataBlock(**meta)
        meta_dict = meta.model_dump()
        # Convert EntrypointBlock to dict for YAML compatibility
        if "entrypoint" in meta_dict:
            entrypoint = meta_dict["entrypoint"]
            if hasattr(entrypoint, "model_dump"):
                entrypoint = entrypoint.model_dump()
            # Convert enum to value
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
        lines.append(f"{YAML_META_CLOSE}")
        return "\n".join(lines)

    def normalize_rest(self, rest: str) -> str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
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
