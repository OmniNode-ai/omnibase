# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_onex_registry_loader.py
# version: 1.0.0
# uuid: 8b6c6b6e-4b4b-4b4b-8b6c-6b6e4b4b4b4b
# author: OmniNode Team
# created_at: 2025-05-23T10:29:04.625488
# last_modified_at: 2025-05-23T17:42:52.030520
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 8b6c6b6e4b4b4b4b8b6c6b6e4b4b4b4b8b6c6b6e4b4b4b4b8b6c6b6e4b4b4b4b
# entrypoint: python@test_onex_registry_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_onex_registry_loader
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Tests for ONEX Registry Loader.

This module contains comprehensive tests for the OnexRegistryLoader class,
following the canonical testing patterns defined in testing.md.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import yaml

from omnibase.core.onex_registry_loader import OnexRegistryLoader
from omnibase.model.enum_onex_status import OnexStatus
from omnibase.protocol.protocol_registry import ProtocolRegistry
from omnibase.protocol.protocol_registry_loader_test_case import (
    ProtocolRegistryLoaderTestCase,
)

from .core_onex_registry_loader_test_cases import (
    REGISTRY_LOADER_TEST_CASES,
    RegistryTestData,
)

# Context constants following canonical pattern from testing.md
MOCK_CONTEXT = 1
INTEGRATION_CONTEXT = 2


class MockRegistryLoader(ProtocolRegistry):
    """Mock registry loader for unit tests following protocol contract."""

    def __init__(self) -> None:
        self.artifacts: Dict[str, Any] = {}
        self._loaded = False
        self._test_data: Optional[RegistryTestData] = None

    def set_test_data(self, test_data: RegistryTestData) -> None:
        """Set test data for mock context."""
        self._test_data = test_data

    @classmethod
    def load_from_disk(cls) -> "ProtocolRegistry":
        """Mock implementation that simulates loading behavior."""
        return cls()

    @classmethod
    def load_mock(cls) -> "ProtocolRegistry":
        """Mock implementation for testing."""
        return cls()

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """Mock implementation."""
        return {}

    def discover_plugins(self) -> List[Any]:
        """Mock implementation."""
        return []

    def get_artifacts_by_type(self, artifact_type: str) -> Any:
        """Mock implementation."""
        return []

    def get_artifact_by_name_and_version(
        self, name: str, version: str, artifact_type: Optional[str] = None
    ) -> Any:
        """Mock implementation."""
        return None

    def get_all_artifacts(self) -> Any:
        """Mock implementation."""
        return {}

    def get_wip_artifacts(self) -> Any:
        """Mock implementation."""
        return []

    def validate_against_onextree(self, onextree_path: Optional[Path] = None) -> Any:
        """Mock implementation."""
        return {"valid": True, "reason": "Mock validation"}

    def get_registry_stats(self) -> Any:
        """Mock implementation."""
        return {"total_artifacts": 0, "by_type": {}, "wip_count": 0, "valid_count": 0}

    def get_load_result(self) -> Any:
        """Get mock load result for testing."""
        if not self._test_data:
            return type(
                "MockResult",
                (),
                {
                    "status": OnexStatus.ERROR,
                    "message": "No test data set",
                    "total_artifacts": 0,
                    "valid_artifacts": 0,
                    "invalid_artifacts": 0,
                    "wip_artifacts": 0,
                },
            )()

        # Simulate the loading result based on test data
        return type(
            "MockResult",
            (),
            {
                "status": OnexStatus.SUCCESS,
                "message": f"Mock loaded {self._test_data.expected_valid}/{self._test_data.expected_total} artifacts",
                "total_artifacts": self._test_data.expected_total,
                "valid_artifacts": self._test_data.expected_valid,
                "invalid_artifacts": self._test_data.expected_invalid,
                "wip_artifacts": self._test_data.expected_wip,
            },
        )()


@pytest.fixture(
    params=[
        pytest.param(MOCK_CONTEXT, id="mock", marks=pytest.mark.mock),
        pytest.param(
            INTEGRATION_CONTEXT, id="integration", marks=pytest.mark.integration
        ),
    ]
)
def registry_loader(request: Any) -> ProtocolRegistry:
    """
    Canonical registry loader fixture for ONEX registry-driven tests.
    Context mapping:
      MOCK_CONTEXT = 1 (mock context; in-memory, isolated)
      INTEGRATION_CONTEXT = 2 (integration context; real registry, disk-backed)
    - "mock" is synonymous with "mock context" in this system.
    - "integration" is synonymous with "real context."
    - IDs are for human-readable test output; markers are for CI tier filtering.
    Returns:
        ProtocolRegistry: A registry loader instance in the appropriate context.
    Raises:
        ValueError: If an unknown context is requested (future-proofing).
    """
    if request.param == MOCK_CONTEXT:
        return MockRegistryLoader()
    elif request.param == INTEGRATION_CONTEXT:
        return OnexRegistryLoader()
    else:
        raise ValueError(f"Unknown registry loader context: {request.param}")


