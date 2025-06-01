import re
from pathlib import Path
from typing import Any, Optional
from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevel, OnexStatus
from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN, get_namespace_prefix
from omnibase.model.model_block_placement_policy import BlockPlacementPolicy
from omnibase.model.model_node_metadata import EntrypointType, Lifecycle, MetaTypeEnum, NodeMetadataBlock, Namespace, EntrypointBlock
from omnibase.model.model_onex_message import OnexMessageModel
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_block_placement import BlockPlacementMixin
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_metadata_block import MetadataBlockMixin
from omnibase.schemas.loader import SchemaLoader
from omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer import serialize_metadata_block
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.runtimes.onex_runtime.v1_0_0.utils.metadata_block_normalizer import normalize_metadata_block, DELIMITERS
from omnibase.model.model_handler_protocol import HandlerMetadataModel, CanHandleResultModel
from omnibase.model.model_extracted_block import ExtractedBlockModel
from omnibase.enums.handler_source import HandlerSourceEnum
_COMPONENT_NAME = Path(__file__).stem


class MetadataYAMLHandler(ProtocolFileTypeHandler, MetadataBlockMixin,
    BlockPlacementMixin):
    """
    Handler for YAML files (.yaml, .yml) for ONEX stamping.
    All block extraction, serialization, and idempotency logic is delegated to the canonical mixins.
    All block emission MUST use the canonical normalize_metadata_block from metadata_block_normalizer (protocol requirement).
    No custom or legacy logic is present; all protocol details are sourced from metadata_constants.
    All extracted metadata blocks must be validated and normalized using the canonical Pydantic model (NodeMetadataBlock) before further processing.
    """
    block_placement_policy = BlockPlacementPolicy(allow_shebang=True,
        max_blank_lines_before_block=1, allow_license_header=True,
        license_header_pattern=None, normalize_blank_lines=True,
        enforce_block_at_top=True, placement_policy_version='1.0.0')

    def __init__(self, default_author: str='OmniNode Team', default_owner:
        str='OmniNode Team', default_copyright: str='OmniNode Team',
        default_description: str='Stamped by MetadataYAMLHandler',
        default_state_contract: str='state_contract://default',
        default_lifecycle: Lifecycle=Lifecycle.ACTIVE, default_meta_type:
        MetaTypeEnum=MetaTypeEnum.TOOL, default_entrypoint_type:
        EntrypointType=EntrypointType.YAML, default_runtime_language_hint:
        str=None, default_namespace_prefix: str=
        f'{get_namespace_prefix()}.stamped', can_handle_predicate: Optional
        [Any]=None, schema_loader: Optional[SchemaLoader]=None, event_bus: Optional[Any]=None):
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
        self.schema_loader = schema_loader
        self._event_bus = event_bus

    @property
    def metadata(self) -> HandlerMetadataModel:
        return HandlerMetadataModel(
            handler_name='yaml_metadata_handler',
            handler_version='1.0.0',
            handler_author='OmniNode Team',
            handler_description='Handles YAML files (.yaml, .yml) for ONEX metadata stamping and validation',
            supported_extensions=['.yaml', '.yml'],
            supported_filenames=[],
            handler_priority=50,
            requires_content_analysis=bool(self.can_handle_predicate),
            source=HandlerSourceEnum.CORE
        )

    @property
    def handler_name(self) -> str:
        return 'yaml_metadata_handler'

    @property
    def handler_version(self) -> str:
        return '1.0.0'

    @property
    def handler_author(self) -> str:
        return 'OmniNode Team'

    @property
    def handler_description(self) -> str:
        return 'Handles YAML files (.yaml, .yml) for ONEX metadata stamping and validation'

    @property
    def supported_extensions(self) -> list[str]:
        return ['.yaml', '.yml']

    @property
    def supported_filenames(self) -> list[str]:
        return []

    @property
    def handler_priority(self) -> int:
        return 50

    @property
    def requires_content_analysis(self) -> bool:
        return False

    def can_handle(self, path: Path, content: str) -> CanHandleResultModel:
        if self.can_handle_predicate:
            import inspect
            sig = inspect.signature(self.can_handle_predicate)
            if len(sig.parameters) == 1:
                result = self.can_handle_predicate(path)
            else:
                result = self.can_handle_predicate(path, content)
            return CanHandleResultModel(can_handle=bool(result))
        return CanHandleResultModel(can_handle=path.suffix.lower() in {'.yaml', '.yml'})

    def extract_block(self, path: Path, content: str) -> ExtractedBlockModel:
        """
        Extracts the ONEX metadata block from YAML content.
        - Uses canonical delimiter constants (YAML_META_OPEN, YAML_META_CLOSE) for all block operations.
        - Attempts to extract both canonical (YAML block with ---/...) and legacy (YAML block with # prefixes, or malformed) blocks.
        - Prefers canonical if both are found; upgrades legacy to canonical.
        - Removes all detected blocks before emitting the new one.
        - Logs warnings if multiple or malformed blocks are found.
        """
        import re
        import yaml
        from omnibase.metadata.metadata_constants import YAML_META_OPEN, YAML_META_CLOSE
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.core.core_structured_logging import emit_log_event
        from omnibase.enums import LogLevel
        canonical_pattern = (
            rf'{re.escape(YAML_META_OPEN)}\n(.*?)(?:\n)?{re.escape(YAML_META_CLOSE)}'
            )
        canonical_match = re.search(canonical_pattern, content, re.DOTALL)
        meta = None
        block_yaml = None
        if canonical_match:
            block_yaml = canonical_match.group(1)
            try:
                meta_dict = yaml.safe_load(block_yaml)
                meta = NodeMetadataBlock.model_validate(meta_dict)
            except Exception as e:
                emit_log_event(LogLevel.WARNING,
                    f'Malformed canonical metadata block in {path}: {e}',
                    node_id=_COMPONENT_NAME, event_bus=self._event_bus)
                meta = None
        if not meta:
            legacy_pattern = (
                rf'{re.escape(YAML_META_OPEN)}\n((?:#.*?\n)+){re.escape(YAML_META_CLOSE)}'
                )
            legacy_match = re.search(legacy_pattern, content, re.DOTALL)
            if legacy_match:
                block_legacy = legacy_match.group(1)
                yaml_lines = []
                for line in block_legacy.splitlines():
                    if line.strip().startswith('# '):
                        yaml_lines.append(line.strip()[2:])
                    elif line.strip().startswith('#'):
                        yaml_lines.append(line.strip()[1:])
                    else:
                        yaml_lines.append(line)
                block_yaml = '\n'.join(yaml_lines)
                try:
                    meta_dict = yaml.safe_load(block_yaml)
                    meta = NodeMetadataBlock.model_validate(meta_dict)
                except Exception as e:
                    emit_log_event(LogLevel.WARNING,
                        f'Malformed legacy metadata block in {path}: {e}',
                        node_id=_COMPONENT_NAME, event_bus=self._event_bus)
                    meta = None
        all_block_pattern = (
            rf'{re.escape(YAML_META_OPEN)}[\s\S]+?{re.escape(YAML_META_CLOSE)}\n*'
            )
        body = re.sub(all_block_pattern, '', content, flags=re.MULTILINE)
        return ExtractedBlockModel(metadata=meta, body=body)

    def serialize_block(self, meta: object, event_bus=None) -> str:
        # Accept both ExtractedBlockModel and NodeMetadataBlock
        if hasattr(meta, 'metadata') and hasattr(meta, 'body'):
            meta_obj = meta.metadata
        else:
            meta_obj = meta
        return serialize_metadata_block(meta_obj, YAML_META_OPEN, YAML_META_CLOSE, comment_prefix='# ', event_bus=event_bus)

    def normalize_rest(self, rest: str) ->str:
        """
        Normalize the rest content after metadata block extraction.
        For YAML files, strip leading document separator '---' to avoid multi-document issues.
        """
        normalized = rest.strip()
        if normalized.startswith('---'):
            lines = normalized.split('\n', 1)
            if len(lines) > 1:
                normalized = lines[1].lstrip('\n')
            else:
                normalized = ''
        return normalized

    def validate(self, path: Path, content: str, **kwargs: Any
        ) ->OnexResultModel:
        """
        Validate the YAML content against the ONEX node schema.
        """
        emit_log_event(LogLevel.DEBUG, f'validate: content=\n{content}',
            node_id=_COMPONENT_NAME, event_bus=self._event_bus)
        try:
            meta_block_str, _ = self.extract_block(path, content)
            emit_log_event(LogLevel.DEBUG,
                f'validate: meta_block_str=\n{meta_block_str}', node_id=
                _COMPONENT_NAME, event_bus=self._event_bus)
            if meta_block_str:
                meta = NodeMetadataBlock.from_file_or_content(meta_block_str,
                    already_extracted_block=meta_block_str)
                emit_log_event(LogLevel.DEBUG,
                    f'validate: loaded meta=\n{meta}', node_id=
                    _COMPONENT_NAME, event_bus=self._event_bus)
            else:
                meta = None
            return OnexResultModel(status=OnexStatus.SUCCESS, target=None,
                messages=[], metadata={'note': 'Validation passed'})
        except Exception as e:
            emit_log_event(LogLevel.ERROR, f'validate: Exception: {e}',
                node_id=_COMPONENT_NAME, event_bus=self._event_bus)
            return OnexResultModel(status=OnexStatus.ERROR, target=None,
                messages=[OnexMessageModel(summary=
                f'Validation failed: {e}', level=LogLevel.ERROR).model_dump()],
                metadata={'note': 'Validation failed', 'error': str(e)})

    def normalize_block_placement(self, content: str, policy: BlockPlacementPolicy) -> str:
        """
        Normalize the placement of the metadata block according to block_placement_policy.
        - Preserves shebang if present.
        - Collapses all blank lines above the block to at most one.
        - Removes leading spaces/tabs before the block delimiter.
        - Ensures block is at the canonical position (top of file after shebang).
        """
        lines = content.splitlines(keepends=True)
        shebang = None
        start = 0
        if policy.allow_shebang and lines and lines[0].startswith('#!'):
            shebang = lines[0]
            start = 1
        open_delim = YAML_META_OPEN
        close_delim = YAML_META_CLOSE
        block_start = None
        block_end = None
        for i, line in enumerate(lines[start:], start):
            if line.lstrip().startswith(open_delim):
                block_start = i
                break
        if block_start is not None:
            for j in range(block_start, len(lines)):
                if lines[j].lstrip().startswith(close_delim):
                    block_end = j
                    break
        if block_start is not None and block_end is not None:
            block_lines = lines[block_start:block_end + 1]
            after_block = lines[block_end + 1:]
            block_lines = [re.sub('^[ \\t]+', '', line) for line in block_lines
                ]
            normalized = []
            if shebang:
                normalized.append(shebang)
            normalized.append('\n')
            normalized.extend(block_lines)
            after_block = list(after_block)
            while after_block and after_block[0].strip() == '':
                after_block.pop(0)
            normalized.extend(after_block)
            return ''.join(normalized)
        else:
            normalized = []
            if shebang:
                normalized.append(shebang)
            normalized.append('\n')
            normalized.extend(lines[start:])
            return ''.join(normalized)

    def _normalize_filename_for_namespace(self, filename: str) ->str:
        """
        Normalize a filename for use in namespace generation.
        Removes leading dots, replaces dashes with underscores, and ensures valid characters.
        """
        import re
        normalized = filename.lstrip('.')
        normalized = re.sub('[^a-zA-Z0-9_]', '_', normalized)
        normalized = re.sub('_+', '_', normalized)
        normalized = normalized.strip('_')
        if not normalized:
            normalized = 'file'
        return normalized

    def stamp(self, path: Path, content: str, **kwargs: object
        ) ->OnexResultModel:
        """
        Stamps the file by emitting a protocol-compliant metadata block using the canonical normalizer.
        All block emission must use normalize_metadata_block from metadata_block_normalizer.
        """
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.enums import OnexStatus
        from omnibase.model.model_onex_message_result import OnexResultModel
        content_no_block = MetadataBlockMixin.remove_all_metadata_blocks(
            str(content) or '', 'yaml')
        content_no_block = content_no_block.lstrip()
        if content_no_block.startswith('---'):
            content_no_block = content_no_block[3:]
            content_no_block = content_no_block.lstrip('\n ')
        prev_meta, _ = self.extract_block(path, content)
        prev_uuid = None
        prev_created_at = None
        if prev_meta is not None:
            try:
                valid_meta = NodeMetadataBlock.model_validate(prev_meta)
                prev_uuid = getattr(valid_meta, 'uuid', None)
                prev_created_at = getattr(valid_meta, 'created_at', None)
            except Exception:
                pass
        create_kwargs = dict(name=path.name, author=self.default_author or
            'OmniNode Team', entrypoint_type='yaml', entrypoint_target=path
            .stem, description=self.default_description or
            'Stamped by YAMLHandler', meta_type=str(self.default_meta_type.
            value) if self.default_meta_type else 'tool', owner=self.
            default_owner or 'OmniNode Team', namespace=f'yaml://{path.stem}')
        if prev_uuid is not None:
            create_kwargs['uuid'] = prev_uuid
        if prev_created_at is not None:
            create_kwargs['created_at'] = prev_created_at
        # Use uuid/created_at from kwargs if provided (idempotency)
        if 'uuid' in kwargs and kwargs['uuid']:
            create_kwargs['uuid'] = kwargs['uuid']
        if 'created_at' in kwargs and kwargs['created_at']:
            create_kwargs['created_at'] = kwargs['created_at']
        meta = NodeMetadataBlock.create_with_defaults(**create_kwargs)
        stamped = normalize_metadata_block(content_no_block, 'yaml', meta=meta)
        return OnexResultModel(status=OnexStatus.SUCCESS, target=str(path),
            messages=[], metadata={'content': stamped, 'note':
            'Stamped (idempotent or updated)', 'hash': meta.hash})

    def pre_validate(self, path: Path, content: str, **kwargs: Any) ->Optional[
        OnexResultModel]:
        return None

    def post_validate(self, path: Path, content: str, **kwargs: Any
        ) ->Optional[OnexResultModel]:
        return None
