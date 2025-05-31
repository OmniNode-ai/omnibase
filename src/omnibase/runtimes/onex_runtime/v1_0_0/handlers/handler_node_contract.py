"""
Node Contract Handler for ONEX node.onex.yaml files.

This handler provides specialized stamping and validation for node metadata files,
automatically resolving template placeholders and ensuring schema compliance.
"""
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.model.model_node_metadata import NodeMetadataBlock, Namespace
_COMPONENT_NAME = Path(__file__).stem


class NodeContractHandler(ProtocolFileTypeHandler):
    """
    Specialized handler for node.onex.yaml contract files.

    This handler can:
    - Detect and resolve template placeholders
    - Generate proper UUIDs, timestamps, and hashes
    - Validate against node metadata schema
    - Infer node information from directory structure
    """

    def __init__(self, event_bus: Optional[Any]=None) ->None:
        """Initialize the node contract handler."""
        super().__init__()
        self._event_bus = event_bus

    @property
    def handler_name(self) ->str:
        """Unique name for this handler."""
        return 'node_contract_handler'

    @property
    def handler_version(self) ->str:
        """Version of this handler implementation."""
        return '1.0.0'

    @property
    def handler_author(self) ->str:
        """Author or team responsible for this handler."""
        return 'OmniNode Team'

    @property
    def handler_description(self) ->str:
        """Brief description of what this handler does."""
        return (
            'Handles node.onex.yaml contract files for template resolution and validation'
            )

    @property
    def supported_extensions(self) ->list[str]:
        """List of file extensions this handler supports."""
        return ['.yaml']

    @property
    def supported_filenames(self) ->list[str]:
        """List of specific filenames this handler supports."""
        return ['node.onex.yaml']

    @property
    def handler_priority(self) ->int:
        """Priority for this handler (higher = more specific)."""
        return 100

    @property
    def requires_content_analysis(self) ->bool:
        """Whether this handler needs to analyze file content."""
        return False

    def can_handle(self, path: Path, content: str) ->bool:
        """
        Check if this handler can process the given file.

        Args:
            path: Path to the file to check
            content: File content (not used for this handler)

        Returns:
            True if this is a node.onex.yaml file
        """
        return path.name == 'node.onex.yaml'

    def _infer_node_info_from_path(self, file_path: Path) ->Dict[str, str]:
        """
        Infer node information from the file path structure.

        Expected structure: .../nodes/{node_name}/v{major}_{minor}_{patch}/node.onex.yaml

        Args:
            file_path: Path to the node.onex.yaml file

        Returns:
            Dictionary with inferred node information
        """
        parts = file_path.parts
        try:
            nodes_index = parts.index('nodes')
            if nodes_index + 2 < len(parts):
                node_name = parts[nodes_index + 1]
                version_dir = parts[nodes_index + 2]
                if version_dir.startswith('v') and '_' in version_dir:
                    version_parts = version_dir[1:].split('_')
                    if len(version_parts) == 3:
                        version = '.'.join(version_parts)
                    else:
                        version = '1.0.0'
                else:
                    version = '1.0.0'
                if node_name == 'template_node':
                    namespace = 'omnibase.nodes.template_node'
                else:
                    namespace = f'onex.nodes.{node_name}'
                return {'node_name': node_name, 'version': version,
                    'namespace': namespace, 'state_contract':
                    f'state_contract://{node_name}_contract.yaml'}
        except (ValueError, IndexError):
            pass
        return {'node_name': 'unknown_node', 'version': '1.0.0',
            'namespace': 'onex.nodes.unknown_node', 'state_contract':
            'state_contract://unknown_node_contract.yaml'}

    def _generate_hash(self, content: str) ->str:
        """
        Generate a SHA-256 hash for the content.

        Args:
            content: Content to hash

        Returns:
            64-character hexadecimal hash
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _resolve_template_placeholders(self, data: Dict[str, Any],
        file_path: Path) ->Dict[str, Any]:
        """
        Resolve template placeholders in the node metadata.

        Args:
            data: Parsed YAML data
            file_path: Path to the file being processed

        Returns:
            Data with resolved placeholders
        """
        node_info = self._infer_node_info_from_path(file_path)
        current_time = datetime.utcnow().isoformat() + 'Z'
        resolved_data = data.copy()
        resolved_data.setdefault('node_name', node_info['node_name'])
        resolved_data.setdefault('version', node_info['version'])
        resolved_data.setdefault('namespace', node_info['namespace'])
        resolved_data.setdefault('state_contract', node_info['state_contract'])
        resolved_data.setdefault('name', file_path.name)
        resolved_data.setdefault('entrypoint', f'python://{file_path.name}')
        resolved_data.setdefault('author', 'OmniNode Team')
        resolved_data.setdefault('copyright', 'OmniNode Team')
        resolved_data.setdefault('owner', 'OmniNode Team')
        resolved_data.setdefault('description',
            'Stamped by NodeContractHandler')
        resolved_data.setdefault('meta_type', 'tool')
        resolved_data.setdefault('lifecycle', 'active')
        resolved_data.setdefault('runtime_language_hint', 'python>=3.11')
        resolved_data.setdefault('created_at', current_time)
        resolved_data.setdefault('last_modified_at', current_time)
        resolved_data.setdefault('uuid', str(uuid.uuid4()))
        resolved_data.setdefault('hash', self._generate_hash(str(
            resolved_data)))
        resolved_data.setdefault('metadata_version', '0.1.0')
        resolved_data.setdefault('schema_version', '1.0.0')
        return resolved_data

    def stamp(self, path: Path, content: str, **kwargs: Any) ->OnexResultModel:
        """
        Stamp a node.onex.yaml file with proper metadata.

        Args:
            path: Path to the node.onex.yaml file
            content: Current file content
            **kwargs: Additional arguments (author, etc.)

        Returns:
            OnexResultModel with stamping results
        """
        emit_log_event(LogLevelEnum.DEBUG, f'[START] stamp for {path}',
            node_id=_COMPONENT_NAME, event_bus=self._event_bus)
        try:
            try:
                data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                return OnexResultModel(status=OnexStatus.ERROR, target=str(
                    path), messages=[], metadata={'file_path': str(path),
                    'error': f'Failed to parse YAML: {e}'})
            resolved_data = self._resolve_template_placeholders(data, path)
            ns = resolved_data.get('namespace')
            if isinstance(ns, str):
                try:
                    resolved_data['namespace'] = Namespace.from_path(path)
                except Exception:
                    resolved_data['namespace'] = Namespace(value=ns)
            elif not isinstance(ns, Namespace):
                resolved_data['namespace'] = Namespace(value=str(ns))
            meta = NodeMetadataBlock.from_serializable_dict(resolved_data)
            canonical_dict = meta.to_serializable_dict()
            hash_data = canonical_dict.copy()
            hash_data.pop('hash', None)
            hash_content = yaml.dump(hash_data, default_flow_style=False,
                sort_keys=True)
            canonical_dict['hash'] = self._generate_hash(hash_content)
            canonical_dict['last_modified_at'] = datetime.utcnow().isoformat(
                ) + 'Z'
            new_content = '---\n\n' + yaml.dump(canonical_dict,
                default_flow_style=False, sort_keys=False)
            emit_log_event(LogLevelEnum.DEBUG,
                f'[END] stamp for {path} - success', node_id=
                _COMPONENT_NAME, event_bus=self._event_bus)
            return OnexResultModel(status=OnexStatus.SUCCESS, target=str(
                path), messages=[], metadata={'content': new_content,
                'file_path': str(path), 'node_name': resolved_data.get(
                'name'), 'version': resolved_data.get('version'), 'hash':
                resolved_data.get('hash'), 'note':
                'Successfully stamped node contract'})
        except Exception as e:
            emit_log_event(LogLevelEnum.ERROR,
                f'Exception in stamp for {path}: {e}', node_id=
                _COMPONENT_NAME, event_bus=self._event_bus)
            return OnexResultModel(status=OnexStatus.ERROR, target=str(path
                ), messages=[], metadata={'file_path': str(path), 'error':
                f'Failed to stamp node contract: {e}'})

    def validate(self, path: Path, content: str, **kwargs: Any
        ) ->OnexResultModel:
        """
        Validate a node.onex.yaml file against the schema.

        Args:
            path: Path to the file to validate
            content: File content to validate
            **kwargs: Additional validation arguments

        Returns:
            OnexResultModel with validation results
        """
        emit_log_event(LogLevelEnum.DEBUG, f'[START] validate for {path}',
            node_id=_COMPONENT_NAME, event_bus=self._event_bus)
        try:
            data = yaml.safe_load(content)
            required_fields = ['schema_version', 'name', 'version', 'uuid',
                'author', 'created_at', 'last_modified_at', 'description',
                'lifecycle', 'hash']
            missing_fields = [field for field in required_fields if field
                 not in data]
            if missing_fields:
                return OnexResultModel(status=OnexStatus.ERROR, message=
                    f'Missing required fields: {missing_fields}', metadata=
                    {'file_path': str(path)})
            template_placeholders = ['TEMPLATE-UUID-REPLACE-ME',
                'TEMPLATE_AUTHOR', 'TEMPLATE_CREATED_AT',
                'TEMPLATE_LAST_MODIFIED_AT', 'TEMPLATE_HASH_TO_BE_COMPUTED']
            found_placeholders = []

            def check_placeholders(obj: Any, path_str: str='') ->None:
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        check_placeholders(v, f'{path_str}.{k}' if path_str
                             else k)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        check_placeholders(item, f'{path_str}[{i}]')
                elif isinstance(obj, str):
                    for placeholder in template_placeholders:
                        if placeholder in obj:
                            found_placeholders.append(
                                f'{path_str}: {placeholder}')
            check_placeholders(data)
            if found_placeholders:
                emit_log_event(LogLevelEnum.WARNING,
                    f'Found template placeholders in {path}: {found_placeholders}'
                    , node_id=_COMPONENT_NAME, event_bus=self._event_bus)
                return OnexResultModel(status=OnexStatus.WARNING, message=
                    f'Found template placeholders: {found_placeholders}',
                    metadata={'file_path': str(path), 'needs_stamping': True})
            emit_log_event(LogLevelEnum.DEBUG,
                f'[END] validate for {path} - success', node_id=
                _COMPONENT_NAME, event_bus=self._event_bus)
            return OnexResultModel(status=OnexStatus.SUCCESS, message=
                'Node contract validation passed', metadata={'file_path':
                str(path)})
        except Exception as e:
            emit_log_event(LogLevelEnum.ERROR,
                f'Exception in validate for {path}: {e}', node_id=
                _COMPONENT_NAME, event_bus=self._event_bus)
            return OnexResultModel(status=OnexStatus.ERROR, message=
                f'Validation failed: {e}', metadata={'file_path': str(path)})

    def extract_block(self, path: Path, content: str) ->tuple[Optional[Any],
        str]:
        """
        Extract metadata block from node.onex.yaml file.

        For node.onex.yaml files, we don't use traditional ONEX metadata blocks,
        so this returns None for metadata and the original content.

        Args:
            path: Path to the file
            content: File content

        Returns:
            Tuple of (metadata, content_without_metadata)
        """
        return None, content

    def serialize_block(self, meta: Any) ->str:
        """
        Serialize metadata block for node.onex.yaml file.

        For node.onex.yaml files, we don't use traditional ONEX metadata blocks,
        so this returns an empty string.

        Args:
            meta: Metadata to serialize

        Returns:
            Serialized metadata block (empty for node contract files)
        """
        return ''

    def pre_validate(self, path: Path, content: str, **kwargs: Any) ->Optional[
        OnexResultModel]:
        """
        Optional pre-validation before stamping.

        Args:
            path: Path to the file
            content: File content
            **kwargs: Additional arguments

        Returns:
            OnexResultModel if validation fails, None if validation passes
        """
        return None

    def post_validate(self, path: Path, content: str, **kwargs: Any
        ) ->Optional[OnexResultModel]:
        """
        Optional post-validation after stamping.

        Args:
            path: Path to the file
            content: File content
            **kwargs: Additional arguments

        Returns:
            OnexResultModel if validation fails, None if validation passes
        """
        return None
