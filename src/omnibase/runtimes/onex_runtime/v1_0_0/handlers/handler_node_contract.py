# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_node_contract.py
# version: 1.0.0
# uuid: 9e3329c4-87f1-4c87-ab13-6f7b60ac5623
# author: OmniNode Team
# created_at: 2025-05-27T14:58:23.511515
# last_modified_at: 2025-05-27T19:50:42.789051
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d125ce70b90045be147df68978e87bffc418d7d758a0fda69ae39355860e7c8b
# entrypoint: python@handler_node_contract.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_node_contract
# meta_type: tool
# === /OmniNode:Metadata ===


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

# Component identifier for logging
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

    def __init__(self) -> None:
        """Initialize the node contract handler."""
        super().__init__()

    # Handler metadata properties (required by ProtocolFileTypeHandler)
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "node_contract_handler"

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
        return "Handles node.onex.yaml contract files for template resolution and validation"

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        return [".yaml"]

    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        return ["node.onex.yaml"]

    @property
    def handler_priority(self) -> int:
        """Priority for this handler (higher = more specific)."""
        return 100  # High priority since this is very specific

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content."""
        return False  # We can determine from filename alone

    def can_handle(self, path: Path, content: str) -> bool:
        """
        Check if this handler can process the given file.

        Args:
            path: Path to the file to check
            content: File content (not used for this handler)

        Returns:
            True if this is a node.onex.yaml file
        """
        return path.name == "node.onex.yaml"

    def _infer_node_info_from_path(self, file_path: Path) -> Dict[str, str]:
        """
        Infer node information from the file path structure.

        Expected structure: .../nodes/{node_name}/v{major}_{minor}_{patch}/node.onex.yaml

        Args:
            file_path: Path to the node.onex.yaml file

        Returns:
            Dictionary with inferred node information
        """
        parts = file_path.parts

        # Find the nodes directory
        try:
            nodes_index = parts.index("nodes")
            if nodes_index + 2 < len(parts):
                node_name = parts[nodes_index + 1]
                version_dir = parts[nodes_index + 2]

                # Extract version from directory name (e.g., "v1_0_0" -> "1.0.0")
                if version_dir.startswith("v") and "_" in version_dir:
                    version_parts = version_dir[1:].split("_")
                    if len(version_parts) == 3:
                        version = ".".join(version_parts)
                    else:
                        version = "1.0.0"
                else:
                    version = "1.0.0"

                return {
                    "node_name": node_name,
                    "version": version,
                    "namespace": f"onex.nodes.{node_name}",
                    "state_contract": f"state_contract://{node_name}_contract.yaml",
                }
        except (ValueError, IndexError):
            pass

        # Fallback values
        return {
            "node_name": "unknown_node",
            "version": "1.0.0",
            "namespace": "onex.nodes.unknown_node",
            "state_contract": "state_contract://unknown_node_contract.yaml",
        }

    def _generate_hash(self, content: str) -> str:
        """
        Generate a SHA-256 hash for the content.

        Args:
            content: Content to hash

        Returns:
            64-character hexadecimal hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _resolve_template_placeholders(
        self, data: Dict[str, Any], file_path: Path
    ) -> Dict[str, Any]:
        """
        Resolve template placeholders in the node metadata.

        Args:
            data: Parsed YAML data
            file_path: Path to the file being processed

        Returns:
            Data with resolved placeholders
        """
        node_info = self._infer_node_info_from_path(file_path)
        current_time = datetime.utcnow().isoformat() + "Z"

        # Template placeholder mappings
        replacements = {
            "TEMPLATE-UUID-REPLACE-ME": str(uuid.uuid4()),
            "TEMPLATE_AUTHOR": "OmniNode Team",
            "TEMPLATE_CREATED_AT": current_time,
            "TEMPLATE_LAST_MODIFIED_AT": current_time,
            "TEMPLATE_HASH_TO_BE_COMPUTED": "placeholder_for_hash",  # Will be replaced later
            "template_node": node_info["node_name"],
            "TEMPLATE: Replace with your node description": f"ONEX {node_info['node_name']} for automated processing",
            "omnibase.nodes.template_node": node_info["namespace"],
            "state_contract://template_node_contract.yaml": node_info["state_contract"],
            "template": "active",  # lifecycle
        }

        # Recursively replace placeholders
        def replace_in_data(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: replace_in_data(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_in_data(item) for item in obj]
            elif isinstance(obj, str):
                for placeholder, replacement in replacements.items():
                    if placeholder in obj:
                        obj = obj.replace(placeholder, replacement)
                return obj
            else:
                return obj

        resolved_data = replace_in_data(data)

        # Special handling for specific fields
        if resolved_data.get("name") == "template_node":
            resolved_data["name"] = node_info["node_name"]

        if resolved_data.get("version") == "1.0.0":
            resolved_data["version"] = node_info["version"]

        # Handle tags - replace template tags with appropriate ones
        if "tags" in resolved_data and isinstance(resolved_data["tags"], list):
            new_tags = []
            for tag in resolved_data["tags"]:
                if tag == "REPLACE_WITH_YOUR_TAGS":
                    # Add appropriate tags based on node name
                    if "logger" in node_info["node_name"]:
                        new_tags.extend(["logging", "observability"])
                    elif "registry" in node_info["node_name"]:
                        new_tags.extend(["registry", "configuration"])
                    elif "template" in node_info["node_name"]:
                        new_tags.extend(["file-generation", "jinja2"])
                    else:
                        new_tags.append("utility")
                else:
                    new_tags.append(tag)
            resolved_data["tags"] = new_tags

        return resolved_data  # type: ignore[no-any-return]

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Stamp a node.onex.yaml file with proper metadata.

        Args:
            path: Path to the node.onex.yaml file
            content: Current file content
            **kwargs: Additional arguments (author, etc.)

        Returns:
            OnexResultModel with stamping results
        """
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[START] stamp for {path}",
            node_id=_COMPONENT_NAME,
        )

        try:
            # Parse YAML
            try:
                data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                return OnexResultModel(
                    status=OnexStatus.ERROR,
                    target=str(path),
                    messages=[],
                    metadata={
                        "file_path": str(path),
                        "error": f"Failed to parse YAML: {e}",
                    },
                )

            # Resolve template placeholders
            resolved_data = self._resolve_template_placeholders(data, path)

            # Generate content for hash calculation (without the hash field)
            hash_data = resolved_data.copy()
            hash_data.pop("hash", None)
            hash_content = yaml.dump(
                hash_data, default_flow_style=False, sort_keys=True
            )

            # Generate and set the hash
            resolved_data["hash"] = self._generate_hash(hash_content)

            # Update timestamps
            resolved_data["last_modified_at"] = datetime.utcnow().isoformat() + "Z"

            # Generate the new content
            new_content = "---\n\n" + yaml.dump(
                resolved_data, default_flow_style=False, sort_keys=False
            )

            emit_log_event(
                LogLevelEnum.DEBUG,
                f"[END] stamp for {path} - success",
                node_id=_COMPONENT_NAME,
            )

            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                target=str(path),
                messages=[],
                metadata={
                    "content": new_content,
                    "file_path": str(path),
                    "node_name": resolved_data.get("name"),
                    "version": resolved_data.get("version"),
                    "hash": resolved_data.get("hash"),
                    "note": "Successfully stamped node contract",
                },
            )

        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Exception in stamp for {path}: {e}",
                node_id=_COMPONENT_NAME,
            )
            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=str(path),
                messages=[],
                metadata={
                    "file_path": str(path),
                    "error": f"Failed to stamp node contract: {e}",
                },
            )

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Validate a node.onex.yaml file against the schema.

        Args:
            path: Path to the file to validate
            content: File content to validate
            **kwargs: Additional validation arguments

        Returns:
            OnexResultModel with validation results
        """
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[START] validate for {path}",
            node_id=_COMPONENT_NAME,
        )

        try:
            data = yaml.safe_load(content)

            # Basic validation checks
            required_fields = [
                "schema_version",
                "name",
                "version",
                "uuid",
                "author",
                "created_at",
                "last_modified_at",
                "description",
                "lifecycle",
                "hash",
            ]

            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return OnexResultModel(
                    status=OnexStatus.ERROR,
                    message=f"Missing required fields: {missing_fields}",
                    metadata={"file_path": str(path)},
                )

            # Check for template placeholders
            template_placeholders = [
                "TEMPLATE-UUID-REPLACE-ME",
                "TEMPLATE_AUTHOR",
                "TEMPLATE_CREATED_AT",
                "TEMPLATE_LAST_MODIFIED_AT",
                "TEMPLATE_HASH_TO_BE_COMPUTED",
            ]

            found_placeholders = []

            def check_placeholders(obj: Any, path_str: str = "") -> None:
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        check_placeholders(v, f"{path_str}.{k}" if path_str else k)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        check_placeholders(item, f"{path_str}[{i}]")
                elif isinstance(obj, str):
                    for placeholder in template_placeholders:
                        if placeholder in obj:
                            found_placeholders.append(f"{path_str}: {placeholder}")

            check_placeholders(data)

            if found_placeholders:
                emit_log_event(
                    LogLevelEnum.WARNING,
                    f"Found template placeholders in {path}: {found_placeholders}",
                    node_id=_COMPONENT_NAME,
                )
                return OnexResultModel(
                    status=OnexStatus.WARNING,
                    message=f"Found template placeholders: {found_placeholders}",
                    metadata={"file_path": str(path), "needs_stamping": True},
                )

            emit_log_event(
                LogLevelEnum.DEBUG,
                f"[END] validate for {path} - success",
                node_id=_COMPONENT_NAME,
            )

            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                message="Node contract validation passed",
                metadata={"file_path": str(path)},
            )

        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Exception in validate for {path}: {e}",
                node_id=_COMPONENT_NAME,
            )
            return OnexResultModel(
                status=OnexStatus.ERROR,
                message=f"Validation failed: {e}",
                metadata={"file_path": str(path)},
            )

    def extract_block(self, path: Path, content: str) -> tuple[Optional[Any], str]:
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
        # Node contract files don't have extractable ONEX metadata blocks
        return None, content

    def serialize_block(self, meta: Any) -> str:
        """
        Serialize metadata block for node.onex.yaml file.

        For node.onex.yaml files, we don't use traditional ONEX metadata blocks,
        so this returns an empty string.

        Args:
            meta: Metadata to serialize

        Returns:
            Serialized metadata block (empty for node contract files)
        """
        # Node contract files don't use serialized metadata blocks
        return ""

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        """
        Optional pre-validation before stamping.

        Args:
            path: Path to the file
            content: File content
            **kwargs: Additional arguments

        Returns:
            OnexResultModel if validation fails, None if validation passes
        """
        # No pre-validation needed for node contract files
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        """
        Optional post-validation after stamping.

        Args:
            path: Path to the file
            content: File content
            **kwargs: Additional arguments

        Returns:
            OnexResultModel if validation fails, None if validation passes
        """
        # No post-validation needed for node contract files
        return None
