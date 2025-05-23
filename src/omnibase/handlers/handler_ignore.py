# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_ignore.py
# version: 1.0.0
# uuid: b04c529c-5d69-491f-892c-46cbb49fdd96
# author: OmniNode Team
# created_at: 2025-05-22T14:05:24.967653
# last_modified_at: 2025-05-22T20:22:47.708377
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: fe37998fea2c08cac213302aa20034fa9776c80c9ae97e4f62ee1b6a32d35f58
# entrypoint: python@handler_ignore.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_ignore
# meta_type: tool
# === /OmniNode:Metadata ===


import logging
from pathlib import Path
from typing import Any, Optional

from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN
from omnibase.model.model_enum_metadata import MetaTypeEnum
from omnibase.model.model_node_metadata import EntrypointType, NodeMetadataBlock
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtime.mixins.mixin_metadata_block import MetadataBlockMixin

logger = logging.getLogger(__name__)


class IgnoreFileHandler(ProtocolFileTypeHandler, MetadataBlockMixin):
    """
    Handler for ignore files (.onexignore, .gitignore) for ONEX stamping.

    This handler processes ignore files to ensure they have proper metadata blocks
    for provenance and auditability. It supports both .onexignore (canonical YAML format)
    and .gitignore files.
    """

    def __init__(self, default_author: str = "OmniNode Team"):
        self.default_author = default_author
        self.default_entrypoint_type = EntrypointType.CLI
        self.default_namespace_prefix = "onex.ignore"
        self.default_meta_type = MetaTypeEnum.IGNORE_CONFIG
        self.default_description = "Ignore file stamped for provenance"

    def can_handle(self, path: Path, content: str) -> bool:
        """Check if this handler can process the given file."""
        return path.suffix in {".onexignore", ".gitignore"}

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

    def serialize_block(self, meta: object) -> str:
        """
        Serialize a complete NodeMetadataBlock model as a YAML block with comment delimiters.
        Expects a complete, validated NodeMetadataBlock model instance.
        All Enums are converted to strings. The block is round-trip parseable.
        """
        from enum import Enum

        from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN
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
        lines = [f"{YAML_META_OPEN}"]
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
        """
        Use the centralized idempotency logic from MetadataBlockMixin for stamping.
        All protocol details are sourced from metadata_constants.
        """
        from omnibase.model.model_node_metadata import NodeMetadataBlock

        # Create a complete metadata model instead of a dictionary
        default_metadata = NodeMetadataBlock.create_with_defaults(
            name=path.name,
            author=self.default_author,
            namespace=self.default_namespace_prefix + f".{path.stem}",
            entrypoint_type=str(self.default_entrypoint_type.value),
            entrypoint_target=path.name,
            description=self.default_description,
            meta_type=str(self.default_meta_type.value),
        )

        # Convert model to dictionary for context_defaults
        context_defaults = default_metadata.model_dump()

        result_tuple: tuple[str, OnexResultModel] = self.stamp_with_idempotency(
            path=path,
            content=content,
            author=self.default_author,
            entrypoint_type=str(self.default_entrypoint_type.value),
            namespace_prefix=self.default_namespace_prefix,
            meta_type=str(self.default_meta_type.value),
            description=self.default_description,
            extract_block_fn=self.extract_block,
            serialize_block_fn=self.serialize_block,
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

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        return OnexResultModel(status=None, target=str(path), messages=[], metadata={})
