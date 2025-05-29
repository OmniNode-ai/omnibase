# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.544017'
# description: Stamped by PythonHandler
# entrypoint: python://node.py
# hash: 692d29b061e4709525f51596523a84a223dec2e8ddf328c3baef6f6c7c817fba
# last_modified_at: '2025-05-29T11:50:11.672789+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: node.py
# namespace: omnibase.node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 55a97da0-83f7-4011-90ce-cc7ee3f5cbc7
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Schema Generator Node for ONEX.

This node generates JSON schemas from Pydantic models for all ONEX state models.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Type, Optional, Protocol

from pydantic import BaseModel

from omnibase.core.core_error_codes import get_exit_code_for_status
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.nodes.registry_loader_node.v1_0_0.models.state import (
    RegistryLoaderInputState,
    RegistryLoaderOutputState,
)
from omnibase.nodes.schema_generator_node.v1_0_0.models.state import (
    SchemaGeneratorInputState,
    SchemaGeneratorOutputState,
    create_schema_generator_input_state,
    create_schema_generator_output_state,
)
from omnibase.nodes.stamper_node.v1_0_0.models.state import (
    StamperInputState,
    StamperOutputState,
)
from omnibase.nodes.template_node.v1_0_0.models.state import (
    TemplateInputState,
    TemplateOutputState,
)
from omnibase.nodes.tree_generator_node.v1_0_0.models.state import (
    TreeGeneratorInputState,
    TreeGeneratorOutputState,
)

