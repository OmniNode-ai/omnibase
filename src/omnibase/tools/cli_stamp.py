import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any, List, Optional

import typer
from typing_extensions import Annotated

from omnibase.core.core_registry import FileTypeRegistry
from omnibase.model.model_enum_output_format import OutputFormatEnum
from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_onex_message_result import OnexStatus
from omnibase.model.model_schema import SchemaModel
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader
from omnibase.protocol.protocol_stamper_engine import ProtocolStamperEngine
from omnibase.tools.fixture_stamper_engine import FixtureStamperEngine
from omnibase.tools.stamper_engine import StamperEngine
from omnibase.utils.directory_traverser import (
    DirectoryTraverser,
    SchemaExclusionRegistry,
)
from omnibase.utils.real_file_io import RealFileIO

# Configure root logger for DEBUG output
logging.basicConfig(level=logging.DEBUG)

# === OmniNode:Metadata ===
metadata_version = "0.1"
name = "cli_stamp"
namespace = "foundation.tools"
version = "0.1.0"
meta_type = "tool"
entrypoint = "cli_stamp.py"
owner = "foundation-team"
# === /OmniNode:Metadata ===

app = typer.Typer(
    name="stamp",
    help="""
Stamp ONEX node metadata files with hashes and signatures.

Eligible file types by default:
  - Markdown (.md)
  - Python (.py)
  - YAML (.yaml, .yml)
  - JSON (.json)

The stamper will recursively process all files with these extensions unless overridden by --include/--exclude patterns or ignore files.

Schema files (e.g., *_schema.yaml, onex_node.yaml) and files in 'schemas/' or 'schema/' directories are excluded by default.

You can use .onexignore or .stamperignore files to further control which files are ignored.

Examples:
  # Dry run (default: show what would be stamped)
  poetry run python -m omnibase.tools.cli_stamp directory . --recursive

  # Actually write changes
  poetry run python -m omnibase.tools.cli_stamp directory . --recursive --write

  # Stamp only markdown files (dry run)
  poetry run python -m omnibase.tools.cli_stamp directory . --include '**/*.md' --recursive

  # Stamp only YAML files, excluding testdata (write mode)
  poetry run python -m omnibase.tools.cli_stamp directory . --include '**/*.yaml' --exclude 'tests/**' --recursive --write

  # Stamp a single file
  poetry run python -m omnibase.tools.cli_stamp stamp docs/dev_logs/jonah/debug/debug_log_2025_05_18.md --author "jonah"

For more details, see docs/tools/stamper.md.
""",
)
logger = logging.getLogger(__name__)

# Add this after logger is defined
logger.debug(f"Debug: str is {str!r}, type: {type(str)}")


def _json_default(obj: object) -> str:
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def get_engine_from_env_or_flag(
    fixture: Optional[str] = None,
) -> "ProtocolStamperEngine":
    fixture_path = fixture or os.environ.get("STAMPER_FIXTURE_PATH")
    fixture_format = os.environ.get("STAMPER_FIXTURE_FORMAT", "json")
    file_type_registry = FileTypeRegistry()  # Registry-driven file type eligibility
    schema_exclusion_registry = (
        SchemaExclusionRegistry()
    )  # Registry-driven schema exclusion
    if fixture_path:
        return FixtureStamperEngine(Path(fixture_path), fixture_format=fixture_format)

    # Use RealFileIO for CLI mode to ensure real files are accessed
    class DummySchemaLoader(ProtocolSchemaLoader):
        def load_onex_yaml(self, path: Path) -> NodeMetadataBlock:
            return NodeMetadataBlock.model_validate({})

        def load_json_schema(self, path: Path) -> SchemaModel:
            return SchemaModel(schema_uri=None)

        def load_schema_for_node(self, node: NodeMetadataBlock) -> dict[str, Any]:
            return {}

    return StamperEngine(
        schema_loader=DummySchemaLoader(),
        directory_traverser=DirectoryTraverser(
            schema_exclusion_registry=schema_exclusion_registry
        ),
        file_io=RealFileIO(),
        file_type_registry=file_type_registry,
    )


