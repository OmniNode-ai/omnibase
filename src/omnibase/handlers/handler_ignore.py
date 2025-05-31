from pathlib import Path
from typing import Any, Optional
from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, MetaTypeEnum
from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN, get_namespace_prefix
from omnibase.model.model_node_metadata import EntrypointType, NodeMetadataBlock, Namespace
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_metadata_block import MetadataBlockMixin
from omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer import serialize_metadata_block
from omnibase.model.model_handler_protocol import (
    HandlerMetadataModel,
    CanHandleResultModel,
    SerializedBlockModel,
)
from omnibase.model.model_extracted_block import ExtractedBlockModel
from omnibase.enums.handler_source import HandlerSourceEnum
_COMPONENT_NAME = Path(__file__).stem


class IgnoreFileHandler(ProtocolFileTypeHandler, MetadataBlockMixin):
    """
    Handler for ignore files (.onexignore, .gitignore) for ONEX stamping.
    Implements the strongly-typed ProtocolFileTypeHandler interface.

    This handler processes ignore files to ensure they have proper metadata blocks
    for provenance and auditability. It supports both .onexignore (canonical YAML format)
    and .gitignore files.
    All extracted metadata blocks must be validated and normalized using the canonical Pydantic model (NodeMetadataBlock) before further processing.
    """

    def __init__(self, default_author: str='OmniNode Team', event_bus: Optional[Any]=None):
        self.default_author = default_author
        self.default_entrypoint_type = EntrypointType.CLI
        self.default_namespace_prefix = f'{get_namespace_prefix()}.ignore'
        self.default_meta_type = MetaTypeEnum.IGNORE_CONFIG
        self.default_description = 'Ignore file stamped for provenance'
        self._event_bus = event_bus

    @property
    def metadata(self) -> HandlerMetadataModel:
        return HandlerMetadataModel(
            handler_name='ignore_file_handler',
            handler_version='1.0.0',
            handler_author='OmniNode Team',
            handler_description='Handles ignore files (.onexignore, .gitignore) for ONEX metadata stamping',
            supported_extensions=[],
            supported_filenames=['.onexignore', '.gitignore'],
            handler_priority=100,
            requires_content_analysis=bool(self.can_handle_predicate),
            source=HandlerSourceEnum.CORE
        )

    @property
    def handler_name(self) -> str:
        return 'ignore_file_handler'

    @property
    def handler_version(self) -> str:
        return '1.0.0'

    @property
    def handler_author(self) -> str:
        return 'OmniNode Team'

    @property
    def handler_description(self) -> str:
        return 'Handles ignore files (.onexignore, .gitignore) for ONEX metadata stamping'

    @property
    def supported_extensions(self) -> list[str]:
        return []

    @property
    def supported_filenames(self) -> list[str]:
        return ['.onexignore', '.gitignore']

    @property
    def handler_priority(self) -> int:
        return 100

    @property
    def requires_content_analysis(self) -> bool:
        return False

    def can_handle(self, path: Path, content: str) -> CanHandleResultModel:
        return CanHandleResultModel(can_handle=path.name in {'.onexignore', '.gitignore'})

    def extract_block(self, path: Path, content: str) -> ExtractedBlockModel:
        import re
        import yaml
        from omnibase.metadata.metadata_constants import YAML_META_OPEN, YAML_META_CLOSE
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.core.core_structured_logging import emit_log_event
        from omnibase.enums import LogLevelEnum
        emit_log_event(LogLevelEnum.DEBUG,
            f'[EXTRACT] Starting extraction for {path}', node_id='ignore_handler', event_bus=self._event_bus)
        block_pattern = (
            f'(?s){re.escape(YAML_META_OPEN)}(.*?){re.escape(YAML_META_CLOSE)}'
        )
        match = re.search(block_pattern, content)
        prev_meta = None
        if match:
            block_content = match.group(1).strip('\n ')
            yaml_lines = []
            for line in block_content.split('\n'):
                if line.startswith('# '):
                    yaml_lines.append(line[2:])
                elif line.startswith('#'):
                    yaml_lines.append(line[1:])
                else:
                    yaml_lines.append(line)
            block_yaml = '\n'.join(yaml_lines).strip()
            if block_yaml:
                try:
                    data = yaml.safe_load(block_yaml)
                    if isinstance(data, dict):
                        prev_meta = NodeMetadataBlock(**data)
                    elif isinstance(data, NodeMetadataBlock):
                        prev_meta = data
                except Exception as e:
                    emit_log_event(LogLevelEnum.DEBUG,
                        f'[EXTRACT] Failed to parse block as YAML: {e}',
                        node_id='ignore_handler', event_bus=self._event_bus)
        rest = re.sub(block_pattern + '\\n?', '', content, count=1)
        emit_log_event(LogLevelEnum.DEBUG,
            f'[EXTRACT] Extraction complete, prev_meta: {prev_meta is not None}',
            node_id='ignore_handler', event_bus=self._event_bus)
        return ExtractedBlockModel(metadata=prev_meta, body=rest)

    def serialize_block(self, meta: NodeMetadataBlock) -> SerializedBlockModel:
        serialized = serialize_metadata_block(meta, YAML_META_OPEN, YAML_META_CLOSE, comment_prefix='# ')
        return SerializedBlockModel(serialized=serialized)

    def normalize_rest(self, rest: str) ->str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: Any) ->OnexResultModel:
        """
        Use the centralized idempotency logic from MetadataBlockMixin for stamping.
        All protocol details are sourced from metadata_constants.
        """
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        default_metadata = NodeMetadataBlock.create_with_defaults(name=path
            .name, author=self.default_author, entrypoint_type=str(self.
            default_entrypoint_type.value), entrypoint_target=path.stem if 
            path.suffix == '.py' else path.name, description=self.
            default_description, meta_type=str(self.default_meta_type.value
            ), file_path=path)
        context_defaults = default_metadata.model_dump()
        context_defaults.pop('namespace', None)
        result_tuple: tuple[str, OnexResultModel
            ] = self.stamp_with_idempotency(path=path, content=content,
            author=self.default_author, entrypoint_type=str(self.
            default_entrypoint_type.value), meta_type=str(self.
            default_meta_type.value), description=self.default_description,
            extract_block_fn=self.extract_block, serialize_block_fn=lambda meta: self.serialize_block(meta.metadata if hasattr(meta, 'metadata') else meta), model_cls=NodeMetadataBlock, context_defaults=
            context_defaults)
        _, result = result_tuple
        return result

    def pre_validate(self, path: Path, content: str, **kwargs: Any) ->Optional[
        OnexResultModel]:
        return None

    def post_validate(self, path: Path, content: str, **kwargs: Any
        ) ->Optional[OnexResultModel]:
        return None

    def validate(self, path: Path, content: str, **kwargs: Any
        ) ->OnexResultModel:
        return OnexResultModel(status=None, target=str(path), messages=[],
            metadata={})
