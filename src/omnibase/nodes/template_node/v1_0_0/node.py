"""
Template Node (ONEX Canonical)

Implements the reducer pattern with .run() and .bind() lifecycle. All business logic is delegated to inline handlers or runtime helpers.
"""

from .models.state import TemplateNodeInputState, TemplateNodeOutputState
from omnibase.protocol.protocol_reducer import ProtocolReducer
from omnibase.model.model_reducer import ActionModel, StateModel
from omnibase.enums.enum_registry_output_status import RegistryOutputStatusEnum
from omnibase.model.model_semver import SemVerModel
from omnibase.model.model_node_metadata import NodeMetadataBlock
import yaml
from pathlib import Path
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import MetadataYAMLHandler
import sys
import json
from .introspection import TemplateNodeIntrospection

NODE_ONEX_YAML_PATH = Path(__file__).parent / "node.onex.yaml"

class TemplateNode(ProtocolReducer):
    """
    Canonical ONEX reducer node implementing ProtocolReducer.
    """
    def __init__(self):
        pass

    def run(self, input_state: TemplateNodeInputState) -> TemplateNodeOutputState:
        """
        Run the template node. In a real node, this would delegate to inline handlers.
        Args:
            input_state (TemplateNodeInputState): Canonical input state for the node.
        Returns:
            TemplateNodeOutputState: Canonical output state for the node.
        """
        return TemplateNodeOutputState(
            version=input_state.version,
            status=RegistryOutputStatusEnum.SUCCESS,
            message="TemplateNode ran successfully.",
            output_field=None,
        )

    def bind(self, *args, **kwargs):
        """
        Bind pattern stub. In ONEX, this is used for chaining nodes.
        """
        return self

    def initial_state(self) -> StateModel:
        """
        Return the initial state for the reducer. Override as needed.
        """
        return TemplateNodeInputState(version=SemVerModel(str(NodeMetadataBlock.from_file(NODE_ONEX_YAML_PATH).version)), required_field="", optional_field=None)

    def dispatch(self, state: StateModel, action: ActionModel) -> StateModel:
        """
        Apply an action to the state and return the new state. Override as needed.
        """
        # For template, just return the state unchanged
        return state

    def introspect(self):
        """
        Return a list of available scenarios for this node from scenarios/index.yaml.
        """
        scenarios_index_path = Path(__file__).parent / "scenarios" / "index.yaml"
        if not scenarios_index_path.exists():
            return {"scenarios": []}
        with open(scenarios_index_path, "r") as f:
            data = yaml.safe_load(f)
        return data

if __name__ == "__main__":
    node = TemplateNode()
    if len(sys.argv) > 1 and sys.argv[1] == "--introspect":
        TemplateNodeIntrospection.handle_introspect_command()
    elif len(sys.argv) > 2 and sys.argv[1] == "--run-scenario":
        scenario_id = sys.argv[2]
        scenarios = TemplateNodeIntrospection.get_scenarios()
        scenario = next((s for s in scenarios if s.get("id") == scenario_id), None)
        if scenario:
            print(json.dumps(scenario, indent=2))
        else:
            print(json.dumps({"error": f"Scenario '{scenario_id}' not found."}, indent=2))
    else:
        print("Usage: node.py --introspect | --run-scenario <scenario_id>")