from .constants import STATUS_FAILURE, STATUS_SUCCESS
from .introspection import SchemaGeneratorNodeIntrospection
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class SchemaGeneratorNode(EventDrivenNodeMixin):
    """
    Schema Generator Node for generating JSON schemas from Pydantic models.

    This node generates JSON schemas from all ONEX node state models and saves them
    to a specified directory for validation and documentation purposes.
    """

    def __init__(self, node_id: str = "schema_generator_node", event_bus: Optional[ProtocolEventBus] = None, **kwargs):
        super().__init__(node_id=node_id, event_bus=event_bus, **kwargs)
        # Define all available models for schema generation
        self.available_models: Dict[str, Type[BaseModel]] = {
            "stamper_input": StamperInputState,
            "stamper_output": StamperOutputState,
            "tree_generator_input": TreeGeneratorInputState,
            "tree_generator_output": TreeGeneratorOutputState,
            "registry_loader_input": RegistryLoaderInputState,
            "registry_loader_output": RegistryLoaderOutputState,
            "template_input": TemplateInputState,
            "template_output": TemplateOutputState,
            "schema_generator_input": SchemaGeneratorInputState,
            "schema_generator_output": SchemaGeneratorOutputState,
        }

    def generate_schema(
        self,
        model_class: Type[BaseModel],
        output_path: Path,
        include_metadata: bool = True,
    ) -> None:
        """Generate JSON schema for a Pydantic model and save to file."""
        try:
            schema = model_class.model_json_schema()

            if include_metadata:
                # Add metadata to the schema
                schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
                schema["$id"] = f"https://onex.schemas/{output_path.name}"

            # Pretty print the JSON schema
            with open(output_path, "w") as f:
                json.dump(schema, f, indent=2, sort_keys=True)

            emit_log_event(
                LogLevelEnum.INFO,
                f"Generated schema: {output_path}",
                node_id=_COMPONENT_NAME,
            )

        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Failed to generate schema for {output_path}: {e}",
                node_id=_COMPONENT_NAME,
            )
            raise

    @telemetry(node_name="schema_generator_node", operation="execute")
    def execute(
        self, input_state: SchemaGeneratorInputState, event_bus: Optional[ProtocolEventBus] = None, **kwargs
    ) -> SchemaGeneratorOutputState:
        """
        Execute the schema generator node.

        Args:
            input_state: Input state containing generation parameters

        Returns:
            SchemaGeneratorOutputState: Output state with generation results
        """
        self.emit_node_start({"input_state": input_state.model_dump()})
        try:
            emit_log_event(
                LogLevelEnum.INFO,
                f"Starting schema generation with input: {input_state}",
                node_id=_COMPONENT_NAME,
            )

            # Create output directory
            output_dir = Path(input_state.output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Determine which models to generate schemas for
            if input_state.models_to_generate:
                models_to_process = {
                    name: model_class
                    for name, model_class in self.available_models.items()
                    if name in input_state.models_to_generate
                }

                # Check for invalid model names
                invalid_models = set(input_state.models_to_generate) - set(
                    self.available_models.keys()
                )
                if invalid_models:
                    error_msg = f"Invalid model names: {invalid_models}. Available: {list(self.available_models.keys())}"
                    emit_log_event(
                        LogLevelEnum.ERROR,
                        error_msg,
                        node_id=_COMPONENT_NAME,
                    )
                    return create_schema_generator_output_state(
                        status=STATUS_FAILURE,
                        message=error_msg,
                        schemas_generated=[],
                        output_directory=input_state.output_directory,
                        total_schemas=0,
                        correlation_id=input_state.correlation_id,
                    )
            else:
                models_to_process = self.available_models

            # Generate schemas
            schemas_generated = []
            for model_name, model_class in models_to_process.items():
                schema_filename = f"{model_name}.schema.json"
                output_path = output_dir / schema_filename

                try:
                    self.generate_schema(
                        model_class, output_path, input_state.include_metadata
                    )
                    schemas_generated.append(schema_filename)
                except Exception as e:
                    emit_log_event(
                        LogLevelEnum.ERROR,
                        f"Failed to generate schema for {model_name}: {e}",
                        node_id=_COMPONENT_NAME,
                    )
                    return create_schema_generator_output_state(
                        status=STATUS_FAILURE,
                        message=f"Failed to generate schema for {model_name}: {e}",
                        schemas_generated=schemas_generated,
                        output_directory=input_state.output_directory,
                        total_schemas=len(schemas_generated),
                        correlation_id=input_state.correlation_id,
                    )

            success_msg = (
                f"Generated {len(schemas_generated)} JSON schemas successfully"
            )
            emit_log_event(
                LogLevelEnum.INFO,
                success_msg,
                node_id=_COMPONENT_NAME,
            )

            output_state = create_schema_generator_output_state(
                status=STATUS_SUCCESS,
                message=success_msg,
                schemas_generated=schemas_generated,
                output_directory=input_state.output_directory,
                total_schemas=len(schemas_generated),
                correlation_id=input_state.correlation_id,
            )
            self.emit_node_success({
                "input_state": input_state.model_dump(),
                "output_state": output_state.model_dump(),
            })
            return output_state

        except Exception as e:
            error_msg = f"Schema generation failed: {e}"
            emit_log_event(
                LogLevelEnum.ERROR,
                error_msg,
                node_id=_COMPONENT_NAME,
            )
            self.emit_node_failure({
                "input_state": input_state.model_dump(),
                "error": str(e),
            })
            raise


def main() -> None:
    """Main entry point for CLI execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate JSON schemas from Pydantic models"
    )
    parser.add_argument(
        "--output-directory",
        default="src/omnibase/schemas",
        help="Directory where JSON schemas will be generated (default: src/omnibase/schemas)",
    )
    parser.add_argument(
        "--models",
        nargs="*",
        help="Specific models to generate schemas for (default: all models)",
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Don't include additional metadata in schemas",
    )
    parser.add_argument(
        "--correlation-id", help="Optional correlation ID for request tracking"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--introspect",
        action="store_true",
        help="Display node contract and capabilities",
    )

    args = parser.parse_args()

    # Handle introspection command
    if args.introspect:
        SchemaGeneratorNodeIntrospection.handle_introspect_command()
        return

    # Configure structured logging based on verbose flag
    if args.verbose:
        emit_log_event(
            LogLevelEnum.DEBUG,
            "Verbose logging enabled for schema generation",
            node_id=_COMPONENT_NAME,
        )

    # Create input state
    input_state = create_schema_generator_input_state(
        output_directory=args.output_directory,
        models_to_generate=args.models,
        include_metadata=not args.no_metadata,
        correlation_id=args.correlation_id,
    )

    # Execute node
    node = SchemaGeneratorNode()
    output_state = node.execute(input_state)

    # Print results
    emit_log_event(
        LogLevelEnum.INFO,
        f"Status: {output_state.status}",
        node_id=_COMPONENT_NAME,
    )
    emit_log_event(
        LogLevelEnum.INFO,
        f"Message: {output_state.message}",
        node_id=_COMPONENT_NAME,
    )
    emit_log_event(
        LogLevelEnum.INFO,
        f"Schemas generated: {output_state.total_schemas}",
        node_id=_COMPONENT_NAME,
    )
    emit_log_event(
        LogLevelEnum.INFO,
        f"Output directory: {output_state.output_directory}",
        node_id=_COMPONENT_NAME,
    )

    if output_state.schemas_generated:
        emit_log_event(
            LogLevelEnum.INFO,
            "Generated files:",
            node_id=_COMPONENT_NAME,
        )
        for schema_file in output_state.schemas_generated:
            emit_log_event(
                LogLevelEnum.INFO,
                f"  - {schema_file}",
                node_id=_COMPONENT_NAME,
            )

    # Use canonical exit code mapping
    exit_code = get_exit_code_for_status(OnexStatus(output_state.status))
    sys.exit(exit_code)


def get_introspection() -> dict:
    """Get introspection data for the schema generator node."""
    return SchemaGeneratorNodeIntrospection.get_introspection_response().model_dump()


if __name__ == "__main__":
    main()
