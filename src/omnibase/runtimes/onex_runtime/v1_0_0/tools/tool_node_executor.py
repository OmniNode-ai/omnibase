from pathlib import Path
from typing import Any

from omnibase.enums.onex_status import OnexStatus
from omnibase.model.model_output_field import OnexFieldModel
from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.node_template.v1_0_0.models.state import NodeTemplateOutputState
from omnibase.runtimes.onex_runtime.v1_0_0.protocol.tool_node_executor_protocol import (
    ToolNodeExecutorProtocol,
)
from omnibase.runtimes.onex_runtime.v1_0_0.tools.metadata_loader_tool import (
    metadata_loader_tool,
)


class ToolNodeExecutor(ToolNodeExecutorProtocol):
    def execute_node(
        self,
        input_state: dict,
        node_onex_yaml_path: Path,
        event_bus: Any,
        input_validation_tool: Any,
        output_field_tool: Any,
        correlation_id: str = None,
    ) -> Any:
        node_metadata_block = metadata_loader_tool.load_node_metadata(
            node_onex_yaml_path, event_bus
        )
        node_version = str(node_metadata_block.version)
        semver = SemVerModel.parse(node_version)
        state, error_output = input_validation_tool.validate_input_state(
            input_state, semver, event_bus, correlation_id=correlation_id
        )
        if error_output is not None:
            return error_output
        output_field = (
            output_field_tool(state, input_state)
            if callable(output_field_tool)
            else output_field_tool.compute_output_field(state, input_state)
        )
        if isinstance(output_field, dict):
            output_field = OnexFieldModel(**output_field)
        return NodeTemplateOutputState(
            version=semver,
            status=OnexStatus.SUCCESS,
            message="NodeTemplate ran successfully.",
            output_field=output_field,
        )


tool_node_executor = ToolNodeExecutor()
