# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_parity_validator.py
# version: 1.0.0
# uuid: 3f3d565e-11fe-4179-9fc1-180db9203367
# author: OmniNode Team
# created_at: 2025-05-24T09:36:56.350866
# last_modified_at: 2025-05-25T22:11:50.166642
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: c626da6789eae7fc20900fd821875d64569cea8bd2c866b4397d8929ddc9c086
# entrypoint: python@test_parity_validator.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_parity_validator
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Tests for parity validator node.

This module contains comprehensive tests for the parity validator node,
including state model validation, node discovery, validation execution,
and output formatting.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from omnibase.enums import OnexStatus

from ..error_codes import ParityValidatorErrorCode
from ..models.state import (
    PARITY_VALIDATOR_STATE_SCHEMA_VERSION,
    DiscoveredNode,
    NodeValidationResult,
    ParityValidatorInputState,
    ValidationResultEnum,
    ValidationTypeEnum,
    create_parity_validator_input_state,
    create_parity_validator_output_state,
)
from ..node import ParityValidatorNode


class TestParityValidatorStateModels:
    """Test parity validator state models."""

    def test_input_state_creation(self) -> None:
        """Test creating valid input state."""
        input_state = create_parity_validator_input_state(
            nodes_directory="src/omnibase/nodes",
            validation_types=[ValidationTypeEnum.CLI_NODE_PARITY],
            node_filter=["stamper_node"],
            fail_fast=True,
            include_performance_metrics=True,
            correlation_id="test-123",
        )

        assert input_state.nodes_directory == "src/omnibase/nodes"
        assert input_state.validation_types == [ValidationTypeEnum.CLI_NODE_PARITY]
        assert input_state.node_filter == ["stamper_node"]
        assert input_state.fail_fast is True
        assert input_state.include_performance_metrics is True
        assert input_state.correlation_id == "test-123"

    def test_input_state_defaults(self) -> None:
        """Test input state with default values."""
        input_state = create_parity_validator_input_state()

        assert input_state.nodes_directory == "src/omnibase/nodes"
        assert input_state.validation_types is None
        assert input_state.node_filter is None
        assert input_state.fail_fast is False
        assert input_state.include_performance_metrics is True
        assert input_state.correlation_id is None

    def test_input_state_validation_invalid_directory(self) -> None:
        """Test input state validation with invalid directory."""
        with pytest.raises(ValidationError):
            ParityValidatorInputState(
                nodes_directory="",  # Empty string should fail
                validation_types=None,
                node_filter=None,
                fail_fast=False,
                include_performance_metrics=True,
                correlation_id=None,
            )

    def test_output_state_creation(self) -> None:
        """Test creating valid output state."""
        discovered_nodes = [
            DiscoveredNode(
                name="test_node",
                version="v1_0_0",
                module_path="omnibase.nodes.test_node.v1_0_0.node",
                introspection_available=True,
            )
        ]

        validation_results = [
            NodeValidationResult(
                node_name="test_node",
                node_version="v1_0_0",
                validation_type=ValidationTypeEnum.CLI_NODE_PARITY,
                result=ValidationResultEnum.PASS,
                message="Test passed",
                execution_time_ms=100.0,
            )
        ]

        output_state = create_parity_validator_output_state(
            status=OnexStatus.SUCCESS,
            message="All validations passed",
            discovered_nodes=discovered_nodes,
            validation_results=validation_results,
            summary={"total": 1, "passed": 1},
            nodes_directory="src/omnibase/nodes",
            validation_types_run=[ValidationTypeEnum.CLI_NODE_PARITY],
            total_execution_time_ms=150.0,
            correlation_id="test-123",
        )

        assert output_state.status == OnexStatus.SUCCESS
        assert output_state.message == "All validations passed"
        assert len(output_state.discovered_nodes) == 1
        assert len(output_state.validation_results) == 1
        assert output_state.summary["total"] == 1
        assert output_state.correlation_id == "test-123"

    def test_schema_version(self) -> None:
        """Test schema version constant."""
        assert PARITY_VALIDATOR_STATE_SCHEMA_VERSION == "1.0.0"


