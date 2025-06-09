from src.omnibase.enums.enum_validation_result import EnumValidationResult
from omnibase.nodes.node_parity_validator.v1_0_0.models.state import DiscoveredNode
from src.omnibase.nodes.node_parity_validator.protocols.protocol_introspection_validity import ProtocolIntrospectionValidity

class ToolIntrospectionValidity(ProtocolIntrospectionValidity):
    def validate_introspection_validity(self, node: DiscoveredNode) -> EnumValidationResult:
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
            # Simulate event bus subscription (stub for protocol compliance)
            # In real usage, inject event bus and subscribe here
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