from pathlib import Path
from typing import Union
import yaml
from omnibase.protocol.protocol_scenario_registry import ProtocolScenarioRegistry
from omnibase.constants import SCENARIOS_FIELD

class ToolScenarioRegistry(ProtocolScenarioRegistry):
    def load_scenario_registry(self, scenarios_index_path: Union[str, Path]) -> dict:
        path = Path(scenarios_index_path)
        if not path.exists():
            return {SCENARIOS_FIELD: []}
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return data

tool_scenario_registry = ToolScenarioRegistry() 