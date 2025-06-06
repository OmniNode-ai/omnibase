from pathlib import Path
from typing import Protocol

from omnibase.nodes.node_template.v1_0_0.models.state import NodeTemplateInputState


class ToolInitialStateProtocol(Protocol):
    def get_initial_state(self, node_onex_yaml_path: Path) -> NodeTemplateInputState:
        """
        Loads node metadata and returns a NodeTemplateInputState.
        """
        ...
