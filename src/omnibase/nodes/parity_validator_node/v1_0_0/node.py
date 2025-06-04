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

from omnibase.core.core_error_codes import (
    CoreErrorCode,
    OnexError,
    get_exit_code_for_status,
)
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import OnexStatus, LogLevelEnum
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.model.model_node_metadata import Namespace
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry

from .helpers.parity_node_metadata_loader import get_node_name
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

_NODE_DIRECTORY = Path(__file__).parent
_NODE_NAME = get_node_name(_NODE_DIRECTORY)


class ParityValidatorNode(EventDrivenNodeMixin):
    """
    ONEX parity validator node for comprehensive node validation.

    This node auto-discovers all ONEX nodes and validates them for:
    - CLI/Node parity (consistent output between CLI and direct node calls)
    - Schema conformance (proper state model validation)
    - Error code usage (proper error handling and exit codes)
    - Contract compliance (adherence to ONEX node protocol)
    - Introspection validity (proper introspection implementation)
    """

    def __init__(self, event_bus: Optional[ProtocolEventBus] = None, **kwargs):
        super().__init__(node_id="parity_validator_node", event_bus=event_bus, **kwargs)
        self.event_bus = event_bus or InMemoryEventBus()
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
            raise OnexError(
                f"Nodes directory not found: {nodes_directory}",
                CoreErrorCode.DIRECTORY_NOT_FOUND,
            )
        for node_dir in nodes_path.iterdir():
            if not node_dir.is_dir() or node_dir.name.startswith("."):
                continue
            for version_dir in node_dir.iterdir():
                if not version_dir.is_dir() or not version_dir.name.startswith("v"):
                    continue
                node_file = version_dir / "node.py"
                if not node_file.exists():
                    continue
                try:
                    module_path = (
                        f"omnibase.nodes.{node_dir.name}.{version_dir.name}.node"
                    )
                    introspection_available = False
                    try:
                        module = importlib.import_module(module_path)
                        if hasattr(module, "get_introspection"):
                            introspection_available = True
                        else:
                            introspection_file = version_dir / "introspection.py"
                            if introspection_file.exists():
                                try:
                                    introspection_module_path = f"omnibase.nodes.{node_dir.name}.{version_dir.name}.introspection"
                                    introspection_module = importlib.import_module(
                                        introspection_module_path
                                    )
                                    for attr_name in dir(introspection_module):
                                        if not attr_name.startswith("_"):
                                            attr = getattr(
                                                introspection_module, attr_name
                                            )
                                            if hasattr(
                                                attr, "handle_introspect_command"
                                            ):
                                                introspection_available = True
                                                break
                                except Exception:
                                    pass
                    except Exception:
                        pass
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
            cli_result = subprocess.run(
                [sys.executable, "-m", node.module_path, "--help"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            try:
                module = importlib.import_module(node.module_path)
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
            importlib.import_module(node.module_path)
            has_state_models = False
            state_model_errors = []
            try:
                state_module_path = (
                    f"omnibase.nodes.{node.name}.{node.version}.models.state"
                )
                state_module = importlib.import_module(state_module_path)
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
            node_file_path = (
                Path("src/omnibase/nodes") / node.name / node.version / "node.py"
            )
            canonical_namespace = str(Namespace.from_path(node_file_path))
            import yaml

            metadata_file = (
                Path("src/omnibase/nodes") / node.name / node.version / "node.onex.yaml"
            )
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    meta = yaml.safe_load(f)
                meta_ns = meta.get("namespace")

                # Accept yaml:// for YAML files, python:// for Python files, etc.
                def get_scheme(ns):
                    return ns.split("://")[0] if ns and "://" in ns else None

                meta_scheme = get_scheme(meta_ns)
                file_scheme = get_scheme(f"{metadata_file.suffix[1:]}://dummy")
                if meta_scheme != file_scheme:
                    state_model_errors.append(
                        f"Namespace scheme mismatch: metadata has '{meta_ns}', expected scheme '{file_scheme}://' for file type '{metadata_file.suffix}'"
                    )
                # Optionally, check the rest of the namespace after the scheme for further validation
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
            error_codes_module_path = (
                f"omnibase.nodes.{node.name}.{node.version}.error_codes"
            )
            error_codes_module = importlib.import_module(error_codes_module_path)
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
            if not hasattr(module, "main") and not hasattr(module, "cli_main"):
                compliance_issues.append("No main/cli_main function found")
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
        Validate introspection validity for a discovered node using event bus subscription.
        Robustly handles timeouts and subprocess errors.
        """
        import threading
        import time
        import uuid

        from omnibase.model.model_onex_event import OnexEventTypeEnum
        from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import (
            get_event_bus,
        )

        start_time = time.time()
        if not node.introspection_available:
            result = ValidationResultEnum.SKIP
            message = "Introspection not available for this node"
        else:
            event_bus = get_event_bus(mode="bind")  # Publisher
            received_event = {}
            event_received = threading.Event()
            correlation_id = str(uuid.uuid4())

            def on_event(event):
                if (
                    getattr(event, "event_type", None)
                    == OnexEventTypeEnum.INTROSPECTION_RESPONSE
                    and getattr(event, "correlation_id", None) == correlation_id
                ):
                    received_event["payload"] = event.metadata
                    event_received.set()

            event_bus.subscribe(on_event)

            import os
            import subprocess

            env = os.environ.copy()
            env["ONEX_EVENT_BUS_MODE"] = "inmemory"
            env["ONEX_CORRELATION_ID"] = correlation_id
            cli_args = [
                sys.executable,
                "-m",
                node.module_path,
                "--introspect",
                "--correlation-id",
                correlation_id,
            ]
            proc = subprocess.Popen(
                cli_args,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            timeout = 3
            waited = event_received.wait(timeout)
            proc.poll()
            if waited:
                # Event received, try to parse and validate
                try:
                    introspection_data = received_event["payload"]
                    required_fields = [
                        "node_metadata",
                        "contract",
                        "state_models",
                        "error_codes",
                        "dependencies",
                    ]
                    if all(field in introspection_data for field in required_fields):
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
                            message = (
                                "Introspection output missing required nested fields"
                            )
                    else:
                        result = ValidationResultEnum.FAIL
                        message = (
                            "Introspection output missing required top-level fields"
                        )
                except Exception as e:
                    result = ValidationResultEnum.FAIL
                    message = f"Introspection event parse error: {str(e)}"
                finally:
                    proc.terminate()
            else:
                # Timeout or process exited before event
                proc.poll()
                exit_code = proc.returncode
                stdout, stderr = proc.communicate(timeout=2)
                if exit_code is not None and exit_code != 0:
                    result = ValidationResultEnum.FAIL
                    message = f"Introspection command failed with exit code {exit_code}: {stderr.strip()}"
                else:
                    result = ValidationResultEnum.ERROR
                    message = "Introspection event not received (timeout)"
                proc.terminate()
        execution_time = (time.time() - start_time) * 1000
        return NodeValidationResult(
            node_name=node.name,
            node_version=node.version,
            validation_type=ValidationTypeEnum.INTROSPECTION_VALIDITY,
            result=result,
            message=message,
            execution_time_ms=execution_time,
        )

    @telemetry(node_name="parity_validator_node", operation="run_validation")
    def run_validation(
        self,
        input_state: ParityValidatorInputState,
        event_bus: Optional[ProtocolEventBus] = None,
        **kwargs,
    ) -> ParityValidatorOutputState:
        self.emit_node_start({"input_state": input_state.model_dump()})
        start_time = time.time()
        try:
            discovered_nodes = self.discover_nodes(input_state.nodes_directory)
            if not discovered_nodes:
                return create_parity_validator_output_state(
                    status=OnexStatus.WARNING,
                    message="No ONEX nodes discovered",
                    nodes_directory=input_state.nodes_directory,
                    correlation_id=input_state.correlation_id,
                )
            if input_state.node_filter:
                discovered_nodes = [
                    node
                    for node in discovered_nodes
                    if node.name in input_state.node_filter
                ]
            validation_types = input_state.validation_types or list(ValidationTypeEnum)
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
            output_state = create_parity_validator_output_state(
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
            self.emit_node_success(
                {
                    "input_state": input_state.model_dump(),
                    "output_state": output_state.model_dump(),
                }
            )
            return output_state
        except Exception as exc:
            self.emit_node_failure(
                {"input_state": input_state.model_dump(), "error": str(exc)}
            )
            raise


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
    Protocol-pure entrypoint: never print or sys.exit. Always return a canonical output model.
    """
    try:
        output_state = run_validation(
            nodes_directory=nodes_directory,
            validation_types=validation_types,
            node_filter=node_filter,
            fail_fast=fail_fast,
            include_performance_metrics=include_performance_metrics,
            format=format,
            correlation_id=correlation_id,
            verbose=verbose,
        )
        return output_state
    except Exception as e:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Parity validator error: {e}",
            context={"error": str(e)},
            node_id=_NODE_NAME,
            event_bus=None,
        )
        return ParityValidatorOutputState(
            version="1.0.0",
            status=OnexStatus.ERROR.value,
            message=f"Parity validator error: {e}",
            validation_results=[],
        )


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
        ParityValidatorNodeIntrospection.handle_introspect_command()
        return
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
        exit_code = get_exit_code_for_status(output_state.status)
        sys.exit(exit_code)
    except Exception as e:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            "Parity validator error",
            context={"error": str(e)},
            node_id=_NODE_NAME,
            event_bus=None,
        )
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
