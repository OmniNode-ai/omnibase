# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "util_tree_ignore"
# namespace: "foundation.util"
# meta_type: "util"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "foundation-team"
# entrypoint: "util_tree_ignore.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["ProtocolTreeIgnoreUtils", "Protocol"]
# base_class: ["ProtocolTreeIgnoreUtils", "Protocol"]
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import yaml
import json
from typing import Any, Protocol
from pathlib import Path
from foundation.model.model_tree_ignore import TreeIgnoreModel
from pydantic import ValidationError

class ProtocolTreeIgnoreUtils(Protocol):
    def load_tree_ignore(self, path: str | Path) -> TreeIgnoreModel:
        """
        Load a .treeignore file from YAML or JSON and validate against the protocol model.
        Args:
            path: Path to the .treeignore file (str or Path).
        Returns:
            TreeIgnoreModel instance.
        Raises:
            ValueError: If the file is invalid or schema validation fails.
        """
        ...

    def save_tree_ignore(self, model: TreeIgnoreModel, path: str | Path, format: str = 'yaml') -> None:
        """
        Save a TreeIgnoreModel to YAML or JSON.
        Args:
            model: TreeIgnoreModel instance to save.
            path: Path to save the file (str or Path).
            format: Output format ('yaml' or 'json').
        Raises:
            ValueError: If the format is unsupported.
        """
        ...

class UtilTreeIgnore(ProtocolTreeIgnoreUtils):
    @staticmethod
    def load_tree_ignore(path: str | Path) -> TreeIgnoreModel:
        """
        Load a .treeignore file from YAML or JSON and validate against the protocol model.
        Args:
            path: Path to the .treeignore file (str or Path).
        Returns:
            TreeIgnoreModel instance.
        Raises:
            ValueError: If the file is invalid or schema validation fails.
        """
        path = Path(path)
        with open(path, 'r') as f:
            if path.suffix in {'.yaml', '.yml', ''}:
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported .treeignore file extension: {path.suffix}")
        try:
            return TreeIgnoreModel.model_validate(data)
        except ValidationError as e:
            raise ValueError(f".treeignore schema validation failed for {path}: {e}")

    @staticmethod
    def save_tree_ignore(model: TreeIgnoreModel, path: str | Path, format: str = 'yaml') -> None:
        """
        Save a TreeIgnoreModel to YAML or JSON.
        Args:
            model: TreeIgnoreModel instance to save.
            path: Path to save the file (str or Path).
            format: Output format ('yaml' or 'json').
        Raises:
            ValueError: If the format is unsupported.
        """
        path = Path(path)
        data = model.model_dump(mode="python")
        with open(path, 'w') as f:
            if format == 'yaml' or path.suffix in {'.yaml', '.yml', ''}:
                yaml.safe_dump(data, f)
            elif format == 'json' or path.suffix == '.json':
                json.dump(data, f, indent=2)
            else:
                raise ValueError(f"Unsupported format for .treeignore: {format}") 