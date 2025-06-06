# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-06-03T00:00:00.000000'
# description: Stamped by PythonHandler
# entrypoint: python://introspection
# hash: <to-be-stamped>
# last_modified_at: '2025-06-03T00:00:00.000000+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: introspection.py
# namespace: python://omnibase.nodes.runtime_node.v1_0_0.introspection
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 1.0.0
# state_contract: state_contract://default
# tools: null
# uuid: <to-be-stamped>
# version: 1.0.0
# === /OmniNode:Metadata ===

"""
Introspection implementation for runtime node.
Implements NodeIntrospectionMixin for standards-compliant introspection.
"""
from pathlib import Path
from typing import List, Optional, Type

import yaml
from pydantic import BaseModel

from omnibase.mixin.mixin_introspection import NodeIntrospectionMixin
from omnibase.model.model_node_introspection import CLIArgumentModel, NodeCapabilityEnum
from omnibase.nodes.parity_validator_node.v1_0_0.helpers.parity_node_metadata_loader import (
    NodeMetadataLoader,
)

from .error_codes import RuntimeErrorCode
from .models.state import RuntimeNodeInputState, RuntimeNodeOutputState


class RuntimeNodeIntrospection(NodeIntrospectionMixin):
    _metadata_loader: Optional[NodeMetadataLoader] = None

    @classmethod
    def _get_metadata_loader(cls) -> NodeMetadataLoader:
        if cls._metadata_loader is None:
            current_file = Path(__file__)
            node_directory = current_file.parent
            cls._metadata_loader = NodeMetadataLoader(node_directory)
        return cls._metadata_loader

    @classmethod
    def get_node_name(cls) -> str:
        return cls._get_metadata_loader().node_name

    @classmethod
    def get_node_version(cls) -> str:
        return cls._get_metadata_loader().node_version

    @classmethod
    def get_node_description(cls) -> str:
        return cls._get_metadata_loader().node_description

    @classmethod
    def get_input_state_class(cls) -> Type[BaseModel]:
        return RuntimeNodeInputState

    @classmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        return RuntimeNodeOutputState

    @classmethod
    def get_error_codes_class(cls) -> Type:
        return RuntimeErrorCode

    @classmethod
    def get_schema_version(cls) -> str:
        return "1.0.0"

    @classmethod
    def get_runtime_dependencies(cls) -> List[str]:
        return [
            "omnibase.core",
            "omnibase.model",
            "omnibase.utils",
        ]

    @classmethod
    def get_optional_dependencies(cls) -> List[str]:
        return ["omnibase.runtimes.onex_runtime"]

    @classmethod
    def get_node_capabilities(cls) -> List[NodeCapabilityEnum]:
        return [
            NodeCapabilityEnum.SUPPORTS_DRY_RUN,
            NodeCapabilityEnum.TELEMETRY_ENABLED,
            NodeCapabilityEnum.SUPPORTS_CORRELATION_ID,
            NodeCapabilityEnum.SUPPORTS_EVENT_BUS,
            NodeCapabilityEnum.SUPPORTS_SCHEMA_VALIDATION,
        ]

    @classmethod
    def get_cli_required_args(cls) -> List[CLIArgumentModel]:
        return [
            CLIArgumentModel(
                name="--required-field",
                type="str",
                required=True,
                description="Required input field for runtime_node",
                default=None,
                choices=None,
            ),
        ]

    @classmethod
    def get_cli_optional_args(cls) -> List[CLIArgumentModel]:
        base_args = super().get_cli_optional_args()
        runtime_args = [
            CLIArgumentModel(
                name="--optional-field",
                type="str",
                required=False,
                description="Optional input field for runtime_node",
                default=None,
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
        return base_args + runtime_args

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        return [0, 1, 2, 3, 4, 5, 6]

    @classmethod
    def get_scenarios(cls) -> list:
        scenarios_index_path = Path(__file__).parent / "scenarios" / "index.yaml"
        if not scenarios_index_path.exists():
            return []
        with open(scenarios_index_path, "r") as f:
            data = yaml.safe_load(f)
        return data.get("scenarios", data)

    @classmethod
    def get_introspection_response(cls) -> dict:
        return {
            "node_name": cls.get_node_name(),
            "node_version": cls.get_node_version(),
            "node_description": cls.get_node_description(),
            "schema_version": cls.get_schema_version(),
            "input_state_model": cls.get_input_state_class().__name__,
            "output_state_model": cls.get_output_state_class().__name__,
            "error_codes": [e.name for e in cls.get_error_codes_class()],
            "capabilities": [c.value for c in cls.get_node_capabilities()],
            "cli_required_args": [
                arg.model_dump() for arg in cls.get_cli_required_args()
            ],
            "cli_optional_args": [
                arg.model_dump() for arg in cls.get_cli_optional_args()
            ],
            "cli_exit_codes": cls.get_cli_exit_codes(),
            "scenarios": cls.get_scenarios(),
        }

    @classmethod
    def handle_introspect_command(cls, event_bus=None):
        import json

        print(json.dumps(cls.get_introspection_response(), indent=2))
