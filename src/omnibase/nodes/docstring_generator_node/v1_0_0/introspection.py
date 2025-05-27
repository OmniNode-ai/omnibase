# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: introspection.py
# version: 1.0.0
# uuid: 53fd7d63-862d-4b0a-b448-caf05ba6213c
# author: OmniNode Team
# created_at: 2025-05-27T07:34:49.189498
# last_modified_at: 2025-05-27T11:48:23.354421
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9c4d2b4ed0fcea2861efacc840f10044e3230c639bc8d3be603b6e134b913f66
# entrypoint: python@introspection.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.introspection
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Introspection implementation for docstring generator node.

This module provides the concrete introspection capabilities for the docstring generator node,
implementing the NodeIntrospectionMixin interface.
"""

from typing import List, Type

from pydantic import BaseModel

from omnibase.mixin.mixin_introspection import NodeIntrospectionMixin
from omnibase.model.model_node_introspection import CLIArgumentModel, NodeCapabilityEnum

from .error_codes import DocstringGeneratorErrorCode
from .models.state import DocstringGeneratorInputState, DocstringGeneratorOutputState


class DocstringGeneratorNodeIntrospection(NodeIntrospectionMixin):
    """Introspection implementation for docstring generator node."""

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
        return "ONEX docstring generator node for creating markdown documentation from JSON/YAML schemas"

    @classmethod
    def get_input_state_class(cls) -> Type[BaseModel]:
        """Return the input state model class."""
        return DocstringGeneratorInputState

    @classmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        """Return the output state model class."""
        return DocstringGeneratorOutputState

    @classmethod
    def get_error_codes_class(cls) -> Type:
        """Return the error codes enum class."""
        return DocstringGeneratorErrorCode

    @classmethod
    def get_schema_version(cls) -> str:
        """Return the schema version."""
        return "1.0.0"

    @classmethod
    def get_runtime_dependencies(cls) -> List[str]:
        """Return runtime dependencies."""
        return [
            "omnibase.core",
            "omnibase.model",
            "omnibase.utils",
            "jinja2",
            "pyyaml",
        ]

    @classmethod
    def get_optional_dependencies(cls) -> List[str]:
        """Return optional dependencies."""
        return ["omnibase.runtimes.onex_runtime"]

    @classmethod
    def get_node_capabilities(cls) -> List[NodeCapabilityEnum]:
        """Return node capabilities."""
        return [
            NodeCapabilityEnum.SUPPORTS_DRY_RUN,
            NodeCapabilityEnum.TELEMETRY_ENABLED,
            NodeCapabilityEnum.SUPPORTS_CORRELATION_ID,
            NodeCapabilityEnum.SUPPORTS_EVENT_BUS,
            NodeCapabilityEnum.SUPPORTS_SCHEMA_VALIDATION,
        ]

    @classmethod
    def get_cli_required_args(cls) -> List[CLIArgumentModel]:
        """Return required CLI arguments."""
        return [
            CLIArgumentModel(
                name="--schema-directory",
                type="str",
                required=True,
                description="Directory containing JSON/YAML schema files to process",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--template-path",
                type="str",
                required=True,
                description="Path to the Jinja2 template file for documentation generation",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--output-directory",
                type="str",
                required=True,
                description="Directory where generated markdown files will be written",
                default=None,
                choices=None,
            ),
        ]

    @classmethod
    def get_cli_optional_args(cls) -> List[CLIArgumentModel]:
        """Return optional CLI arguments."""
        base_args = super().get_cli_optional_args()
        docstring_args = [
            CLIArgumentModel(
                name="--changelog-path",
                type="str",
                required=False,
                description="Optional path to changelog file to include in generated docs",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--include-examples",
                type="bool",
                required=False,
                description="Include schema examples in generated documentation",
                default=True,
                choices=None,
            ),
            CLIArgumentModel(
                name="--dry-run",
                type="bool",
                required=False,
                description="Show what would be generated without creating files",
                default=False,
                choices=None,
            ),
            CLIArgumentModel(
                name="--force",
                type="bool",
                required=False,
                description="Overwrite existing files",
                default=False,
                choices=None,
            ),
            CLIArgumentModel(
                name="--introspect",
                type="bool",
                required=False,
                description="Show node introspection information",
                default=False,
                choices=None,
            ),
            CLIArgumentModel(
                name="--correlation-id",
                type="str",
                required=False,
                description="Correlation ID for request tracking",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--verbose",
                type="bool",
                required=False,
                description="Enable verbose output",
                default=False,
                choices=None,
            ),
        ]
        return base_args + docstring_args

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        """Return possible CLI exit codes."""
        return [0, 1, 2, 3, 4, 5, 6]  # Full range of ONEX exit codes
