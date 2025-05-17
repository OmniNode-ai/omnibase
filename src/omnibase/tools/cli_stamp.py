import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set

import typer
import yaml
from typing_extensions import Annotated

from omnibase.model.model_enum_ignore_pattern_source import IgnorePatternSourceEnum, TraversalModeEnum
from omnibase.model.model_enum_output_format import OutputFormatEnum
from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.model.model_file_filter import FileFilterModel
from omnibase.model.model_onex_message_result import (
    OnexMessageModel,
    OnexResultModel,
    OnexStatus,
)
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader
from omnibase.protocol.protocol_stamper import ProtocolStamper
from omnibase.schema.loader import SchemaLoader
from omnibase.utils.directory_traverser import DirectoryTraverser
from omnibase.utils.tree_file_discovery_source import TreeFileDiscoverySource
from omnibase.utils.hybrid_file_discovery_source import HybridFileDiscoverySource
from omnibase.protocol.protocol_file_io import ProtocolFileIO
from omnibase.utils.in_memory_file_io import InMemoryFileIO
from omnibase.model.model_enum_file_status import FileStatusEnum
from omnibase.utils.utils_node_metadata_extractor import load_node_metadata_from_dict
from omnibase.tools.stamper_engine import StamperEngine
from omnibase.tools.fixture_stamper_engine import FixtureStamperEngine

# === OmniNode:Metadata ===
metadata_version = "0.1"
name = "cli_stamp"
namespace = "foundation.tools"
version = "0.1.0"
type = "tool"
entrypoint = "cli_stamp.py"
owner = "foundation-team"
# === /OmniNode:Metadata ===

app = typer.Typer(
    name="stamp", help="Stamp ONEX node metadata files with hashes and signatures"
)
logger = logging.getLogger(__name__)


def get_engine_from_env_or_flag(fixture: Optional[str] = None) -> 'ProtocolStamperEngine':
    fixture_path = fixture or os.environ.get("STAMPER_FIXTURE_PATH")
    fixture_format = os.environ.get("STAMPER_FIXTURE_FORMAT", "json")
    if fixture_path:
        return FixtureStamperEngine(Path(fixture_path), fixture_format=fixture_format)
    # Default: real engine
    return StamperEngine(
        schema_loader=SchemaLoader(),
        directory_traverser=DirectoryTraverser(),
        file_io=None,
    )

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
    output_format: OutputFormatEnum = typer.Option(
        OutputFormatEnum.TEXT, "--format", "-f", help="Output format (text, json)"
    ),
    fixture: Optional[str] = typer.Option(
        None, "--fixture", help="Path to JSON or YAML fixture for protocol-driven testing"
    ),
) -> int:
    """
    Stamp an ONEX node metadata file with a hash and timestamp.
    """
    engine = get_engine_from_env_or_flag(fixture)
    template_type = TemplateTypeEnum.MINIMAL
    if template.upper() in TemplateTypeEnum.__members__:
        template_type = TemplateTypeEnum[template.upper()]
    result = engine.stamp_file(
        Path(path),
        template=template_type,
        overwrite=overwrite,
        repair=repair,
        author=author,
    )
    if output_format == OutputFormatEnum.JSON:
        typer.echo(json.dumps(result.model_dump(), indent=2))
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
    recursive: Annotated[bool, typer.Option("--recursive", "-r", help="Recursively process subdirectories")] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", "-n", help="Only check files, don't modify them")] = False,
    include: Annotated[List[str], typer.Option("--include", "-i", help="File patterns to include (e.g., '*.yaml')")] = None,
    exclude: Annotated[List[str], typer.Option("--exclude", "-e", help="File patterns to exclude")] = None,
    ignore_file: Annotated[Optional[Path], typer.Option("--ignore-file", help="Path to .stamperignore file")] = None,
    template: Annotated[str, typer.Option("--template", "-t", help="Template type (minimal, full, etc.)")] = "minimal",
    author: Annotated[str, typer.Option("--author", "-a", help="Author to include in stamp")] = "OmniNode Team",
    overwrite: Annotated[bool, typer.Option("--overwrite", "-o", help="Overwrite existing metadata blocks")] = False,
    repair: Annotated[bool, typer.Option("--repair", help="Repair malformed metadata blocks")] = False,
    force: Annotated[bool, typer.Option("--force", help="Force overwrite of existing metadata blocks")] = False,
    output_format: Annotated[OutputFormatEnum, typer.Option("--format", "-f", help="Output format (text, json)")] = OutputFormatEnum.TEXT,
    fixture: Annotated[Optional[str], typer.Option("--fixture", help="Path to JSON or YAML fixture for protocol-driven testing")] = None,
    discovery_source: Annotated[str, typer.Option("--discovery-source", help="File discovery source: filesystem, tree, hybrid_warn, hybrid_strict")] = "filesystem",
    enforce_tree: Annotated[bool, typer.Option("--enforce-tree", help="Error on drift between filesystem and .tree (alias for hybrid_strict)")] = False,
    tree_only: Annotated[bool, typer.Option("--tree-only", help="Only process files listed in .tree (alias for tree)")] = False,
) -> int:
    """
    Stamp all eligible files in a directory, using the selected file discovery source.
    """
    engine = get_engine_from_env_or_flag(fixture)
    template_type = TemplateTypeEnum.MINIMAL
    if template.upper() in TemplateTypeEnum.__members__:
        template_type = TemplateTypeEnum[template.upper()]
    result = engine.process_directory(
        Path(directory),
        template=template_type,
        recursive=recursive,
        dry_run=dry_run,
        include_patterns=include,
        exclude_patterns=exclude,
        ignore_file=ignore_file,
        author=author,
        overwrite=overwrite,
        repair=repair,
        force_overwrite=force,
    )
    if output_format == OutputFormatEnum.JSON:
        typer.echo(json.dumps(result.model_dump(), indent=2))
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

if __name__ == "__main__":
    app()
