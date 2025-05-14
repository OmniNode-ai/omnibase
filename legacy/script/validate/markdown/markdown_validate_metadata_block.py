# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "markdown_validate_metadata_block"
# namespace: "omninode.tools.markdown_validate_metadata_block"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T22:11:58+00:00"
# last_modified_at: "2025-05-05T22:11:58+00:00"
# entrypoint: "markdown_validate_metadata_block.py"
# protocols_supported:
#   - "["O.N.E. v0.1"]"
# protocol_class:
#   - '['ProtocolValidateMetadataBlock']'
# base_class:
#   - '['ProtocolValidateMetadataBlock']'
# mock_safe: true
# === /OmniNode:Metadata ===

"""
MarkdownValidateMetadataBlock: Markdown-specific metadata block validator implementing ProtocolValidateMetadataBlock.

This validator enforces metadata block compliance for Markdown files, including:
- Required fields presence and format
- Protocol compliance
- Type safety
- Runtime protocol checking
"""
from typing import Any, Dict, List, Optional, cast
from pathlib import Path
import re
from foundation.protocol.protocol_validate_metadata_block import ProtocolValidateMetadataBlock
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedMessageModel, UnifiedStatus
from foundation.script.validate.common.common_json_utils import safe_json_dumps
from foundation.util.util_metadata_block_extractor_registry import get_extractor
from foundation.protocol.protocol_stubs import ProtocolValidateMetadataBlock as ProtocolStub
from foundation.model.model_metadata import MetadataBlockModel

