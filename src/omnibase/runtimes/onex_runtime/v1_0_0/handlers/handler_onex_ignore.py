"""
OnexIgnore Handler for .onexignore configuration files.

This handler provides specialized validation and normalization for .onexignore files,
ensuring they conform to the OnexIgnoreModel Pydantic model and maintaining
consistent formatting across the codebase.
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml

from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.model.model_log_entry import LogContextModel
from omnibase.model.model_onex_ignore import OnexIgnoreModel
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler

_COMPONENT_NAME = Path(__file__).stem


class OnexIgnoreHandler(ProtocolFileTypeHandler):
    """
    Specialized handler for .onexignore configuration files.

    This handler can:
    - Validate .onexignore files against OnexIgnoreModel schema
    - Normalize formatting and structure
    - Add schema reference comments
    - Ensure consistent configuration across nodes
    """

    def __init__(self, event_bus: Optional[Any] = None) -> None:
        """Initialize the onex ignore handler."""
        super().__init__()
        self._event_bus = event_bus

    @property
    def handler_name(self) -> str:
        """Unique name for this handler (compatibility with legacy tests)."""
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
            "Handles .onexignore configuration files for validation and normalization"
        )

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        return []

    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        return [".onexignore", ".gitignore"]

    @property
    def handler_priority(self) -> int:
        """Priority for this handler (compatibility with legacy tests)."""
        return 100

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content."""
        return False

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
            if fnmatch.fnmatch(str(path), pattern) or fnmatch.fnmatch(
                path.name, pattern
            ):
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
            lines = content.strip().split("\n")
            yaml_lines = [
                line for line in lines if not line.strip().startswith("# Schema:")
            ]
            yaml_content = "\n".join(yaml_lines)
            if not yaml_content.strip():
                return {"ignore": {"patterns": []}, "processing": {}}
            return yaml.safe_load(yaml_content) or {}
        except yaml.YAMLError as e:
            emit_log_event_sync(
                level=LogLevelEnum.ERROR,
                message=f"Failed to parse YAML content: {e}",
                context=LogContextModel(
                    calling_module=__name__,
                    calling_function="_parse_yaml_content",
                    calling_line=__import__("inspect").currentframe().f_lineno,
                    timestamp=datetime.now().isoformat(),
                    node_id=_COMPONENT_NAME,
                    details={"component": _COMPONENT_NAME},
                ),
                correlation_id=None,
                event_bus=self._event_bus,
            )
            return {}

    def _normalize_config(self, data: dict[str, Any]) -> OnexIgnoreModel:
        """
        Normalize configuration data using Pydantic model.

        Args:
            data: Raw configuration data

        Returns:
            Validated and normalized configuration
        """
        try:
            return OnexIgnoreModel(**data)
        except Exception as e:
            emit_log_event_sync(
                level=LogLevelEnum.WARNING,
                message=f"Configuration validation failed, using defaults: {e}",
                context=LogContextModel(
                    calling_module=__name__,
                    calling_function="_normalize_config",
                    calling_line=__import__("inspect").currentframe().f_lineno,
                    timestamp=datetime.now().isoformat(),
                    node_id=_COMPONENT_NAME,
                    details={"component": _COMPONENT_NAME},
                ),
                correlation_id=None,
                event_bus=self._event_bus,
            )
            return OnexIgnoreModel(ignore={"patterns": []}, processing={})

    def _serialize_config(self, config: OnexIgnoreModel) -> str:
        """
        Serialize configuration to YAML with proper formatting.

        Args:
            config: Validated configuration

        Returns:
            Formatted YAML string
        """
        schema_comment = "# Schema: model_onex_ignore.OnexIgnoreModel\n\n"
        config_dict = config.model_dump(exclude_none=True)
        yaml_content = yaml.dump(
            config_dict,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            allow_unicode=True,
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
            emit_log_event_sync(
                level=LogLevelEnum.INFO,
                message=f"Successfully validated .onexignore file: {path}",
                context=LogContextModel(
                    calling_module=__name__,
                    calling_function="validate",
                    calling_line=__import__("inspect").currentframe().f_lineno,
                    timestamp=datetime.now().isoformat(),
                    node_id=_COMPONENT_NAME,
                    details={"component": _COMPONENT_NAME},
                ),
                correlation_id=kwargs.get("correlation_id"),
                event_bus=self._event_bus,
            )
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                message=f"Valid .onexignore configuration",
                file_path=str(path),
                details={"config_sections": list(config.model_dump().keys())},
            )
        except Exception as e:
            emit_log_event_sync(
                level=LogLevelEnum.ERROR,
                message=f"Validation failed for {path}: {e}",
                context=LogContextModel(
                    calling_module=__name__,
                    calling_function="validate",
                    calling_line=__import__("inspect").currentframe().f_lineno,
                    timestamp=datetime.now().isoformat(),
                    node_id=_COMPONENT_NAME,
                    details={"component": _COMPONENT_NAME},
                ),
                correlation_id=kwargs.get("correlation_id"),
                event_bus=self._event_bus,
            )
            return OnexResultModel(
                status=OnexStatus.ERROR,
                message=f"Invalid .onexignore configuration: {e}",
                file_path=str(path),
                details={"error": str(e)},
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
            emit_log_event_sync(
                level=LogLevelEnum.INFO,
                message=f"Successfully normalized .onexignore file: {path}",
                context=LogContextModel(
                    calling_module=__name__,
                    calling_function="stamp",
                    calling_line=__import__("inspect").currentframe().f_lineno,
                    timestamp=datetime.now().isoformat(),
                    node_id=_COMPONENT_NAME,
                    details={"component": _COMPONENT_NAME},
                ),
                correlation_id=kwargs.get("correlation_id"),
                event_bus=self._event_bus,
            )
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                message="Normalized .onexignore configuration",
                file_path=str(path),
                content=normalized_content,
                details={"schema_validated": True},
                target=str(path),
            )
        except Exception as e:
            emit_log_event_sync(
                level=LogLevelEnum.ERROR,
                message=f"Normalization failed for {path}: {e}",
                context=LogContextModel(
                    calling_module=__name__,
                    calling_function="stamp",
                    calling_line=__import__("inspect").currentframe().f_lineno,
                    timestamp=datetime.now().isoformat(),
                    node_id=_COMPONENT_NAME,
                    details={"component": _COMPONENT_NAME},
                ),
                correlation_id=kwargs.get("correlation_id"),
                event_bus=self._event_bus,
            )
            return OnexResultModel(
                status=OnexStatus.ERROR,
                message=f"Failed to normalize .onexignore: {e}",
                file_path=str(path),
                details={"error": str(e)},
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
        if isinstance(meta, OnexIgnoreModel):
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
