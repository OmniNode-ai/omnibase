from omnibase.enums.enum_validation_result import EnumValidationResult
from omnibase.enums.enum_validation_type import EnumValidationType
from omnibase.nodes.node_manager.v1_0_0.protocols.protocol_node_validation_tool import ProtocolNodeValidationTool
from omnibase.nodes.node_manager.v1_0_0.models import ModelDiscoveredNode
import subprocess
import sys

class NodeValidationTool(ProtocolNodeValidationTool):
    """
    Provides validation routines for ONEX nodes using ModelDiscoveredNode and canonical protocols.
    """
    def validate_cli_node_parity(self, node: ModelDiscoveredNode) -> EnumValidationResult:
        try:
            cli_result = subprocess.run(
                [sys.executable, "-m", node.module_path, "--help"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            try:
                import importlib
                module = importlib.import_module(node.module_path)
                has_main = hasattr(module, "main") or hasattr(module, "cli_main")
                if cli_result.returncode == 0 and has_main:
                    return EnumValidationResult.PASS
                elif cli_result.returncode == 0:
                    return EnumValidationResult.PASS
                else:
                    return EnumValidationResult.FAIL
            except Exception:
                return EnumValidationResult.FAIL
        except subprocess.TimeoutExpired:
            return EnumValidationResult.ERROR
        except Exception:
            return EnumValidationResult.ERROR

    def validate_schema_conformance(self, node: ModelDiscoveredNode) -> EnumValidationResult:
        try:
            import importlib
            from pathlib import Path
            import yaml
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
            metadata_file = (
                Path("src/omnibase/nodes") / node.name / node.version / "node.onex.yaml"
            )
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    meta = yaml.safe_load(f)
                meta_ns = meta.get("namespace")
                def get_scheme(ns):
                    return ns.split("://")[0] if ns and "://" in ns else None
                meta_scheme = get_scheme(meta_ns)
                file_scheme = get_scheme(f"{metadata_file.suffix[1:]}://dummy")
                if meta_scheme != file_scheme:
                    state_model_errors.append(
                        f"Namespace scheme mismatch: metadata has '{meta_ns}', expected scheme '{file_scheme}://' for file type '{metadata_file.suffix}'"
                    )
            if has_state_models and not state_model_errors:
                return EnumValidationResult.PASS
            elif has_state_models:
                return EnumValidationResult.FAIL
            else:
                return EnumValidationResult.FAIL
        except Exception:
            return EnumValidationResult.ERROR

    def validate_error_code_usage(self, node: ModelDiscoveredNode) -> EnumValidationResult:
        try:
            import importlib
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
                return EnumValidationResult.PASS
            else:
                return EnumValidationResult.FAIL
        except ImportError:
            return EnumValidationResult.FAIL
        except Exception:
            return EnumValidationResult.ERROR

    def validate_contract_compliance(self, node: ModelDiscoveredNode) -> EnumValidationResult:
        try:
            import importlib
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
                return EnumValidationResult.PASS
            else:
                return EnumValidationResult.FAIL
        except Exception:
            return EnumValidationResult.ERROR

    def validate_introspection_validity(self, node: ModelDiscoveredNode) -> EnumValidationResult:
        try:
            import threading
            import time
            import uuid
            import subprocess
            import os
            if not node.introspection_available:
                return EnumValidationResult.SKIP
            correlation_id = str(uuid.uuid4())
            event_received = threading.Event()
            received_event = {}
            def on_event(event):
                if (
                    getattr(event, "event_type", None) == "INTROSPECTION_RESPONSE"
                    and getattr(event, "correlation_id", None) == correlation_id
                ):
                    received_event["payload"] = getattr(event, "metadata", None)
                    event_received.set()
            env = os.environ.copy()
            env["ONEX_EVENT_BUS_MODE"] = "inmemory"
            env["ONEX_CORRELATION_ID"] = correlation_id
            cli_args = [
                "python", "-m", node.module_path, "--introspect", "--correlation-id", correlation_id
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
                        if all(field in node_metadata for field in metadata_fields) and all(field in contract for field in contract_fields):
                            return EnumValidationResult.PASS
                        else:
                            return EnumValidationResult.FAIL
                    else:
                        return EnumValidationResult.FAIL
                except Exception:
                    return EnumValidationResult.FAIL
                finally:
                    proc.terminate()
            else:
                proc.poll()
                exit_code = proc.returncode
                try:
                    proc.communicate(timeout=2)
                except Exception:
                    pass
                if exit_code is not None and exit_code != 0:
                    return EnumValidationResult.FAIL
                else:
                    return EnumValidationResult.ERROR
                proc.terminate()
        except Exception:
            return EnumValidationResult.ERROR

    def validate(self, node: ModelDiscoveredNode, validation_type: EnumValidationType) -> EnumValidationResult:
        if validation_type == EnumValidationType.CLI_NODE_PARITY:
            return self.validate_cli_node_parity(node)
        elif validation_type == EnumValidationType.SCHEMA_CONFORMANCE:
            return self.validate_schema_conformance(node)
        elif validation_type == EnumValidationType.ERROR_CODE_USAGE:
            return self.validate_error_code_usage(node)
        elif validation_type == EnumValidationType.CONTRACT_COMPLIANCE:
            return self.validate_contract_compliance(node)
        elif validation_type == EnumValidationType.INTROSPECTION_VALIDITY:
            return self.validate_introspection_validity(node)
        else:
            return EnumValidationResult.ERROR 