@pytest.fixture
def temp_registry_structure() -> Any:
    """Fixture to create temporary registry structure for integration tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.mark.parametrize("case_id", [case.id for case in REGISTRY_LOADER_TEST_CASES])
def test_registry_loader_behavior(
    registry_loader: ProtocolRegistry, temp_registry_structure: Path, case_id: str
) -> None:
    """
    Registry-driven test that validates protocol contracts.

    This test follows the canonical pattern from testing.md:
    - Uses registry-driven test case discovery
    - Validates protocol contracts only (not implementation details)
    - Supports both mock and integration contexts via fixture injection
    - Uses CI tier markers for test selection
    """
    # Find the test case from registry
    test_case = next(case for case in REGISTRY_LOADER_TEST_CASES if case.id == case_id)

    # Set up test environment based on context
    if isinstance(registry_loader, MockRegistryLoader):
        # Mock context - set test data
        registry_loader.set_test_data(test_case.test_data)
        result = registry_loader.get_load_result()
    elif isinstance(registry_loader, OnexRegistryLoader):
        # Integration context - create real files
        _setup_integration_test_environment(temp_registry_structure, test_case)
        registry_loader.root_path = temp_registry_structure
        registry_loader.registry_path = temp_registry_structure / "registry.yaml"
        result = registry_loader._load_registry_data()

    # Validate protocol contract (not implementation details)
    assert result.status == test_case.expected_status, f"Status mismatch for {case_id}"
    assert (
        result.total_artifacts == test_case.test_data.expected_total
    ), f"Total artifacts mismatch for {case_id}"
    assert (
        result.valid_artifacts == test_case.test_data.expected_valid
    ), f"Valid artifacts mismatch for {case_id}"
    assert (
        result.invalid_artifacts == test_case.test_data.expected_invalid
    ), f"Invalid artifacts mismatch for {case_id}"
    assert (
        result.wip_artifacts == test_case.test_data.expected_wip
    ), f"WIP artifacts mismatch for {case_id}"


def test_registry_loader_initialization_protocol(
    registry_loader: ProtocolRegistry,
) -> None:
    """Test registry loader initialization follows protocol contract."""
    # Protocol-first validation - test public interface only
    assert hasattr(registry_loader, "load_from_disk")
    assert hasattr(registry_loader, "load_mock")
    assert hasattr(registry_loader, "get_node")
    assert hasattr(registry_loader, "discover_plugins")


def test_missing_registry_file_protocol(
    registry_loader: ProtocolRegistry, temp_registry_structure: Path
) -> None:
    """Test protocol behavior when registry file is missing."""
    if isinstance(registry_loader, OnexRegistryLoader):
        # Integration context - test with missing file
        registry_loader.root_path = temp_registry_structure
        registry_loader.registry_path = temp_registry_structure / "nonexistent.yaml"

        result = registry_loader._load_registry_data()

        # Protocol-first validation
        assert result.status == OnexStatus.ERROR
        assert "Registry file not found" in result.message
        assert result.total_artifacts == 0
        assert result.valid_artifacts == 0
    # Mock context doesn't need file system, so skip


def _setup_integration_test_environment(
    temp_path: Path, test_case: ProtocolRegistryLoaderTestCase
) -> None:
    """
    Set up integration test environment with real files.

    This helper creates the necessary directory structure and files
    for integration testing of the registry loader.
    """
    # Create registry.yaml
    registry_data = test_case.test_data.registry_yaml

    registry_path = temp_path / "registry.yaml"
    with open(registry_path, "w") as f:
        yaml.dump(registry_data, f)

    # Create artifact directories and files
    for artifact_type, artifacts in test_case.test_data.artifacts.items():
        for artifact_name, versions in artifacts.items():
            for version, files in versions.items():
                # Create version directory
                if artifact_type == "nodes":
                    artifact_dir = temp_path / "nodes" / artifact_name / version
                elif artifact_type == "cli_tools":
                    artifact_dir = temp_path / "cli_tools" / artifact_name / version
                else:
                    artifact_dir = temp_path / artifact_type / artifact_name / version

                artifact_dir.mkdir(parents=True, exist_ok=True)

                # Create files in the version directory
                for filename, content in files.items():
                    file_path = artifact_dir / filename
                    if filename == ".wip":
                        # Create empty .wip marker file
                        file_path.touch()
                    else:
                        # Create YAML file with content
                        with open(file_path, "w") as f:
                            yaml.dump(content, f)

    # Create .onextree file if test data includes it
    if (
        hasattr(test_case.test_data, "onextree_data")
        and test_case.test_data.onextree_data
    ):
        onextree_path = temp_path / ".onextree"
        with open(onextree_path, "w") as f:
            yaml.dump(test_case.test_data.onextree_data, f)


def test_onextree_validation_protocol(
    registry_loader: ProtocolRegistry, temp_registry_structure: Path
) -> None:
    """Test .onextree validation follows protocol contract."""
    if isinstance(registry_loader, OnexRegistryLoader):
        # Set up a simple test environment
        _setup_integration_test_environment(
            temp_registry_structure,
            type(
                "TestCase",
                (),
                {
                    "test_data": type(
                        "TestData",
                        (),
                        {"expected_wip": 0, "artifacts": {}, "registry_yaml": {}},
                    )()
                },
            )(),
        )
        registry_loader.root_path = temp_registry_structure
        registry_loader.registry_path = temp_registry_structure / "registry.yaml"

        # Test .onextree validation
        result = registry_loader.validate_against_onextree()
        assert isinstance(result, dict)
        assert "valid" in result
        assert "reason" in result
        assert "missing_artifacts" in result
        assert "extra_artifacts" in result


def test_compatibility_metadata_protocol(
    registry_loader: ProtocolRegistry, temp_registry_structure: Path
) -> None:
    """Test compatibility metadata handling follows protocol contract."""
    if isinstance(registry_loader, OnexRegistryLoader):
        # Find a test case with compatibility metadata
        compat_test_case = next(
            case
            for case in REGISTRY_LOADER_TEST_CASES
            if case.id == "compatibility_metadata_support"
        )

        # Set up test environment
        _setup_integration_test_environment(temp_registry_structure, compat_test_case)
        registry_loader.root_path = temp_registry_structure
        registry_loader.registry_path = temp_registry_structure / "registry.yaml"

        # Load the registry
        result = registry_loader._load_registry_data()

        # Verify compatibility metadata is preserved
        assert result.status == OnexStatus.SUCCESS
        artifacts = registry_loader.get_artifacts_by_type("nodes")
        assert len(artifacts) > 0

        # Check that metadata includes compatibility information
        compat_artifact = artifacts[0]
        assert compat_artifact.metadata is not None
        assert "compatibility" in compat_artifact.metadata


def test_multiple_versions_protocol(
    registry_loader: ProtocolRegistry, temp_registry_structure: Path
) -> None:
    """Test multiple version support follows protocol contract."""
    if isinstance(registry_loader, OnexRegistryLoader):
        # Find the multiple versions test case
        versions_test_case = next(
            case
            for case in REGISTRY_LOADER_TEST_CASES
            if case.id == "multiple_versions_support"
        )

        # Set up test environment
        _setup_integration_test_environment(temp_registry_structure, versions_test_case)
        registry_loader.root_path = temp_registry_structure
        registry_loader.registry_path = temp_registry_structure / "registry.yaml"

        # Load the registry
        result = registry_loader._load_registry_data()

        # Verify multiple versions are loaded
        assert result.status == OnexStatus.SUCCESS
        assert result.total_artifacts == 3
        assert result.valid_artifacts == 3
        assert result.wip_artifacts == 1

        # Check that we can retrieve specific versions
        artifacts = registry_loader.get_artifacts_by_type("nodes")
        assert len(artifacts) == 3

        # Verify different versions exist
        versions = [artifact.version for artifact in artifacts]
        assert "v1_0_0" in versions
        assert "v1_1_0" in versions
        assert "v2_0_0" in versions


def test_wip_marker_precedence_protocol(
    registry_loader: ProtocolRegistry, temp_registry_structure: Path
) -> None:
    """Test WIP marker precedence follows protocol contract."""
    if isinstance(registry_loader, OnexRegistryLoader):
        # Find the WIP precedence test case
        wip_test_case = next(
            case
            for case in REGISTRY_LOADER_TEST_CASES
            if case.id == "wip_precedence_over_metadata"
        )

        # Set up test environment
        _setup_integration_test_environment(temp_registry_structure, wip_test_case)
        registry_loader.root_path = temp_registry_structure
        registry_loader.registry_path = temp_registry_structure / "registry.yaml"

        # Load the registry
        result = registry_loader._load_registry_data()

        # Verify WIP marker takes precedence
        assert result.status == OnexStatus.SUCCESS
        assert result.wip_artifacts == 1

        # Check that the artifact is marked as WIP
        wip_artifacts = registry_loader.get_wip_artifacts()
        assert len(wip_artifacts) == 1
        assert wip_artifacts[0].is_wip is True


def test_artifact_retrieval_protocol(
    registry_loader: ProtocolRegistry, temp_registry_structure: Path
) -> None:
    """Test artifact retrieval methods follow protocol contract."""
    if isinstance(registry_loader, OnexRegistryLoader):
        # Set up a simple test environment
        _setup_integration_test_environment(
            temp_registry_structure,
            type(
                "TestCase",
                (),
                {
                    "test_data": type(
                        "TestData",
                        (),
                        {"expected_wip": 0, "artifacts": {}, "registry_yaml": {}},
                    )()
                },
            )(),
        )
        registry_loader.root_path = temp_registry_structure
        registry_loader.registry_path = temp_registry_structure / "registry.yaml"

        # Load the registry
        registry_loader._load_registry_data()

        # Test protocol methods
        artifacts = registry_loader.get_artifacts_by_type("nodes")
        assert isinstance(artifacts, list)

        all_artifacts = registry_loader.get_all_artifacts()
        assert isinstance(all_artifacts, dict)

        wip_artifacts = registry_loader.get_wip_artifacts()
        assert isinstance(wip_artifacts, list)

        stats = registry_loader.get_registry_stats()
        assert isinstance(stats, dict)
        assert "total_artifacts" in stats
