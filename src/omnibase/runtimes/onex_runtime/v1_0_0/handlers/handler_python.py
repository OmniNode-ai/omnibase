# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T08:19:40.026642'
# description: Stamped by PythonHandler
# entrypoint: python://handler_python
# hash: c12e7807bd8fda3b2c1897ba7a815f128df103d4f9363d75675cfb8f23e660d1
# last_modified_at: '2025-05-29T14:14:00.470548+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: handler_python.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_python
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 7afa3e03-4735-44ea-b656-17f21e9cb87d
# version: 1.0.0
# === /OmniNode:Metadata ===


import re
from pathlib import Path
from typing import Any, Optional

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
from omnibase.model.model_node_metadata import (
    EntrypointType,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataBlock,
    ToolCollection,
    EntrypointBlock,
)
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_block_placement import (
    BlockPlacementMixin,
)
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_metadata_block import (
    MetadataBlockMixin,
)

open_delim = PY_META_OPEN
close_delim = PY_META_CLOSE

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class PythonHandler(ProtocolFileTypeHandler, MetadataBlockMixin, BlockPlacementMixin):
    """
    Handler for Python files (.py) for ONEX stamping.
    All block extraction, serialization, and idempotency logic is delegated to the canonical mixins.
    All block emission MUST use the canonical normalize_metadata_block from metadata_block_normalizer (protocol requirement).
    No custom or legacy logic is present; all protocol details are sourced from metadata_constants.
    All extracted metadata blocks must be validated and normalized using the canonical Pydantic model (NodeMetadataBlock) before further processing.
    """

    def __init__(
        self,
        default_author: str = "OmniNode Team",
        default_owner: str = "OmniNode Team",
        default_copyright: str = "OmniNode Team",
        default_description: str = "Stamped by PythonHandler",
        default_state_contract: str = "state_contract://default",
        default_lifecycle: Lifecycle = Lifecycle.ACTIVE,
        default_meta_type: MetaTypeEnum = MetaTypeEnum.TOOL,
        default_entrypoint_type: EntrypointType = EntrypointType.PYTHON,
        default_runtime_language_hint: str = "python>=3.11",
        default_namespace_prefix: str = "omnibase.stamped",
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

    # Handler metadata properties (required by ProtocolFileTypeHandler)
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "python_handler"

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
        return "Handles Python files (.py) for ONEX metadata stamping and validation"

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        return [".py", ".pyx"]

    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        return []  # Python handler works with extensions, not specific filenames

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 50  # Runtime handler priority

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content."""
        return bool(self.can_handle_predicate)  # Only if custom predicate is provided

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
        """
        Extracts the ONEX metadata block from Python content.
        - Uses canonical delimiter constants (PY_META_OPEN, PY_META_CLOSE) for all block operations.
        - Attempts to extract both canonical (YAML in # comment block) and legacy (YAML in # block with old field names, or malformed) blocks.
        - Prefers canonical if both are found; upgrades legacy to canonical.
        - Removes all detected blocks before emitting the new one.
        - Logs warnings if multiple or malformed blocks are found.
        """
        import re
        import yaml
        from omnibase.metadata.metadata_constants import PY_META_OPEN, PY_META_CLOSE
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.core.core_structured_logging import emit_log_event
        from omnibase.enums import LogLevelEnum

        # 1. Try canonical block (YAML in # comment block)
        canonical_pattern = (
            rf"{re.escape(PY_META_OPEN)}\n(.*?)(?:\n)?{re.escape(PY_META_CLOSE)}"
        )
        canonical_match = re.search(canonical_pattern, content, re.DOTALL)
        meta = None
        block_yaml = None
        if canonical_match:
            block_content = canonical_match.group(1)
            # Remove '# ' or '#' prefix from each line
            yaml_lines = []
            for line in block_content.splitlines():
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
                    f"Malformed canonical metadata block in {path}: {e}",
                    node_id=_COMPONENT_NAME,
                )
                meta = None
        # 2. If not found, try legacy block (YAML in # block with old field names)
        if not meta:
            legacy_pattern = (
                rf"{re.escape(PY_META_OPEN)}\n((?:#.*?\n)+){re.escape(PY_META_CLOSE)}"
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
        # 3. Remove all detected blocks using canonical delimiters
        all_block_pattern = (
            rf"{re.escape(PY_META_OPEN)}[\s\S]+?{re.escape(PY_META_CLOSE)}\n*"
        )
        body = re.sub(all_block_pattern, "", content, flags=re.MULTILINE)
        return meta, body

    def serialize_block(self, meta: object) -> str:
        emit_log_event(
            "DEBUG",
            f"[SERIALIZE_BLOCK] Enter serialize_block for meta type {type(meta)}",
            node_id=_COMPONENT_NAME,
        )
        from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
        from omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer import (
            serialize_metadata_block,
        )

        result = serialize_metadata_block(
            meta, PY_META_OPEN, PY_META_CLOSE, comment_prefix="# "
        )
        emit_log_event(
            "DEBUG",
            f"[SERIALIZE_BLOCK] Exit serialize_block for meta type {type(meta)}",
            node_id=_COMPONENT_NAME,
        )
        return result

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
        content_no_block = MetadataBlockMixin.remove_all_metadata_blocks(str(content) or "", "python")
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
            author=getattr(self, "default_author", None) or "OmniNode Team",
            entrypoint_type="python",
            entrypoint_target=path.stem,
            description=getattr(self, "default_description", None)
            or "Stamped by PythonHandler",
            meta_type=(
                str(getattr(self, "default_meta_type", None).value)
                if getattr(self, "default_meta_type", None)
                else "tool"
            ),
            owner=getattr(self, "default_owner", None) or "OmniNode Team",
            namespace=f"python://{path.stem}",
        )
        if prev_uuid is not None:
            create_kwargs["uuid"] = prev_uuid
        if prev_created_at is not None:
            create_kwargs["created_at"] = prev_created_at
        # PATCH: Accept tools from kwargs if present
        if "tools" in kwargs and kwargs["tools"] is not None:
            create_kwargs["tools"] = kwargs["tools"]
        meta = NodeMetadataBlock.create_with_defaults(**create_kwargs)
        # Use canonical normalizer for emission
        stamped = normalize_metadata_block(content_no_block, "python", meta=meta)
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
