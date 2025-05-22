# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: cli_validate.py
# version: 1.0.0
# uuid: 70e9c7b3-9084-4a4d-8f69-101160b8e6c8
# author: OmniNode Team
# created_at: 2025-05-22T14:05:21.448567
# last_modified_at: 2025-05-22T20:50:39.721457
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: f1cc5426ed9c0524fd5166fd19cf224ae714d534f2f2d152eee11ae38321b238
# entrypoint: python@cli_validate.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.cli_validate
# meta_type: tool
# === /OmniNode:Metadata ===


import argparse
import logging
from pathlib import Path
from typing import Any, List, Optional

import typer

from omnibase.core.errors import OmniBaseError
from omnibase.model.model_enum_log_level import LogLevelEnum, SeverityLevelEnum
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_message_result import (
    OnexMessageModel,
    OnexResultModel,
    OnexStatus,
)
from omnibase.model.model_result_cli import ModelResultCLI
from omnibase.model.model_schema import SchemaModel
from omnibase.model.model_validate_error import (
    ValidateMessageModel,
    ValidateResultModel,
)
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader
from omnibase.runtime.protocol.protocol_validate import ProtocolValidate

app = typer.Typer(name="validate", help="Validate ONEX node metadata files")
logger = logging.getLogger(__name__)


