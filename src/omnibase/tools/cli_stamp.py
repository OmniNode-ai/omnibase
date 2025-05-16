import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

import typer
import yaml

from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.model.model_unified_result import (
    OnexResultModel,
    OnexStatus,
    UnifiedMessageModel,
)
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader
from omnibase.protocol.protocol_stamper import ProtocolStamper
from omnibase.schema.loader import SchemaLoader

app = typer.Typer(
    name="stamp", help="Stamp ONEX node metadata files with hashes and signatures"
)
logger = logging.getLogger(__name__)


class CLIStamper(ProtocolStamper):
    """
    Stamper for ONEX node metadata files.
    Implements ProtocolStamper for CLI-based stamping.

    This class follows the protocol-based interface design pattern and properly
    accepts dependencies through constructor injection rather than instantiating them.
    """

    def __init__(self, schema_loader: ProtocolSchemaLoader):
        """
        Initialize the stamper with injected dependencies.

        Args:
            schema_loader: A ProtocolSchemaLoader implementation for loading and validating schemas
        """
        self.schema_loader = schema_loader

    def stamp(self, path: str) -> OnexResultModel:
        """
        Stamp an ONEX metadata file at the given path.
        For M0, this is a stub that computes a hash and returns a fixed result.
        """
        try:
            filepath = Path(path)

            if not filepath.exists():
                return OnexResultModel(
                    status=OnexStatus.error,
                    target=path,
                    messages=[
                        UnifiedMessageModel(
                            summary=f"Path does not exist: {path}", level="error"
                        )
                    ],
                )

            if not filepath.is_file():
                return OnexResultModel(
                    status=OnexStatus.error,
                    target=path,
                    messages=[
                        UnifiedMessageModel(
                            summary=f"Path is not a file: {path}", level="error"
                        )
                    ],
                )

            suffix = filepath.suffix.lower()
            if suffix not in [".yaml", ".yml", ".json"]:
                return OnexResultModel(
                    status=OnexStatus.error,
                    target=path,
                    messages=[
                        UnifiedMessageModel(
                            summary=f"Unsupported file type: {suffix}", level="error"
                        )
                    ],
                )

            # Compute a trace hash for the file (stub for M0)
            trace_hash = self._compute_trace_hash(filepath)

            # TODO: M1+ Add real stamping logic with signatures, timestamps, etc.
            # This is just a stub for M0

            return OnexResultModel(
                status=OnexStatus.success,
                target=path,
                messages=[
                    UnifiedMessageModel(
                        summary=f"Successfully computed trace hash for {path}",
                        level="info",
                        details=f"Trace hash: {trace_hash}",
                    )
                ],
                metadata={
                    "trace_hash": trace_hash,
                    "stamped_at": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.error,
                target=path,
                messages=[
                    UnifiedMessageModel(
                        summary=f"Error stamping file: {str(e)}", level="error"
                    )
                ],
            )

    def stamp_file(
        self,
        path: Path,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
        author: str = "OmniNode Team",
        **kwargs,
    ) -> OnexResultModel:
        """
        Stamp the file with a metadata block, replacing any existing block.
        For M0, this is a stub that returns a fixed result.
        """
        try:
            if not path.exists():
                return OnexResultModel(
                    status=OnexStatus.error,
                    target=str(path),
                    messages=[
                        UnifiedMessageModel(
                            summary=f"Path does not exist: {path}", level="error"
                        )
                    ],
                )

            # For M0, we just compute a trace hash and return success
            # We don't actually modify the file
            trace_hash = self._compute_trace_hash(path)

            # TODO: M1+ Implement template-based stamping
            # - Load the file
            # - Parse the metadata block
            # - Add/update required fields (trace_hash, timestamp, etc.)
            # - Write the file back

            return OnexResultModel(
                status=OnexStatus.success,
                target=str(path),
                messages=[
                    UnifiedMessageModel(
                        summary=f"Simulated stamping for M0: {path}",
                        level="info",
                        details=f"Trace hash: {trace_hash}",
                    )
                ],
                metadata={
                    "trace_hash": trace_hash,
                    "template": template.value,
                    "stamped_at": datetime.now().isoformat(),
                    "author": author,
                },
            )
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.error,
                target=str(path),
                messages=[
                    UnifiedMessageModel(
                        summary=f"Error stamping file: {str(e)}", level="error"
                    )
                ],
            )

    def _compute_trace_hash(self, filepath: Path) -> str:
        """
        Compute a trace hash for a file.
        For M0, this is a simple hash of the file contents.
        """
        try:
            # Load the file
            if filepath.suffix.lower() in [".yaml", ".yml"]:
                with open(filepath, "r") as f:
                    data = yaml.safe_load(f)
            else:
                with open(filepath, "r") as f:
                    data = json.load(f)

            # Serialize the data for hashing
            content = json.dumps(data, sort_keys=True)

            # Compute the hash
            sha256 = hashlib.sha256(content.encode("utf-8"))
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error computing trace hash for {filepath}: {str(e)}")
            return f"error-{str(e)}"


@app.command()
def stamp(
    path: str = typer.Argument(..., help="Path to file to stamp"),
    author: str = typer.Option(
        "OmniNode Team", "--author", "-a", help="Author to include in stamp"
    ),
    template: str = typer.Option(
        "minimal", "--template", "-t", help="Template type (minimal, full, etc.)"
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", "-o", help="Overwrite existing metadata block"
    ),
    repair: bool = typer.Option(
        False, "--repair", "-r", help="Repair malformed metadata block"
    ),
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format (text, json)"
    ),
) -> int:
    """
    Stamp an ONEX node metadata file with a hash and timestamp.
    """
    # Initialize with dependency - in future this would come from a DI container
    schema_loader = SchemaLoader()
    stamper = CLIStamper(schema_loader)

    # Convert template string to enum
    template_type = TemplateTypeEnum.MINIMAL
    if template.upper() in TemplateTypeEnum.__members__:
        template_type = TemplateTypeEnum[template.upper()]

    # Call the stamper
    result = stamper.stamp_file(
        Path(path),
        template=template_type,
        overwrite=overwrite,
        repair=repair,
        author=author,
    )

    # Print result based on output format
    if output_format == "json":
        typer.echo(json.dumps(result.dict(), indent=2))
    else:
        # Default text output
        typer.echo(f"Status: {result.status.value}")
        for msg in result.messages:
            prefix = (
                "[ERROR]"
                if msg.level == "error"
                else "[WARNING]" if msg.level == "warning" else "[INFO]"
            )
            typer.echo(f"{prefix} {msg.summary}")
            if msg.details:
                typer.echo(f"  Details: {msg.details}")

        if result.metadata:
            typer.echo("\nMetadata:")
            for key, value in result.metadata.items():
                typer.echo(f"  {key}: {value}")

    # Return exit code based on status
    return 1 if result.status == OnexStatus.error else 0


if __name__ == "__main__":
    app()
