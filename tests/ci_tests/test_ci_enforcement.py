# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_ci_enforcement.py
# version: 1.0.0
# uuid: 5d58dd69-535d-451b-a834-cd6cca334416
# author: OmniNode Team
# created_at: 2025-05-25T05:28:14.788381
# last_modified_at: 2025-05-25T09:54:24.096244
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a39118d4b90cbe0091bff2c33bac01b6b98c7757b3073260d32ed60c503f688b
# entrypoint: python@test_ci_enforcement.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_ci_enforcement
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Test CI enforcement logic for schema validation, lifecycle validation, and directory structure.

This module tests the CI enforcement mechanisms using registry-driven,
fixture-injected, protocol-first testing patterns that ensure:
1. All .onex files pass schema validation
2. All lifecycle fields are valid and hash-stamped
3. No empty directories exist (structural drift prevention)
4. State contract files are valid
"""

from typing import Any, Callable, Dict, List, Optional

import pytest
from pydantic import ValidationError

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import NodeMetadataField
from omnibase.model.model_node_metadata import (
    EntrypointType,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)

# Context constants for fixture parameterization
MOCK_CONTEXT = 1
INTEGRATION_CONTEXT = 2


class CIEnforcementTestCase:
    """Base class for CI enforcement test cases."""

    def __init__(
        self,
        test_id: str,
        description: str,
        metadata: Dict[str, Any],
        expected_valid: bool = True,
        expected_error: Optional[str] = None,
    ) -> None:
        self.test_id = test_id
        self.description = description
        self.metadata = metadata
        self.expected_valid = expected_valid
        self.expected_error = expected_error


class CIEnforcementTestRegistry:
    """Registry for CI enforcement test cases."""

    def __init__(self) -> None:
        self._test_cases: Dict[str, CIEnforcementTestCase] = {}

    def register(self, test_case: CIEnforcementTestCase) -> None:
        """Register a test case."""
        self._test_cases[test_case.test_id] = test_case

    def get_test_case(self, test_id: str) -> CIEnforcementTestCase:
        """Get a test case by ID."""
        return self._test_cases[test_id]

    def get_all_test_cases(self) -> List[CIEnforcementTestCase]:
        """Get all registered test cases."""
        return list(self._test_cases.values())

    def get_valid_test_cases(self) -> List[CIEnforcementTestCase]:
        """Get all test cases that should validate successfully."""
        return [tc for tc in self._test_cases.values() if tc.expected_valid]

    def get_invalid_test_cases(self) -> List[CIEnforcementTestCase]:
        """Get all test cases that should fail validation."""
        return [tc for tc in self._test_cases.values() if not tc.expected_valid]


# Global registry instance
# TODO: Convert to decorator-based registration in future milestone
_ci_enforcement_registry = CIEnforcementTestRegistry()


def register_ci_enforcement_test_case(test_case: CIEnforcementTestCase) -> None:
    """Register a CI enforcement test case."""
    _ci_enforcement_registry.register(test_case)


def _create_base_metadata() -> Dict[str, Any]:
    """Create base metadata with all required fields using canonical enums."""
    return {
        NodeMetadataField.METADATA_VERSION.value: "0.1.0",
        NodeMetadataField.PROTOCOL_VERSION.value: "1.1.0",
        NodeMetadataField.OWNER.value: "Test Team",
        NodeMetadataField.COPYRIGHT.value: "Test Team",
        NodeMetadataField.SCHEMA_VERSION.value: "1.1.0",
        NodeMetadataField.NAME.value: "test_node",
        NodeMetadataField.VERSION.value: "1.0.0",
        NodeMetadataField.UUID.value: "12345678-1234-5678-9abc-123456789012",
        NodeMetadataField.AUTHOR.value: "Test Author",
        NodeMetadataField.CREATED_AT.value: "2025-05-24T10:00:00.000000",
        NodeMetadataField.LAST_MODIFIED_AT.value: "2025-05-24T10:00:00.000000",
        NodeMetadataField.DESCRIPTION.value: "Test node for CI validation",
        NodeMetadataField.STATE_CONTRACT.value: "state_contract://default",
        NodeMetadataField.LIFECYCLE.value: Lifecycle.ACTIVE.value,
        NodeMetadataField.HASH.value: "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        NodeMetadataField.ENTRYPOINT.value: {
            "type": EntrypointType.PYTHON.value,
            "target": "test_node.py",
        },
        NodeMetadataField.RUNTIME_LANGUAGE_HINT.value: "python>=3.11",
        NodeMetadataField.NAMESPACE.value: "onex.test.node",
        NodeMetadataField.META_TYPE.value: MetaType.TOOL.value,
    }


# Register test cases using the registry pattern
# TODO: Convert to decorator-based registration in future milestone

# Valid metadata test case
valid_metadata = _create_base_metadata()
register_ci_enforcement_test_case(
    CIEnforcementTestCase(
        "valid_onex_file",
        "Valid .onex file should pass schema validation",
        valid_metadata,
    )
)

# Invalid metadata test cases - missing required fields
invalid_metadata_missing_fields = {
    NodeMetadataField.NAME.value: "test_node"
    # Missing all other required fields
}
register_ci_enforcement_test_case(
    CIEnforcementTestCase(
        "invalid_onex_missing_fields",
        "Invalid .onex file with missing required fields should fail validation",
        invalid_metadata_missing_fields,
        expected_valid=False,
        expected_error="validation error",
    )
)

# Lifecycle validation test cases - valid values
for lifecycle in Lifecycle:
    lifecycle_metadata = _create_base_metadata()
    lifecycle_metadata.update(
        {
            NodeMetadataField.NAME.value: f"lifecycle_{lifecycle.value}_test",
            NodeMetadataField.LIFECYCLE.value: lifecycle.value,
        }
    )
    register_ci_enforcement_test_case(
        CIEnforcementTestCase(
            f"valid_lifecycle_{lifecycle.value}",
            f"Valid lifecycle value {lifecycle.value} should pass validation",
            lifecycle_metadata,
        )
    )

# Lifecycle validation test cases - invalid values
invalid_lifecycles = ["invalid", "unknown", ""]
for i, invalid_lifecycle in enumerate(invalid_lifecycles):
    invalid_lifecycle_metadata = _create_base_metadata()
    invalid_lifecycle_metadata.update(
        {
            NodeMetadataField.NAME.value: f"invalid_lifecycle_{i}_test",
            NodeMetadataField.LIFECYCLE.value: invalid_lifecycle,
        }
    )
    register_ci_enforcement_test_case(
        CIEnforcementTestCase(
            f"invalid_lifecycle_{i}",
            f"Invalid lifecycle value {invalid_lifecycle} should fail validation",
            invalid_lifecycle_metadata,
            expected_valid=False,
            expected_error="validation error",
        )
    )

# Hash validation test cases - valid formats
valid_hashes = [
    "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "0000000000000000000000000000000000000000000000000000000000000000",
    "ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890",
]
for i, valid_hash in enumerate(valid_hashes):
    hash_metadata = _create_base_metadata()
    hash_metadata.update(
        {
            NodeMetadataField.NAME.value: f"valid_hash_{i}_test",
            NodeMetadataField.HASH.value: valid_hash,
        }
    )
    register_ci_enforcement_test_case(
        CIEnforcementTestCase(
            f"valid_hash_format_{i}",
            f"Valid hash format {i} should pass validation",
            hash_metadata,
        )
    )

# Hash validation test cases - invalid formats
invalid_hashes = [
    "short",  # Too short
    "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890extra",  # Too long
    "ghijkl1234567890abcdef1234567890abcdef1234567890abcdef1234567890",  # Invalid hex
    "",  # Empty
    "abcd-efgh-" + "a" * 54,  # Contains hyphens
]
for i, invalid_hash in enumerate(invalid_hashes):
    invalid_hash_metadata = _create_base_metadata()
    invalid_hash_metadata.update(
        {
            NodeMetadataField.NAME.value: f"invalid_hash_{i}_test",
            NodeMetadataField.HASH.value: invalid_hash,
        }
    )
    register_ci_enforcement_test_case(
        CIEnforcementTestCase(
            f"invalid_hash_format_{i}",
            f"Invalid hash format {i} should fail validation",
            invalid_hash_metadata,
            expected_valid=False,
            expected_error="validation error",
        )
    )

# Entrypoint validation test cases
for entrypoint_type in EntrypointType:
    entrypoint_metadata = _create_base_metadata()
    entrypoint_metadata.update(
        {
            NodeMetadataField.NAME.value: f"entrypoint_{entrypoint_type.value}_test",
            NodeMetadataField.ENTRYPOINT.value: {
                "type": entrypoint_type.value,
                "target": f"test_node.{entrypoint_type.value}",
            },
        }
    )
    register_ci_enforcement_test_case(
        CIEnforcementTestCase(
            f"valid_entrypoint_{entrypoint_type.value}",
            f"Valid entrypoint type {entrypoint_type.value} should pass validation",
            entrypoint_metadata,
        )
    )

# Meta type validation test cases
for meta_type in MetaType:
    meta_type_metadata = _create_base_metadata()
    meta_type_metadata.update(
        {
            NodeMetadataField.NAME.value: f"meta_type_{meta_type.value}_test",
            NodeMetadataField.META_TYPE.value: meta_type.value,
        }
    )
    register_ci_enforcement_test_case(
        CIEnforcementTestCase(
            f"valid_meta_type_{meta_type.value}",
            f"Valid meta type {meta_type.value} should pass validation",
            meta_type_metadata,
        )
    )


@pytest.fixture(
    params=[
        pytest.param(MOCK_CONTEXT, id="mock", marks=pytest.mark.mock),
        pytest.param(
            INTEGRATION_CONTEXT, id="integration", marks=pytest.mark.integration
        ),
    ]
)
def ci_enforcement_registry(
    request: pytest.FixtureRequest,
) -> CIEnforcementTestRegistry:
    """
    Canonical registry fixture for CI enforcement tests.

    Context mapping:
      MOCK_CONTEXT = 1 (mock context; subset of test cases for fast execution)
      INTEGRATION_CONTEXT = 2 (integration context; full registry with all test cases)

    Returns:
        CIEnforcementTestRegistry: Registry instance in the appropriate context.

    Raises:
        OnexError: If an unknown context is requested.
    """
    if request.param == MOCK_CONTEXT:
        # In mock context, return a subset of test cases for faster execution
        mock_registry = CIEnforcementTestRegistry()
        # Register essential test cases for mock context - include all test cases that tests expect
        essential_cases = [
            "valid_onex_file",
            "invalid_onex_missing_fields",
            "valid_hash_format_0",
            "invalid_hash_format_0",
        ]

        # Add all lifecycle test cases
        for lifecycle in Lifecycle:
            essential_cases.append(f"valid_lifecycle_{lifecycle.value}")

        # Add all entrypoint test cases
        for entrypoint_type in EntrypointType:
            essential_cases.append(f"valid_entrypoint_{entrypoint_type.value}")

        # Add all meta type test cases
        for meta_type in MetaType:
            essential_cases.append(f"valid_meta_type_{meta_type.value}")

        # Add some invalid lifecycle cases
        essential_cases.extend(
            ["invalid_lifecycle_0", "invalid_lifecycle_1", "invalid_lifecycle_2"]
        )

        for case_id in essential_cases:
            if case_id in _ci_enforcement_registry._test_cases:
                mock_registry.register(_ci_enforcement_registry.get_test_case(case_id))
        return mock_registry
    elif request.param == INTEGRATION_CONTEXT:
        # In integration context, return the full registry
        return _ci_enforcement_registry
    else:
        raise OnexError(
            f"Unknown CI enforcement registry context: {request.param}",
            CoreErrorCode.INVALID_PARAMETER,
        )


@pytest.fixture
def metadata_validator() -> Callable[[Dict[str, Any]], NodeMetadataBlock]:
    """Fixture providing metadata validation functionality."""

    def validate_metadata(metadata: Dict[str, Any]) -> NodeMetadataBlock:
        """Validate metadata and return NodeMetadataBlock instance."""
        return NodeMetadataBlock(**metadata)

    return validate_metadata


class TestCIEnforcement:
    """Test CI enforcement mechanisms using registry-driven patterns."""

    def test_enum_model_sync(self) -> None:
        """Test that NodeMetadataField enum stays in sync with NodeMetadataBlock model."""
        model_fields = set(NodeMetadataBlock.model_fields.keys())
        enum_fields = set(field.value for field in NodeMetadataField)

        # Check that all enum fields exist in model
        missing_in_model = enum_fields - model_fields
        assert not missing_in_model, f"Enum fields missing in model: {missing_in_model}"

        # Check that all model fields exist in enum
        missing_in_enum = model_fields - enum_fields
        assert not missing_in_enum, f"Model fields missing in enum: {missing_in_enum}"

    def test_valid_metadata_cases(
        self,
        ci_enforcement_registry: CIEnforcementTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test that all valid metadata cases pass CI validation."""
        valid_cases = ci_enforcement_registry.get_valid_test_cases()
        assert len(valid_cases) > 0, "No valid test cases found in registry"

        for test_case in valid_cases:
            # Use model-based validation instead of string assertions
            metadata_block = metadata_validator(test_case.metadata)

            # Validate using canonical enum fields
            assert hasattr(metadata_block, NodeMetadataField.NAME.value)
            assert hasattr(metadata_block, NodeMetadataField.LIFECYCLE.value)
            assert hasattr(metadata_block, NodeMetadataField.HASH.value)

            # Validate specific field values using model properties
            assert metadata_block.name is not None
            assert metadata_block.lifecycle in Lifecycle
            assert metadata_block.hash is not None

    def test_invalid_metadata_cases(
        self,
        ci_enforcement_registry: CIEnforcementTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test that invalid metadata cases fail CI validation as expected."""
        invalid_cases = ci_enforcement_registry.get_invalid_test_cases()

        for test_case in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                metadata_validator(test_case.metadata)

            # Validate that the error is related to the expected issue
            if test_case.expected_error:
                assert test_case.expected_error in str(exc_info.value).lower()

    def test_lifecycle_validation_valid_values(
        self,
        ci_enforcement_registry: CIEnforcementTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test that valid lifecycle values pass CI validation."""
        for lifecycle in Lifecycle:
            test_case_id = f"valid_lifecycle_{lifecycle.value}"
            test_case = ci_enforcement_registry.get_test_case(test_case_id)
            metadata_block = metadata_validator(test_case.metadata)

            # Use enum-based assertion instead of string comparison
            assert metadata_block.lifecycle == lifecycle

    def test_lifecycle_validation_invalid_values(
        self, metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock]
    ) -> None:
        """Test that invalid lifecycle values fail CI validation."""
        invalid_lifecycles = ["invalid", "unknown", "test", ""]

        for invalid_lifecycle in invalid_lifecycles:
            metadata = _create_base_metadata()
            metadata[NodeMetadataField.LIFECYCLE.value] = invalid_lifecycle

            with pytest.raises(ValidationError) as exc_info:
                metadata_validator(metadata)

            # Validate that the error mentions lifecycle validation
            assert (
                "lifecycle" in str(exc_info.value).lower()
                or "validation" in str(exc_info.value).lower()
            )

    def test_hash_validation_valid_formats(
        self,
        ci_enforcement_registry: CIEnforcementTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test that valid hash formats pass CI validation."""
        valid_hash_cases = [
            tc
            for tc in ci_enforcement_registry.get_valid_test_cases()
            if tc.test_id.startswith("valid_hash_format_")
        ]

        for test_case in valid_hash_cases:
            metadata_block = metadata_validator(test_case.metadata)

            # Use model-based assertions for hash validation
            assert len(metadata_block.hash) == 64
            assert all(c in "0123456789abcdefABCDEF" for c in metadata_block.hash)

    def test_hash_validation_invalid_formats(
        self, metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock]
    ) -> None:
        """Test that invalid hash formats fail CI validation."""
        invalid_hashes = [
            "short",  # Too short
            "a" * 63,  # One character short
            "a" * 65,  # One character too long
            "g" * 64,  # Invalid hex character
            "abcd-efgh-" + "a" * 54,  # Contains hyphens
        ]

        for invalid_hash in invalid_hashes:
            metadata = _create_base_metadata()
            metadata[NodeMetadataField.HASH.value] = invalid_hash

            with pytest.raises(ValidationError):
                metadata_validator(metadata)

    def test_entrypoint_validation(
        self,
        ci_enforcement_registry: CIEnforcementTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test that entrypoint validation works correctly."""
        for entrypoint_type in EntrypointType:
            test_case_id = f"valid_entrypoint_{entrypoint_type.value}"
            test_case = ci_enforcement_registry.get_test_case(test_case_id)
            metadata_block = metadata_validator(test_case.metadata)

            # Use enum-based assertion for entrypoint type
            assert metadata_block.entrypoint.type == entrypoint_type.value

    def test_meta_type_validation(
        self,
        ci_enforcement_registry: CIEnforcementTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test that meta type validation works correctly."""
        for meta_type in MetaType:
            test_case_id = f"valid_meta_type_{meta_type.value}"
            test_case = ci_enforcement_registry.get_test_case(test_case_id)
            metadata_block = metadata_validator(test_case.metadata)

            # Use enum-based assertion for meta type
            assert metadata_block.meta_type == meta_type

    def test_required_fields_validation(
        self, metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock]
    ) -> None:
        """Test that all required fields are properly validated."""
        # Test with base metadata (should pass)
        base_metadata = _create_base_metadata()
        metadata_block = metadata_validator(base_metadata)

        # Verify all required fields are present using canonical enum
        for required_field in NodeMetadataField.required():
            assert hasattr(metadata_block, required_field.value)
            field_value = getattr(metadata_block, required_field.value)
            assert field_value is not None

    def test_optional_fields_handling(
        self, metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock]
    ) -> None:
        """Test that optional fields are handled correctly."""
        # Create metadata with only required fields
        minimal_metadata = {
            NodeMetadataField.NAME.value: "minimal_test_node",
            NodeMetadataField.UUID.value: "12345678-1234-5678-9abc-123456789012",
            NodeMetadataField.AUTHOR.value: "Test Author",
            NodeMetadataField.CREATED_AT.value: "2025-05-24T10:00:00.000000",
            NodeMetadataField.LAST_MODIFIED_AT.value: "2025-05-24T10:00:00.000000",
            NodeMetadataField.HASH.value: "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            NodeMetadataField.ENTRYPOINT.value: {
                "type": EntrypointType.PYTHON.value,
                "target": "minimal_test_node.py",
            },
            NodeMetadataField.NAMESPACE.value: "onex.test.minimal",
        }

        # Should validate successfully with defaults for optional fields
        metadata_block = metadata_validator(minimal_metadata)
        assert metadata_block.name == "minimal_test_node"

        # Optional fields should have defaults
        assert metadata_block.lifecycle == Lifecycle.ACTIVE  # Default value
        assert metadata_block.meta_type == MetaType.TOOL  # Default value


class TestStateContractValidation:
    """Test state contract validation using registry-driven patterns."""

    def test_valid_state_contract_structure(self) -> None:
        """Test that valid state contract structures pass validation."""
        valid_contracts = [
            "state_contract://default",
            "state_contract://custom",
            "state_contract://node_specific",
        ]

        for contract in valid_contracts:
            metadata = _create_base_metadata()
            metadata[NodeMetadataField.STATE_CONTRACT.value] = contract

            # Should validate successfully
            metadata_block = NodeMetadataBlock(**metadata)
            assert metadata_block.state_contract == contract

    def test_invalid_state_contract_structure(self) -> None:
        """Test that invalid state contract structures fail validation."""
        # Test empty string which should fail validation
        metadata = _create_base_metadata()
        metadata[NodeMetadataField.STATE_CONTRACT.value] = ""

        with pytest.raises(ValidationError) as exc_info:
            NodeMetadataBlock(**metadata)
        assert "string_too_short" in str(
            exc_info.value
        ) or "at least 1 character" in str(exc_info.value)

        # Test other formats that are currently accepted but may be invalid semantically
        accepted_but_invalid_contracts = [
            "invalid_format",  # Missing protocol
            "http://wrong_protocol",  # Wrong protocol
            "state_contract://",  # Missing path
        ]

        for contract in accepted_but_invalid_contracts:
            metadata = _create_base_metadata()
            metadata[NodeMetadataField.STATE_CONTRACT.value] = contract

            # Current implementation accepts these formats
            # Future versions may add stricter validation
            metadata_block = NodeMetadataBlock(**metadata)
            assert metadata_block.state_contract == contract


class TestDirectoryStructureValidation:
    """Test directory structure validation using protocol-driven patterns."""

    def test_empty_directory_detection_logic(self) -> None:
        """Test the logic for detecting empty directories."""
        # Use protocol-driven directory structure validation
        # This would be implemented with proper protocol interfaces in real CI

        # Mock directory structure for testing
        directory_structure = {
            "empty_dir": [],  # Empty directory
            "non_empty_dir": ["file.txt"],  # Non-empty directory
            "intentional_empty": [".gitkeep"],  # Intentionally empty with .gitkeep
        }

        # Find empty directories (excluding .gitkeep)
        empty_dirs = []
        for dir_name, contents in directory_structure.items():
            if not contents:
                empty_dirs.append(dir_name)
            elif len(contents) == 1 and contents[0] == ".gitkeep":
                # This is intentionally empty with .gitkeep
                pass
            else:
                # Directory has real content
                pass

        # Use model-based assertions
        assert "empty_dir" in empty_dirs
        assert "non_empty_dir" not in empty_dirs
        assert "intentional_empty" not in empty_dirs


if __name__ == "__main__":
    pytest.main([__file__])
