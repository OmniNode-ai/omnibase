from typing import Any, Dict, Optional
from pathlib import Path
from foundation.registry.registry_metadata_block_hash import RegistryMetadataBlockHash
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedMessageModel, UnifiedStatus
from foundation.model.model_metadata import MetadataBlockModel
from foundation.protocol.protocol_validate import ProtocolValidate
import yaml
from foundation.util.util_metadata_block_extractor_registry import get_extractor
import os

class ValidateMetadataBlockHashRegistry(ProtocolValidate):
    """
    Validator that enforces the metadata block hash registry.
    Checks that the hash in each file's metadata block matches the registry.
    Implements ProtocolValidate for DI and orchestrator compliance.
    """
    def __init__(self, registry: RegistryMetadataBlockHash, logger: Optional[Any] = None) -> None:
        """
        Initialize the validator with a DI-injected registry and logger.
        """
        self.registry = registry
        self.logger = logger

    def get_name(self) -> str:
        """
        Return the validator name for registry/discovery.
        """
        return "metadata_block_hash_registry"

    def validate(self, target: Path, config: Optional[Dict[str, Any]] = None) -> UnifiedResultModel:
        """
        Validate that the file's metadata block hash matches the registry.
        Args:
            target: Path to the file to validate
            config: Optional configuration dictionary
        Returns:
            UnifiedResultModel: Validation result with messages and status
        """
        messages = []
        if not target.exists() or not target.is_file():
            messages.append(UnifiedMessageModel(
                summary="File does not exist.",
                file=str(target),
                level="error",
                severity="error",
                type="error"
            ))
            if self.logger:
                self.logger.error(f"File does not exist: {target}")
            return UnifiedResultModel(messages=messages, status=UnifiedStatus.error)
        try:
            lines = target.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            messages.append(UnifiedMessageModel(
                summary=f"Failed to read file: {e}",
                file=str(target),
                level="error",
                severity="error",
                type="error"
            ))
            if self.logger:
                self.logger.error(f"Failed to read file {target}: {e}")
            return UnifiedResultModel(messages=messages, status=UnifiedStatus.error)
        # Determine file type for extractor
        ext = target.suffix.lower()
        if ext == ".py":
            language = "python"
        elif ext in {".yaml", ".yml"}:
            language = "yaml"
        elif ext == ".md":
            language = "markdown"
        else:
            language = "python"  # Default to python-style for unknown
        extractor = get_extractor(language)
        if not extractor:
            messages.append(UnifiedMessageModel(
                summary=f"No metadata block extractor found for language: {language}",
                file=str(target),
                level="error",
                severity="error",
                type="error"
            ))
            if self.logger:
                self.logger.error(f"No metadata block extractor found for language: {language} in {target}")
            return UnifiedResultModel(messages=messages, status=UnifiedStatus.error)
        block = extractor.extract_block(lines)
        if not block:
            messages.append(UnifiedMessageModel(
                summary="No metadata block found.",
                file=str(target),
                level="error",
                severity="error",
                type="error"
            ))
            if self.logger:
                self.logger.error(f"No metadata block found in {target}")
            return UnifiedResultModel(messages=messages, status=UnifiedStatus.error)
        # Parse YAML from block
        try:
            meta = yaml.safe_load(block)
        except Exception as e:
            messages.append(UnifiedMessageModel(
                summary=f"YAML parse error in metadata block: {e}",
                file=str(target),
                level="error",
                severity="error",
                type="error"
            ))
            if self.logger:
                self.logger.error(f"YAML parse error in {target}: {e}")
            return UnifiedResultModel(messages=messages, status=UnifiedStatus.error)
        if not isinstance(meta, dict):
            messages.append(UnifiedMessageModel(
                summary="Metadata block is not a dictionary.",
                file=str(target),
                level="error",
                severity="error",
                type="error"
            ))
            if self.logger:
                self.logger.error(f"Metadata block is not a dictionary in {target}")
            return UnifiedResultModel(messages=messages, status=UnifiedStatus.error)
        hash_in_block = meta.get("tree_hash")
        if not hash_in_block:
            messages.append(UnifiedMessageModel(
                summary="No tree_hash found in metadata block.",
                file=str(target),
                level="error",
                severity="error",
                type="error"
            ))
            if self.logger:
                self.logger.error(f"No tree_hash found in metadata block for {target}")
            return UnifiedResultModel(messages=messages, status=UnifiedStatus.error)
        hash_in_registry = self.registry.get(str(target.resolve()))
        if not hash_in_registry:
            messages.append(UnifiedMessageModel(
                summary="No hash found in registry for this file.",
                file=str(target),
                level="error",
                severity="error",
                type="error"
            ))
            if self.logger:
                self.logger.error(f"No hash found in registry for {target}")
            return UnifiedResultModel(messages=messages, status=UnifiedStatus.error)
        if hash_in_block != hash_in_registry:
            messages.append(UnifiedMessageModel(
                summary=f"tree_hash mismatch: block={hash_in_block}, registry={hash_in_registry}",
                file=str(target),
                level="error",
                severity="error",
                type="error"
            ))
            if self.logger:
                self.logger.error(f"tree_hash mismatch for {target}: block={hash_in_block}, registry={hash_in_registry}")
            return UnifiedResultModel(messages=messages, status=UnifiedStatus.error)
        return UnifiedResultModel(messages=messages, status=UnifiedStatus.success)

    def validate_main(self, args: Any) -> int:
        """
        CLI entrypoint for validation.
        Args:
            args: Command line arguments
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        target = Path(args.target)
        result = self.validate(target)
        return 0 if result.status == UnifiedStatus.success else 1

    @classmethod
    def metadata(cls) -> MetadataBlockModel:
        """
        Return the metadata block for registry registration.
        """
        return MetadataBlockModel(
            metadata_version="0.1",
            name="metadata_block_hash_registry",
            namespace="omninode.tools.metadata_block_hash_registry",
            version="1.0.0",
            entrypoint="validate_metadata_block_hash_registry.py",
            protocols_supported=["O.N.E. v0.1"],
            protocol_version="0.1.0",
            author="OmniNode Team",
            owner="jonah@omninode.ai",
            copyright="Copyright (c) 2025 OmniNode.ai",
            created_at="2025-05-13T00:00:00+00:00",
            last_modified_at="2025-05-13T00:00:00+00:00",
            description="Validator for enforcing metadata block hash registry compliance.",
            tags=["metadata", "hash", "registry", "validator"],
            dependencies=[],
            config={}
        ) 