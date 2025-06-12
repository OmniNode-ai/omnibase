from omnibase.enums.enum_validation_result import EnumValidationResult
from omnibase.nodes.node_manager.v1_0_0.models import ModelDiscoveredNode
from omnibase.nodes.node_manager.v1_0_0.protocols.protocol_schema_conformance import ProtocolSchemaConformance
from omnibase.nodes.node_logger.protocols.protocol_logger_emit_log_event import ProtocolLoggerEmitLogEvent

class ToolSchemaConformance(ProtocolSchemaConformance):
    def __init__(self, logger_tool: ProtocolLoggerEmitLogEvent = None):
        if logger_tool is None:
            raise RuntimeError("Logger tool must be provided via DI or registry (protocol-pure).")
        self.logger_tool = logger_tool

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