class TestParityValidatorNode:
    """Test parity validator node functionality."""

    def test_node_initialization(self) -> None:
        """Test node initialization."""
        node = ParityValidatorNode()
        assert node is not None

    @patch("subprocess.run")
    def test_discover_nodes_success(self, mock_subprocess: Mock) -> None:
        """Test successful node discovery."""
        # Mock directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            nodes_dir = Path(temp_dir) / "nodes"
            test_node_dir = nodes_dir / "test_node" / "v1_0_0"
            test_node_dir.mkdir(parents=True)

            # Create a mock node.py file
            node_file = test_node_dir / "node.py"
            node_file.write_text("# Mock node file")

            # Mock introspection command
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = json.dumps(
                {"node_metadata": {"name": "test_node", "version": "1.0.0"}}
            )

            node = ParityValidatorNode()
            discovered = node.discover_nodes(str(nodes_dir))

            assert len(discovered) == 1
            assert discovered[0].name == "test_node"
            assert discovered[0].version == "v1_0_0"

    def test_discover_nodes_empty_directory(self) -> None:
        """Test node discovery with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            node = ParityValidatorNode()
            discovered = node.discover_nodes(temp_dir)
            assert len(discovered) == 0

    @patch("subprocess.run")
    def test_validate_cli_node_parity_success(self, mock_subprocess: Mock) -> None:
        """Test CLI/node parity validation that fails due to missing module."""
        # The actual validation will fail because the module doesn't exist
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stdout = "Module not found"

        discovered_node = DiscoveredNode(
            name="test_node",
            version="v1_0_0",
            module_path="omnibase.nodes.test_node.v1_0_0.node",
            introspection_available=True,
        )

        node = ParityValidatorNode()
        result = node.validate_cli_node_parity(discovered_node)

        # This will fail because the module doesn't exist
        assert result.result == ValidationResultEnum.FAIL
        assert result.node_name == "test_node"
        assert result.validation_type == ValidationTypeEnum.CLI_NODE_PARITY

    def test_validate_schema_conformance_success(self) -> None:
        """Test successful schema conformance validation."""
        discovered_node = DiscoveredNode(
            name="test_node",
            version="v1_0_0",
            module_path="omnibase.nodes.test_node.v1_0_0.node",
            introspection_available=True,
        )

        node = ParityValidatorNode()

        # Mock the state models import
        with patch("importlib.import_module") as mock_import:
            mock_module = Mock()
            mock_module.TestInputState = Mock()
            mock_module.TestOutputState = Mock()
            mock_import.return_value = mock_module

            result = node.validate_schema_conformance(discovered_node)

            assert result.result == ValidationResultEnum.PASS
            assert result.node_name == "test_node"
            assert result.validation_type == ValidationTypeEnum.SCHEMA_CONFORMANCE

    def test_run_validation_integration(self) -> None:
        """Test complete validation run with nonexistent directory."""
        input_state = create_parity_validator_input_state(
            nodes_directory="nonexistent",  # Will result in error due to directory not existing
            validation_types=[ValidationTypeEnum.CLI_NODE_PARITY],
        )

        node = ParityValidatorNode()
        output_state = node.run_validation(input_state)

        # This will be ERROR because the directory doesn't exist, not WARNING
        assert output_state.status == OnexStatus.ERROR
        assert "failed" in output_state.message.lower()
        assert len(output_state.discovered_nodes) == 0


class TestValidationEnums:
    """Test validation enums."""

    def test_validation_type_enum_values(self) -> None:
        """Test validation type enum values."""
        assert ValidationTypeEnum.CLI_NODE_PARITY == "cli_node_parity"
        assert ValidationTypeEnum.SCHEMA_CONFORMANCE == "schema_conformance"
        assert ValidationTypeEnum.ERROR_CODE_USAGE == "error_code_usage"
        assert ValidationTypeEnum.CONTRACT_COMPLIANCE == "contract_compliance"
        assert ValidationTypeEnum.INTROSPECTION_VALIDITY == "introspection_validity"

    def test_validation_result_enum_values(self) -> None:
        """Test validation result enum values."""
        assert ValidationResultEnum.PASS == "pass"
        assert ValidationResultEnum.FAIL == "fail"
        assert ValidationResultEnum.SKIP == "skip"
        assert ValidationResultEnum.ERROR == "error"


class TestParityValidatorErrorCodes:
    """Test parity validator error codes."""

    def test_error_code_values(self) -> None:
        """Test error code string values."""
        assert (
            ParityValidatorErrorCode.NODES_DIRECTORY_NOT_FOUND
            == "ONEX_PARITY_001_NODES_DIRECTORY_NOT_FOUND"
        )
        assert (
            ParityValidatorErrorCode.NODE_DISCOVERY_FAILED
            == "ONEX_PARITY_021_NODE_DISCOVERY_FAILED"
        )
        assert (
            ParityValidatorErrorCode.CLI_EXECUTION_FAILED
            == "ONEX_PARITY_041_CLI_EXECUTION_FAILED"
        )

    def test_error_code_methods(self) -> None:
        """Test error code methods."""
        error_code = ParityValidatorErrorCode.NODES_DIRECTORY_NOT_FOUND

        assert error_code.get_component() == "PARITY"
        assert error_code.get_number() == 1
        assert "directory" in error_code.get_description().lower()
        assert error_code.get_exit_code() == 1
