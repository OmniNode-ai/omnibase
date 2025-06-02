import re
from pathlib import Path
from typing import Any, Optional

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevel
from omnibase.enums.handler_source import HandlerSourceEnum
from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
from omnibase.model.model_extracted_block import ExtractedBlockModel
from omnibase.model.model_handler_protocol import (
    CanHandleResultModel,
    HandlerMetadataModel,
    SerializedBlockModel,
)
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataBlock,
    ToolCollection,
)
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_block_placement import (
    BlockPlacementMixin,
)
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_metadata_block import (
    MetadataBlockMixin,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.metadata_block_normalizer import (
    DELIMITERS,
    normalize_metadata_block,
)

open_delim = PY_META_OPEN
close_delim = PY_META_CLOSE
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
        event_bus: Optional[Any] = None,
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
        self._event_bus = event_bus

    @property
    def handler_name(self) -> str:
        return self.metadata.handler_name

    @property
    def handler_version(self) -> str:
        return self.metadata.handler_version

    @property
    def handler_author(self) -> str:
        return self.metadata.handler_author

    @property
    def handler_description(self) -> str:
        return self.metadata.handler_description

    @property
    def supported_extensions(self) -> list[str]:
        return self.metadata.supported_extensions

    @property
    def supported_filenames(self) -> list[str]:
        return self.metadata.supported_filenames

    @property
    def handler_priority(self) -> int:
        return self.metadata.handler_priority

    @property
    def requires_content_analysis(self) -> bool:
        return self.metadata.requires_content_analysis

    @property
    def metadata(self) -> HandlerMetadataModel:
        return HandlerMetadataModel(
            handler_name="python_handler",
            handler_version="1.0.0",
            handler_author="OmniNode Team",
            handler_description="Handles Python files (.py) for ONEX metadata stamping and validation",
            supported_extensions=[".py", ".pyx"],
            supported_filenames=[],
            handler_priority=50,
            requires_content_analysis=bool(self.can_handle_predicate),
            source=HandlerSourceEnum.CORE,
        )

    def can_handle(self, path: Path, content: str) -> CanHandleResultModel:
        if self.can_handle_predicate:
            result = self.can_handle_predicate(path)
            if isinstance(result, bool):
                return CanHandleResultModel(can_handle=result)
            return CanHandleResultModel(can_handle=False)
        return CanHandleResultModel(can_handle=path.suffix.lower() == ".py")

    def extract_block(self, path: Path, content: str) -> ExtractedBlockModel:
        import re

        import yaml

        from omnibase.core.core_structured_logging import emit_log_event
        from omnibase.enums import LogLevel
        from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
        from omnibase.model.model_node_metadata import NodeMetadataBlock

        canonical_pattern = (
            rf"{re.escape(PY_META_OPEN)}\n(.*?)(?:\n)?{re.escape(PY_META_CLOSE)}"
        )
        canonical_match = re.search(canonical_pattern, content, re.DOTALL)
        meta = None
        block_yaml = None
        if canonical_match:
            block_content = canonical_match.group(1)
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
                    LogLevel.WARNING,
                    f"Malformed canonical metadata block in {path}: {e}",
                    node_id=_COMPONENT_NAME,
                    event_bus=self._event_bus,
                )
                meta = None
        if not meta:
            legacy_pattern = (
                rf"{re.escape(PY_META_OPEN)}\n((?:#.*?\n)+){re.escape(PY_META_CLOSE)}"
            )
            legacy_match = re.search(legacy_pattern, content, re.DOTALL)
            if legacy_match:
                block_legacy = legacy_match.group(1)
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
                        LogLevel.WARNING,
                        f"Malformed legacy metadata block in {path}: {e}",
                        node_id=_COMPONENT_NAME,
                        event_bus=self._event_bus,
                    )
                    meta = None
        all_block_pattern = (
            rf"{re.escape(PY_META_OPEN)}[\s\S]+?{re.escape(PY_META_CLOSE)}\n*"
        )
        body = re.sub(all_block_pattern, "", content, flags=re.MULTILINE)
        return ExtractedBlockModel(metadata=meta, body=body)

    def serialize_block(self, meta: object, event_bus=None) -> str:
        from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
        from omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer import (
            serialize_metadata_block,
        )

        # Accept both ExtractedBlockModel and NodeMetadataBlock
        if hasattr(meta, "metadata") and hasattr(meta, "body"):
            meta_obj = meta.metadata
        else:
            meta_obj = meta
        result = serialize_metadata_block(
            meta_obj,
            PY_META_OPEN,
            PY_META_CLOSE,
            comment_prefix="# ",
            event_bus=event_bus,
        )
        return result

    def normalize_rest(self, rest: str) -> str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: object) -> OnexResultModel:
        """
        Stamps the file by emitting a protocol-compliant metadata block using the canonical normalizer.
        All block emission must use normalize_metadata_block from metadata_block_normalizer.
        """
        from omnibase.enums import OnexStatus
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.model.model_onex_message_result import OnexResultModel

        content_no_block = MetadataBlockMixin.remove_all_metadata_blocks(
            str(content) or "", "python"
        )
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
        if "tools" in kwargs and kwargs["tools"] is not None:
            create_kwargs["tools"] = kwargs["tools"]
        meta = NodeMetadataBlock.create_with_defaults(**create_kwargs)
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
