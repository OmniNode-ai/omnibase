# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.907090'
# description: Stamped by PythonHandler
# entrypoint: python://node
# hash: d22122fab9fda37574749d4aa38c7070f0bb1a9d5b33717d2016d9becb76bbad
# last_modified_at: '2025-05-29T14:13:59.115671+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: node.py
# namespace: python://omnibase.nodes.docstring_generator_node.v1_0_0.node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 706a79a8-f34c-4841-922b-428bfe8cfdde
# version: 1.0.0
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
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import yaml
from jinja2 import Environment, FileSystemLoader

from omnibase.core.core_error_codes import (
    CoreErrorCode,
    OnexError,
    get_exit_code_for_status,
)
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.mixin.mixin_introspection import NodeIntrospectionMixin
from omnibase.model.model_log_entry import LogContextModel
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry

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


class DocstringGeneratorNode(EventDrivenNodeMixin, NodeIntrospectionMixin):
    """
    ONEX docstring generator node for creating markdown documentation from schemas.

    This node processes JSON/YAML schema files and generates comprehensive markdown
    documentation using configurable Jinja2 templates.
    """

    def __init__(self, event_bus: Optional[ProtocolEventBus] = None, **kwargs):
        super().__init__(
            node_id="docstring_generator_node", event_bus=event_bus, **kwargs
        )
        self.event_bus = event_bus or InMemoryEventBus()
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
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"Failed to load changelog: {e}",
                    context=LogContextModel(
                        calling_module=__name__,
                        calling_function="load_changelog",
                        calling_line=__import__("inspect").currentframe().f_lineno,
                        timestamp=datetime.now().isoformat(),
                        node_id=_COMPONENT_NAME,
                    ),
                    node_id=_COMPONENT_NAME,
                    event_bus=self.event_bus,
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

    @telemetry(node_name="docstring_generator_node", operation="generate_documentation")
    def generate_documentation(
        self,
        input_state: DocstringGeneratorInputState,
        event_bus: Optional[ProtocolEventBus] = None,
        **kwargs,
    ) -> DocstringGeneratorOutputState:
        self.emit_node_start({"input_state": input_state.model_dump()})
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

            emit_log_event_sync(
                LogLevelEnum.INFO,
                "Documentation generation completed",
                context=LogContextModel(
                    calling_module=__name__,
                    calling_function="generate_documentation",
                    calling_line=__import__("inspect").currentframe().f_lineno,
                    timestamp=datetime.now().isoformat(),
                    node_id=_COMPONENT_NAME,
                ),
                node_id=_COMPONENT_NAME,
                event_bus=self.event_bus,
            )

            output_state = create_docstring_generator_output_state(
                status=status,
                message=message,
                generated_documents=self.generated_documents,
                skipped_files=self.skipped_files,
                error_files=self.error_files,
                summary=summary,
                output_directory=input_state.output_directory,
                correlation_id=input_state.correlation_id,
            )
            self.emit_node_success(
                {
                    "input_state": input_state.model_dump(),
                    "output_state": output_state.model_dump(),
                }
            )
            return output_state
        except Exception as e:
            self.emit_node_failure(
                {
                    "input_state": input_state.model_dump(),
                    "error": str(e),
                }
            )
            raise

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
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"Generated documentation: {out_path}",
                    context=LogContextModel(
                        calling_module=__name__,
                        calling_function="_process_single_schema",
                        calling_line=__import__("inspect").currentframe().f_lineno,
                        timestamp=datetime.now().isoformat(),
                        node_id=_COMPONENT_NAME,
                    ),
                    node_id=_COMPONENT_NAME,
                    event_bus=self.event_bus,
                )

        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Failed to process schema {schema_path}: {e}",
                context=LogContextModel(
                    calling_module=__name__,
                    calling_function="_process_single_schema",
                    calling_line=__import__("inspect").currentframe().f_lineno,
                    timestamp=datetime.now().isoformat(),
                    node_id=_COMPONENT_NAME,
                ),
                node_id=_COMPONENT_NAME,
                event_bus=self.event_bus,
            )
            self.error_files.append(str(schema_path))


def run_docstring_generator_node(
    input_state: DocstringGeneratorInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    **kwargs,
) -> DocstringGeneratorOutputState:
    """
    Run the docstring generator node with the given input state.

    Args:
        input_state: Input configuration for documentation generation
        event_bus: Optional event bus for event emission
        **kwargs: Additional keyword arguments for compatibility

    Returns:
        DocstringGeneratorOutputState with generation results
    """
    if event_bus is None:
        event_bus = get_event_bus(mode="bind")  # Publisher
    node = DocstringGeneratorNode(event_bus=event_bus)
    return node.generate_documentation(input_state, event_bus=event_bus, **kwargs)


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
    event_bus: Optional[ProtocolEventBus] = None,
    **kwargs,
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
        event_bus: Optional event bus for event emission
        **kwargs: Additional keyword arguments for compatibility

    Returns:
        DocstringGeneratorOutputState with generation results
    """
    if event_bus is None:
        event_bus = get_event_bus(mode="bind")  # Publisher
    input_state = create_docstring_generator_input_state(
        schema_directory=schema_directory,
        template_path=template_path,
        output_directory=output_directory,
        changelog_path=changelog_path,
        verbose=verbose,
        include_examples=include_examples,
        correlation_id=correlation_id,
    )

    return run_docstring_generator_node(input_state, event_bus=event_bus, **kwargs)


def cli_main() -> DocstringGeneratorOutputState:
    """
    Protocol-pure entrypoint: never print or sys.exit. Always return a canonical output model.
    """
    import argparse
    parser = argparse.ArgumentParser(description="ONEX Docstring Generator Node CLI")
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
    if "--introspect" in sys.argv:
        event_bus = InMemoryEventBus()
        DocstringGeneratorNodeIntrospection.handle_introspect_command(
            event_bus=event_bus
        )
        return DocstringGeneratorOutputState(
            version="1.0.0",
            status=OnexStatus.SUCCESS.value,
            message="Introspection command handled",
        )

    args = parser.parse_args()

    try:
        result = main(
            schema_directory=args.schema_directory,
            template_path=args.template_path,
            output_directory=args.output_directory,
            changelog_path=args.changelog_path,
            verbose=args.verbose,
            include_examples=not args.no_examples,
            correlation_id=args.correlation_id,
        )
        return result
    except Exception as e:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Docstring generator node error: {e}",
            node_id="docstring_generator_node",
            event_bus=None,
        )
        return DocstringGeneratorOutputState(
            version="1.0.0",
            status=OnexStatus.ERROR.value,
            message=f"Docstring generator node error: {e}",
        )


if __name__ == "__main__":
    cli_main()
