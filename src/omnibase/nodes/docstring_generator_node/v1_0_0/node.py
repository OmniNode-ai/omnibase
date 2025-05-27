# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node.py
# version: 1.0.0
# uuid: b6a24725-5d94-4d44-9c94-0041d94414e2
# author: OmniNode Team
# created_at: 2025-05-27T07:34:49.190824
# last_modified_at: 2025-05-27T11:48:23.381627
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a892d836cbcbd2218d884d66d82625f657020d29431e4367eee01563e0e4846c
# entrypoint: python@node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.node
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Docstring Generator Node - Generates markdown documentation from JSON schemas.

This node processes JSON/YAML schema files and generates comprehensive markdown
documentation using Jinja2 templates. It extracts schema metadata, field definitions,
examples, and generates human-readable documentation.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import yaml
from jinja2 import Environment, FileSystemLoader

from omnibase.core.core_error_codes import (
    CoreErrorCode,
    OnexError,
    get_exit_code_for_status,
)
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.mixin.mixin_introspection import NodeIntrospectionMixin

from .introspection import DocstringGeneratorNodeIntrospection
from .models.state import (
    DocstringGeneratorInputState,
    DocstringGeneratorOutputState,
    GeneratedDocument,
    create_docstring_generator_input_state,
    create_docstring_generator_output_state,
)

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class DocstringGeneratorNode(NodeIntrospectionMixin):
    """
    ONEX docstring generator node for creating markdown documentation from schemas.

    This node processes JSON/YAML schema files and generates comprehensive markdown
    documentation using configurable Jinja2 templates.
    """

    def __init__(self) -> None:
        """Initialize the docstring generator node."""
        super().__init__()
        self.generated_documents: List[GeneratedDocument] = []
        self.skipped_files: List[str] = []
        self.error_files: List[str] = []

    @classmethod
    def get_node_name(cls) -> str:
        """Return the canonical node name."""
        return "docstring_generator_node"

    @classmethod
    def get_node_version(cls) -> str:
        """Return the node version."""
        return "1.0.0"

    @classmethod
    def get_node_description(cls) -> str:
        """Return the node description."""
        return "Generates markdown documentation from JSON/YAML schemas using Jinja2 templates"

    @classmethod
    def get_input_state_class(cls) -> type:
        """Return the input state model class."""
        return DocstringGeneratorInputState

    @classmethod
    def get_output_state_class(cls) -> type:
        """Return the output state model class."""
        return DocstringGeneratorOutputState

    @classmethod
    def get_error_codes_class(cls) -> type:
        """Return the error codes enum class."""
        from .error_codes import DocstringGeneratorErrorCode

        return DocstringGeneratorErrorCode

    def load_changelog(self, changelog_path: Optional[str]) -> Optional[str]:
        """Load changelog content if available."""
        if not changelog_path:
            return None

        changelog_file = Path(changelog_path)
        if changelog_file.exists():
            try:
                with changelog_file.open("r") as f:
                    return f.read()
            except Exception as e:
                emit_log_event(
                    LogLevelEnum.WARNING,
                    f"Failed to load changelog: {e}",
                    node_id=_COMPONENT_NAME,
                )
        return None

    def load_schema(self, path: Path) -> Dict[str, Any]:
        """Load a schema from a file and return as a dictionary."""
        try:
            if path.suffix.lower() in [".yaml", ".yml"]:
                with path.open("r") as f:
                    return cast(Dict[str, Any], yaml.safe_load(f))
            elif path.suffix.lower() == ".json":
                with path.open("r") as f:
                    return cast(Dict[str, Any], json.load(f))
            else:
                raise OnexError(
                    f"Unsupported schema file extension: {path.suffix}",
                    CoreErrorCode.INVALID_PARAMETER,
                )
        except Exception as e:
            raise OnexError(
                f"Failed to load schema from {path}: {e}",
                CoreErrorCode.FILE_READ_ERROR,
            )

    def extract_fields(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract field definitions from a schema dictionary."""
        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        fields = []

        for name, prop in props.items():
            field = {
                "name": name,
                "type": prop.get("type", "object"),
                "required": name in required,
                "description": prop.get("description", ""),
                "enum": prop.get("enum", None),
            }
            fields.append(field)

        return fields

    def extract_examples(self, schema: Dict[str, Any]) -> List[str]:
        """Extract example strings from a schema dictionary."""
        examples = schema.get("examples", [])
        if isinstance(examples, list):
            return [yaml.dump(ex, sort_keys=False) for ex in examples]
        return []

    def generate_documentation(
        self, input_state: DocstringGeneratorInputState
    ) -> DocstringGeneratorOutputState:
        """
        Generate markdown documentation from schema files.

        Args:
            input_state: Configuration for documentation generation

        Returns:
            DocstringGeneratorOutputState with generation results
        """
        emit_log_event(
            LogLevelEnum.INFO,
            "Starting documentation generation",
            context={
                "schema_directory": input_state.schema_directory,
                "output_directory": input_state.output_directory,
                "template_path": input_state.template_path,
            },
            node_id=_COMPONENT_NAME,
        )

        try:
            # Reset state
            self.generated_documents = []
            self.skipped_files = []
            self.error_files = []

            # Validate input paths
            schema_dir = Path(input_state.schema_directory)
            if not schema_dir.exists():
                raise OnexError(
                    f"Schema directory not found: {input_state.schema_directory}",
                    CoreErrorCode.DIRECTORY_NOT_FOUND,
                )

            template_path = Path(input_state.template_path)
            if not template_path.exists():
                raise OnexError(
                    f"Template file not found: {input_state.template_path}",
                    CoreErrorCode.FILE_NOT_FOUND,
                )

            # Create output directory
            output_dir = Path(input_state.output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Load template
            env = Environment(loader=FileSystemLoader(str(template_path.parent)))
            template = env.get_template(template_path.name)

            # Load changelog if specified
            changelog = self.load_changelog(input_state.changelog_path)

            # Process schema files
            self._process_schema_files(
                schema_dir, template, output_dir, changelog, input_state
            )

            # Generate summary
            summary = {
                "total_schemas": len(self.generated_documents)
                + len(self.skipped_files)
                + len(self.error_files),
                "generated": len(self.generated_documents),
                "skipped": len(self.skipped_files),
                "errors": len(self.error_files),
            }

            # Determine overall status
            if self.error_files:
                status = OnexStatus.ERROR
                message = f"Generated {len(self.generated_documents)} docs with {len(self.error_files)} errors"
            elif self.skipped_files:
                status = OnexStatus.WARNING
                message = f"Generated {len(self.generated_documents)} docs with {len(self.skipped_files)} skipped"
            else:
                status = OnexStatus.SUCCESS
                message = f"Successfully generated {len(self.generated_documents)} documentation files"

            emit_log_event(
                LogLevelEnum.INFO,
                "Documentation generation completed",
                context=summary,
                node_id=_COMPONENT_NAME,
            )

            return create_docstring_generator_output_state(
                status=status,
                message=message,
                generated_documents=self.generated_documents,
                skipped_files=self.skipped_files,
                error_files=self.error_files,
                summary=summary,
                output_directory=input_state.output_directory,
                correlation_id=input_state.correlation_id,
            )

        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Documentation generation failed: {e}",
                node_id=_COMPONENT_NAME,
            )
            return create_docstring_generator_output_state(
                status=OnexStatus.ERROR,
                message=f"Documentation generation failed: {e}",
                error_files=[str(e)],
                summary={"total_schemas": 0, "generated": 0, "skipped": 0, "errors": 1},
                output_directory=input_state.output_directory,
                correlation_id=input_state.correlation_id,
            )

    def _process_schema_files(
        self,
        schema_dir: Path,
        template: Any,
        output_dir: Path,
        changelog: Optional[str],
        input_state: DocstringGeneratorInputState,
    ) -> None:
        """Process all schema files in the directory."""
        # Discover schemas (deduplicate YAML/JSON pairs)
        seen = set()

        # Process YAML files first
        for schema_path in sorted(schema_dir.glob("*.yaml")):
            name = schema_path.stem
            seen.add(name)
            self._process_single_schema(
                schema_path, name, template, output_dir, changelog, input_state
            )

        # Process JSON files not already seen
        for schema_path in sorted(schema_dir.glob("*.json")):
            name = schema_path.stem
            if name in seen:
                continue
            self._process_single_schema(
                schema_path, name, template, output_dir, changelog, input_state
            )

    def _process_single_schema(
        self,
        schema_path: Path,
        name: str,
        template: Any,
        output_dir: Path,
        changelog: Optional[str],
        input_state: DocstringGeneratorInputState,
    ) -> None:
        """Process a single schema file."""
        try:
            schema = self.load_schema(schema_path)
            title = schema.get("title", name)
            version = schema.get(
                "SCHEMA_VERSION", schema.get("schema_version", "unknown")
            )
            description = schema.get("description", "")
            fields = self.extract_fields(schema)
            examples = (
                self.extract_examples(schema) if input_state.include_examples else []
            )

            # Render documentation
            doc = template.render(
                title=title,
                version=version,
                description=description,
                changelog=changelog,
                fields=fields,
                examples=examples,
            )

            # Write output file
            out_path = output_dir / f"{name}.md"
            with out_path.open("w") as f:
                f.write(doc)

            # Record success
            generated_doc = GeneratedDocument(
                schema_name=name,
                schema_path=str(schema_path),
                output_path=str(out_path),
                title=title,
                version=version,
                field_count=len(fields),
                example_count=len(examples),
            )
            self.generated_documents.append(generated_doc)

            if input_state.verbose:
                emit_log_event(
                    LogLevelEnum.INFO,
                    f"Generated documentation: {out_path}",
                    node_id=_COMPONENT_NAME,
                )

        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Failed to process schema {schema_path}: {e}",
                node_id=_COMPONENT_NAME,
            )
            self.error_files.append(str(schema_path))


def run_docstring_generator_node(
    input_state: DocstringGeneratorInputState,
) -> DocstringGeneratorOutputState:
    """
    Run the docstring generator node with the given input state.

    Args:
        input_state: Input configuration for documentation generation

    Returns:
        DocstringGeneratorOutputState with generation results
    """
    node = DocstringGeneratorNode()
    return node.generate_documentation(input_state)


def get_introspection() -> Dict[str, Any]:
    """
    Get introspection data for the docstring generator node.

    Returns:
        Dictionary containing node introspection information
    """
    response = DocstringGeneratorNodeIntrospection.get_introspection_response()
    return response.model_dump()


def main(
    schema_directory: str = "src/omnibase/schemas",
    template_path: str = "docs/templates/schema_doc.md.j2",
    output_directory: str = "docs/generated",
    changelog_path: Optional[str] = "docs/changelog.md",
    verbose: bool = False,
    include_examples: bool = True,
    correlation_id: Optional[str] = None,
) -> DocstringGeneratorOutputState:
    """
    Main entry point for the docstring generator node.

    Args:
        schema_directory: Directory containing schema files
        template_path: Path to Jinja2 template file
        output_directory: Directory for generated documentation
        changelog_path: Optional path to changelog file
        verbose: Enable verbose logging
        include_examples: Include schema examples in documentation
        correlation_id: Optional correlation ID for tracking

    Returns:
        DocstringGeneratorOutputState with generation results
    """
    input_state = create_docstring_generator_input_state(
        schema_directory=schema_directory,
        template_path=template_path,
        output_directory=output_directory,
        changelog_path=changelog_path,
        verbose=verbose,
        include_examples=include_examples,
        correlation_id=correlation_id,
    )

    return run_docstring_generator_node(input_state)


def cli_main() -> None:
    """CLI entry point for the docstring generator node."""
    parser = argparse.ArgumentParser(
        description="Generate markdown documentation from JSON/YAML schemas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m omnibase.nodes.docstring_generator_node.v1_0_0.node
  python -m omnibase.nodes.docstring_generator_node.v1_0_0.node --verbose
  python -m omnibase.nodes.docstring_generator_node.v1_0_0.node --schema-dir custom/schemas
        """,
    )

    parser.add_argument(
        "--schema-directory",
        type=str,
        default="src/omnibase/schemas",
        help="Directory containing JSON/YAML schema files (default: src/omnibase/schemas)",
    )
    parser.add_argument(
        "--template-path",
        type=str,
        default="docs/templates/schema_doc.md.j2",
        help="Path to Jinja2 template file (default: docs/templates/schema_doc.md.j2)",
    )
    parser.add_argument(
        "--output-directory",
        type=str,
        default="docs/generated",
        help="Output directory for generated documentation (default: docs/generated)",
    )
    parser.add_argument(
        "--changelog-path",
        type=str,
        default="docs/changelog.md",
        help="Path to changelog file to include (default: docs/changelog.md)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--no-examples",
        action="store_true",
        help="Exclude schema examples from generated documentation",
    )
    parser.add_argument(
        "--correlation-id",
        type=str,
        help="Optional correlation ID for request tracking",
    )

    # Handle introspection
    if len(sys.argv) > 1 and sys.argv[1] == "--introspect":
        DocstringGeneratorNodeIntrospection.handle_introspect_command()
        return

    args = parser.parse_args()

    result = main(
        schema_directory=args.schema_directory,
        template_path=args.template_path,
        output_directory=args.output_directory,
        changelog_path=args.changelog_path,
        verbose=args.verbose,
        include_examples=not args.no_examples,
        correlation_id=args.correlation_id,
    )

    # Print results
    if args.verbose:
        print(f"Status: {result.status.value}")
        print(f"Message: {result.message}")
        print(f"Generated: {len(result.generated_documents)} files")
        if result.skipped_files:
            print(f"Skipped: {len(result.skipped_files)} files")
        if result.error_files:
            print(f"Errors: {len(result.error_files)} files")
    else:
        print(result.message)

    # Exit with appropriate code
    sys.exit(get_exit_code_for_status(result.status))


if __name__ == "__main__":
    cli_main()
