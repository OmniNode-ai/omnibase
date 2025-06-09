from src.omnibase.enums.enum_validation_result import EnumValidationResult
from omnibase.nodes.node_parity_validator.v1_0_0.models.state import DiscoveredNode
from src.omnibase.nodes.node_parity_validator.protocols.protocol_cli_node_parity import ProtocolCliNodeParity
import subprocess
import sys

class ToolCliNodeParity(ProtocolCliNodeParity):
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