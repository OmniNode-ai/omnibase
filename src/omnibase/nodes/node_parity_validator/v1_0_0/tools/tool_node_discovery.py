from pathlib import Path
from typing import List
from pydantic import BaseModel

class DiscoveredNode(BaseModel):
    name: str
    version: str
    module_path: str
    introspection_available: bool
    cli_entrypoint: str | None = None
    error_count: int = 0

class ProtocolNodeDiscoveryTool(Protocol):
    def discover_nodes(self, nodes_directory: str) -> List[DiscoveredNode]:
        ...

class NodeDiscoveryTool:
    """Discovers ONEX nodes in a given directory."""
    def discover_nodes(self, nodes_directory: str) -> List[DiscoveredNode]:
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
                discovered.append(DiscoveredNode(
                    name=node_dir.name,
                    version=version_dir.name,
                    module_path=module_path,
                    introspection_available=introspection_available,
                    cli_entrypoint=f"python -m {module_path}",
                    error_count=0,
                ))
        return discovered 