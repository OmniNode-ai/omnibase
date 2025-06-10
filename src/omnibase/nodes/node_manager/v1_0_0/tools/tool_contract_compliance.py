from omnibase.enums.enum_validation_result import EnumValidationResult
from omnibase.nodes.node_manager.v1_0_0.models import ModelDiscoveredNode
from omnibase.nodes.node_manager.v1_0_0.protocols.protocol_contract_compliance import ProtocolContractCompliance
import subprocess
import sys

class ToolContractCompliance(ProtocolContractCompliance):
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