class CLIValidator(ProtocolValidate):
    """
    Validator for ONEX node metadata files.
    Implements ProtocolValidate for CLI-based validation.

    This class follows the protocol-based interface design pattern and properly
    accepts dependencies through constructor injection rather than instantiating them.
    """

    description: str = "ONEX CLI Validator"
    logger: Any = logger

    def __init__(self, schema_loader: ProtocolSchemaLoader):
        """
        Initialize the validator with injected dependencies.

        Args:
            schema_loader: A ProtocolSchemaLoader implementation for loading and validating schemas
        """
        self.schema_loader = schema_loader
        self.last_validation_errors: List[ValidateMessageModel] = []

    def validate_main(self, args: object) -> OnexResultModel:
        """Entry point for the CLI command."""
        try:
            # Safely extract path and config from args
            path = None
            config = None
            if hasattr(args, "path"):
                path = getattr(args, "path", None)
            elif isinstance(args, (list, tuple)) and len(args) > 0:
                path = args[0]
            if hasattr(args, "config"):
                config = getattr(args, "config", None)
            # Defensive: if still None, error
            if not path:
                return OnexResultModel(
                    status=OnexStatus.ERROR,
                    target=None,
                    messages=[
                        OnexMessageModel(
                            summary="No path provided",
                            level=LogLevelEnum.ERROR,
                            file=None,
                            line=None,
                            details=None,
                            code=None,
                            context=None,
                            timestamp=None,
                            type=None,
                        )
                    ],
                    summary=None,
                )

            result = self.validate(path, config)
            return OnexResultModel(
                status=result.status,
                target=path,
                messages=[
                    OnexMessageModel(
                        summary=msg.message,
                        level=severity_to_log_level(msg.severity),
                        file=msg.file,
                        line=msg.line,
                        details=None,
                        code=msg.code,
                        context=msg.context,
                        timestamp=None,
                        type=None,
                    )
                    for msg in result.messages
                ],
                summary=None,  # Use None or construct UnifiedSummaryModel if available
            )
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=None,
                messages=[
                    OnexMessageModel(
                        summary=f"Error during validation: {str(e)}",
                        level=LogLevelEnum.ERROR,
                        file=None,
                        line=None,
                        details=None,
                        code=None,
                        context=None,
                        timestamp=None,
                        type=None,
                    )
                ],
            )

    def validate(
        self, target: str, config: Optional[str] = None
    ) -> ValidateResultModel:
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
                ValidateMessageModel(
                    message=f"Error validating {target}: {str(e)}",
                    severity=SeverityLevelEnum.ERROR,
                )
            )
            return ValidateResultModel(
                messages=self.last_validation_errors,
                status=OnexStatus.ERROR,
                summary=f"Error validating {target}: {str(e)}",
            )

    def _validate_file(
        self, file_path: Path, config: Optional[str] = None
    ) -> ValidateResultModel:
        """
        Validate a single file.
        For M0, this is a stub that loads the file and returns success.
        """
        try:
            # M0: Simple stub implementation that just checks if file exists and has expected extension
            if file_path.suffix not in [".yaml", ".yml", ".json"]:
                self.last_validation_errors.append(
                    ValidateMessageModel(
                        message=f"Unsupported file type: {file_path.suffix}",
                        severity=SeverityLevelEnum.ERROR,
                        file=str(file_path),
                    )
                )
                return ValidateResultModel(
                    messages=self.last_validation_errors,
                    status=OnexStatus.ERROR,
                    summary=f"Unsupported file type: {file_path.suffix}",
                )

            # TODO: M1+ Add real validation using schema loader and core metadata validation logic
            # TODO: Check for required fields in the ONEX metadata
            # TODO: Validate against schemas using jsonschema library

            # For M0, just load the file to see if it parses correctly
            try:
                if file_path.suffix in [".yaml", ".yml"]:
                    self.schema_loader.load_onex_yaml(file_path)
                else:
                    self.schema_loader.load_json_schema(file_path)

                self.last_validation_errors.append(
                    ValidateMessageModel(
                        message=f"File parsed successfully: {file_path}",
                        severity=SeverityLevelEnum.SUCCESS,
                        file=str(file_path),
                    )
                )
                return ValidateResultModel(
                    messages=self.last_validation_errors,
                    status=OnexStatus.SUCCESS,
                    summary=f"Successfully validated {file_path}",
                )
            except OmniBaseError as e:
                self.last_validation_errors.append(
                    ValidateMessageModel(
                        message=f"Error parsing file: {str(e)}",
                        severity=SeverityLevelEnum.ERROR,
                        file=str(file_path),
                    )
                )
                return ValidateResultModel(
                    messages=self.last_validation_errors,
                    status=OnexStatus.ERROR,
                    summary=f"Error parsing file: {file_path}",
                )
        except Exception as e:
            self.last_validation_errors.append(
                ValidateMessageModel(
                    message=f"Unexpected error validating file: {str(e)}",
                    severity=SeverityLevelEnum.ERROR,
                    file=str(file_path),
                )
            )
            return ValidateResultModel(
                messages=self.last_validation_errors,
                status=OnexStatus.ERROR,
                summary=f"Unexpected error: {str(e)}",
            )

    def _validate_directory(
        self, dir_path: Path, config: Optional[str] = None
    ) -> ValidateResultModel:
        """
        Validate all files in a directory.
        For M0, this is a stub that returns success with no validation.
        """
        # TODO: M1+ Implement directory validation logic
        self.last_validation_errors.append(
            ValidateMessageModel(
                message=f"Directory validation not yet implemented for M0: {dir_path}",
                severity=SeverityLevelEnum.WARNING,
            )
        )
        return ValidateResultModel(
            messages=self.last_validation_errors,
            status=OnexStatus.WARNING,
            summary=f"Directory validation not yet implemented for M0: {dir_path}",
        )

    def _error_result(self, message: str) -> ValidateResultModel:
        """Helper to create error results."""
        self.last_validation_errors.append(
            ValidateMessageModel(message=message, severity=SeverityLevelEnum.ERROR)
        )
        return ValidateResultModel(
            messages=self.last_validation_errors,
            status=OnexStatus.ERROR,
            summary=message,
        )

    def get_name(self) -> str:
        """Get the name of this validator."""
        return "onex-validate"

    def get_validation_errors(self) -> List[ValidateMessageModel]:
        """Get detailed validation errors from the last validation."""
        return self.last_validation_errors

    def discover_plugins(self) -> List[NodeMetadataBlock]:
        """
        Returns a list of plugin metadata blocks supported by this validator.
        Enables dynamic test/validator scaffolding and runtime plugin contract enforcement.
        Compliant with ONEX execution model and Cursor Rule.
        See ONEX protocol spec and Cursor Rule for required fields and extension policy.
        """
        # M0: Return a stub node metadata block for demonstration
        stub_node = NodeMetadataBlock(
            metadata_version="0.0.1",
            protocol_version="0.0.1",
            owner="OmniNode Team",
            copyright="Copyright OmniNode",
            schema_version="0.0.1",
            name="Stub Plugin",
            version="0.0.1",
            uuid="00000000-0000-0000-0000-000000000000",
            author="OmniNode Team",
            created_at="2024-01-01T00:00:00Z",
            last_modified_at="2024-01-01T00:00:00Z",
            description="Stub plugin for demonstration",
            state_contract="stub://contract",
            lifecycle=Lifecycle.DRAFT,
            hash="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            entrypoint=EntrypointBlock(
                type=EntrypointType.PYTHON, target="src/omnibase/tools/stub.py"
            ),
            namespace="omninode.stub",
            meta_type=MetaType.PLUGIN,
        )
        return [stub_node]

    def describe_flags(self, format: str = "json") -> Any:
        """
        ProtocolCLI: Return a structured description of all CLI flags.
        # TODO: Implement flag description logic (protocol compliance)
        """
        raise NotImplementedError(
            "describe_flags is not yet implemented (protocol compliance)"
        )

    def get_parser(self) -> argparse.ArgumentParser:
        """
        ProtocolCLI: Return an argument parser for the CLI.
        # TODO: Implement argument parser for CLIValidator (protocol compliance)
        """
        raise NotImplementedError(
            "get_parser is not yet implemented (protocol compliance)"
        )

    def main(self, argv: Optional[List[str]] = None) -> ModelResultCLI:
        """
        ProtocolCLI: Main entrypoint for CLI execution.
        # TODO: Implement main CLI logic (protocol compliance)
        """
        raise NotImplementedError("main is not yet implemented (protocol compliance)")

    def run(self, args: List[str]) -> ModelResultCLI:
        """
        ProtocolCLI: Run the CLI with the given arguments.
        # TODO: Implement run logic for CLIValidator (protocol compliance)
        """
        raise NotImplementedError("run is not yet implemented (protocol compliance)")


