from pathlib import Path
from typing import Union

from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.runtimes.onex_runtime.v1_0_0.protocols.metadata_loader_tool_protocol import (
    MetadataLoaderToolProtocol,
)


class MetadataLoaderTool(MetadataLoaderToolProtocol):
    def load_node_metadata(
        self, node_onex_yaml_path: Union[str, Path], event_bus
    ) -> NodeMetadataBlock:
        """
        Loads and parses node.onex.yaml into a NodeMetadataBlock.
        """
        path = Path(node_onex_yaml_path)
        with open(path, "r") as f:
            node_metadata_content = f.read()
        return NodeMetadataBlock.from_file_or_content(
            node_metadata_content, event_bus=event_bus
        )


metadata_loader_tool = MetadataLoaderTool()
