import json
from pathlib import Path
from typing import Dict, Type
from pydantic import BaseModel
from omnibase.enums.onex_status import OnexStatus
from omnibase.nodes.node_manager.v1_0_0.models.state import NodeManagerInputState, NodeManagerOutputState
from omnibase.nodes.node_manager.v1_0_0.models.state import SemVerModel
from omnibase.enums import LogLevelEnum
from omnibase.nodes.node_logger.protocols.protocol_logger_emit_log_event import ProtocolLoggerEmitLogEvent

class ToolSchemaGenerator:
    """
    Canonical tool for generating JSON schemas from Pydantic models for ONEX nodes.
    Uses contract-driven input/output state models.
    """
    def __init__(self, available_models: Dict[str, Type[BaseModel]], logger_tool: ProtocolLoggerEmitLogEvent = None):
        self.available_models = available_models
        if logger_tool is None:
            raise RuntimeError("Logger tool must be provided via DI or registry (protocol-pure).")
        self.logger_tool = logger_tool

    def generate_schema(self, model_class: Type[BaseModel], output_path: Path, include_metadata: bool = True) -> None:
        schema = model_class.model_json_schema()
        if include_metadata:
            schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
            schema["$id"] = f"https://onex.schemas/{output_path.name}"
        with open(output_path, "w") as f:
            json.dump(schema, f, indent=2, sort_keys=True)

    def run(self, input_state: NodeManagerInputState) -> NodeManagerOutputState:
        output_dir = Path(input_state.input_field)
        output_dir.mkdir(parents=True, exist_ok=True)
        models_to_generate = getattr(input_state, "optional_field", None)
        if models_to_generate:
            models_to_process = {
                name: model_class
                for name, model_class in self.available_models.items()
                if name in models_to_generate
            }
        else:
            models_to_process = self.available_models
        schemas_generated = []
        for model_name, model_class in models_to_process.items():
            schema_filename = f"{model_name}.schema.json"
            output_path = output_dir / schema_filename
            try:
                self.generate_schema(model_class, output_path, include_metadata=True)
                schemas_generated.append(schema_filename)
            except Exception as e:
                return NodeManagerOutputState(
                    version=input_state.version,
                    status=OnexStatus.ERROR,
                    message=f"Failed to generate schema for {model_name}: {e}",
                    output_field=None,
                    event_id=input_state.event_id,
                    correlation_id=input_state.correlation_id,
                    node_name=input_state.node_name,
                    node_version=input_state.node_version,
                    timestamp=input_state.timestamp,
                    schemas_generated=schemas_generated,
                    output_directory=str(output_dir),
                    total_schemas=len(schemas_generated),
                )
        return NodeManagerOutputState(
            version=input_state.version,
            status=OnexStatus.SUCCESS,
            message=f"Generated {len(schemas_generated)} JSON schemas successfully",
            output_field=None,
            event_id=input_state.event_id,
            correlation_id=input_state.correlation_id,
            node_name=input_state.node_name,
            node_version=input_state.node_version,
            timestamp=input_state.timestamp,
            schemas_generated=schemas_generated,
            output_directory=str(output_dir),
            total_schemas=len(schemas_generated),
        ) 