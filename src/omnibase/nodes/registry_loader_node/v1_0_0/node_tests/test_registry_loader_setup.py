# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.496749'
# description: Stamped by PythonHandler
# entrypoint: python://test_registry_loader_setup.py
# hash: 811f6f8a73b7c5559f7500cb1e5bf3a3f5bb58f5198f7cfd18ab2c495a0fd67b
# last_modified_at: '2025-05-29T11:50:11.609882+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_registry_loader_setup.py
# namespace: omnibase.test_registry_loader_setup
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 35e29eb9-de2b-4cf1-a98b-5e2b9741385f
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Test setup helper for registry loader node tests.

Provides protocol-driven test environment setup following canonical patterns.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def create_test_registry(temp_path: Path, registry_data: Dict[str, Any]) -> None:
    """
    Create a test registry structure with the provided data.

    Args:
        temp_path: Temporary directory path
        registry_data: Registry data to write to registry.yaml
    """
    registry_dir = temp_path / "registry"
    registry_dir.mkdir(parents=True, exist_ok=True)

    registry_file = registry_dir / "registry.yaml"
    with open(registry_file, "w") as f:
        yaml.dump(registry_data, f)


def create_test_artifact(
    temp_path: Path,
    artifact_type: str,
    artifact_name: str,
    version: str,
    files: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Create a test artifact directory structure.

    Args:
        temp_path: Base temporary directory
        artifact_type: Type of artifact (nodes, cli_tools, etc.)
        artifact_name: Name of the artifact
        version: Version of the artifact
        files: Optional dictionary of files to create

    Returns:
        Path to the created artifact directory
    """
    artifact_dir = temp_path / artifact_type / artifact_name / version
    artifact_dir.mkdir(parents=True, exist_ok=True)

    if files:
        for filename, content in files.items():
            file_path = artifact_dir / filename
            if filename == ".wip":
                # Create empty .wip marker file
                file_path.touch()
            elif isinstance(content, dict):
                # YAML content
                with open(file_path, "w") as f:
                    yaml.dump(content, f)
            else:
                # String content
                with open(file_path, "w") as f:
                    f.write(str(content))

    return artifact_dir
