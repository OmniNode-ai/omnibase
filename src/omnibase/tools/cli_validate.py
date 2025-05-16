# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "cli_validate"
# namespace: "omnibase.tools.cli_validate"
# meta_type: "tool"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-19T18:30:00+00:00"
# last_modified_at: "2025-05-19T18:30:00+00:00"
# entrypoint: "cli_validate.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolValidate']
# base_class: ['ProtocolValidate']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import typer
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from omnibase.protocol.protocol_validate import ProtocolValidate
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader
from omnibase.model.model_validate_error import ValidateResultModel, ValidateMessageModel
from omnibase.model.model_unified_result import OnexResultModel, OnexStatus
from omnibase.schema.loader import SchemaLoader
from omnibase.core.errors import OmniBaseError
from omnibase.model.model_node_metadata import NodeMetadataBlock

app = typer.Typer(name="validate", help="Validate ONEX node metadata files")
logger = logging.getLogger(__name__)

class CLIValidator(ProtocolValidate):
    """
    Validator for ONEX node metadata files.
    Implements ProtocolValidate for CLI-based validation.
    
    This class follows the protocol-based interface design pattern and properly
    accepts dependencies through constructor injection rather than instantiating them.
    """
    
    def __init__(self, schema_loader: ProtocolSchemaLoader):
        """
        Initialize the validator with injected dependencies.
        
        Args:
            schema_loader: A ProtocolSchemaLoader implementation for loading and validating schemas
        """
        self.schema_loader = schema_loader
        self.last_validation_errors: List[ValidateMessageModel] = []
    
    def validate_main(self, args) -> OnexResultModel:
        """
        Entry point for the CLI command.
        """
        try:
            path = args.path or args[0] if args and len(args) > 0 else None
            config = args.config if hasattr(args, "config") else None
            
            if not path:
                return OnexResultModel(
                    status=OnexStatus.error,
                    messages=[ValidateMessageModel(message="No path provided", severity="error")]
                )
            
            result = self.validate(path, config)
            return OnexResultModel(
                status=result.status,
                target=path,
                messages=[msg.dict() for msg in result.messages],
                summary={
                    "total": len(result.messages),
                    "passed": sum(1 for msg in result.messages if msg.severity == "success"),
                    "failed": sum(1 for msg in result.messages if msg.severity == "error"),
                    "warnings": sum(1 for msg in result.messages if msg.severity == "warning"),
                    "skipped": 0
                } if result.messages else None
            )
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.error,
                messages=[ValidateMessageModel(message=f"Error during validation: {str(e)}", severity="error")]
            )
    
    def validate(self, target, config=None) -> ValidateResultModel:
        """
        Validate a target file or directory.
        """
        try:
            self.last_validation_errors = []
            target_path = Path(target)
            
            if not target_path.exists():
                return self._error_result(f"Path does not exist: {target}")
            
            if target_path.is_file():
                return self._validate_file(target_path, config)
            elif target_path.is_dir():
                return self._validate_directory(target_path, config)
            else:
                return self._error_result(f"Path is not a file or directory: {target}")
        except Exception as e:
            self.last_validation_errors.append(
                ValidateMessageModel(message=f"Error validating {target}: {str(e)}", severity="error")
            )
            return ValidateResultModel(
                messages=self.last_validation_errors,
                status=OnexStatus.error,
                summary=f"Error validating {target}: {str(e)}"
            )
    
    def _validate_file(self, file_path: Path, config=None) -> ValidateResultModel:
        """
        Validate a single file.
        For M0, this is a stub that loads the file and returns success.
        """
        try:
            # M0: Simple stub implementation that just checks if file exists and has expected extension
            if not file_path.suffix in ['.yaml', '.yml', '.json']:
                self.last_validation_errors.append(
                    ValidateMessageModel(
                        message=f"Unsupported file type: {file_path.suffix}",
                        severity="error",
                        file=str(file_path)
                    )
                )
                return ValidateResultModel(
                    messages=self.last_validation_errors,
                    status=OnexStatus.error,
                    summary=f"Unsupported file type: {file_path.suffix}"
                )
            
            # TODO: M1+ Add real validation using schema loader and core metadata validation logic
            # TODO: Check for required fields in the ONEX metadata
            # TODO: Validate against schemas using jsonschema library
            
            # For M0, just load the file to see if it parses correctly
            try:
                if file_path.suffix in ['.yaml', '.yml']:
                    self.schema_loader.load_onex_yaml(file_path)
                else:
                    self.schema_loader.load_json_schema(file_path)
                    
                self.last_validation_errors.append(
                    ValidateMessageModel(
                        message=f"File parsed successfully: {file_path}",
                        severity="success",
                        file=str(file_path)
                    )
                )
                return ValidateResultModel(
                    messages=self.last_validation_errors,
                    status=OnexStatus.success,
                    summary=f"Successfully validated {file_path}"
                )
            except OmniBaseError as e:
                self.last_validation_errors.append(
                    ValidateMessageModel(
                        message=f"Error parsing file: {str(e)}",
                        severity="error",
                        file=str(file_path)
                    )
                )
                return ValidateResultModel(
                    messages=self.last_validation_errors,
                    status=OnexStatus.error,
                    summary=f"Error parsing file: {file_path}"
                )
        except Exception as e:
            self.last_validation_errors.append(
                ValidateMessageModel(
                    message=f"Unexpected error validating file: {str(e)}",
                    severity="error",
                    file=str(file_path)
                )
            )
            return ValidateResultModel(
                messages=self.last_validation_errors,
                status=OnexStatus.error,
                summary=f"Unexpected error: {str(e)}"
            )
    
    def _validate_directory(self, dir_path: Path, config=None) -> ValidateResultModel:
        """
        Validate all files in a directory.
        For M0, this is a stub that returns success with no validation.
        """
        # TODO: M1+ Implement directory validation logic
        self.last_validation_errors.append(
            ValidateMessageModel(
                message=f"Directory validation not yet implemented for M0: {dir_path}",
                severity="warning"
            )
        )
        return ValidateResultModel(
            messages=self.last_validation_errors,
            status=OnexStatus.warning,
            summary=f"Directory validation not yet implemented for M0: {dir_path}"
        )
    
    def _error_result(self, message: str) -> ValidateResultModel:
        """Helper to create error results."""
        self.last_validation_errors.append(
            ValidateMessageModel(message=message, severity="error")
        )
        return ValidateResultModel(
            messages=self.last_validation_errors,
            status=OnexStatus.error,
            summary=message
        )
    
    def get_name(self) -> str:
        """Get the name of this validator."""
        return "onex-validate"
    
    def get_validation_errors(self) -> List[ValidateMessageModel]:
        """Get detailed validation errors from the last validation."""
        return self.last_validation_errors

    def discover_plugins(self) -> list[NodeMetadataBlock]:
        """
        Returns a list of plugin metadata blocks supported by this validator.
        Enables dynamic test/validator scaffolding and runtime plugin contract enforcement.
        Compliant with ONEX execution model and Cursor Rule.
        See ONEX protocol spec and Cursor Rule for required fields and extension policy.
        """
        # M0: Return a stub node metadata block for demonstration
        stub_node = NodeMetadataBlock(
            node_id="stub_plugin",
            node_type="plugin",
            version_hash="v0.0.1-stub",
            entry_point=None,  # Should be EntrypointBlock, update as needed
            contract_type="custom",
            contract={},
        )
        return [stub_node]

@app.command()
def validate(
    path: str = typer.Argument(..., help="Path to file or directory to validate"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format (text, json, github)")
) -> int:
    """
    Validate ONEX node metadata files.
    """
    # Initialize with dependency - in future this would come from a DI container
    schema_loader = SchemaLoader()
    validator = CLIValidator(schema_loader)
    
    result = validator.validate(path, config)
    
    # Print result based on output format
    if output_format == "json":
        typer.echo(result.to_json())
    elif output_format == "github":
        typer.echo(result.to_ci())
    else:
        # Default text output
        typer.echo(f"Status: {result.status.value}")
        typer.echo(f"Summary: {result.summary}")
        
        for msg in result.messages:
            prefix = "[ERROR]" if msg.severity == "error" else "[WARNING]" if msg.severity == "warning" else "[INFO]"
            file_info = f" {msg.file}:{msg.line}" if msg.file else ""
            typer.echo(f"{prefix}{file_info} {msg.message}")
    
    # Return exit code based on status
    return 1 if result.status == OnexStatus.error else 0

if __name__ == "__main__":
    app() 