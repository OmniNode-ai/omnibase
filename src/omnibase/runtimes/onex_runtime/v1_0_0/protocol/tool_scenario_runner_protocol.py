from pathlib import Path
from typing import Any, Protocol, Optional

from omnibase.model.model_scenario_precondition import ModelScenarioPreConditionResult
from omnibase.model.model_scenario import ScenarioConfigModel


class ToolScenarioRunnerProtocol(Protocol):
    def run_scenario(
        self,
        node: Any,
        scenario_id: str,
        scenario_registry: dict,
        node_scenarios_dir: Path = None,
    ) -> Any:
        """
        Loads the scenario YAML for the given scenario_id, extracts input, runs the node, and returns the result.
        node_scenarios_dir is required for resolving relative entrypoints.
        """
        ...
    
    async def validate_preconditions(
        self,
        scenario_config: ScenarioConfigModel,
        skip_preconditions: bool = False
    ) -> ModelScenarioPreConditionResult:
        """
        Validate pre-conditions for a scenario before execution.
        Checks external service availability when dependency_mode is 'real'.
        Returns structured pre-condition results for logging and decision making.
        """
        ...
