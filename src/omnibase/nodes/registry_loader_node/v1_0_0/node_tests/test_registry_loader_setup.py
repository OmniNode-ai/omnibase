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

from omnibase.core.core_tests.core_onex_registry_loader_test_cases import (
    RegistryTestData,
)


def setup_test_environment(temp_path: Path, test_data: RegistryTestData) -> None:
    """
    Set up test environment based on registry test data.

    This follows protocol-driven patterns by using the existing test data
    structures and delegating file I/O to a centralized helper.

    Args:
        temp_path: Temporary directory path
        test_data: Test data containing registry and artifact information
    """
    # Create registry structure
    _create_registry_structure(temp_path, test_data.registry_yaml)

    # Create artifacts based on test data and registry paths
    for artifact_type, artifacts in test_data.artifacts.items():
        for artifact_name, versions in artifacts.items():
            for version, files in versions.items():
                # Find the path for this artifact from the registry data
                artifact_path = _find_artifact_path(
                    test_data.registry_yaml, artifact_type, artifact_name, version
                )

                if artifact_path:
                    artifact_dir = temp_path / artifact_path
                    artifact_dir.mkdir(parents=True, exist_ok=True)

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


def _find_artifact_path(
    registry_data: Dict[str, Any], artifact_type: str, artifact_name: str, version: str
) -> Optional[str]:
    """
    Find the path for a specific artifact from registry data.

    Args:
        registry_data: Registry YAML data
        artifact_type: Type of artifact (nodes, cli_tools, etc.)
        artifact_name: Name of the artifact
        version: Version of the artifact

    Returns:
        Path string if found, None otherwise
    """
    if artifact_type not in registry_data:
        return None

    for artifact in registry_data[artifact_type]:
        if artifact.get("name") == artifact_name:
            for version_info in artifact.get("versions", []):
                if version_info.get("version") == version:
                    return str(version_info.get("path"))

    return None


def _create_registry_structure(temp_path: Path, registry_data: Dict[str, Any]) -> None:
    """
    Create registry.yaml file structure.

    Args:
        temp_path: Temporary directory path
        registry_data: Registry data to write
    """
    registry_dir = temp_path / "registry"
    registry_dir.mkdir()

    with open(registry_dir / "registry.yaml", "w") as f:
        yaml.dump(registry_data, f)