@app.command()
def validate(
    path: str = typer.Argument(..., help="Path to file or directory to validate"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    config: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format (text, json, github)"
    ),
) -> int:
    """
    Validate ONEX node metadata files.
    """

    # Initialize with dependency - in future this would come from a DI container
    from pathlib import Path

    from omnibase.model.model_node_metadata import NodeMetadataBlock

    class DummySchemaLoader(ProtocolSchemaLoader):
        def load_onex_yaml(self, path: Path) -> NodeMetadataBlock:
            return NodeMetadataBlock.model_validate({})

        def load_json_schema(self, path: Path) -> SchemaModel:
            return SchemaModel(schema_uri=None)

        def load_schema_for_node(self, node: NodeMetadataBlock) -> dict[str, Any]:
            return {}

    class DummyCLIValidator(CLIValidator):
        def validate_node(self, node: NodeMetadataBlock) -> Any:
            return None

    loader = DummySchemaLoader()
    validator = DummyCLIValidator(loader)
    validator.description = "ONEX CLI Validator"  # Ensure attribute is set

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
            prefix = (
                "[ERROR]"
                if msg.severity == "error"
                else "[WARNING]" if msg.severity == "warning" else "[INFO]"
            )
            file_info = f" {msg.file}:{msg.line}" if msg.file else ""
            typer.echo(f"{prefix}{file_info} {msg.message}")

    # Return exit code based on status
    return 1 if result.status == OnexStatus.ERROR else 0


# Helper function to map SeverityLevelEnum to LogLevelEnum
def severity_to_log_level(severity: SeverityLevelEnum) -> LogLevelEnum:
    mapping = {
        SeverityLevelEnum.ERROR: LogLevelEnum.ERROR,
        SeverityLevelEnum.WARNING: LogLevelEnum.WARNING,
        SeverityLevelEnum.INFO: LogLevelEnum.INFO,
        SeverityLevelEnum.DEBUG: LogLevelEnum.DEBUG,
        SeverityLevelEnum.CRITICAL: LogLevelEnum.CRITICAL,
    }
    return mapping.get(severity, LogLevelEnum.ERROR)


if __name__ == "__main__":
    app()
