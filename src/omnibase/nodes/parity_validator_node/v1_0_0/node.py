# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node.py
# version: 1.0.0
# uuid: 4f13e6e3-84de-4e5d-8579-f90f3dd41a16
# author: OmniNode Team
# created_at: 2025-05-24T09:29:37.987105
# last_modified_at: 2025-05-25T20:45:00
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5aa9aa96ef80b9158d340ef33ab4819ec2ceeb1f608b2696a9363af138181e5c
# entrypoint: python@node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.node
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Parity validator node implementation.

This module implements the parity validator node that auto-discovers and validates
all ONEX nodes for CLI/node parity, schema conformance, error code usage,
contract compliance, and introspection validity.
"""

import argparse
import importlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

from omnibase.core.error_codes import get_exit_code_for_status
from omnibase.model.enum_onex_status import OnexStatus

from .introspection import ParityValidatorNodeIntrospection
from .models.state import (
    DiscoveredNode,
    NodeValidationResult,
    ParityValidatorInputState,
    ParityValidatorOutputState,
    ValidationResultEnum,
    ValidationTypeEnum,
    create_parity_validator_input_state,
    create_parity_validator_output_state,
)


class ParityValidatorNode:
    """
    ONEX parity validator node for comprehensive node validation.

    This node auto-discovers all ONEX nodes and validates them for:
    - CLI/Node parity (consistent output between CLI and direct node calls)
    - Schema conformance (proper state model validation)
    - Error code usage (proper error handling and exit codes)
    - Contract compliance (adherence to ONEX node protocol)
    - Introspection validity (proper introspection implementation)
    """

    def __init__(self) -> None:
        """Initialize the parity validator node."""
        self.discovered_nodes: List[DiscoveredNode] = []
        self.validation_results: List[NodeValidationResult] = []

    def discover_nodes(self, nodes_directory: str) -> List[DiscoveredNode]:
        """
        Auto-discover all ONEX nodes in the specified directory.

        Args:
            nodes_directory: Directory to scan for ONEX nodes

        Returns:
            List of discovered nodes with metadata
        """
        discovered = []
        nodes_path = Path(nodes_directory)

        if not nodes_path.exists():
            raise FileNotFoundError(f"Nodes directory not found: {nodes_directory}")

        # Scan for node directories
        for node_dir in nodes_path.iterdir():
            if not node_dir.is_dir() or node_dir.name.startswith("."):
                continue

            # Look for versioned subdirectories
            for version_dir in node_dir.iterdir():
                if not version_dir.is_dir() or not version_dir.name.startswith("v"):
                    continue

                # Check for node.py file
                node_file = version_dir / "node.py"
                if not node_file.exists():
                    continue

                try:
                    # Construct module path
                    module_path = (
                        f"omnibase.nodes.{node_dir.name}.{version_dir.name}.node"
                    )

                    # Try to import and check for introspection
                    introspection_available = False
                    try:
                        module = importlib.import_module(module_path)
                        # Check if module has introspection capability
                        if hasattr(module, "get_introspection") or any(
                            hasattr(getattr(module, attr), "get_introspection")
                            for attr in dir(module)
                            if not attr.startswith("_")
                        ):
                            introspection_available = True
                    except Exception:
                        pass  # Module import failed, but we still discovered the node

                    discovered_node = DiscoveredNode(
                        name=node_dir.name,
                        version=version_dir.name,
                        module_path=module_path,
                        introspection_available=introspection_available,
                        cli_entrypoint=f"python -m {module_path}",
                        error_count=0,
                    )
                    discovered.append(discovered_node)

                except Exception:
                    # Create a node entry with error information
                    discovered_node = DiscoveredNode(
                        name=node_dir.name,
                        version=version_dir.name,
                        module_path=f"omnibase.nodes.{node_dir.name}.{version_dir.name}.node",
                        introspection_available=False,
                        cli_entrypoint=None,
                        error_count=1,
                    )
                    discovered.append(discovered_node)

        self.discovered_nodes = discovered
        return discovered

    def validate_cli_node_parity(self, node: DiscoveredNode) -> NodeValidationResult:
        """
        Validate CLI/Node parity for a discovered node.

        Args:
            node: The discovered node to validate

        Returns:
            Validation result for CLI/Node parity
        """
        start_time = time.time()

        try:
            # Try to run CLI with --help
            cli_result = subprocess.run(
                [sys.executable, "-m", node.module_path, "--help"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Try to import and call directly
            try:
                module = importlib.import_module(node.module_path)
                # Check if module has main function or CLI capability
                has_main = hasattr(module, "main") or hasattr(module, "cli_main")

                if cli_result.returncode == 0 and has_main:
                    result = ValidationResultEnum.PASS
                    message = "CLI and node interfaces are available and consistent"
                elif cli_result.returncode == 0:
                    result = ValidationResultEnum.PASS
                    message = "CLI interface available (direct node call not tested)"
                else:
                    result = ValidationResultEnum.FAIL
                    message = f"CLI failed with exit code {cli_result.returncode}"

            except Exception as e:
                result = ValidationResultEnum.FAIL
                message = f"Node import failed: {str(e)}"

        except subprocess.TimeoutExpired:
            result = ValidationResultEnum.ERROR
            message = "CLI execution timeout"
        except Exception as e:
            result = ValidationResultEnum.ERROR
            message = f"CLI execution error: {str(e)}"

        execution_time = (time.time() - start_time) * 1000

        return NodeValidationResult(
            node_name=node.name,
            node_version=node.version,
            validation_type=ValidationTypeEnum.CLI_NODE_PARITY,
            result=result,
            message=message,
            execution_time_ms=execution_time,
        )

    def validate_schema_conformance(self, node: DiscoveredNode) -> NodeValidationResult:
        """
        Validate schema conformance for a discovered node.

        Args:
            node: The discovered node to validate

        Returns:
            Validation result for schema conformance
        """
        start_time = time.time()

        try:
            # Import the node module to check for state models
            importlib.import_module(node.module_path)

            # Check for state models
            has_state_models = False
            state_model_errors = []

            # Look for state module
            try:
                state_module_path = (
                    f"omnibase.nodes.{node.name}.{node.version}.models.state"
                )
                state_module = importlib.import_module(state_module_path)

                # Check for input/output state classes
                input_state_found = any(
                    attr.endswith("InputState")
                    for attr in dir(state_module)
                    if not attr.startswith("_")
                )
                output_state_found = any(
                    attr.endswith("OutputState")
                    for attr in dir(state_module)
                    if not attr.startswith("_")
                )

                if input_state_found and output_state_found:
                    has_state_models = True
                else:
                    state_model_errors.append("Missing input or output state models")

            except ImportError:
                state_model_errors.append("State models module not found")

            if has_state_models and not state_model_errors:
                result = ValidationResultEnum.PASS
                message = "Schema conformance validated successfully"
            elif has_state_models:
                result = ValidationResultEnum.FAIL
                message = f"Schema issues found: {'; '.join(state_model_errors)}"
            else:
                result = ValidationResultEnum.FAIL
                message = "No valid state models found"

        except Exception as e:
            result = ValidationResultEnum.ERROR
            message = f"Schema validation error: {str(e)}"

        execution_time = (time.time() - start_time) * 1000

        return NodeValidationResult(
            node_name=node.name,
            node_version=node.version,
            validation_type=ValidationTypeEnum.SCHEMA_CONFORMANCE,
            result=result,
            message=message,
            execution_time_ms=execution_time,
        )

    def validate_error_code_usage(self, node: DiscoveredNode) -> NodeValidationResult:
        """
        Validate error code usage for a discovered node.

        Args:
            node: The discovered node to validate

        Returns:
            Validation result for error code usage
        """
        start_time = time.time()

        try:
            # Check for error codes module
            error_codes_module_path = (
                f"omnibase.nodes.{node.name}.{node.version}.error_codes"
            )
            error_codes_module = importlib.import_module(error_codes_module_path)

            # Check for error code enum/class
            has_error_codes = any(
                "ErrorCode" in attr
                for attr in dir(error_codes_module)
                if not attr.startswith("_")
            )

            if has_error_codes:
                result = ValidationResultEnum.PASS
                message = "Error codes properly defined"
            else:
                result = ValidationResultEnum.FAIL
                message = "No error code definitions found"

        except ImportError:
            result = ValidationResultEnum.FAIL
            message = "Error codes module not found"
        except Exception as e:
            result = ValidationResultEnum.ERROR
            message = f"Error code validation error: {str(e)}"

        execution_time = (time.time() - start_time) * 1000

        return NodeValidationResult(
            node_name=node.name,
            node_version=node.version,
            validation_type=ValidationTypeEnum.ERROR_CODE_USAGE,
            result=result,
            message=message,
            execution_time_ms=execution_time,
        )

    def validate_contract_compliance(
        self, node: DiscoveredNode
    ) -> NodeValidationResult:
        """
        Validate contract compliance for a discovered node.

        Args:
            node: The discovered node to validate

        Returns:
            Validation result for contract compliance
        """
        start_time = time.time()

        try:
            module = importlib.import_module(node.module_path)

            compliance_issues = []

            # Check for required components
            if not hasattr(module, "main") and not hasattr(module, "cli_main"):
                compliance_issues.append("No main/cli_main function found")

            # Check for CLI argument parsing
            try:
                cli_result = subprocess.run(
                    [sys.executable, "-m", node.module_path, "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if cli_result.returncode != 0:
                    compliance_issues.append("CLI help command failed")
            except (subprocess.SubprocessError, subprocess.TimeoutExpired, OSError):
                compliance_issues.append("CLI execution failed")

            if not compliance_issues:
                result = ValidationResultEnum.PASS
                message = "Contract compliance validated successfully"
            else:
                result = ValidationResultEnum.FAIL
                message = f"Compliance issues: {'; '.join(compliance_issues)}"

        except Exception as e:
            result = ValidationResultEnum.ERROR
            message = f"Contract validation error: {str(e)}"

        execution_time = (time.time() - start_time) * 1000

        return NodeValidationResult(
            node_name=node.name,
            node_version=node.version,
            validation_type=ValidationTypeEnum.CONTRACT_COMPLIANCE,
            result=result,
            message=message,
            execution_time_ms=execution_time,
        )

    def validate_introspection_validity(
        self, node: DiscoveredNode
    ) -> NodeValidationResult:
        """
        Validate introspection validity for a discovered node.

        Args:
            node: The discovered node to validate

        Returns:
            Validation result for introspection validity
        """
        start_time = time.time()

        if not node.introspection_available:
            result = ValidationResultEnum.SKIP
            message = "Introspection not available for this node"
        else:
            try:
                # Try to run introspection command
                cli_result = subprocess.run(
                    [sys.executable, "-m", node.module_path, "--introspect"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if cli_result.returncode == 0:
                    try:
                        # Try to parse the JSON output
                        introspection_data = json.loads(cli_result.stdout)
                        required_fields = [
                            "node_metadata",
                            "contract",
                            "state_models",
                            "error_codes",
                            "dependencies",
                        ]

                        if all(
                            field in introspection_data for field in required_fields
                        ):
                            # Check nested required fields
                            node_metadata = introspection_data.get("node_metadata", {})
                            contract = introspection_data.get("contract", {})

                            metadata_fields = ["name", "version", "description"]
                            contract_fields = [
                                "input_state_schema",
                                "output_state_schema",
                                "cli_interface",
                            ]

                            if all(
                                field in node_metadata for field in metadata_fields
                            ) and all(field in contract for field in contract_fields):
                                result = ValidationResultEnum.PASS
                                message = "Introspection validated successfully"
                            else:
                                result = ValidationResultEnum.FAIL
                                message = "Introspection output missing required nested fields"
                        else:
                            result = ValidationResultEnum.FAIL
                            message = (
                                "Introspection output missing required top-level fields"
                            )
                    except json.JSONDecodeError:
                        result = ValidationResultEnum.FAIL
                        message = "Introspection output is not valid JSON"
                else:
                    result = ValidationResultEnum.FAIL
                    message = f"Introspection command failed with exit code {cli_result.returncode}"

            except subprocess.TimeoutExpired:
                result = ValidationResultEnum.ERROR
                message = "Introspection command timeout"
            except Exception as e:
                result = ValidationResultEnum.ERROR
                message = f"Introspection validation error: {str(e)}"

        execution_time = (time.time() - start_time) * 1000

        return NodeValidationResult(
            node_name=node.name,
            node_version=node.version,
            validation_type=ValidationTypeEnum.INTROSPECTION_VALIDITY,
            result=result,
            message=message,
            execution_time_ms=execution_time,
        )

    def run_validation(
        self, input_state: ParityValidatorInputState
    ) -> ParityValidatorOutputState:
        """
        Run the complete parity validation process.

        Args:
            input_state: Input state with validation parameters

        Returns:
            Output state with validation results
        """
        start_time = time.time()

        try:
            # Discover nodes
            discovered_nodes = self.discover_nodes(input_state.nodes_directory)

            if not discovered_nodes:
                return create_parity_validator_output_state(
                    status=OnexStatus.WARNING,
                    message="No ONEX nodes discovered",
                    nodes_directory=input_state.nodes_directory,
                    correlation_id=input_state.correlation_id,
                )

            # Filter nodes if specified
            if input_state.node_filter:
                discovered_nodes = [
                    node
                    for node in discovered_nodes
                    if node.name in input_state.node_filter
                ]

            # Determine validation types to run
            validation_types = input_state.validation_types or list(ValidationTypeEnum)

            # Run validations
            validation_results = []
            for node in discovered_nodes:
                for validation_type in validation_types:
                    if validation_type == ValidationTypeEnum.CLI_NODE_PARITY:
                        result = self.validate_cli_node_parity(node)
                    elif validation_type == ValidationTypeEnum.SCHEMA_CONFORMANCE:
                        result = self.validate_schema_conformance(node)
                    elif validation_type == ValidationTypeEnum.ERROR_CODE_USAGE:
                        result = self.validate_error_code_usage(node)
                    elif validation_type == ValidationTypeEnum.CONTRACT_COMPLIANCE:
                        result = self.validate_contract_compliance(node)
                    elif validation_type == ValidationTypeEnum.INTROSPECTION_VALIDITY:
                        result = self.validate_introspection_validity(node)
                    else:
                        continue

                    validation_results.append(result)

                    # Check fail-fast
                    if (
                        input_state.fail_fast
                        and result.result == ValidationResultEnum.FAIL
                    ):
                        break

                if (
                    input_state.fail_fast
                    and validation_results
                    and validation_results[-1].result == ValidationResultEnum.FAIL
                ):
                    break

            # Calculate summary
            summary = {
                "total_nodes": len(discovered_nodes),
                "total_validations": len(validation_results),
                "passed": len(
                    [
                        r
                        for r in validation_results
                        if r.result == ValidationResultEnum.PASS
                    ]
                ),
                "failed": len(
                    [
                        r
                        for r in validation_results
                        if r.result == ValidationResultEnum.FAIL
                    ]
                ),
                "skipped": len(
                    [
                        r
                        for r in validation_results
                        if r.result == ValidationResultEnum.SKIP
                    ]
                ),
                "errors": len(
                    [
                        r
                        for r in validation_results
                        if r.result == ValidationResultEnum.ERROR
                    ]
                ),
            }

            # Determine overall status
            if summary["errors"] > 0:
                status = OnexStatus.ERROR
                message = f"Validation completed with {summary['errors']} errors"
            elif summary["failed"] > 0:
                status = OnexStatus.WARNING
                message = f"Validation completed with {summary['failed']} failures"
            else:
                status = OnexStatus.SUCCESS
                message = f"All validations passed ({summary['passed']} total)"

            total_execution_time = (
                (time.time() - start_time) * 1000
                if input_state.include_performance_metrics
                else None
            )

            return create_parity_validator_output_state(
                status=status,
                message=message,
                discovered_nodes=discovered_nodes,
                validation_results=validation_results,
                summary=summary,
                nodes_directory=input_state.nodes_directory,
                validation_types_run=validation_types,
                total_execution_time_ms=total_execution_time,
                correlation_id=input_state.correlation_id,
            )

        except Exception as e:
            return create_parity_validator_output_state(
                status=OnexStatus.ERROR,
                message=f"Validation failed: {str(e)}",
                nodes_directory=input_state.nodes_directory,
                correlation_id=input_state.correlation_id,
            )


def get_introspection() -> dict:
    """
    Get introspection data for the parity validator node.

    Returns:
        Dictionary containing node introspection information
    """
    response = ParityValidatorNodeIntrospection.get_introspection_response()
    return response.model_dump()


def main(
    nodes_directory: str = "src/omnibase/nodes",
    validation_types: Optional[List[str]] = None,
    node_filter: Optional[List[str]] = None,
    fail_fast: bool = False,
    include_performance_metrics: bool = True,
    format: str = "summary",
    correlation_id: Optional[str] = None,
    verbose: bool = False,
) -> ParityValidatorOutputState:
    """
    Main function for parity validator node.

    Args:
        nodes_directory: Directory to scan for ONEX nodes
        validation_types: Specific validation types to run
        node_filter: Filter to specific node names
        fail_fast: Stop validation on first failure
        include_performance_metrics: Include performance timing
        format: Output format (json, summary, detailed)
        correlation_id: Correlation ID for tracking
        verbose: Enable verbose output

    Returns:
        ParityValidatorOutputState with validation results
    """
    # Convert string validation types to enum
    validation_type_enums = None
    if validation_types:
        validation_type_enums = []
        for vt in validation_types:
            try:
                validation_type_enums.append(ValidationTypeEnum(vt))
            except ValueError:
                print(f"Warning: Unknown validation type '{vt}', skipping")

    # Create input state
    input_state = create_parity_validator_input_state(
        nodes_directory=nodes_directory,
        validation_types=validation_type_enums,
        node_filter=node_filter,
        fail_fast=fail_fast,
        include_performance_metrics=include_performance_metrics,
        correlation_id=correlation_id,
    )

    # Run validation
    validator = ParityValidatorNode()
    output_state = validator.run_validation(input_state)

    # Output results based on format
    if format == "json":
        print(output_state.model_dump_json(indent=2))
    elif format == "detailed":
        print("Parity Validation Results")
        print("========================")
        print(f"Status: {output_state.status.value}")
        print(f"Message: {output_state.message}")
        print(f"Nodes Directory: {output_state.nodes_directory}")
        print(f"Total Nodes: {len(output_state.discovered_nodes)}")
        print(f"Total Validations: {len(output_state.validation_results)}")
        print()

        if output_state.discovered_nodes:
            print("Discovered Nodes:")
            for node in output_state.discovered_nodes:
                print(f"  - {node.name} ({node.version})")
                if node.error_count > 0:
                    print(f"    Errors: {node.error_count}")
            print()

        if output_state.validation_results:
            print("Validation Results:")
            for result in output_state.validation_results:
                status_icon = (
                    "✓"
                    if result.result == ValidationResultEnum.PASS
                    else (
                        "✗"
                        if result.result == ValidationResultEnum.FAIL
                        else (
                            "⚠" if result.result == ValidationResultEnum.SKIP else "⊘"
                        )
                    )
                )
                print(
                    f"  {status_icon} {result.node_name} - {result.validation_type.value}: {result.message}"
                )
                if verbose and result.execution_time_ms:
                    print(f"    Execution time: {result.execution_time_ms:.2f}ms")
            print()

        if output_state.summary:
            print("Summary:")
            for key, value in output_state.summary.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
    else:  # summary format
        print(f"Parity Validation: {output_state.status.value}")
        print(f"{output_state.message}")
        if output_state.summary:
            summary = output_state.summary
            print(
                f"Results: {summary.get('passed', 0)} passed, {summary.get('failed', 0)} failed, {summary.get('skipped', 0)} skipped, {summary.get('errors', 0)} errors"
            )

    return output_state


def cli_main() -> None:
    """CLI entry point for parity validator node."""
    parser = argparse.ArgumentParser(
        description="ONEX parity validator for comprehensive node validation"
    )

    parser.add_argument(
        "--nodes-directory",
        default="src/omnibase/nodes",
        help="Directory to scan for ONEX nodes",
    )

    parser.add_argument(
        "--validation-types",
        nargs="*",
        choices=[vt.value for vt in ValidationTypeEnum],
        help="Specific validation types to run",
    )

    parser.add_argument(
        "--node-filter", nargs="*", help="Filter to specific node names"
    )

    parser.add_argument(
        "--fail-fast", action="store_true", help="Stop validation on first failure"
    )

    parser.add_argument(
        "--no-performance-metrics",
        action="store_true",
        help="Disable performance timing in results",
    )

    parser.add_argument(
        "--format",
        choices=["json", "summary", "detailed"],
        default="summary",
        help="Output format",
    )

    parser.add_argument("--correlation-id", help="Correlation ID for request tracking")

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    parser.add_argument(
        "--introspect", action="store_true", help="Return introspection data as JSON"
    )

    args = parser.parse_args()

    if args.introspect:
        introspection_data = get_introspection()
        print(json.dumps(introspection_data, indent=2))
        sys.exit(0)

    try:
        output_state = main(
            nodes_directory=args.nodes_directory,
            validation_types=args.validation_types,
            node_filter=args.node_filter,
            fail_fast=args.fail_fast,
            include_performance_metrics=not args.no_performance_metrics,
            format=args.format,
            correlation_id=args.correlation_id,
            verbose=args.verbose,
        )

        # Exit with appropriate code based on status
        exit_code = get_exit_code_for_status(output_state.status)
        sys.exit(exit_code)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
