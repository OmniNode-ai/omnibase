# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-29T06:01:44.013539'
# description: Stamped by PythonHandler
# entrypoint: python://project_metadata_handler
# hash: 3f3624106f1d928306e6d07a44259dc2a2e72887f8861f8ebd6bdbea9b03c7e3
# last_modified_at: '2025-05-29T14:14:00.486698+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: project_metadata_handler.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.handlers.project_metadata_handler
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: cd33d19b-47df-4b9e-9972-70048f782ade
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any, Optional
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.model.model_project_metadata import ProjectMetadataBlock
from omnibase.model.model_onex_message_result import OnexResultModel, OnexMessageModel
from omnibase.enums import OnexStatus
import yaml

class ProjectMetadataHandler(ProtocolFileTypeHandler):
    """
    Handler for ONEX project-level metadata (project.onex.yaml).
    """
    
    # Handler metadata properties (required by ProtocolFileTypeHandler)
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "project_metadata_handler"

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
        return "Handles project.onex.yaml files for ONEX project metadata"

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        return [".yaml"]

    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        return ["project.onex.yaml"]

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 100  # High priority since this is very specific

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content."""
        return False  # We match on filename only

    def can_handle(self, path: Path, content: str) -> bool:
        return path.name == "project.onex.yaml"

    def load(self, path: Path) -> ProjectMetadataBlock:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return ProjectMetadataBlock.from_dict(data)

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """Stamp the project metadata file."""
        try:
            meta = self.load(path)
            # Update last_modified_at
            from datetime import datetime
            meta.last_modified_at = datetime.utcnow().isoformat()
            
            write = kwargs.get('write', False)
            if write:
                with open(path, "w") as f:
                    yaml.safe_dump(meta.model_dump(), f)
            
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                target=str(path),
                messages=[OnexMessageModel(summary="Project metadata stamped successfully")],
                metadata=meta.model_dump()
            )
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=str(path),
                messages=[OnexMessageModel(summary=f"Failed to stamp project metadata: {str(e)}")],
                metadata={}
            )

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """Validate the project metadata file."""
        try:
            meta = self.load(path)
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                target=str(path),
                messages=[OnexMessageModel(summary="Project metadata validation passed")],
                metadata=meta.model_dump()
            )
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=str(path),
                messages=[OnexMessageModel(summary=f"Project metadata validation failed: {str(e)}")],
                metadata={}
            )

    def pre_validate(self, path: Path, content: str, **kwargs: Any) -> Optional[OnexResultModel]:
        return None

    def post_validate(self, path: Path, content: str, **kwargs: Any) -> Optional[OnexResultModel]:
        return None

    def introspect(self, path: Path) -> dict:
        meta = self.load(path)
        return meta.model_dump()
