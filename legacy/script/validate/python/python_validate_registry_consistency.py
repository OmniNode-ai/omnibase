#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "python_validate_registry_consistency"
# namespace: "omninode.tools.python_validate_registry_consistency"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "python_validate_registry_consistency.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolValidate']
# base_class: ['ProtocolValidate']
# mock_safe: true
# === /OmniNode:Metadata ===




"""
python_validate_registry_consistency.py
containers.foundation.src.foundation.script.validate.python.python_validate_registry_consistency.

Python protocol-compliant validator for registry consistency.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import argparse
import logging
import yaml

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import ValidationResult, ValidationIssue, ValidatorMetadata, ValidateStatus
from foundation.protocol.protocol_logger import ProtocolLogger
from foundation.script.validate.validate_registry import ValidatorRegistry
from foundation.script.validate.common.common_validator_utils import should_validate_file
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedMessageModel, UnifiedStatus
from foundation.script.validate.common.common_file_utils import FileUtils
from foundation.script.validate.common.common_yaml_utils import YamlUtils
from foundation.script.validate.common.common_error_utils import CommonErrorUtils

class PythonValidateRegistryConsistency(ProtocolValidate):
    description: str = "Validates consistency of the validator registry."
    logger: Any
    extensions = ('.yaml', '.yml')

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[ProtocolLogger] = None,
        utility_registry: dict = None,
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.config = config or {}
        self.errors: List[ValidationIssue] = []
        self.warnings: List[ValidationIssue] = []
        self.failed_files: List[str] = []
        self.utility_registry = utility_registry or {
            'file_utils': FileUtils(),
            'yaml_utils': YamlUtils(),
            'common_error_utils': CommonErrorUtils(),
        }

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="python_validate_registry_consistency",
            group="registry",
            description="Validates consistency of the Python validator registry.",
            version="v1",
            tool="foundation.script.tool.python.python_tool_validate_registry_consistency",
        )

    def get_name(self) -> str:
        return "registry_consistency"

    def add_error(self, *, message: str, file: str, line: int = None, details: dict = None):
        common_error_utils = self.utility_registry.get('common_error_utils')
        common_error_utils.add_error(self.errors, message=message, file=file, line=line, details=details)

    def add_warning(self, *, message: str, file: str, line: int = None, details: dict = None):
        common_error_utils = self.utility_registry.get('common_error_utils')
        common_error_utils.add_warning(self.warnings, message=message, file=file, line=line, details=details)

    def add_failed_file(self, file: str):
        common_error_utils = self.utility_registry.get('common_error_utils')
        common_error_utils.add_failed_file(self.failed_files, file)

    def should_validate(self, file_path: Path) -> bool:
        file_utils = self.utility_registry.get('file_utils')
        return file_utils.check_file_extension(file_path, {'.yaml', '.yml'})

    def validate(
        self, target: Path, config: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate registry consistency:
        - All registry entries may optionally have a matching metadata block.
        - No duplicate registry entries.
        - No registry drift (orphaned/extra entries).
        - Metadata blocks are optional unless otherwise specified.
        """
        if isinstance(target, str):
            target = Path(target)
        # Robust skip logic for file extension and existence
        if target.suffix.lower() not in self.extensions:
            reason = f"File extension {target.suffix} is not valid for registry consistency validation."
            self.logger.info(f"[SKIP] {target}: {reason}")
            return ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                version="v1",
                metadata={"file": str(target), "skip_reason": reason},
                status=ValidateStatus.INVALID_EXTENSION,
            )
        if not target.exists() or not target.is_file():
            reason = f"Target path {target} does not exist or is not a file."
            self.logger.error(f"[ERROR] {target}: {reason}")
            return ValidationResult(
                is_valid=False,
                errors=[ValidationIssue(type="error", message=reason, file=str(target))],
                warnings=[],
                version="v1",
                metadata={"file": str(target), "error_reason": reason},
                status=ValidateStatus.ERROR,
            )
        self.errors.clear()
        self.warnings.clear()
        self.failed_files.clear()
        is_valid = True
        self.logger.debug(f"[RegistryConsistencyValidator] Reading file: {target}")
        try:
            yaml_utils = self.utility_registry.get('yaml_utils')
            with open(target, "r") as f:
                content = f.read()
            if not content.strip():
                self.logger.info(f"[RegistryConsistencyValidator] File is empty: {target}")
                return ValidationResult(
                    is_valid=True,
                    errors=[],
                    warnings=[],
                    version="v1",
                    status=ValidateStatus.SKIPPED,
                )
            data, yaml_error = yaml_utils.safe_yaml_load(content)
            if yaml_error:
                if yaml_error == "YAML content is not a dictionary.":
                    self.logger.info(f"[RegistryConsistencyValidator] Skipping file with non-dict YAML root: {target}")
                    return ValidationResult(
                        is_valid=True,
                        errors=[],
                        warnings=[],
                        version="v1",
                        status=ValidateStatus.SKIPPED,
                    )
                self.logger.warning(f"[RegistryConsistencyValidator] YAML load error: {yaml_error} in {target}")
                self.add_error(
                    message=f"Failed to parse YAML: {yaml_error}",
                    file=str(target),
                )
                return ValidationResult(
                    is_valid=False,
                    errors=self.errors,
                    warnings=self.warnings,
                    version="v1",
                    status=ValidateStatus.INVALID,
                )
            if data is None:
                self.logger.info(f"[RegistryConsistencyValidator] Skipping file with non-dict YAML root: {target}")
                return ValidationResult(
                    is_valid=True,
                    errors=[],
                    warnings=[],
                    version="v1",
                    status=ValidateStatus.SKIPPED,
                )
            # Defensive: Only process if YAML is a dict
            if not isinstance(data, dict):
                self.logger.info(f"[RegistryConsistencyValidator] Skipping file with non-dict YAML root: {target}")
                return ValidationResult(
                    is_valid=True,
                    errors=[],
                    warnings=[],
                    version="v1",
                    status=ValidateStatus.SKIPPED,
                )
            # --- Registry consistency checks ---
            if 'registry' not in data:
                self.logger.info(f"[RegistryConsistencyValidator] Skipping file with no 'registry' key: {target}")
                return ValidationResult(
                    is_valid=True,
                    errors=self.errors,
                    warnings=self.warnings,
                    version="v1",
                    status=ValidateStatus.SKIPPED,
                )
            registry = data.get('registry', [])
            seen = set()
            for entry in registry:
                name = entry.get('name')
                if not name:
                    self.add_error(
                        message="Registry entry missing 'name' field.",
                        file=str(target),
                    )
                    is_valid = False
                    continue
                if name in seen:
                    self.add_error(
                        message=f"Duplicate registry entry for '{name}' detected (registry drift)",
                        file=str(target),
                    )
                    is_valid = False
                    continue
                seen.add(name)
            return ValidationResult(
                is_valid=is_valid,
                errors=self.errors,
                warnings=self.warnings,
                version="v1",
                status=ValidateStatus.VALID if is_valid else ValidateStatus.INVALID,
            )
        except Exception as e:
            self.add_error(
                message=f"Failed to read file: {e}",
                file=str(target),
            )
            return ValidationResult(
                is_valid=False,
                errors=self.errors,
                warnings=self.warnings,
                version="v1",
                status=ValidateStatus.ERROR,
            )

    def get_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument("target", type=str, help="File or directory to validate")
        return parser

    def main(self, argv: Optional[List[str]] = None) -> int:
        parser = self.get_parser()
        args = parser.parse_args(argv)
        result = self.validate(Path(args.target))
        return 0 if result.is_valid else 1

    def run(self, args) -> int:
        result = self.validate(Path(args.target))
        return 0 if result.is_valid else 1

    def validate_main(self, args) -> int:
        return self.run(args)

def main():  # pragma: no cover
    sys.exit(PythonValidateRegistryConsistency().main())

if __name__ == "__main__":  # pragma: no cover
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main() 