class MarkdownValidateMetadataBlock(ProtocolValidateMetadataBlock):
    """Markdown-specific metadata block validator implementing ProtocolValidateMetadataBlock."""
    
    def __init__(self, logger: Optional[Any] = None, config: Optional[Dict[str, Any]] = None, utility_registry: Any = None) -> None:
        """Initialize the validator with optional logger, config, and utility registry.
        
        Args:
            logger: Optional logger instance
            config: Optional configuration dictionary
            utility_registry: Optional utility registry for file, YAML, and JSON utilities
        """
        self.logger = logger
        self.config = config or {}
        self.messages: List[UnifiedMessageModel] = []
        self.failed_files: List[str] = []
        self.utility_registry = utility_registry
        # Runtime protocol check
        if not isinstance(self, ProtocolStub):
            raise TypeError(f"{self.__class__.__name__} must implement ProtocolValidateMetadataBlock")

    def get_name(self) -> str:
        """Get the validator name.
        
        Returns:
            str: The validator name
        """
        return "markdown_metadata_block"

    def validate(self, target: Path, config: Optional[Dict[str, Any]] = None) -> UnifiedResultModel:
        """Validate the metadata block in the target file.
        
        Args:
            target: Path to the file to validate
            config: Optional configuration dictionary
            
        Returns:
            UnifiedResultModel: Validation result with messages and status
            
        Raises:
            RuntimeError: If required utilities are missing
        """
        # Always convert target to Path
        if not isinstance(target, Path):
            target = Path(target)
            
        # Get utilities from registry
        file_utils = self.utility_registry.get('file_utils')
        yaml_utils = self.utility_registry.get('yaml_utils')
        json_utils = self.utility_registry.get('json_utils')
        
        if file_utils is None or yaml_utils is None or json_utils is None:
            raise RuntimeError(
                "utility_registry missing required utilities: file_utils, yaml_utils, or json_utils. "
                "Ensure common_file_utils.py, common_yaml_utils.py, and common_json_utils.py are imported before use."
            )
            
        # Validate file extension
        valid_exts = {'.md', '.markdown'}
        self.messages.clear()
        if not file_utils.check_file_extension(target, valid_exts):
            return UnifiedResultModel(messages=[], status=UnifiedStatus.skipped)
            
        # Check file existence
        if not file_utils.file_exists(target):
            return UnifiedResultModel(
                messages=[UnifiedMessageModel(
                    summary="File does not exist.",
                    level="error",
                    file=str(target),
                    severity="error",
                    type="error"
                )],
                status=UnifiedStatus.error
            )
            
        # Extract and validate metadata block
        with open(target, "r") as f:
            lines = f.readlines()
        extractor = get_extractor('markdown')
        block_str = extractor.extract_block(lines) if extractor else None
        
        if not block_str:
            self.messages.append(UnifiedMessageModel(
                summary="No metadata block found.",
                level="error",
                file=str(target),
                severity="error",
                type="error"
            ))
            return UnifiedResultModel(messages=self.messages, status=UnifiedStatus.error)
            
        # Parse YAML
        meta_dict, yaml_error = yaml_utils.safe_yaml_load(block_str)
        if yaml_error:
            details_str = json_utils['safe_json_dumps']({"block_str": block_str}, self.utility_registry) if json_utils else str({"block_str": block_str})
            self.messages.append(UnifiedMessageModel(
                summary=f"YAML load error in metadata block: {yaml_error}",
                file=str(target),
                level="error",
                severity="error",
                type="error",
                details=details_str
            ))
            return UnifiedResultModel(messages=self.messages, status=UnifiedStatus.error)
            
        # Validate required fields
        REQUIRED_FIELDS = [
            "metadata_version",
            "name",
            "namespace",
            "version",
            "entrypoint",
            "protocols_supported",
            "owner",
            "type",  # Added type as a required field
        ]
        
        if not isinstance(meta_dict, dict):
            self.messages.append(UnifiedMessageModel(
                summary="Metadata block is not a dictionary.",
                level="error",
                file=str(target),
                severity="error",
                type="error"
            ))
            return UnifiedResultModel(messages=self.messages, status=UnifiedStatus.error)
            
        # Check for commented out fields
        block_lines = block_str.splitlines()
        commented_fields = []
        for field in REQUIRED_FIELDS:
            comment_pattern = f"# {field}:"
            if any(line.strip().startswith(comment_pattern) for line in block_lines):
                commented_fields.append(field)
                
        missing_fields = [f for f in REQUIRED_FIELDS if f not in meta_dict]
        if commented_fields:
            self.messages.append(UnifiedMessageModel(
                summary=f"Metadata block validation error: required fields present only as comments: {', '.join(commented_fields)}",
                level="error",
                file=str(target),
                severity="error",
                type="error"
            ))
            return UnifiedResultModel(messages=self.messages, status=UnifiedStatus.error)
            
        if missing_fields:
            self.messages.append(UnifiedMessageModel(
                summary=f"Metadata block validation error: missing fields: {', '.join(missing_fields)}",
                level="error",
                file=str(target),
                severity="error",
                type="error"
            ))
            return UnifiedResultModel(messages=self.messages, status=UnifiedStatus.error)
            
        return UnifiedResultModel(messages=self.messages, status=UnifiedStatus.success)

    def validate_main(self, args: Any) -> int:
        """CLI entrypoint for validation.
        
        Args:
            args: Command line arguments
            
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        result = self.validate(Path(args.target))
        return 0 if result.status == UnifiedStatus.success else 1

    @classmethod
    def metadata(cls) -> MetadataBlockModel:
        """Get validator metadata.
        
        Returns:
            MetadataBlockModel: Metadata describing the validator
        """
        return MetadataBlockModel(
            metadata_version="0.1",
            name="markdown_validate_metadata_block",
            namespace="omninode.tools.markdown_validate_metadata_block",
            version="1.0.0",
            entrypoint="markdown_validate_metadata_block.py",
            protocols_supported=["O.N.E. v0.1"],
            protocol_version="0.1.0",
            author="OmniNode Team",
            owner="jonah@omninode.ai",
            copyright="Copyright (c) 2025 OmniNode.ai",
            created_at="2025-05-07T12:00:00Z",
            last_modified_at="2025-05-07T12:00:00Z"
        ) 