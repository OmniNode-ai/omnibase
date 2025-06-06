from pathlib import Path
from typing import Protocol, Union


class ProtocolScenarioRegistry(Protocol):
    def load_scenario_registry(self, scenarios_index_path: Union[str, Path]) -> dict:
        """
        Loads and parses the scenario registry/index YAML and returns the data as a dict.
        """
        ...
