import yaml
from pathlib import Path
import importlib

class MixinNodeIdFromContract:
    """
    Mixin to load node_id (node_name) from node.onex.yaml or contract.yaml in the node's directory.
    Provides the _load_node_id() utility method for use in node __init__.
    """
    def _get_node_dir(self):
        module = importlib.import_module(self.__class__.__module__)
        node_file = Path(module.__file__)
        return node_file.parent

    def _load_node_id(self, contract_path: Path = None):
        # Default to node.onex.yaml or contract.yaml in the node's directory
        node_dir = self._get_node_dir()
        if contract_path is None:
            contract_path = node_dir / "node.onex.yaml"
            if not contract_path.exists():
                contract_path = node_dir / "contract.yaml"
        if not contract_path.exists():
            raise FileNotFoundError(f"No contract file found at {contract_path}")
        with open(contract_path, "r") as f:
            contract = yaml.safe_load(f)
        return contract.get("node_name") or contract.get("name") 