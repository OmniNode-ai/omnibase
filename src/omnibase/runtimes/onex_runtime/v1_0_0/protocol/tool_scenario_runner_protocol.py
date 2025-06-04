from typing import Protocol, Any
from pathlib import Path

class ToolScenarioRunnerProtocol(Protocol):
    def run_scenario(self, node: Any, scenario_id: str, scenario_registry: dict, node_scenarios_dir: Path = None) -> Any:
        """
        Loads the scenario YAML for the given scenario_id, extracts input, runs the node, and returns the result.
        node_scenarios_dir is required for resolving relative entrypoints.
        """
        ... 