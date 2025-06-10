from pathlib import Path
from typing import List
from omnibase.nodes.node_manager.v1_0_0.models import ModelDiscoveredNode

class NodeDiscoveryTool:
    """
    Discovers ONEX nodes in a given directory, returning a list of ModelDiscoveredNode.
    """
    def discover_nodes(self, nodes_directory: str) -> List[ModelDiscoveredNode]:
        discovered = []
        nodes_path = Path(nodes_directory)
        if not nodes_path.exists():
            return []
        for node_dir in nodes_path.iterdir():
            if not node_dir.is_dir() or node_dir.name.startswith("."):
                continue
            for version_dir in node_dir.iterdir():
                if not version_dir.is_dir() or not version_dir.name.startswith("v"):
                    continue
                node_file = version_dir / "node.py"
                if not node_file.exists():
                    continue
                module_path = f"omnibase.nodes.{node_dir.name}.{version_dir.name}.node"
                introspection_available = (version_dir / "introspection.py").exists()
                discovered.append(ModelDiscoveredNode(
                    name=node_dir.name,
                    version=version_dir.name,
                    module_path=module_path,
                    introspection_available=introspection_available,
                    cli_entrypoint=f"python -m {module_path}",
                    error_count=0,
                ))
        return discovered 