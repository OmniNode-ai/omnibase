# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: cli_stamp.py
# version: 1.0.0
# uuid: 1d7e01b2-814c-4355-a6e0-8e34c2461342
# author: OmniNode Team
# created_at: 2025-05-22T12:17:04.435833
# last_modified_at: 2025-05-22T20:50:39.727803
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: da48e519140285e4043517a65b184487fb0cc98d0293eb5a4af958f6c2fb3aef
# entrypoint: python@cli_stamp.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.cli_stamp
# meta_type: tool
# === /OmniNode:Metadata ===


import datetime
import json
import logging
import os
import pathlib
from pathlib import Path
from typing import Any, List, Optional, cast

import typer

# Import shared error handling
from omnibase.core.error_codes import (
    get_exit_code_for_status as shared_get_exit_code_for_status,
)
from omnibase.fixtures.mocks.dummy_schema_loader import DummySchemaLoader
from omnibase.model.enum_onex_status import OnexStatus
from omnibase.model.model_enum_output_format import OutputFormatEnum
from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.protocol.protocol_stamper_engine import ProtocolStamperEngine
from omnibase.tools.fixture_stamper_engine import FixtureStamperEngine
from omnibase.utils.directory_traverser import (
    DirectoryTraverser,
    SchemaExclusionRegistry,
)
from omnibase.utils.real_file_io import RealFileIO

from .error_codes import StamperError
from .helpers.stamper_engine import StamperEngine
from .introspection import StamperNodeIntrospection

# Configure root logger for DEBUG output
logging.basicConfig(level=logging.DEBUG)

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
logger = logging.getLogger(__name__)

# Add this after logger is defined
logger.debug(f"Debug: str is {str!r}, type: {type(str)}")


def _json_default(obj: object) -> str:
    if isinstance(obj, pathlib.PurePath):
        return str(obj)
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


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
    logger = logging.getLogger("omnibase.tools.cli_stamp")
    # Log all registered handler extensions and their handler class names
    handler_registry = cast(Any, engine).handler_registry  # type: ignore[attr-defined]
    registered = (
        handler_registry._handlers if hasattr(handler_registry, "_handlers") else {}
    )
    logger.debug(f"Registered handler extensions: {list(registered.keys())}")
    logger.debug(f"Handler classes: {[type(h).__name__ for h in registered.values()]}")
    logger.debug(f"Stamper CLI received {len(paths)} files: {paths}")
    print(f"[DEBUG] Files passed to stamper: {paths}")
    logger.info(f"[DEBUG] Files passed to stamper: {paths}")
    logger.debug(
        f"[START] CLI command 'file' with paths={paths}, author={author}, template_type={template_type_str}, overwrite={overwrite}, repair={repair}, output_fmt={output_fmt}, fixture={fixture}"
    )
    any_error = False
    for path in paths:
        file_path = Path(path)
        logger.info(f"Processing file: {path}")

        # Check ignore patterns for each file
        if hasattr(engine, "load_onexignore"):
            directory = file_path.parent
            ignore_patterns = engine.load_onexignore(directory)
            if hasattr(engine, "should_ignore") and engine.should_ignore(
                file_path, ignore_patterns
            ):
                logger.info(f"Skipping file {path} due to .onexignore patterns")
                print(f"[INFO] Skipping file {path} (ignored by .onexignore)")
                continue

        handler = cast(Any, engine).handler_registry.get_handler(file_path)  # type: ignore[attr-defined]
        if handler is None:
            logger.warning(f"No handler registered for file: {path}. Skipping.")
            print(f"[DEBUG] No handler registered for file: {path}. Skipping.")
            continue
        try:
            result = engine.stamp_file(
                file_path,
                template=template_type,
                overwrite=overwrite,
                repair=repair,
                author=author,
            )
            logger.info(
                f"[END] CLI command 'file' for path={path}, result status={result.status}, messages={result.messages}, metadata={result.metadata}"
            )
        except Exception as e:
            logger.error(f"Error processing file {path}: {e}")
            print(f"[ERROR] Exception processing file {path}: {e}")
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
    logger.debug("[END] Stamper CLI finished processing all files.")
    print("[DEBUG] Stamper CLI finished processing all files.")

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
    logger = logging.getLogger("omnibase.tools.cli_stamp")
    logger.debug(
        f"[START] CLI command 'directory' with directory={directory}, recursive={recursive}, write={write}, include={include}, exclude={exclude}, ignore_file={ignore_file}, template_type={template_type_str}, author={author}, overwrite={overwrite}, repair={repair}, force={force}, output_fmt={output_fmt}, fixture={fixture}, discovery_source={discovery_source}, enforce_tree={enforce_tree}, tree_only={tree_only}"
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
    logger.debug(
        f"[END] CLI command 'directory' for directory={directory}, result status={result.status}, messages={result.messages}, metadata={result.metadata}"
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

        logger.error(f"[STAMPER ERROR] {e}", exc_info=True)
        typer.echo(f"[ERROR] {e}", err=True)
        sys.exit(e.get_exit_code())
    except Exception as e:
        import sys
        import traceback

        logger.error(f"[FATAL] Unhandled exception in CLI: {e}", exc_info=True)
        typer.echo(f"[FATAL] Unhandled exception: {e}", err=True)
        typer.echo(traceback.format_exc(), err=True)
        sys.exit(shared_get_exit_code_for_status(OnexStatus.ERROR))


if __name__ == "__main__":

    try:
        main()
    except Exception:
        pass
