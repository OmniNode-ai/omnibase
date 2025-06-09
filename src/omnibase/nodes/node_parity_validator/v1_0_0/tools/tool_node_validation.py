from src.omnibase.enums.enum_validation_result import EnumValidationResult
from src.omnibase.enums.enum_validation_type import EnumValidationType
from src.omnibase.nodes.node_parity_validator.protocols.protocol_node_validation_tool import ProtocolNodeValidationTool
from omnibase.nodes.node_parity_validator.v1_0_0.models.state import DiscoveredNode
import subprocess
import sys

class NodeValidationTool(ProtocolNodeValidationTool):
    """Provides validation routines for ONEX nodes."""
    def validate_cli_node_parity(self, node: DiscoveredNode) -> EnumValidationResult:
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

    def validate_schema_conformance(self, node: DiscoveredNode) -> EnumValidationResult:
        try:
            import importlib
            from pathlib import Path
            import yaml
            # Try to import the node module
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

    def validate_error_code_usage(self, node: DiscoveredNode) -> EnumValidationResult:
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

    # Implement each method by extracting and adapting logic from legacy node.py
    # Use strong typing and protocol-first design
    pass 