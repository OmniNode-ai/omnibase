"""
Specialized handler for state contract files (contract.yaml).

This handler provides:
- Validation of contract structure using StateContractModel
- Proper ONEX metadata stamping
- Template placeholder resolution
- Hash generation and timestamp management
- Integration with the stamper tool ecosystem
"""
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevel, OnexStatus
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.model.model_state_contract import StateContractModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
_COMPONENT_NAME = Path(__file__).stem


class StateContractHandler(ProtocolFileTypeHandler):
    """
    Specialized handler for contract.yaml state contract files.

    This handler can:
    - Validate contract structure using StateContractModel
    - Add proper ONEX metadata stamping
    - Resolve template placeholders
    - Generate proper UUIDs, timestamps, and hashes
    - Ensure consistency across all contract files
    """

    def __init__(self, event_bus: Optional[Any]=None) ->None:
        """Initialize the state contract handler."""
        super().__init__()
        self._event_bus = event_bus

    @property
    def handler_name(self) ->str:
        """Unique name for this handler."""
        return 'state_contract_handler'

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
            'Handles contract.yaml state contract files for validation and stamping'
            )

    @property
    def supported_extensions(self) ->list[str]:
        """List of file extensions this handler supports."""
        return ['.yaml']

    @property
    def supported_filenames(self) ->list[str]:
        """List of specific filenames this handler supports."""
        return ['contract.yaml']

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
        Determine if this handler can process the given file.

        Args:
            path: Path to the file
            content: File content (not used for this handler)

        Returns:
            True if this handler can process the file
        """
        return path.name == 'contract.yaml'

    def _generate_hash(self, content: str) ->str:
        """
        Generate SHA-256 hash of the content.

        Args:
            content: Content to hash

        Returns:
            SHA-256 hash as hexadecimal string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _generate_uuid(self) ->str:
        """
        Generate a new UUID for the contract.

        Returns:
            UUID as string
        """
        import uuid
        return str(uuid.uuid4())

    def _infer_node_name_from_path(self, path: Path) ->str:
        """
        Infer the node name from the file path.

        Args:
            path: Path to the contract.yaml file

        Returns:
            Inferred node name
        """
        parts = path.parts
        for i, part in enumerate(parts):
            if part.endswith('_node') and i + 1 < len(parts) and parts[i + 1
                ].startswith('v'):
                return part
        parent = path.parent.name
        if parent.endswith('_node'):
            return parent
        grandparent = path.parent.parent.name
        if grandparent.endswith('_node'):
            return grandparent
        return 'unknown_node'

    def _resolve_template_placeholders(self, data: Dict[str, Any], path: Path
        ) ->Dict[str, Any]:
        """
        Resolve template placeholders in the contract data.

        Args:
            data: Contract data dictionary
            path: Path to the contract file

        Returns:
            Contract data with resolved placeholders
        """
        resolved_data = data.copy()
        if 'node_name' not in resolved_data or resolved_data['node_name'] in [
            'TEMPLATE_NODE', 'template_node']:
            resolved_data['node_name'] = self._infer_node_name_from_path(path)
        resolved_data.setdefault('name', path.name)
        resolved_data.setdefault('entrypoint', f'python://{path.name}')
        resolved_data.setdefault('owner', 'OmniNode Team')
        resolved_data.setdefault('copyright', 'OmniNode Team')
        resolved_data.setdefault('schema_version', '1.1.0')
        resolved_data.setdefault('version', '1.0.0')
        resolved_data.setdefault('author', 'OmniNode Team')
        resolved_data.setdefault('description',
            'Stamped by StateContractHandler')
        resolved_data.setdefault('state_contract', 'state_contract://default')
        resolved_data.setdefault('lifecycle', 'active')
        resolved_data.setdefault('runtime_language_hint', 'python>=3.11')
        resolved_data.setdefault('namespace',
            f"onex.stamped.{resolved_data['node_name']}_contract")
        resolved_data.setdefault('meta_type', 'tool')
        return resolved_data

    def validate(self, path: Path, content: str, **kwargs: Any
        ) ->OnexResultModel:
        """
        Validate a state contract file.

        Args:
            path: Path to the contract file
            content: File content
            **kwargs: Additional arguments

        Returns:
            OnexResultModel with validation results
        """
        emit_log_event(LogLevel.DEBUG, f'[START] validate for {path}',
            node_id=_COMPONENT_NAME, event_bus=self._event_bus)
        try:
            try:
                data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                return OnexResultModel(status=OnexStatus.ERROR, target=str(
                    path), messages=[f'Failed to parse YAML: {e}'],
                    metadata={'file_path': str(path), 'error':
                    f'YAML parsing error: {e}'})
            if not data:
                return OnexResultModel(status=OnexStatus.ERROR, target=str(
                    path), messages=['Contract file is empty'], metadata={
                    'file_path': str(path)})
            try:
                contract_model = StateContractModel.from_yaml_dict(data)
                emit_log_event(LogLevel.DEBUG,
                    f'[END] validate for {path} - success', node_id=
                    _COMPONENT_NAME, event_bus=self._event_bus)
                return OnexResultModel(status=OnexStatus.SUCCESS, target=
                    str(path), messages=['Contract validation successful'],
                    metadata={'file_path': str(path), 'node_name':
                    contract_model.node_name, 'contract_version':
                    contract_model.contract_version, 'note':
                    'Contract structure is valid'})
            except Exception as e:
                return OnexResultModel(status=OnexStatus.ERROR, target=str(
                    path), messages=[f'Contract validation failed: {e}'],
                    metadata={'file_path': str(path), 'error':
                    f'Validation error: {e}'})
        except Exception as e:
            emit_log_event(LogLevel.ERROR,
                f'[ERROR] validate for {path}: {e}', node_id=
                _COMPONENT_NAME, event_bus=self._event_bus)
            return OnexResultModel(status=OnexStatus.ERROR, target=str(path
                ), messages=[f'Validation failed: {e}'], metadata={
                'file_path': str(path), 'error': str(e)})

    def stamp(self, path: Path, content: str, **kwargs: Any) ->OnexResultModel:
        """
        Stamp a contract.yaml file with proper metadata.

        Args:
            path: Path to the contract.yaml file
            content: Current file content
            **kwargs: Additional arguments (author, etc.)

        Returns:
            OnexResultModel with stamping results
        """
        emit_log_event(LogLevel.DEBUG, f'[START] stamp for {path}',
            node_id=_COMPONENT_NAME, event_bus=self._event_bus)
        try:
            try:
                data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                return OnexResultModel(status=OnexStatus.ERROR, target=str(
                    path), messages=[], metadata={'file_path': str(path),
                    'error': f'Failed to parse YAML: {e}'})
            if not data:
                data = {}
            resolved_data = self._resolve_template_placeholders(data, path)
            try:
                contract_model = StateContractModel.from_yaml_dict(
                    resolved_data)
                resolved_data = contract_model.to_yaml_dict()
            except Exception as e:
                emit_log_event(LogLevel.WARNING,
                    f'Contract validation failed during stamping: {e}',
                    node_id=_COMPONENT_NAME, event_bus=self._event_bus)
            hash_data = resolved_data.copy()
            hash_data.pop('hash', None)


            class CustomYAMLDumper(yaml.SafeDumper):

                def increase_indent(self, flow: bool=False, indentless:
                    bool=False) ->None:
                    return super().increase_indent(flow, False)
            hash_content = yaml.dump(hash_data, default_flow_style=False,
                sort_keys=True, indent=2, Dumper=CustomYAMLDumper)
            resolved_data['hash'] = self._generate_hash(hash_content)
            resolved_data['last_modified_at'] = datetime.utcnow().isoformat(
                ) + 'Z'
            new_content = '---\n\n' + yaml.dump(resolved_data,
                default_flow_style=False, sort_keys=False, indent=2, Dumper
                =CustomYAMLDumper)
            emit_log_event(LogLevel.DEBUG,
                f'[END] stamp for {path} - success', node_id=
                _COMPONENT_NAME, event_bus=self._event_bus)
            return OnexResultModel(status=OnexStatus.SUCCESS, target=str(
                path), messages=[], metadata={'content': new_content,
                'file_path': str(path), 'node_name': resolved_data.get(
                'node_name'), 'contract_version': resolved_data.get(
                'contract_version'), 'hash': resolved_data.get('hash'),
                'note': 'Successfully stamped state contract'})
        except Exception as e:
            emit_log_event(LogLevel.ERROR,
                f'[ERROR] stamp for {path}: {e}', node_id=_COMPONENT_NAME,
                event_bus=self._event_bus)
            return OnexResultModel(status=OnexStatus.ERROR, target=str(path
                ), messages=[], metadata={'file_path': str(path), 'error':
                str(e)})

    def extract_block(self, path: Path, content: str) ->tuple[Optional[Any],
        str]:
        """
        Extract metadata block from contract.yaml file.

        For contract.yaml files, we don't use traditional ONEX metadata blocks,
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
        Serialize metadata block for contract.yaml file.

        For contract.yaml files, we don't use traditional ONEX metadata blocks,
        so this returns an empty string.

        Args:
            meta: Metadata to serialize

        Returns:
            Serialized metadata block (empty for contract files)
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
