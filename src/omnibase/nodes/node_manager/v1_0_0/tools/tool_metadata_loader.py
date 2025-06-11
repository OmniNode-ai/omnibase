from pathlib import Path
from typing import Optional
import yaml
from omnibase.nodes.node_manager.v1_0_0.models.model_metadata import ModelMetadata
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader

class ToolNodeMetadataLoader(ProtocolSchemaLoader):
    """
    Canonical loader for ONEX node metadata blocks from node.onex.yaml.
    Implements ProtocolSchemaLoader for registry/protocol compliance.
    Returns a ModelMetadata instance.
    """
    def __init__(self, node_dir: Path):
        self.node_dir = node_dir

    @property
    def name(self) -> str:
        """Return the canonical node name from node.onex.yaml."""
        onex_path = self.node_dir / "node.onex.yaml"
        metadata = self.load_onex_yaml(onex_path)
        return metadata.name

    def load_onex_yaml(self, path: Path) -> ModelMetadata:
        if not path.exists():
            raise FileNotFoundError(f"node.onex.yaml not found at {path}")
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return ModelMetadata(**data)

    def load_json_schema(self, path: Path):
        raise NotImplementedError("JSON schema loading not implemented in ToolNodeMetadataLoader.")

    def load_schema_for_node(self, node: ModelMetadata):
        raise NotImplementedError("Schema loading for node not implemented in ToolNodeMetadataLoader.") 