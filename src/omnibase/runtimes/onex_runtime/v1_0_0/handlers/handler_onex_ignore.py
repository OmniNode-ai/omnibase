# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T08:57:38.441159'
# description: Stamped by PythonHandler
# entrypoint: python://handler_onex_ignore
# hash: a9db205affb48551fb12b322773f248cb8753c9f6aff732f430db954bc7738ad
# last_modified_at: '2025-05-29T14:14:00.462902+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: handler_onex_ignore.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_onex_ignore
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: b65a12f1-f81e-4c3c-b6da-ba1f2f4aaf9e
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
OnexIgnore Handler for .onexignore configuration files.

This handler provides specialized validation and normalization for .onexignore files,
ensuring they conform to the OnexIgnoreConfig Pydantic model and maintaining
consistent formatting across the codebase.
"""

import hashlib
from pathlib import Path
from typing import Any, Optional

import yaml

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.model.model_onex_ignore import OnexIgnoreConfig
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler

_COMPONENT_NAME = Path(__file__).stem


class OnexIgnoreHandler(ProtocolFileTypeHandler):
    """
    Specialized handler for .onexignore configuration files.

    This handler can:
    - Validate .onexignore files against OnexIgnoreConfig schema
    - Normalize formatting and structure
    - Add schema reference comments
    - Ensure consistent configuration across nodes
    """

    def __init__(self) -> None:
        """Initialize the onex ignore handler."""
        super().__init__()

    # Handler metadata properties (required by ProtocolFileTypeHandler)
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "onex_ignore_handler"

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
        return "Handles .onexignore configuration files for validation and normalization"

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        return []  # We match on filename only

    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        return [".onexignore"]

    @property
    def handler_priority(self) -> int:
        """Priority for this handler (higher = more specific)."""
        return 90  # High priority for specific config files

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content."""
        return False  # We match on filename only

    @property
    def processing_category(self) -> str:
        """Category of processing this handler performs."""
        return "config_validation"

    @property
    def force_processing_patterns(self) -> list[str]:
        """File patterns this handler should process despite ignore rules."""
        return [".onexignore", "**/.onexignore"]

    def can_handle(self, path: Path, content: str) -> bool:
        """
        Check if this handler can process the given file.

        Args:
            path: Path to the file to check
            content: File content (not used for this handler)

        Returns:
            True if this is a .onexignore file
        """
        return path.name == ".onexignore"

    def should_process_despite_ignore(self, path: Path) -> bool:
        """
        Return True if this file should be processed even if it matches ignore patterns.
        
        Args:
            path: Path to the file to check
            
        Returns:
            True if this handler should force process this file
        """
        import fnmatch
        
        for pattern in self.force_processing_patterns:
            if fnmatch.fnmatch(str(path), pattern) or fnmatch.fnmatch(path.name, pattern):
                return True
        return False

    def _parse_yaml_content(self, content: str) -> dict[str, Any]:
        """
        Parse YAML content, handling comments and schema references.

        Args:
            content: Raw file content

        Returns:
            Parsed YAML data
        """
        try:
            # Remove schema comment line if present
            lines = content.strip().split('\n')
            yaml_lines = [line for line in lines if not line.strip().startswith('# Schema:')]
            yaml_content = '\n'.join(yaml_lines)
            
            if not yaml_content.strip():
                # Empty file, return default structure
                return {
                    "ignore": {"patterns": []},
                    "processing": {}
                }
            
            return yaml.safe_load(yaml_content) or {}
        except yaml.YAMLError as e:
            emit_log_event(
                level=LogLevelEnum.ERROR,
                message=f"Failed to parse YAML content: {e}",
                context={"component": _COMPONENT_NAME},
                correlation_id=None,
            )
            return {}

    def _normalize_config(self, data: dict[str, Any]) -> OnexIgnoreConfig:
        """
        Normalize configuration data using Pydantic model.

        Args:
            data: Raw configuration data

        Returns:
            Validated and normalized configuration
        """
        try:
            return OnexIgnoreConfig(**data)
        except Exception as e:
            emit_log_event(
                level=LogLevelEnum.WARNING,
                message=f"Configuration validation failed, using defaults: {e}",
                context={"component": _COMPONENT_NAME},
                correlation_id=None,
            )
            # Return minimal valid configuration
            return OnexIgnoreConfig(
                ignore={"patterns": []},
                processing={}
            )

    def _serialize_config(self, config: OnexIgnoreConfig) -> str:
        """
        Serialize configuration to YAML with proper formatting.

        Args:
            config: Validated configuration

        Returns:
            Formatted YAML string
        """
        # Add schema reference comment
        schema_comment = "# Schema: model_onex_ignore.OnexIgnoreConfig\n\n"
        
        # Convert to dict and serialize
        config_dict = config.model_dump(exclude_none=True)
        yaml_content = yaml.dump(
            config_dict,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            allow_unicode=True
        )
        
        return schema_comment + yaml_content

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Validate .onexignore file against schema.

        Args:
            path: Path to the file
            content: File content
            **kwargs: Additional validation options

        Returns:
            Validation result
        """
        try:
            data = self._parse_yaml_content(content)
            config = self._normalize_config(data)
            
            emit_log_event(
                level=LogLevelEnum.INFO,
                message=f"Successfully validated .onexignore file: {path}",
                context={"component": _COMPONENT_NAME},
                correlation_id=kwargs.get("correlation_id"),
            )
            
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                message=f"Valid .onexignore configuration",
                file_path=str(path),
                details={"config_sections": list(config.model_dump().keys())}
            )
            
        except Exception as e:
            emit_log_event(
                level=LogLevelEnum.ERROR,
                message=f"Validation failed for {path}: {e}",
                context={"component": _COMPONENT_NAME},
                correlation_id=kwargs.get("correlation_id"),
            )
            
            return OnexResultModel(
                status=OnexStatus.ERROR,
                message=f"Invalid .onexignore configuration: {e}",
                file_path=str(path),
                details={"error": str(e)}
            )

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Normalize and format .onexignore file.

        Args:
            path: Path to the file
            content: File content
            **kwargs: Additional stamping options

        Returns:
            Stamping result with normalized content
        """
        try:
            data = self._parse_yaml_content(content)
            config = self._normalize_config(data)
            normalized_content = self._serialize_config(config)
            
            emit_log_event(
                level=LogLevelEnum.INFO,
                message=f"Successfully normalized .onexignore file: {path}",
                context={"component": _COMPONENT_NAME},
                correlation_id=kwargs.get("correlation_id"),
            )
            
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                message="Normalized .onexignore configuration",
                file_path=str(path),
                content=normalized_content,
                details={"schema_validated": True}
            )
            
        except Exception as e:
            emit_log_event(
                level=LogLevelEnum.ERROR,
                message=f"Normalization failed for {path}: {e}",
                context={"component": _COMPONENT_NAME},
                correlation_id=kwargs.get("correlation_id"),
            )
            
            return OnexResultModel(
                status=OnexStatus.ERROR,
                message=f"Failed to normalize .onexignore: {e}",
                file_path=str(path),
                details={"error": str(e)}
            )

    def extract_block(self, path: Path, content: str) -> tuple[Optional[Any], str]:
        """
        Extract configuration block from .onexignore file.

        Args:
            path: Path to the file
            content: File content

        Returns:
            Tuple of (config_object, remaining_content)
        """
        data = self._parse_yaml_content(content)
        config = self._normalize_config(data)
        return config, ""

    def serialize_block(self, meta: Any) -> str:
        """
        Serialize configuration object to string.

        Args:
            meta: Configuration object

        Returns:
            Serialized configuration
        """
        if isinstance(meta, OnexIgnoreConfig):
            return self._serialize_config(meta)
        return str(meta)

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        """Optional pre-validation step."""
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        """Optional post-validation step."""
        return None
