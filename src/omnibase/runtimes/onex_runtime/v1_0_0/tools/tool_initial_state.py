from pathlib import Path

from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.node_template.v1_0_0.models.state import NodeTemplateInputState
from omnibase.runtimes.onex_runtime.v1_0_0.protocol.tool_initial_state_protocol import (
    ToolInitialStateProtocol,
)


class ToolInitialState(ToolInitialStateProtocol):
    def get_initial_state(self, node_onex_yaml_path: Path) -> NodeTemplateInputState:
        version = SemVerModel(
            str(NodeMetadataBlock.from_file(node_onex_yaml_path).version)
        )
        return NodeTemplateInputState(
            version=version, input_field="", optional_field=None
        )


tool_initial_state = ToolInitialState()
