# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: introspection_mixin.py
# version: 1.0.0
# uuid: adc3d8ab-2ae8-4e24-90f6-d7714cd95594
# author: OmniNode Team
# created_at: 2025-05-25T17:23:59.551487
# last_modified_at: 2025-05-25T22:11:50.176713
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: fd17b6b3589afd6f94408edb0070e7eb5f58cabbebbda54d19df02ee762affb5
# entrypoint: python@introspection_mixin.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.introspection_mixin
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Base Introspection Mixin for ONEX Nodes.

This module provides a reusable mixin class that implements standardized
introspection capabilities for ONEX nodes. All nodes should inherit from
this mixin to provide consistent --introspect functionality.
"""

import json
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

from pydantic import BaseModel

from omnibase.model.model_node_introspection import (
    CLIArgumentModel,
    CLIInterfaceModel,
    ContractModel,
    DependenciesModel,
    ErrorCodeModel,
    ErrorCodesModel,
    NodeCapabilityEnum,
    NodeIntrospectionResponse,
    NodeMetadataModel,
    StateFieldModel,
    StateModelModel,
    StateModelsModel,
    create_node_introspection_response,
)


class NodeIntrospectionMixin(ABC):
    """
    Base mixin providing standardized introspection capabilities for ONEX nodes.

    All ONEX nodes should inherit from this mixin to provide consistent
    --introspect functionality that enables auto-discovery and validation.

    Usage:
        class MyNode(NodeIntrospectionMixin):
            @classmethod
            def get_node_name(cls) -> str:
                return "my_node"

            # ... implement other abstract methods
    """

    @classmethod
    @abstractmethod
    def get_node_name(cls) -> str:
        """Return the canonical node name."""
        pass

    @classmethod
    @abstractmethod
    def get_node_version(cls) -> str:
        """Return the node version."""
        pass

    @classmethod
    @abstractmethod
    def get_node_description(cls) -> str:
        """Return the node description."""
        pass

    @classmethod
    @abstractmethod
    def get_input_state_class(cls) -> Type[BaseModel]:
        """Return the input state model class."""
        pass

    @classmethod
    @abstractmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        """Return the output state model class."""
        pass

    @classmethod
    @abstractmethod
    def get_error_codes_class(cls) -> Type:
        """Return the error codes enum class."""
        pass

    @classmethod
    def get_node_author(cls) -> str:
        """Return the node author. Override if different from default."""
        return "ONEX Team"

    @classmethod
    def get_schema_version(cls) -> str:
        """Return the schema version. Override if different from default."""
        return "1.0.0"

    @classmethod
    def get_protocol_version(cls) -> str:
        """Return the protocol version. Override if different from default."""
        return "1.1.0"

    @classmethod
    def get_python_version_requirement(cls) -> str:
        """Return Python version requirement. Override if different from default."""
        return ">=3.11"

    @classmethod
    def get_runtime_dependencies(cls) -> List[str]:
        """Return runtime dependencies. Override to specify dependencies."""
        return ["omnibase.core", "omnibase.model"]

    @classmethod
    def get_optional_dependencies(cls) -> List[str]:
        """Return optional dependencies. Override to specify optional deps."""
        return []

    @classmethod
    def get_external_tools(cls) -> List[str]:
        """Return external tool dependencies. Override to specify tools."""
        return []

    @classmethod
    def get_node_capabilities(cls) -> List[NodeCapabilityEnum]:
        """Return node capabilities. Override to specify capabilities."""
        return []

    @classmethod
    def get_cli_entrypoint(cls) -> str:
        """Return CLI entrypoint command. Override if different from default."""
        node_name = cls.get_node_name()
        return f"python -m omnibase.nodes.{node_name}.v1_0_0.node"

    @classmethod
    def get_cli_required_args(cls) -> List[CLIArgumentModel]:
        """Return required CLI arguments. Override to specify required args."""
        return []

    @classmethod
    def get_cli_optional_args(cls) -> List[CLIArgumentModel]:
        """Return optional CLI arguments. Override to specify optional args."""
        return [
            CLIArgumentModel(
                name="--introspect",
                type="bool",
                required=False,
                description="Display node contract and capabilities",
                default=None,
                choices=None,
            )
        ]

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        """Return possible CLI exit codes. Override if different from default."""
        return [0, 1, 2]

    @classmethod
    def _extract_state_model_fields(
        cls, model_class: Type[BaseModel]
    ) -> List[StateFieldModel]:
        """Extract field information from a Pydantic model."""
        fields = []

        for field_name, field_info in model_class.model_fields.items():
            # Get field type as string
            field_type = str(field_info.annotation) if field_info.annotation else "Any"

            # Determine if field is required
            is_required = field_info.is_required()

            # Get field description
            description = field_info.description or f"Field {field_name}"

            # Get default value
            default_value = (
                field_info.default if hasattr(field_info, "default") else None
            )

            fields.append(
                StateFieldModel(
                    name=field_name,
                    type=field_type,
                    required=is_required,
                    description=description,
                    default=default_value,
                )
            )

        return fields

    @classmethod
    def _extract_error_codes(cls) -> ErrorCodesModel:
        """Extract error codes from the node's error codes class."""
        error_codes_class = cls.get_error_codes_class()

        # Get component name (e.g., "STAMP" from StamperErrorCode)
        component = "UNKNOWN"
        if hasattr(error_codes_class, "__name__"):
            class_name = error_codes_class.__name__
            if class_name.endswith("ErrorCode"):
                # Extract component from class name (e.g., StamperErrorCode -> STAMP)
                component = class_name.replace("ErrorCode", "").upper()

        # Extract error codes
        codes = []
        if hasattr(error_codes_class, "__members__"):
            for error_code in error_codes_class.__members__.values():
                # Get error code details
                code_value = error_code.value

                # Extract number from code (e.g., "ONEX_STAMP_001_..." -> 1)
                number = 0
                if hasattr(error_code, "get_number"):
                    number = error_code.get_number()

                # Get description
                description = "Unknown error"
                if hasattr(error_code, "get_description"):
                    description = error_code.get_description()

                # Get exit code
                exit_code = 1
                if hasattr(error_code, "get_exit_code"):
                    exit_code = error_code.get_exit_code()

                # Determine category from code name
                category = "general"
                if "_FILE_" in code_value:
                    category = "file"
                elif "_DIRECTORY_" in code_value:
                    category = "directory"
                elif "_VALIDATION_" in code_value:
                    category = "validation"
                elif "_CONFIG" in code_value:
                    category = "configuration"

                codes.append(
                    ErrorCodeModel(
                        code=code_value,
                        number=number,
                        description=description,
                        exit_code=exit_code,
                        category=category,
                    )
                )

        return ErrorCodesModel(component=component, codes=codes, total_codes=len(codes))

    @classmethod
    def get_introspection_response(cls) -> NodeIntrospectionResponse:
        """
        Generate complete introspection response for the node.

        Returns:
            NodeIntrospectionResponse with all node metadata and capabilities
        """
        from omnibase.core.version_resolver import global_resolver

        node_name = cls.get_node_name()

        # Get version information from resolver
        version_info = global_resolver.get_version_info(node_name)

        # Create enhanced node metadata with version information
        node_metadata = NodeMetadataModel(
            name=node_name,
            version=cls.get_node_version(),
            description=cls.get_node_description(),
            author=cls.get_node_author(),
            schema_version=cls.get_schema_version(),
            created_at=None,  # Could be extracted from metadata if available
            last_modified_at=None,  # Could be extracted from metadata if available
            # Enhanced version information
            available_versions=version_info.get("available_versions", []),
            latest_version=version_info.get("latest_version"),
            total_versions=version_info.get("total_versions", 0),
            version_status=version_info.get("version_status", {}),
            # Ecosystem information
            category=cls._get_node_category(),
            tags=cls._get_node_tags(),
            maturity=cls._get_node_maturity(),
            use_cases=cls._get_node_use_cases(),
            performance_profile=cls._get_performance_profile(),
        )

        # Create contract model
        contract = ContractModel(
            input_state_schema=f"{node_name}_input.schema.json",
            output_state_schema=f"{node_name}_output.schema.json",
            cli_interface=CLIInterfaceModel(
                entrypoint=cls.get_cli_entrypoint(),
                required_args=cls.get_cli_required_args(),
                optional_args=cls.get_cli_optional_args(),
                exit_codes=cls.get_cli_exit_codes(),
                supports_introspect=True,
            ),
            protocol_version=cls.get_protocol_version(),
        )

        # Create state models
        input_class = cls.get_input_state_class()
        output_class = cls.get_output_state_class()

        state_models = StateModelsModel(
            input=StateModelModel(
                class_name=input_class.__name__,
                schema_version=cls.get_schema_version(),
                fields=cls._extract_state_model_fields(input_class),
                schema_file=f"{node_name}_input.schema.json",
            ),
            output=StateModelModel(
                class_name=output_class.__name__,
                schema_version=cls.get_schema_version(),
                fields=cls._extract_state_model_fields(output_class),
                schema_file=f"{node_name}_output.schema.json",
            ),
        )

        # Create error codes model
        error_codes = cls._extract_error_codes()

        # Create dependencies model
        dependencies = DependenciesModel(
            runtime=cls.get_runtime_dependencies(),
            optional=cls.get_optional_dependencies(),
            python_version=cls.get_python_version_requirement(),
            external_tools=cls.get_external_tools(),
        )

        # Get capabilities
        capabilities = cls.get_node_capabilities()

        # Create and return the complete response
        return create_node_introspection_response(
            node_metadata=node_metadata,
            contract=contract,
            state_models=state_models,
            error_codes=error_codes,
            dependencies=dependencies,
            capabilities=capabilities,
            introspection_version="1.1.0",  # Enhanced version with ecosystem info
        )

    @classmethod
    def _get_node_category(cls) -> str:
        """Return node category. Override to specify category."""
        return "utility"

    @classmethod
    def _get_node_tags(cls) -> List[str]:
        """Return node tags. Override to specify tags."""
        return []

    @classmethod
    def _get_node_maturity(cls) -> str:
        """Return node maturity level. Override to specify maturity."""
        return "stable"

    @classmethod
    def _get_node_use_cases(cls) -> List[str]:
        """Return node use cases. Override to specify use cases."""
        return []

    @classmethod
    def _get_performance_profile(cls) -> Dict[str, Any]:
        """Return performance profile. Override to specify performance characteristics."""
        return {
            "typical_execution_time": "unknown",
            "memory_usage": "unknown",
            "cpu_intensive": False,
        }

    @classmethod
    def handle_introspect_command(cls) -> None:
        """
        Handle the --introspect command by generating and printing the response.

        This method should be called from the node's main() function when
        --introspect is detected in the command line arguments.
        """
        try:
            response = cls.get_introspection_response()
            print(response.model_dump_json(indent=2))
            sys.exit(0)
        except Exception as e:
            error_response = {
                "error": "Introspection failed",
                "message": str(e),
                "node": cls.get_node_name(),
            }
            print(json.dumps(error_response, indent=2))
            sys.exit(1)
