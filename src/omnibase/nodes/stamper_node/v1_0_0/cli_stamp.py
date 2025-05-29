# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.584921'
# description: Stamped by PythonHandler
# entrypoint: python://cli_stamp
# hash: 150baa52e3dd455e9e884ce6a0b20dd5a94937e29952d2c434f3fded3a7b32b0
# last_modified_at: '2025-05-29T14:13:59.777696+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: cli_stamp.py
# namespace: python://omnibase.nodes.stamper_node.v1_0_0.cli_stamp
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 3c91993c-6dfe-428d-a9e4-20f05591479c
# version: 1.0.0
# === /OmniNode:Metadata ===


import datetime
import json
import os
import pathlib
from pathlib import Path
from typing import Any, List, Optional, cast

import typer

# Import shared error handling
from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_error_codes import (
    get_exit_code_for_status as shared_get_exit_code_for_status,
)
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus, OutputFormatEnum, TemplateTypeEnum
from omnibase.fixtures.mocks.dummy_schema_loader import DummySchemaLoader
from omnibase.protocol.protocol_stamper_engine import ProtocolStamperEngine
from omnibase.utils.directory_traverser import (
    DirectoryTraverser,
    SchemaExclusionRegistry,
)
from omnibase.utils.real_file_io import RealFileIO

from .error_codes import StamperError
from .helpers.fixture_stamper_engine import FixtureStamperEngine
from .helpers.stamper_engine import StamperEngine
from .introspection import StamperNodeIntrospection

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem

app = typer.Typer(
    name="stamp",
    help="""
Stamp ONEX node metadata files with hashes and signatures.

Eligible file types by default:
  - Markdown (.md)
  - Python (.py)
  - YAML (.yaml, .yml)
  - JSON (.json)

The stamper will process all files with these extensions in the specified directory by default. Use --recursive to include subdirectories.

Schema files (e.g., *_schema.yaml, onex_node.yaml) and files in 'schemas/' or 'schema/' directories are excluded by default.

You can use .onexignore files to further control which files are ignored.

Examples:
  # Dry run (default: show what would be stamped, top-level only)
  poetry run python -m omnibase.tools.cli_stamp directory .

  # Actually write changes, recursively
  poetry run python -m omnibase.tools.cli_stamp directory . --recursive --write

  # Stamp only markdown files (dry run, top-level only)
  poetry run python -m omnibase.tools.cli_stamp directory . --include '**/*.md'

  # Stamp only YAML files, excluding testdata (write mode, recursively)
  poetry run python -m omnibase.tools.cli_stamp directory . --include '**/*.yaml' --exclude 'src/omnibase/**/tests/**' --recursive --write

  # Stamp a single file
  poetry run python -m omnibase.tools.cli_stamp stamp docs/dev_logs/jonah/debug/debug_log_2025_05_18.md --author "jonah"

For more details, see docs/tools/stamper.md.
""",
)


def _json_default(obj: object) -> str:
    if isinstance(obj, pathlib.PurePath):
        return str(obj)
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise OnexError(
        f"Object of type {type(obj).__name__} is not JSON serializable",
        CoreErrorCode.INVALID_PARAMETER,
    )


def get_engine_from_env_or_flag(
    fixture: Optional[str] = None,
) -> "ProtocolStamperEngine":
    """
    Get a stamper engine from environment variables or fixture flag.
    Returns FixtureStamperEngine if fixture is provided, otherwise StamperEngine.
    """
    fixture_path = fixture or os.environ.get("STAMPER_FIXTURE_PATH")
    fixture_format = os.environ.get("STAMPER_FIXTURE_FORMAT", "json")
    schema_exclusion_registry = (
        SchemaExclusionRegistry()
    )  # Registry-driven schema exclusion
    if fixture_path:
        return FixtureStamperEngine(Path(fixture_path), fixture_format=fixture_format)

    # Use RealFileIO for CLI mode to ensure real files are accessed
    return StamperEngine(
        schema_loader=DummySchemaLoader(),
        directory_traverser=DirectoryTraverser(
            schema_exclusion_registry=schema_exclusion_registry
        ),
        file_io=RealFileIO(),
    )


