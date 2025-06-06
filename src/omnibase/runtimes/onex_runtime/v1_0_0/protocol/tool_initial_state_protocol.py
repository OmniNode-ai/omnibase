from pathlib import Path
from typing import Protocol

from omnibase.nodes.template_node.v1_0_0.models.state import TemplateNodeInputState


class ToolInitialStateProtocol(Protocol):
    def get_initial_state(self, node_onex_yaml_path: Path) -> TemplateNodeInputState:
        """
        Loads node metadata and returns a TemplateNodeInputState.
        """
        ...
