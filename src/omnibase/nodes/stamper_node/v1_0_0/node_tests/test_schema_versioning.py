# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_schema_versioning.py
# version: 1.0.0
# uuid: 11998ecf-330d-4a13-b676-69788bee897a
# author: OmniNode Team
# created_at: 2025-05-25T15:00:35.750519
# last_modified_at: 2025-05-25T19:21:33.370630
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 95dacf61f547abf8e51f1864e0a2b05b82a227e77bfee561884e49abd24c8db3
# entrypoint: python@test_schema_versioning.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_schema_versioning
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Tests for schema versioning functionality in stamper node state models.

This module tests the schema versioning system including validation,
compatibility checking, and factory functions.
"""

import pytest

from omnibase.core.error_codes import OnexError
from omnibase.runtimes.onex_runtime.v1_0_0.utils.schema_version_validator import (
    SchemaVersionError,
    SchemaVersionValidator,
    validate_semantic_version,
)

from ..models.state import (
    STAMPER_STATE_SCHEMA_VERSION,
    StamperInputState,
    StamperOutputState,
    create_stamper_input_state,
    create_stamper_output_state,
    validate_schema_version_compatibility,
)
from ..models.state import validate_semantic_version as state_validate_semantic_version


class TestSchemaVersionValidation:
    """Test schema version validation utilities."""

    def test_validate_semantic_version_valid(self) -> None:
        """Test validation of valid semantic version strings."""
        valid_versions = [
            "1.0.0",
            "0.1.0",
            "10.20.30",
            "1.0.0-alpha",
            "1.0.0-alpha.1",
            "1.0.0+build.1",
            "1.0.0-alpha+build.1",
        ]

        for version in valid_versions:
            # Should not raise exception
            result = validate_semantic_version(version)
            assert result == version

            # Test state module function too
            result = state_validate_semantic_version(version)
            assert result == version

    def test_validate_semantic_version_invalid(self) -> None:
        """Test validation of invalid semantic version strings."""
        invalid_versions = [
            "1",
            "1.0",
            "1.0.0.0",
            "v1.0.0",
            "1.0.0-",
            "1.0.0+",
            "",
            "invalid",
            "1.0.0-alpha..1",
        ]

        for version in invalid_versions:
            with pytest.raises((OnexError, SchemaVersionError)):
                validate_semantic_version(version)

            with pytest.raises(OnexError):
                state_validate_semantic_version(version)

    def test_validate_schema_version_compatibility_same_version(self) -> None:
        """Test compatibility validation with same version."""
        version = "1.1.0"
        result = validate_schema_version_compatibility(version)
        assert result == version

    def test_validate_schema_version_compatibility_backward_compatible(self) -> None:
        """Test compatibility validation with backward compatible versions."""
        # Minor version can be lower
        result = validate_schema_version_compatibility("1.0.0")
        assert result == "1.0.0"

        # Patch version differences are allowed
        result = validate_schema_version_compatibility("1.1.5")
        assert result == "1.1.5"

    def test_validate_schema_version_compatibility_major_mismatch(self) -> None:
        """Test compatibility validation with major version mismatch."""
        with pytest.raises(OnexError) as exc_info:
            validate_schema_version_compatibility("2.0.0")

        assert "Major version mismatch" in str(exc_info.value)
        assert "requires migration" in str(exc_info.value)

    def test_validate_schema_version_compatibility_newer_minor(self) -> None:
        """Test compatibility validation with newer minor version."""
        with pytest.raises(OnexError) as exc_info:
            validate_schema_version_compatibility("1.2.0")

        assert "newer than current schema version" in str(exc_info.value)
        assert "upgrade the implementation" in str(exc_info.value)


class TestStamperInputStateValidation:
    """Test StamperInputState validation and schema versioning."""

    def test_create_valid_input_state(self) -> None:
        """Test creating a valid input state."""
        state = StamperInputState(
            version="1.1.0",
            file_path="/path/to/file.py",
            author="Test Author",
            correlation_id="test-123",
        )

        assert state.version == "1.1.0"
        assert state.file_path == "/path/to/file.py"
        assert state.author == "Test Author"
        assert state.correlation_id == "test-123"

    def test_input_state_version_validation(self) -> None:
        """Test version field validation in input state."""
        # Valid version
        state = StamperInputState(
            version="1.0.0", file_path="/path/to/file.py", author="Test Author"
        )
        assert state.version == "1.0.0"

        # Invalid version format
        with pytest.raises(OnexError) as exc_info:
            StamperInputState(
                version="invalid", file_path="/path/to/file.py", author="Test Author"
            )
        assert "does not follow semantic versioning format" in str(exc_info.value)

        # Incompatible version
        with pytest.raises(OnexError) as exc_info:
            StamperInputState(
                version="2.0.0", file_path="/path/to/file.py", author="Test Author"
            )
        assert "Major version mismatch" in str(exc_info.value)

    def test_input_state_field_validation(self) -> None:
        """Test field validation in input state."""
        # Empty file_path
        with pytest.raises(OnexError) as exc_info:
            StamperInputState(version="1.1.0", file_path="", author="Test Author")
        assert "file_path cannot be empty" in str(exc_info.value)

        # Empty author
        with pytest.raises(OnexError) as exc_info:
            StamperInputState(version="1.1.0", file_path="/path/to/file.py", author="")
        assert "author cannot be empty" in str(exc_info.value)

    def test_input_state_defaults(self) -> None:
        """Test default values in input state."""
        state = StamperInputState(version="1.1.0", file_path="/path/to/file.py")

        assert state.author == "OmniNode Team"
        assert state.correlation_id is None


class TestStamperOutputStateValidation:
    """Test StamperOutputState validation and schema versioning."""

    def test_create_valid_output_state(self) -> None:
        """Test creating a valid output state."""
        state = StamperOutputState(
            version="1.1.0",
            status="success",
            message="File stamped successfully",
            correlation_id="test-123",
        )

        assert state.version == "1.1.0"
        assert state.status == "success"
        assert state.message == "File stamped successfully"
        assert state.correlation_id == "test-123"

    def test_output_state_status_validation(self) -> None:
        """Test status field validation in output state."""
        # Valid statuses
        valid_statuses = ["success", "failure", "warning"]
        for status in valid_statuses:
            state = StamperOutputState(
                version="1.1.0", status=status, message="Test message"
            )
            assert state.status == status

        # Invalid status
        with pytest.raises(OnexError) as exc_info:
            StamperOutputState(
                version="1.1.0", status="invalid", message="Test message"
            )
        assert "status must be one of" in str(exc_info.value)

    def test_output_state_message_validation(self) -> None:
        """Test message field validation in output state."""
        # Empty message
        with pytest.raises(OnexError) as exc_info:
            StamperOutputState(version="1.1.0", status="success", message="")
        assert "message cannot be empty" in str(exc_info.value)


class TestFactoryFunctions:
    """Test factory functions for creating state models."""

    def test_create_stamper_input_state_defaults(self) -> None:
        """Test creating input state with default values."""
        state = create_stamper_input_state("/path/to/file.py")

        assert state.version == STAMPER_STATE_SCHEMA_VERSION
        assert state.file_path == "/path/to/file.py"
        assert state.author == "OmniNode Team"
        assert state.correlation_id is None

    def test_create_stamper_input_state_custom_values(self) -> None:
        """Test creating input state with custom values."""
        state = create_stamper_input_state(
            file_path="/custom/path.py",
            author="Custom Author",
            correlation_id="custom-123",
            version="1.0.0",
        )

        assert state.version == "1.0.0"
        assert state.file_path == "/custom/path.py"
        assert state.author == "Custom Author"
        assert state.correlation_id == "custom-123"

    def test_create_stamper_output_state_version_propagation(self) -> None:
        """Test that output state propagates version from input state."""
        input_state = create_stamper_input_state("/path/to/file.py", version="1.0.0")

        output_state = create_stamper_output_state(
            status="success", message="Done", input_state=input_state
        )

        assert output_state.version == input_state.version
        assert output_state.status == "success"
        assert output_state.message == "Done"

    def test_create_stamper_output_state_correlation_propagation(self) -> None:
        """Test that output state propagates correlation_id from input state."""
        input_state = create_stamper_input_state(
            "/path/to/file.py", correlation_id="test-123"
        )

        output_state = create_stamper_output_state(
            status="success", message="Done", input_state=input_state
        )

        assert output_state.correlation_id == input_state.correlation_id

    def test_create_stamper_output_state_correlation_override(self) -> None:
        """Test that output state can override correlation_id."""
        input_state = create_stamper_input_state(
            "/path/to/file.py", correlation_id="input-123"
        )

        output_state = create_stamper_output_state(
            status="success",
            message="Done",
            input_state=input_state,
            correlation_id="output-456",
        )

        assert output_state.correlation_id == "output-456"


class TestSchemaVersionValidator:
    """Test the SchemaVersionValidator utility class."""

    def test_validator_initialization(self) -> None:
        """Test validator initialization."""
        validator = SchemaVersionValidator()
        assert len(validator.get_registered_schemas()) == 0

    def test_register_schema(self) -> None:
        """Test schema registration."""
        validator = SchemaVersionValidator()
        validator.register_schema("test_schema", "1.0.0")

        schemas = validator.get_registered_schemas()
        assert "test_schema" in schemas
        assert schemas["test_schema"] == "1.0.0"

    def test_register_schema_invalid_version(self) -> None:
        """Test schema registration with invalid version."""
        validator = SchemaVersionValidator()

        with pytest.raises(SchemaVersionError):
            validator.register_schema("test_schema", "invalid")

    def test_is_compatible(self) -> None:
        """Test version compatibility checking."""
        validator = SchemaVersionValidator()

        # Same version
        assert validator.is_compatible("1.0.0", "1.0.0")

        # Backward compatible
        assert validator.is_compatible("1.0.0", "1.1.0")
        assert validator.is_compatible("1.1.0", "1.2.0")

        # Not compatible
        assert not validator.is_compatible("2.0.0", "1.0.0")  # Major mismatch
        assert not validator.is_compatible("1.2.0", "1.1.0")  # Newer minor

    def test_suggest_migration_path(self) -> None:
        """Test migration path suggestions."""
        validator = SchemaVersionValidator()

        # No migration needed
        steps = validator.suggest_migration_path("1.0.0", "1.0.0")
        assert "No migration required" in steps[0]

        # Major version upgrade
        steps = validator.suggest_migration_path("1.0.0", "2.0.0")
        assert any("Migrate to major version 2.0.0" in step for step in steps)

        # Minor version upgrade
        steps = validator.suggest_migration_path("1.0.0", "1.1.0")
        assert any("Upgrade to minor version 1.1.0" in step for step in steps)


class TestIntegrationWithOnexVersionLoader:
    """Test integration with OnexVersionLoader."""

    def test_version_consistency(self) -> None:
        """Test that schema versions are consistent with OnexVersionLoader."""
        # This test ensures that the schema version constants are properly
        # aligned with the version loading system
        assert STAMPER_STATE_SCHEMA_VERSION == "1.1.1"

        # Test that we can create states with the current schema version
        state = create_stamper_input_state("/test/file.py")
        assert state.version == STAMPER_STATE_SCHEMA_VERSION
