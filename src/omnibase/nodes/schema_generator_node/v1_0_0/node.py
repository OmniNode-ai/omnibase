# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node.py
# version: 1.0.0
# uuid: e955abb8-abc4-4413-b6e1-e0dd53559476
# author: OmniNode Team
# created_at: 2025-05-25T15:37:23.452851
# last_modified_at: 2025-05-25T19:48:02.872869
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 4da1cc55270ce5786e7bf09220fa901eecbe22b76a8894730b815a1b15b13b2e
# entrypoint: python@node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.node
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Schema Generator Node Implementation.

This module implements the schema generator node that generates JSON schemas
from Pydantic state models for validation and documentation purposes.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Type

from pydantic import BaseModel

from omnibase.nodes.registry_loader_node.v1_0_0.models.state import (
    RegistryLoaderInputState,
    RegistryLoaderOutputState,
)
from omnibase.nodes.schema_generator_node.v1_0_0.models.state import (
    SchemaGeneratorInputState,
    SchemaGeneratorOutputState,
    create_schema_generator_output_state,
)

# Import all state models for schema generation
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

# Status constants
STATUS_SUCCESS = "success"
STATUS_FAILURE = "failure"
STATUS_WARNING = "warning"

# Configure logging
logger = logging.getLogger(__name__)


class SchemaGeneratorNode:
    """
    Schema Generator Node for generating JSON schemas from Pydantic models.

    This node generates JSON schemas from all ONEX node state models and saves them
    to a specified directory for validation and documentation purposes.
    """

    def __init__(self) -> None:
        """Initialize the schema generator node."""
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

            logger.info(f"Generated schema: {output_path}")

        except Exception as e:
            logger.error(f"Failed to generate schema for {output_path}: {e}")
            raise

    def execute(
        self, input_state: SchemaGeneratorInputState
    ) -> SchemaGeneratorOutputState:
        """
        Execute the schema generator node.

        Args:
            input_state: Input state containing generation parameters

        Returns:
            SchemaGeneratorOutputState: Output state with generation results
        """
        try:
            logger.info(f"Starting schema generation with input: {input_state}")

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
                    logger.error(error_msg)
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
                    logger.error(f"Failed to generate schema for {model_name}: {e}")
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
            logger.info(success_msg)

            return create_schema_generator_output_state(
                status=STATUS_SUCCESS,
                message=success_msg,
                schemas_generated=schemas_generated,
                output_directory=input_state.output_directory,
                total_schemas=len(schemas_generated),
                correlation_id=input_state.correlation_id,
            )

        except Exception as e:
            error_msg = f"Schema generation failed: {e}"
            logger.error(error_msg)
            return create_schema_generator_output_state(
                status=STATUS_FAILURE,
                message=error_msg,
                schemas_generated=[],
                output_directory=input_state.output_directory,
                total_schemas=0,
                correlation_id=input_state.correlation_id,
            )


def main() -> None:
    """Main entry point for CLI execution."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Generate JSON schemas from Pydantic models"
    )
    parser.add_argument(
        "--output-directory",
        default="src/schemas",
        help="Directory where JSON schemas will be generated (default: src/schemas)",
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

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create input state
    from omnibase.nodes.schema_generator_node.v1_0_0.models.state import (
        create_schema_generator_input_state,
    )

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
    print(f"Status: {output_state.status}")
    print(f"Message: {output_state.message}")
    print(f"Schemas generated: {output_state.total_schemas}")
    print(f"Output directory: {output_state.output_directory}")

    if output_state.schemas_generated:
        print("Generated files:")
        for schema_file in output_state.schemas_generated:
            print(f"  - {schema_file}")

    # Exit with appropriate code
    sys.exit(0 if output_state.status == STATUS_SUCCESS else 1)


if __name__ == "__main__":
    main()
