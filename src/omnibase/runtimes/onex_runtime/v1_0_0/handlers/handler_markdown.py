import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.enums.handler_source import HandlerSourceEnum
from omnibase.metadata.metadata_constants import MD_META_CLOSE, MD_META_OPEN, get_namespace_prefix
from omnibase.model.model_node_metadata import NodeMetadataBlock, Namespace
if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_block_placement import BlockPlacementMixin
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_metadata_block import MetadataBlockMixin
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.model.model_handler_protocol import HandlerMetadataModel, CanHandleResultModel, ExtractedBlockModel
_COMPONENT_NAME = Path(__file__).stem


class MarkdownHandler(ProtocolFileTypeHandler, MetadataBlockMixin,
    BlockPlacementMixin):
    """
    Handler for Markdown (.md) files for ONEX stamping.
    All block extraction, serialization, and idempotency logic is delegated to the canonical mixins.
    All block emission MUST use the canonical normalize_metadata_block from metadata_block_normalizer (protocol requirement).
    No custom or legacy logic is present; all protocol details are sourced from metadata_constants.
    All extracted metadata blocks must be validated and normalized using the canonical Pydantic model (NodeMetadataBlock) before further processing.
    """

    def __init__(self, default_author: str='OmniNode Team',
        default_entrypoint_type: str='markdown', default_namespace_prefix:
        str=f'{get_namespace_prefix()}.stamped', default_meta_type:
        Optional[Any]=None, default_description: Optional[str]=None, event_bus: Optional[Any]=None) ->None:
        self.default_author = default_author
        self.default_entrypoint_type = default_entrypoint_type
        self.default_namespace_prefix = default_namespace_prefix
        self.default_meta_type = default_meta_type
        self.default_description = default_description
        self._event_bus = event_bus

    @property
    def metadata(self) -> HandlerMetadataModel:
        return HandlerMetadataModel(
            handler_name='markdown_handler',
            handler_version='1.0.0',
            handler_author='OmniNode Team',
            handler_description='Handles Markdown files (.md) for ONEX metadata stamping and validation',
            supported_extensions=['.md', '.markdown'],
            supported_filenames=[],
            handler_priority=50,
            requires_content_analysis=bool(self.can_handle_predicate),
            source=HandlerSourceEnum.CORE
        )

    @property
    def handler_name(self) -> str:
        return 'markdown_handler'

    @property
    def handler_version(self) -> str:
        return '1.0.0'

    @property
    def handler_author(self) -> str:
        return 'OmniNode Team'

    @property
    def handler_description(self) -> str:
        return 'Handles Markdown files (.md) for ONEX metadata stamping and validation'

    @property
    def supported_extensions(self) -> list[str]:
        return ['.md', '.markdown']

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
        return CanHandleResultModel(can_handle=path.suffix.lower() in {'.md', '.markdown', '.mdx'})

    def extract_block(self, path: Path, content: str) -> ExtractedBlockModel:
        """
        Extracts the ONEX metadata block from Markdown content.
        - Uses canonical delimiter constants (MD_META_OPEN, MD_META_CLOSE) for all block operations.
        - Attempts to extract canonical (YAML in HTML comment), legacy (YAML in HTML comment with # prefixes), and legacy field-per-comment (<!-- field: value -->) blocks.
        - Prefers canonical if both are found; upgrades legacy to canonical.
        - Removes all detected blocks before emitting the new one.
        - Logs warnings if multiple or malformed blocks are found.
        """
        import re
        import yaml
        from omnibase.metadata.metadata_constants import MD_META_OPEN, MD_META_CLOSE
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.core.core_structured_logging import emit_log_event
        from omnibase.enums import LogLevelEnum
        canonical_pattern = (
            rf'{re.escape(MD_META_OPEN)}\n(.*?)(?:\n)?{re.escape(MD_META_CLOSE)}'
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
                emit_log_event(LogLevelEnum.WARNING,
                    f'Malformed canonical metadata block in {path}: {e}',
                    node_id=_COMPONENT_NAME, event_bus=self._event_bus)
                meta = None
        if not meta:
            legacy_pattern = (
                rf'{re.escape(MD_META_OPEN)}\n((?:#.*?\n)+){re.escape(MD_META_CLOSE)}'
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
                    emit_log_event(LogLevelEnum.WARNING,
                        f'Malformed legacy metadata block in {path}: {e}',
                        node_id=_COMPONENT_NAME, event_bus=self._event_bus)
                    meta = None
        if not meta:
            field_comment_pattern = (
                rf'{re.escape(MD_META_OPEN)}\n((?:<!--.*?-->\n?)+){re.escape(MD_META_CLOSE)}'
                )
            field_comment_match = re.search(field_comment_pattern, content,
                re.DOTALL)
            if field_comment_match:
                block_fields = field_comment_match.group(1)
                field_pattern = r'<!--\s*([a-zA-Z0-9_]+):\s*(.*?)\s*-->'
                meta_dict = {}
                for line in block_fields.splitlines():
                    m = re.match(field_pattern, line.strip())
                    if m:
                        key, value = m.group(1), m.group(2)
                        meta_dict[key] = value
                if meta_dict:
                    try:
                        meta = NodeMetadataBlock.model_validate(meta_dict)
                        emit_log_event(LogLevelEnum.WARNING,
                            f'Upgraded legacy field-per-comment metadata block to canonical in {path}'
                            , node_id=_COMPONENT_NAME, event_bus=self.
                            _event_bus)
                    except Exception as e:
                        emit_log_event(LogLevelEnum.WARNING,
                            f'Malformed field-per-comment metadata block in {path}: {e}'
                            , node_id=_COMPONENT_NAME, event_bus=self.
                            _event_bus)
                        meta = None
        all_block_pattern = (
            rf'{re.escape(MD_META_OPEN)}[\s\S]+?{re.escape(MD_META_CLOSE)}\n*'
            )
        body = re.sub(all_block_pattern, '', content, flags=re.MULTILINE)
        return ExtractedBlockModel(metadata=meta, body=body)

    def serialize_block(self, meta: object, event_bus=None) -> str:
        from omnibase.metadata.metadata_constants import MD_META_OPEN, MD_META_CLOSE
        from omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer import serialize_metadata_block
        # Accept both ExtractedBlockModel and NodeMetadataBlock
        if hasattr(meta, 'metadata') and hasattr(meta, 'body'):
            meta_obj = meta.metadata
        else:
            meta_obj = meta
        return serialize_metadata_block(meta_obj, MD_META_OPEN, MD_META_CLOSE, comment_prefix='', event_bus=event_bus)

    def normalize_rest(self, rest: str) ->str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: object
        ) ->OnexResultModel:
        """
        Stamps the file by emitting a protocol-compliant metadata block using the canonical normalizer.
        All block emission must use normalize_metadata_block from metadata_block_normalizer.
        """
        from omnibase.nodes.stamper_node.v1_0_0.helpers.metadata_block_normalizer import normalize_metadata_block
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.enums import OnexStatus
        from omnibase.model.model_onex_message_result import OnexResultModel
        content_no_block = MetadataBlockMixin.remove_all_metadata_blocks(
            str(content) or '', 'markdown')
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
            'OmniNode Team', entrypoint_type='markdown', entrypoint_target=
            path.stem, description=self.default_description or
            'Stamped by MarkdownHandler', meta_type=str(self.
            default_meta_type.value) if self.default_meta_type else 'tool',
            owner=getattr(self, 'default_owner', None) or 'OmniNode Team',
            namespace=f'markdown://{path.stem}')
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
        stamped = normalize_metadata_block(content_no_block, 'markdown',
            meta=meta)
        return OnexResultModel(status=OnexStatus.SUCCESS, target=str(path),
            messages=[], metadata={'content': stamped, 'note':
            'Stamped (idempotent or updated)', 'hash': meta.hash})

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