@app.command("file")
def file(
    paths: List[str] = typer.Argument(..., help="Path(s) to file(s) to stamp"),
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
    Stamp one or more ONEX node metadata files with a hash and timestamp.
    Usage: onex stamp file <file1> <file2> ...
    """
    engine = get_engine_from_env_or_flag(fixture)
    template_type = TemplateTypeEnum.MINIMAL
    if template_type_str.upper() in TemplateTypeEnum.__members__:
        template_type = TemplateTypeEnum[template_type_str.upper()]
    # Log all registered handler extensions and their handler class names
    handler_registry = cast(Any, engine).handler_registry  # type: ignore[attr-defined]
    registered = (
        handler_registry._handlers if hasattr(handler_registry, "_handlers") else {}
    )
    emit_log_event(
        LogLevelEnum.DEBUG,
        f"Registered handler extensions: {list(registered.keys())}",
        node_id=_COMPONENT_NAME,
    )
    emit_log_event(
        LogLevelEnum.DEBUG,
        f"Handler classes: {[type(h).__name__ for h in registered.values()]}",
        node_id=_COMPONENT_NAME,
    )
    emit_log_event(
        LogLevelEnum.DEBUG,
        f"Stamper CLI received {len(paths)} files: {paths}",
        node_id=_COMPONENT_NAME,
    )
    # Already logging this message in a more structured format above
    emit_log_event(
        LogLevelEnum.DEBUG,
        f"[START] CLI command 'file' with paths={paths}, author={author}, template_type={template_type_str}, overwrite={overwrite}, repair={repair}, output_fmt={output_fmt}, fixture={fixture}",
        node_id=_COMPONENT_NAME,
    )
    any_error = False
    for path in paths:
        file_path = Path(path)
        emit_log_event(
            LogLevelEnum.INFO,
            f"Processing file: {path}",
            node_id=_COMPONENT_NAME,
        )

        # Check ignore patterns for each file
        if hasattr(engine, "load_onexignore"):
            directory = file_path.parent
            ignore_patterns = engine.load_onexignore(directory)
            if hasattr(engine, "should_ignore") and engine.should_ignore(
                file_path, ignore_patterns
            ):
                emit_log_event(
                    LogLevelEnum.INFO,
                    f"Skipping file {path} due to .onexignore patterns",
                    node_id=_COMPONENT_NAME,
                )
                # Already logged in structured format above
                continue

        handler = cast(Any, engine).handler_registry.get_handler(file_path)  # type: ignore[attr-defined]
        if handler is None:
            emit_log_event(
                LogLevelEnum.WARNING,
                f"No handler registered for file: {path}. Skipping.",
                node_id=_COMPONENT_NAME,
            )
            # Already logged in structured format above
            continue
        try:
            result = engine.stamp_file(
                file_path,
                template=template_type,
                overwrite=overwrite,
                repair=repair,
                author=author,
            )
            emit_log_event(
                LogLevelEnum.INFO,
                f"[END] CLI command 'file' for path={path}, result status={result.status}, messages={result.messages}, metadata={result.metadata}",
                node_id=_COMPONENT_NAME,
            )
        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Error processing file {path}: {e}",
                node_id=_COMPONENT_NAME,
            )
            # Already logged in structured format above
            any_error = True
            continue
        if output_fmt == OutputFormatEnum.JSON:
            typer.echo(json.dumps(result.model_dump(), indent=2, default=_json_default))
        else:
            typer.echo(f"[{result.status.value}] {path}")
            for msg in result.messages:
                typer.echo(f"  {msg.summary}")
                if msg.details:
                    typer.echo(f"    {msg.details}")
            if result.metadata:
                for key, value in result.metadata.items():
                    typer.echo(f"  {key}: {value}")
        if result.status == OnexStatus.ERROR:
            any_error = True
    emit_log_event(
        LogLevelEnum.DEBUG,
        "[END] Stamper CLI finished processing all files.",
        node_id=_COMPONENT_NAME,
    )
    # Already logged in structured format above

    # Use the shared exit code mapping for consistent behavior
    if any_error:
        return shared_get_exit_code_for_status(OnexStatus.ERROR)
    return shared_get_exit_code_for_status(OnexStatus.SUCCESS)


@app.command()
def directory(
    directory: str = typer.Argument(..., help="Directory to process"),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        is_flag=True,
        help="Recursively process subdirectories (default: only top-level directory)",
    ),
    write: bool = typer.Option(
        False,
        "--write",
        "-w",
        is_flag=True,
        help="Actually write changes to files (default: dry run)",
    ),
    include: Optional[List[str]] = typer.Option(
        None,
        "--include",
        "-i",
        help="File patterns to include (e.g., '*.yaml')",
    ),
    exclude: Optional[List[str]] = typer.Option(
        None,
        "--exclude",
        "-e",
        help="File patterns to exclude",
    ),
    ignore_file: Optional[Path] = typer.Option(
        None,
        "--ignore-file",
        help="Path to .onexignore file",
    ),
    template_type_str: str = typer.Option(
        "minimal",
        "--template",
        "-t",
        help="Template type (minimal, full, etc.)",
    ),
    author: str = typer.Option(
        "OmniNode Team",
        "--author",
        "-a",
        help="Author to include in stamp",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        "-o",
        help="Overwrite existing metadata blocks",
    ),
    repair: bool = typer.Option(
        False,
        "--repair",
        help="Repair malformed metadata blocks",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force overwrite of existing metadata blocks",
    ),
    output_fmt: OutputFormatEnum = typer.Option(
        OutputFormatEnum.TEXT,
        "--format",
        "-f",
        help="Output format (text, json)",
    ),
    fixture: Optional[str] = typer.Option(
        None,
        "--fixture",
        help="Path to JSON or YAML fixture for protocol-driven testing",
    ),
    discovery_source: str = typer.Option(
        "filesystem",
        "--discovery-source",
        help="File discovery source: filesystem, tree, hybrid_warn, hybrid_strict",
    ),
    enforce_tree: bool = typer.Option(
        False,
        "--enforce-tree",
        help="Error on drift between filesystem and .tree (alias for hybrid_strict)",
    ),
    tree_only: bool = typer.Option(
        False,
        "--tree-only",
        help="Only process files listed in .tree (alias for tree)",
    ),
) -> int:
    """
    Stamp all eligible files in a directory, using the selected file discovery source.
    """
    engine = get_engine_from_env_or_flag(fixture)
    template_type = TemplateTypeEnum.MINIMAL
    if template_type_str.upper() in TemplateTypeEnum.__members__:
        template_type = TemplateTypeEnum[template_type_str.upper()]
    emit_log_event(
        LogLevelEnum.DEBUG,
        f"[START] CLI command 'directory' with directory={directory}, recursive={recursive}, write={write}, include={include}, exclude={exclude}, ignore_file={ignore_file}, template_type={template_type_str}, author={author}, overwrite={overwrite}, repair={repair}, force={force}, output_fmt={output_fmt}, fixture={fixture}, discovery_source={discovery_source}, enforce_tree={enforce_tree}, tree_only={tree_only}",
        node_id=_COMPONENT_NAME,
    )
    result = engine.process_directory(
        Path(directory),
        template=template_type,
        recursive=recursive,
        dry_run=not write,
        include_patterns=include,
        exclude_patterns=exclude,
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
        # After processing a directory, print a summary of skipped files (with reasons)
        if hasattr(result, "metadata") and result.metadata:
            skipped_files = result.metadata.get("skipped_files")
            skipped_file_reasons = result.metadata.get("skipped_file_reasons")
            if skipped_files and skipped_file_reasons:
                typer.echo("\n=== Skipped Files Summary ===")
                for f in skipped_files:
                    reason = skipped_file_reasons.get(str(f), "unknown reason")
                    typer.echo(f"- {f}: {reason}")
                typer.echo(f"Total skipped: {len(skipped_files)}")
    emit_log_event(
        LogLevelEnum.DEBUG,
        f"[END] CLI command 'directory' for directory={directory}, result status={result.status}, messages={result.messages}, metadata={result.metadata}",
        node_id=_COMPONENT_NAME,
    )

    # Use the shared exit code mapping for consistent behavior
    return shared_get_exit_code_for_status(result.status)


@app.command("introspect")
def introspect() -> int:
    """
    Display node contract, capabilities, and metadata.

    Returns comprehensive information about this node including:
    - Node metadata and version
    - Input/output state models
    - CLI interface specification
    - Error codes and exit code mapping
    - Dependencies and capabilities
    """
    try:
        StamperNodeIntrospection.handle_introspect_command()
        return 0
    except Exception as e:
        typer.echo(f"[ERROR] Introspection failed: {e}", err=True)
        return 1


def main() -> None:
    try:
        app()
    except StamperError as e:
        # Handle stamper-specific errors with proper exit codes
        import sys

        emit_log_event(
            LogLevelEnum.ERROR,
            f"[STAMPER ERROR] {e}",
            node_id=_COMPONENT_NAME,
        )
        typer.echo(f"[ERROR] {e}", err=True)
        sys.exit(e.get_exit_code())
    except Exception as e:
        import sys
        import traceback

        emit_log_event(
            LogLevelEnum.ERROR,
            f"[FATAL] Unhandled exception in CLI: {e}",
            node_id=_COMPONENT_NAME,
        )
        typer.echo(f"[FATAL] Unhandled exception: {e}", err=True)
        typer.echo(traceback.format_exc(), err=True)
        sys.exit(shared_get_exit_code_for_status(OnexStatus.ERROR))


if __name__ == "__main__":

    try:
        main()
    except Exception:
        pass
