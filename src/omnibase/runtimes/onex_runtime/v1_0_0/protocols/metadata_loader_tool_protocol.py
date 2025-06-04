from typing import Protocol, Union
from pathlib import Path
from omnibase.model.model_node_metadata import NodeMetadataBlock

class MetadataLoaderToolProtocol(Protocol):
    def load_node_metadata(self, node_onex_yaml_path: Union[str, Path], event_bus) -> NodeMetadataBlock:
        """
        Loads and parses node.onex.yaml into a NodeMetadataBlock.
        """
        ... 