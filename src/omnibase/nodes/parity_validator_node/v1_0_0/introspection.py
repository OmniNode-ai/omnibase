# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: introspection.py
# version: 1.0.0
# uuid: fa458511-8903-4aaf-ac0a-634fbd5b6903
# author: OmniNode Team
# created_at: 2025-05-25T17:41:00.489162
# last_modified_at: 2025-05-25T22:11:50.182183
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: af673743af6538c60c4edbad5f72f15dace44b8bfbf25dfa55d41fb6e6c594fb
# entrypoint: python@introspection.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.introspection
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Introspection implementation for parity validator node.

This module provides the concrete introspection capabilities for the parity validator node,
implementing the NodeIntrospectionMixin interface.
"""

from typing import Any, Dict, List, Type

from pydantic import BaseModel

from omnibase.mixin.introspection_mixin import NodeIntrospectionMixin
from omnibase.model.model_node_introspection import CLIArgumentModel, NodeCapabilityEnum

from .error_codes import ParityValidatorErrorCode
from .models.state import ParityValidatorInputState, ParityValidatorOutputState


class ParityValidatorNodeIntrospection(NodeIntrospectionMixin):
    """Introspection implementation for parity validator node."""

    @classmethod
    def get_node_name(cls) -> str:
        """Return the canonical node name."""
        return "parity_validator_node"

    @classmethod
    def get_node_version(cls) -> str:
        """Return the node version."""
        return "1.0.0"

    @classmethod
    def get_node_description(cls) -> str:
        """Return node description."""
        return "ONEX parity validator for auto-discovering and validating all ONEX nodes for CLI/node parity, schema conformance, and contract compliance"

    @classmethod
    def _get_node_category(cls) -> str:
        """Return node category."""
        return "validation"

    @classmethod
    def _get_node_tags(cls) -> List[str]:
        """Return node tags."""
        return ["testing", "validation", "quality-assurance", "ci-cd", "auto-discovery"]

    @classmethod
    def _get_node_maturity(cls) -> str:
        """Return node maturity level."""
        return "stable"

    @classmethod
    def _get_node_use_cases(cls) -> List[str]:
        """Return node use cases."""
        return [
            "CI/CD validation pipelines",
            "Pre-commit hooks for quality assurance",
            "Third-party node validation",
            "Development testing and debugging",
            "Ecosystem compliance monitoring",
            "Automated quality gates",
        ]

    @classmethod
    def _get_performance_profile(cls) -> Dict[str, Any]:
        """Return performance profile."""
        return {
            "typical_execution_time": "1-5 seconds for 6 nodes",
            "memory_usage": "low (< 100MB)",
            "cpu_intensive": False,
            "scales_with": "number of nodes discovered",
            "parallel_execution": "sequential (planned: parallel)",
            "caching": "none (planned: validation result caching)",
        }

    @classmethod
    def get_input_state_class(cls) -> Type[BaseModel]:
        """Return the input state model class."""
        return ParityValidatorInputState

    @classmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        """Return the output state model class."""
        return ParityValidatorOutputState

    @classmethod
    def get_error_codes_class(cls) -> Type:
        """Return the error codes enum class."""
        return ParityValidatorErrorCode

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
            "omnibase.mixin",
            "omnibase.utils",
            "omnibase.nodes",
        ]

    @classmethod
    def get_optional_dependencies(cls) -> List[str]:
        """Return optional dependencies."""
        return ["omnibase.runtimes.onex_runtime"]

    @classmethod
    def get_node_capabilities(cls) -> List[NodeCapabilityEnum]:
        """Return node capabilities."""
        return [
            NodeCapabilityEnum.SUPPORTS_BATCH_PROCESSING,
            NodeCapabilityEnum.TELEMETRY_ENABLED,
            NodeCapabilityEnum.SUPPORTS_CORRELATION_ID,
            NodeCapabilityEnum.SUPPORTS_EVENT_BUS,
            NodeCapabilityEnum.SUPPORTS_SCHEMA_VALIDATION,
            NodeCapabilityEnum.SUPPORTS_ERROR_RECOVERY,
        ]

    @classmethod
    def get_cli_required_args(cls) -> List[CLIArgumentModel]:
        """Return required CLI arguments."""
        return []  # Parity validator has no required args - uses sensible defaults

    @classmethod
    def get_cli_optional_args(cls) -> List[CLIArgumentModel]:
        """Return optional CLI arguments."""
        base_args = super().get_cli_optional_args()
        parity_args = [
            CLIArgumentModel(
                name="--nodes-directory",
                type="str",
                required=True,
                description="Directory containing ONEX nodes to validate",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--validation-types",
                type="List[str]",
                required=False,
                description="Specific validation types to run",
                default=None,
                choices=[
                    "cli_node_parity",
                    "schema_conformance",
                    "error_code_usage",
                    "contract_compliance",
                    "introspection_validity",
                ],
            ),
            CLIArgumentModel(
                name="--node-filter",
                type="str",
                required=False,
                description="Filter nodes by name pattern",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--fail-fast",
                type="bool",
                required=False,
                description="Stop validation on first failure",
                default=False,
                choices=None,
            ),
            CLIArgumentModel(
                name="--no-performance-metrics",
                type="bool",
                required=False,
                description="Disable performance timing in results",
                default=False,
                choices=None,
            ),
            CLIArgumentModel(
                name="--format",
                type="str",
                required=False,
                description="Output format for validation results",
                default="summary",
                choices=["json", "summary", "detailed"],
            ),
            CLIArgumentModel(
                name="--include-performance-metrics",
                type="bool",
                required=False,
                description="Include performance metrics in output",
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
                name="--introspect",
                type="bool",
                required=False,
                description="Show node introspection information",
                default=False,
                choices=None,
            ),
        ]
        return base_args + parity_args

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        """Return possible CLI exit codes."""
        return [0, 1, 2, 3, 4, 5, 6]  # Full range of ONEX exit codes
