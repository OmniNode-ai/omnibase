from pathlib import Path
from omnibase.model.model_state_contract import load_state_contract_from_file

class MixinNodeSetup:
    """
    Canonical mixin for ONEX nodes to provide contract and metadata access.
    Usage: Inherit in your node class to get contract, node_id, node_version, node_onex_yaml_path, etc.
    """
    @property
    def contract_path(self):
        return Path(__file__).parent / "contract.yaml"

    @property
    def node_onex_yaml_path(self):
        return Path(__file__).parent / "node.onex.yaml"

    @property
    def contract(self):
        if not hasattr(self, "_contract"):
            self._contract = load_state_contract_from_file(self.contract_path)
        return self._contract

    @property
    def node_id(self):
        return self.contract.node_name

    @property
    def node_version(self):
        return self.contract.node_version

    @property
    def contract_version(self):
        return self.contract.contract_version 