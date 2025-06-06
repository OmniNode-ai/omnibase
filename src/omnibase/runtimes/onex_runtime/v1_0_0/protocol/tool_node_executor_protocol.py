from pathlib import Path
from typing import Any, Protocol


class ToolNodeExecutorProtocol(Protocol):
    def execute_node(
        self,
        input_state: dict,
        node_onex_yaml_path: Path,
        event_bus: Any,
        input_validation_tool: Any,
        output_field_tool: Any,
    ) -> Any:
        """
        Canonical ONEX node execution pipeline: loads metadata, parses version, validates input, computes output.
        Returns the output state (node-specific model).
        """
        ...
