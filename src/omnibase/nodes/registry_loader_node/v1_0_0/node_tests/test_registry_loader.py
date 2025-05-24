# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_registry_loader.py
# version: 1.0.0
# uuid: 3f3d565e-11fe-4179-9fc1-180db9203367
# author: OmniNode Team
# created_at: 2025-05-24T09:36:56.350866
# last_modified_at: 2025-05-24T13:39:57.892470
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 1837633bc3baba3af3d99ef7f1a63e7c47f6d67a8cb844a479bbcf2932b4724f
# entrypoint: python@test_registry_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_registry_loader
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Test suite for registry_loader_node.

Tests the registry loading functionality using canonical testing patterns:
- Registry-driven test cases from existing infrastructure
- Protocol-driven testing with fixture injection
- Model-based assertions instead of string-based checks
"""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from omnibase.core.core_tests.core_onex_registry_loader_test_cases import (
    REGISTRY_LOADER_TEST_CASES,
)
from omnibase.model.enum_onex_status import OnexStatus

from ..helpers.registry_engine import RegistryEngine
from ..models.state import (
    ArtifactTypeEnum,
    RegistryLoaderInputState,
    RegistryLoaderOutputState,
)
from ..node import run_registry_loader_node


class TestRegistryLoaderNode:
    """
    Test class for registry_loader_node.

    Tests core functionality using existing registry test infrastructure
    following canonical testing patterns.
    """

    @pytest.mark.parametrize(
        "test_case", REGISTRY_LOADER_TEST_CASES, ids=lambda tc: tc.id
    )
    def test_registry_loader_with_existing_cases(
        self, test_case: Any, registry_test_environment: Any
    ) -> None:
        """
        Test registry loader node using existing registry test cases.

        This leverages the comprehensive test cases from the core registry loader
        and uses fixture injection for test environment setup.
        """
        temp_path = registry_test_environment(test_case.test_data)

        input_state = RegistryLoaderInputState(
            version="1.0.0",
            root_directory=str(temp_path),
            include_wip=True,  # Include WIP to test all scenarios
        )

        mock_event_bus = Mock()
        result = run_registry_loader_node(input_state, event_bus=mock_event_bus)

        # Verify the result matches expectations using model-based assertions
        assert isinstance(result, RegistryLoaderOutputState)
        assert result.version == "1.0.0"

        # Check status based on test case expectations
        if test_case.expected_status == OnexStatus.SUCCESS:
            assert result.status in [OnexStatus.SUCCESS, OnexStatus.WARNING]
        else:
            assert result.status == test_case.expected_status

        # Verify artifact counts using model fields
        assert result.artifact_count == test_case.test_data.expected_total
        assert result.valid_artifact_count == test_case.test_data.expected_valid
        assert result.invalid_artifact_count == test_case.test_data.expected_invalid
        assert result.wip_artifact_count == test_case.test_data.expected_wip
        assert len(result.artifacts) == test_case.test_data.expected_total

        # Verify WIP artifacts are correctly identified using model properties
        wip_artifacts = [a for a in result.artifacts if a.is_wip]
        assert len(wip_artifacts) == test_case.test_data.expected_wip

        # Verify valid/invalid artifacts using model metadata
        valid_artifacts = [
            a for a in result.artifacts if a.metadata.get("_is_valid", True)
        ]
        invalid_artifacts = [
            a for a in result.artifacts if not a.metadata.get("_is_valid", True)
        ]
        assert len(valid_artifacts) == test_case.test_data.expected_valid
        assert len(invalid_artifacts) == test_case.test_data.expected_invalid

        # Verify events were emitted
        assert (
            mock_event_bus.publish.call_count >= 2
        )  # At least START and SUCCESS/FAILURE

    def test_registry_loader_artifact_type_filtering(
        self, registry_test_environment: Any
    ) -> None:
        """
        Test artifact type filtering functionality using enum-based filtering.
        """
        # Find any test case that has node artifacts
        node_case = None
        for case in REGISTRY_LOADER_TEST_CASES:
            if (
                case.test_data.expected_total > 0
                and "nodes" in case.test_data.registry_yaml
                and len(case.test_data.registry_yaml["nodes"]) > 0
            ):
                node_case = case
                break

        if not node_case:
            pytest.skip("No test case with node artifacts found")

        temp_path = registry_test_environment(node_case.test_data)

        # Test filtering to only nodes using enum
        input_state = RegistryLoaderInputState(
            version="1.0.0",
            root_directory=str(temp_path),
            artifact_types=[ArtifactTypeEnum.NODES],
        )

        mock_event_bus = Mock()
        result = run_registry_loader_node(input_state, event_bus=mock_event_bus)

        # Should only include nodes - verify using enum comparison
        nodes_found = [
            a for a in result.artifacts if a.artifact_type == ArtifactTypeEnum.NODES
        ]
        assert len(nodes_found) > 0
        assert ArtifactTypeEnum.NODES in result.artifact_types_found

        # Verify no other types are included
        non_node_artifacts = [
            a for a in result.artifacts if a.artifact_type != ArtifactTypeEnum.NODES
        ]
        assert len(non_node_artifacts) == 0

    def test_registry_loader_wip_handling(self, registry_test_environment: Any) -> None:
        """
        Test WIP artifact handling with include/exclude scenarios.
        """
        # Find a test case with WIP artifacts
        wip_case = None
        for case in REGISTRY_LOADER_TEST_CASES:
            if case.test_data.expected_wip > 0:
                wip_case = case
                break

        if not wip_case:
            pytest.skip("No WIP test case found")

        temp_path = registry_test_environment(wip_case.test_data)

        # Test excluding WIP artifacts
        input_state = RegistryLoaderInputState(
            version="1.0.0",
            root_directory=str(temp_path),
            include_wip=False,
        )

        mock_event_bus = Mock()
        result = run_registry_loader_node(input_state, event_bus=mock_event_bus)

        # Should exclude WIP artifacts
        wip_artifacts = [a for a in result.artifacts if a.is_wip]
        assert len(wip_artifacts) == 0
        assert result.wip_artifact_count == 0

        # Test including WIP artifacts
        input_state.include_wip = True
        result = run_registry_loader_node(input_state, event_bus=mock_event_bus)

        # Should include WIP artifacts
        wip_artifacts = [a for a in result.artifacts if a.is_wip]
        assert len(wip_artifacts) == wip_case.test_data.expected_wip
        assert result.wip_artifact_count == wip_case.test_data.expected_wip

    def test_registry_loader_error_scenarios(self) -> None:
        """
        Test various error scenarios and error handling.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test 1: Missing registry.yaml
            input_state = RegistryLoaderInputState(
                version="1.0.0",
                root_directory=str(temp_path),
            )

            mock_event_bus = Mock()
            result = run_registry_loader_node(input_state, event_bus=mock_event_bus)

            # Verify error status using enum
            assert result.status == OnexStatus.ERROR
            assert "Failed to load registry.yaml" in result.message
            assert result.artifact_count == 0

    def test_registry_engine_directly(self) -> None:
        """
        Test the registry engine directly for more granular testing.
        """
        engine = RegistryEngine()

        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = RegistryLoaderInputState(
                version="1.0.0",
                root_directory=str(temp_dir),
                include_wip=False,
            )

            result = engine.load_registry(input_state)

            # Verify engine results using model validation
            assert isinstance(result, RegistryLoaderOutputState)
            assert result.status == OnexStatus.ERROR  # No registry.yaml
            assert result.artifact_count == 0

    def test_registry_loader_state_validation(self) -> None:
        """
        Test input and output state validation using Pydantic models.
        """
        # Test valid input state with enum
        input_state = RegistryLoaderInputState(
            version="1.0.0",
            root_directory="/tmp",
            artifact_types=[ArtifactTypeEnum.NODES],
        )

        assert input_state.artifact_types == [ArtifactTypeEnum.NODES]
        assert input_state.include_wip is False  # Default value

        # Test serialization/deserialization
        json_data = input_state.model_dump_json()
        assert isinstance(json_data, str)

        parsed_state = RegistryLoaderInputState.model_validate_json(json_data)
        assert parsed_state.artifact_types == [ArtifactTypeEnum.NODES]

        # Test invalid enum value
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            RegistryLoaderInputState(
                version="1.0.0",
                root_directory="/tmp",
                artifact_types=["invalid_type"],  # type: ignore
            )


# Fixtures following canonical patterns
@pytest.fixture
def registry_loader_input_state() -> RegistryLoaderInputState:
    """
    Fixture for common input state.
    """
    return RegistryLoaderInputState(
        version="1.0.0",
        root_directory="/tmp/test_registry",
        include_wip=False,
    )


@pytest.fixture
def mock_event_bus() -> Mock:
    """
    Fixture for mock event bus.
    """
    return Mock()


@pytest.fixture
def registry_test_environment() -> Any:
    """
    Fixture to create test environment from registry test data.

    This follows the protocol-driven pattern by accepting test data
    and setting up the appropriate file structure.
    """

    def _setup_environment(test_data: Any) -> Path:
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)

        # Use the existing test infrastructure to set up the environment
        # This delegates to the existing, tested setup logic
        from ..node_tests.test_registry_loader_setup import setup_test_environment

        setup_test_environment(temp_path, test_data)

        return temp_path

    return _setup_environment
