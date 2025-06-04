from omnibase.nodes.template_node.v1_0_0.models.state import TemplateNodeInputState
from omnibase.model.model_semver import SemVerModel
from omnibase.model.model_node_metadata import NodeMetadataBlock
from pathlib import Path
from omnibase.runtimes.onex_runtime.v1_0_0.protocol.tool_initial_state_protocol import ToolInitialStateProtocol

class ToolInitialState(ToolInitialStateProtocol):
    def get_initial_state(self, node_onex_yaml_path: Path) -> TemplateNodeInputState:
        version = SemVerModel(str(NodeMetadataBlock.from_file(node_onex_yaml_path).version))
        return TemplateNodeInputState(version=version, input_field="", optional_field=None)

tool_initial_state = ToolInitialState() 