@app.command()
def stamp(
    path: str = typer.Argument(..., help="Path to file to stamp"),
    author: str = typer.Option(
        "OmniNode Team", "--author", "-a", help="Author to include in stamp"
    ),
    template_type_str: str = typer.Option(
        "minimal", "--template", "-t", help="Template type (minimal, full, etc.)"
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", "-o", help="Overwrite existing metadata block"
    ),
    repair: bool = typer.Option(
        False, "--repair", "-r", help="Repair malformed metadata block"
    ),
    output_fmt: OutputFormatEnum = typer.Option(
        OutputFormatEnum.TEXT, "--format", "-f", help="Output format (text, json)"
    ),
    fixture: Optional[str] = typer.Option(
        None,
        "--fixture",
        help="Path to JSON or YAML fixture for protocol-driven testing",
    ),
) -> int:
    """
    Stamp an ONEX node metadata file with a hash and timestamp.
    """
    engine = get_engine_from_env_or_flag(fixture)
    template_type = TemplateTypeEnum.MINIMAL
    if template_type_str.upper() in TemplateTypeEnum.__members__:
        template_type = TemplateTypeEnum[template_type_str.upper()]
    result = engine.stamp_file(
        Path(path),
        template=template_type,
        overwrite=overwrite,
        repair=repair,
        author=author,
    )
    if output_fmt == OutputFormatEnum.JSON:
        typer.echo(json.dumps(result.model_dump(), indent=2, default=_json_default))
    else:
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
    return 1 if result.status == OnexStatus.error else 0


@app.command()
def directory(
    directory: Annotated[str, typer.Argument(help="Directory to process")],
    recursive: Annotated[
        bool,
        typer.Option("--recursive", "-r", help="Recursively process subdirectories"),
    ] = True,
    write: Annotated[
        bool,
        typer.Option(
            "--write",
            "-w",
            is_flag=True,
            help="Actually write changes to files (default: dry run)",
        ),
    ] = False,
    include: Annotated[
        Optional[List[str]],
        typer.Option(
            "--include", "-i", help="File patterns to include (e.g., '*.yaml')"
        ),
    ] = None,
    exclude: Annotated[
        Optional[List[str]],
        typer.Option("--exclude", "-e", help="File patterns to exclude"),
    ] = None,
    ignore_file: Annotated[
        Optional[Path],
        typer.Option("--ignore-file", help="Path to .stamperignore file"),
    ] = None,
    template_type_str: Annotated[
        str,
        typer.Option("--template", "-t", help="Template type (minimal, full, etc.)"),
    ] = "minimal",
    author: Annotated[
        str, typer.Option("--author", "-a", help="Author to include in stamp")
    ] = "OmniNode Team",
    overwrite: Annotated[
        bool,
        typer.Option("--overwrite", "-o", help="Overwrite existing metadata blocks"),
    ] = False,
    repair: Annotated[
        bool, typer.Option("--repair", help="Repair malformed metadata blocks")
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Force overwrite of existing metadata blocks"),
    ] = False,
    output_fmt: Annotated[
        OutputFormatEnum,
        typer.Option("--format", "-f", help="Output format (text, json)"),
    ] = OutputFormatEnum.TEXT,
    fixture: Annotated[
        Optional[str],
        typer.Option(
            "--fixture", help="Path to JSON or YAML fixture for protocol-driven testing"
        ),
    ] = None,
    discovery_source: Annotated[
        str,
        typer.Option(
            "--discovery-source",
            help="File discovery source: filesystem, tree, hybrid_warn, hybrid_strict",
        ),
    ] = "filesystem",
    enforce_tree: Annotated[
        bool,
        typer.Option(
            "--enforce-tree",
            help="Error on drift between filesystem and .tree (alias for hybrid_strict)",
        ),
    ] = False,
    tree_only: Annotated[
        bool,
        typer.Option(
            "--tree-only", help="Only process files listed in .tree (alias for tree)"
        ),
    ] = False,
) -> int:
    """
    Stamp all eligible files in a directory, using the selected file discovery source.
    """
    engine = get_engine_from_env_or_flag(fixture)
    template_type = TemplateTypeEnum.MINIMAL
    if template_type_str.upper() in TemplateTypeEnum.__members__:
        template_type = TemplateTypeEnum[template_type_str.upper()]
    ignore_patterns = []
    if isinstance(engine, StamperEngine):
        ignore_patterns = engine.load_onexignore(Path(directory))
    # Set dry_run based on write flag
    dry_run = not write
    result = engine.process_directory(
        Path(directory),
        template=template_type,
        recursive=recursive,
        dry_run=dry_run,
        include_patterns=include,
        exclude_patterns=exclude + ignore_patterns if exclude else ignore_patterns,
        ignore_file=ignore_file,
        author=author,
        overwrite=overwrite,
        repair=repair,
        force_overwrite=force,
    )
    if output_fmt == OutputFormatEnum.JSON:
        typer.echo(json.dumps(result.model_dump(), indent=2, default=_json_default))
    else:
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
    return 1 if result.status == OnexStatus.error else 0


def main() -> None:
    app()


if __name__ == "__main__":
    main()
