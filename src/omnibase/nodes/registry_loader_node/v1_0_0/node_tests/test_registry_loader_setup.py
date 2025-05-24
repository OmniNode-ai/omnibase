# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_registry_loader_setup.py
# version: 1.0.0
# uuid: 4f3d565e-11fe-4179-9fc1-180db9203368
# author: OmniNode Team
# created_at: 2025-05-24T09:36:56.350866
# last_modified_at: 2025-05-24T20:11:12.084377
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5cf65fb07e7618e167e8fd22b15e1dab08c5d636e4fb8ceed3e0e7dbb3362fcb
# entrypoint: python@test_registry_loader_setup.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_registry_loader_setup
# meta_type: tool
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
