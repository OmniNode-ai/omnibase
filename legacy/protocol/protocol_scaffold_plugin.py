from typing import Protocol, Any, Dict, List, Optional, runtime_checkable
from pathlib import Path

@runtime_checkable
class ProtocolScaffoldPlugin(Protocol):
    """
    Protocol for scaffold generator plugins.
    All scaffold plugins must implement this interface for registry-based discovery and DI.
    """
    def __init__(self, logger: Any, registry: Any, config: Optional[dict] = None) -> None:
        """
        Initialize the scaffold plugin with DI-compliant dependencies.
        Args:
            logger: Logger instance (DI-injected)
            registry: Registry instance for metadata/templates (DI-injected)
            config: Optional configuration dictionary
        """
        ...

    def generate(self, name: str, output_dir: Path, **kwargs) -> None:
        """
        Generate the scaffold in the specified output directory.
        Args:
            name: Name of the scaffolded entity (e.g., service, container)
            output_dir: Target directory for generated files
            kwargs: Additional plugin-specific options
        """
        ...

    def get_metadata(self) -> Dict[str, Any]:
        """
        Return plugin metadata (type, version, description, etc.).
        Returns:
            Dictionary of plugin metadata
        """
        ...

    def validate(self, output_dir: Path) -> List[str]:
        """
        Validate the generated scaffold output.
        Args:
            output_dir: Directory to validate
        Returns:
            List of validation error messages (empty if valid)
        """
        ... 