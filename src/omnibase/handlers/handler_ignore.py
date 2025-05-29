# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.567844'
# description: Stamped by PythonHandler
# entrypoint: python://handler_ignore
# hash: 609c7c755cc6700164fe30b6066a774ab0313288aa73ef00ae9d41813aaa2f26
# last_modified_at: '2025-05-29T14:02:16.013466+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: handler_ignore.py
# namespace: python://omnibase.handlers.handler_ignore
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 3fbce0b6-a151-4d5e-b849-72e748536eee
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any, Optional

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, MetaTypeEnum
from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN, get_namespace_prefix
from omnibase.model.model_node_metadata import EntrypointType, NodeMetadataBlock, Namespace
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_metadata_block import (
    MetadataBlockMixin,
)
from omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer import (
    serialize_metadata_block,
)

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class IgnoreFileHandler(ProtocolFileTypeHandler, MetadataBlockMixin):
    """
    Handler for ignore files (.onexignore, .gitignore) for ONEX stamping.

    This handler processes ignore files to ensure they have proper metadata blocks
    for provenance and auditability. It supports both .onexignore (canonical YAML format)
    and .gitignore files.
    All extracted metadata blocks must be validated and normalized using the canonical Pydantic model (NodeMetadataBlock) before further processing.
    """

    def __init__(self, default_author: str = "OmniNode Team"):
        self.default_author = default_author
        self.default_entrypoint_type = EntrypointType.CLI
        self.default_namespace_prefix = f"{get_namespace_prefix()}.ignore"
        self.default_meta_type = MetaTypeEnum.IGNORE_CONFIG
        self.default_description = "Ignore file stamped for provenance"

    # Handler metadata properties (required by ProtocolFileTypeHandler)
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "ignore_file_handler"

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
            "Handles ignore files (.onexignore, .gitignore) for ONEX metadata stamping"
        )

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        return []  # Ignore handler works with specific filenames, not extensions

    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        return [".onexignore", ".gitignore"]

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 100  # Core handler priority (highest)

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content."""
        return False  # Ignore handler uses filename-based detection

    def can_handle(self, path: Path, content: str) -> bool:
        """Check if this handler can process the given file."""
        return path.name in {".onexignore", ".gitignore"}

    def extract_block(self, path: Path, content: str) -> tuple[Optional[Any], str]:
        import re
        import yaml
        from omnibase.metadata.metadata_constants import YAML_META_OPEN, YAML_META_CLOSE
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.core.core_structured_logging import emit_log_event
        from omnibase.enums import LogLevelEnum

        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[EXTRACT] Starting extraction for {path}",
            node_id="ignore_handler",
        )
        # Find the block between the delimiters
        block_pattern = rf"(?s){re.escape(YAML_META_OPEN)}(.*?){re.escape(YAML_META_CLOSE)}"
        match = re.search(block_pattern, content)
        if not match:
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"[EXTRACT] No metadata block found in {path}",
                node_id="ignore_handler",
            )
            return None, content
        block_content = match.group(1).strip("\n ")
        # Remove '# ' prefix from each line to get clean YAML
        yaml_lines = []
        for line in block_content.split("\n"):
            if line.startswith("# "):
                yaml_lines.append(line[2:])  # Remove '# ' prefix
            elif line.startswith("#"):
                yaml_lines.append(line[1:])  # Remove '#' prefix
            else:
                yaml_lines.append(line)  # Keep line as-is
        block_yaml = "\n".join(yaml_lines).strip()
        prev_meta = None
        if block_yaml:
            try:
                data = yaml.safe_load(block_yaml)
                if isinstance(data, dict):
                    prev_meta = NodeMetadataBlock(**data)
                elif isinstance(data, NodeMetadataBlock):
                    prev_meta = data
                else:
                    prev_meta = None
            except Exception as e:
                emit_log_event(
                    LogLevelEnum.DEBUG,
                    f"[EXTRACT] Failed to parse block as YAML: {e}",
                    node_id="ignore_handler",
                )
                prev_meta = None
        # Remove the block from the content
        rest = re.sub(block_pattern + r"\n?", "", content, count=1)
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[EXTRACT] Extraction complete, prev_meta: {prev_meta is not None}",
            node_id="ignore_handler",
        )
        return prev_meta, rest

    def serialize_block(self, meta: object) -> str:
        """
        Serialize a complete NodeMetadataBlock model as a YAML block with comment delimiters.
        Expects a complete, validated NodeMetadataBlock model instance.
        All Enums are converted to strings. The block is round-trip parseable.
        """
        return serialize_metadata_block(
            meta, YAML_META_OPEN, YAML_META_CLOSE, comment_prefix="# "
        )

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
            entrypoint_type=str(self.default_entrypoint_type.value),
            entrypoint_target=(path.stem if path.suffix == ".py" else path.name),
            description=self.default_description,
            meta_type=str(self.default_meta_type.value),
            file_path=path,
        )

        # Convert model to dictionary for context_defaults
        context_defaults = default_metadata.model_dump()
        # Remove namespace since it's now generated automatically from file path
        context_defaults.pop("namespace", None)

        result_tuple: tuple[str, OnexResultModel] = self.stamp_with_idempotency(
            path=path,
            content=content,
            author=self.default_author,
            entrypoint_type=str(self.default_entrypoint_type.value),
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
