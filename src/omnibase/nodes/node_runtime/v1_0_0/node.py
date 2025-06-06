# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-06-03T00:00:00.000000'
# description: Canonical runtime node with dispatch table for ONEX helpers
# entrypoint: python://node
# hash: <to-be-stamped>
# last_modified_at: '2025-06-03T00:00:00.000000+00:00'
# lifecycle: active
# meta_type: node
# metadata_version: 0.1.0
# name: node.py
# namespace: python://omnibase.nodes.node_runtime.v1_0_0.node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 1.0.0
# state_contract: state_contract://default
# tools: null
# uuid: <to-be-stamped>
# version: 1.0.0
# === /OmniNode:Metadata ===

"""
node_runtime: Canonical ONEX runtime node exposing core helpers via dispatch table.
Implements the reducer pattern and is discoverable via introspection.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseModel

from omnibase.enums.enum_log_level import LogLevelEnum
from omnibase.enums.enum_onex_status import OnexStatus
from omnibase.enums.enum_registry_output_status import RegistryOutputStatusEnum
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_reducer import ActionModel, StateModel
from omnibase.model.model_semver import SemVerModel
from omnibase.protocol.protocol_reducer import ProtocolReducer
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import (
    MetadataYAMLHandler,
)

from .introspection import RuntimeNodeIntrospection
from .models.dispatch import DispatchTableModel
from .models.state import RuntimeNodeInputState, RuntimeNodeOutputState

NODE_ONEX_YAML_PATH = Path(__file__).parent / "node.onex.yaml"


# Example core helpers (stub implementations)
def merge_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two or more state dicts (stub)."""
    # In real implementation, merge logic would be here
    return {"merged": True, **state}


def emit_event(state: Dict[str, Any]) -> Dict[str, Any]:
    """Emit an event (stub)."""
    # In real implementation, event emission logic would be here
    return {"event_emitted": True, **state}


# Dispatch table for runtime helpers
DISPATCH_TABLE = {
    "merge_state": merge_state,
    "emit_event": emit_event,
}


class RuntimeNodeInputState(BaseModel):
    action: str
    params: Dict[str, Any] = {}


class RuntimeNodeOutputState(BaseModel):
    result: Any
    status: str = "success"


class RuntimeNode(ProtocolReducer):
    """
    Canonical ONEX reducer node implementing ProtocolReducer.
    """

    def __init__(self):
        pass

    def run(self, input_state: RuntimeNodeInputState) -> RuntimeNodeOutputState:
        """
        Run the runtime node. In a real node, this would delegate to inline handlers.
        Args:
            input_state (RuntimeNodeInputState): Canonical input state for the node.
        Returns:
            RuntimeNodeOutputState: Canonical output state for the node.
        """
        action = input_state.action
        handler = DISPATCH_TABLE.get(action)
        if not handler:
            return RuntimeNodeOutputState(
                result={"error": f"Unknown action: {action}"}, status="error"
            )
        result = handler(input_state.params)
        return RuntimeNodeOutputState(result=result, status="success")

    def bind(self, *args, **kwargs):
        """
        Bind pattern stub. In ONEX, this is used for chaining nodes.
        """
        return self

    def initial_state(self) -> StateModel:
        """
        Return the initial state for the reducer. Override as needed.
        """
        return RuntimeNodeInputState(
            version=SemVerModel(
                str(NodeMetadataBlock.from_file(NODE_ONEX_YAML_PATH).version)
            ),
            required_field="",
            optional_field=None,
        )

    def dispatch(self, state: StateModel, action: ActionModel) -> StateModel:
        """
        Apply an action to the state and return the new state. Override as needed.
        """
        # For runtime, just return the state unchanged
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


def load_dispatch_table() -> DispatchTableModel:
    """Load and validate the dispatch.yaml file as a DispatchTableModel."""
    dispatch_path = Path(__file__).parent / "dispatch.yaml"
    if not dispatch_path.exists():
        return DispatchTableModel(actions=[])
    with open(dispatch_path, "r") as f:
        data = yaml.safe_load(f)
    return DispatchTableModel.model_validate(data)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--introspect":
        dispatch_table = load_dispatch_table()
        print(
            json.dumps(
                {
                    "actions": [a.model_dump() for a in dispatch_table.actions],
                    "input_model": RuntimeNodeInputState.schema(),
                    "output_model": RuntimeNodeOutputState.schema(),
                },
                indent=2,
            )
        )
    else:
        # Example CLI usage: python node.py merge_state '{"foo": 1}'
        if len(sys.argv) < 3:
            print("Usage: python node.py <action> <params_json>")
            sys.exit(1)
        action = sys.argv[1]
        params = json.loads(sys.argv[2])
        node = RuntimeNode()
        input_state = RuntimeNodeInputState(action=action, params=params)
        output = node.run(input_state)
        print(output.model_dump_json(indent=2))
