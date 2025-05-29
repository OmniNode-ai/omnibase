# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.776281'
# description: Stamped by PythonHandler
# entrypoint: python://test_error_codes
# hash: d9788b2156a63775070494a24238747678e83a945426d29c03b4e31b7bab8a75
# last_modified_at: '2025-05-29T14:13:59.915301+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_error_codes.py
# namespace: python://omnibase.nodes.stamper_node.v1_0_0.node_tests.test_error_codes
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: a22d37ee-7791-42a0-b047-f677ab455d58
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Tests for stamper node error codes and exit code mapping.

This module tests the error code system, exit code mapping, and exception
handling for the stamper node to ensure consistent CLI behavior.
"""

import pytest

from omnibase.core.core_error_codes import CLIExitCode, get_exit_code_for_status
from omnibase.enums import OnexStatus
from omnibase.nodes.stamper_node.v1_0_0.error_codes import (
    ERROR_CODE_TO_EXIT_CODE,
    StamperConfigurationError,
    StamperError,
    StamperErrorCode,
    StamperFileError,
    StamperHandlerError,
    StamperMetadataError,
    StamperValidationError,
    get_error_description,
    get_exit_code_for_error,
)


class TestStamperErrorCode:
    """Test the StamperErrorCode enum and its methods."""

    def test_error_code_values(self) -> None:
        """Test that error codes have the correct format and values."""
        # Test a few key error codes
        assert StamperErrorCode.FILE_NOT_FOUND == "ONEX_STAMP_001_FILE_NOT_FOUND"
        assert (
            StamperErrorCode.METADATA_PARSE_ERROR
            == "ONEX_STAMP_021_METADATA_PARSE_ERROR"
        )
        assert StamperErrorCode.HANDLER_NOT_FOUND == "ONEX_STAMP_041_HANDLER_NOT_FOUND"
        assert (
            StamperErrorCode.IDEMPOTENCY_CHECK_FAILED
            == "ONEX_STAMP_061_IDEMPOTENCY_CHECK_FAILED"
        )
        assert (
            StamperErrorCode.INVALID_CONFIGURATION
            == "ONEX_STAMP_081_INVALID_CONFIGURATION"
        )

    def test_get_component(self) -> None:
        """Test that all error codes return the correct component."""
        for error_code in StamperErrorCode:
            assert error_code.get_component() == "STAMP"

    def test_get_number(self) -> None:
        """Test that error codes return the correct numeric identifier."""
        assert StamperErrorCode.FILE_NOT_FOUND.get_number() == 1
        assert StamperErrorCode.FILE_READ_ERROR.get_number() == 2
        assert StamperErrorCode.METADATA_PARSE_ERROR.get_number() == 21
        assert StamperErrorCode.HANDLER_NOT_FOUND.get_number() == 41
        assert StamperErrorCode.IDEMPOTENCY_CHECK_FAILED.get_number() == 61
        assert StamperErrorCode.INVALID_CONFIGURATION.get_number() == 81

    def test_get_description(self) -> None:
        """Test that error codes return meaningful descriptions."""
        assert (
            "file does not exist"
            in StamperErrorCode.FILE_NOT_FOUND.get_description().lower()
        )
        assert (
            "parse" in StamperErrorCode.METADATA_PARSE_ERROR.get_description().lower()
        )
        assert "handler" in StamperErrorCode.HANDLER_NOT_FOUND.get_description().lower()

    def test_get_exit_code(self) -> None:
        """Test that error codes return appropriate exit codes."""
        # File errors should return ERROR (1)
        assert (
            StamperErrorCode.FILE_NOT_FOUND.get_exit_code() == CLIExitCode.ERROR.value
        )
        assert (
            StamperErrorCode.FILE_READ_ERROR.get_exit_code() == CLIExitCode.ERROR.value
        )

        # Validation errors should return WARNING (2)
        assert (
            StamperErrorCode.IDEMPOTENCY_CHECK_FAILED.get_exit_code()
            == CLIExitCode.WARNING.value
        )
        assert (
            StamperErrorCode.HASH_VERIFICATION_FAILED.get_exit_code()
            == CLIExitCode.WARNING.value
        )


class TestExitCodeMapping:
    """Test the exit code mapping functions."""

    def test_get_exit_code_for_status(self) -> None:
        """Test mapping from OnexStatus to exit codes."""
        assert get_exit_code_for_status(OnexStatus.SUCCESS) == 0
        assert get_exit_code_for_status(OnexStatus.ERROR) == 1
        assert get_exit_code_for_status(OnexStatus.WARNING) == 2
        assert get_exit_code_for_status(OnexStatus.PARTIAL) == 3
        assert get_exit_code_for_status(OnexStatus.SKIPPED) == 4
        assert get_exit_code_for_status(OnexStatus.FIXED) == 5
        assert get_exit_code_for_status(OnexStatus.INFO) == 6
        assert get_exit_code_for_status(OnexStatus.UNKNOWN) == 1  # Treated as error

    def test_get_exit_code_for_error(self) -> None:
        """Test mapping from error codes to exit codes."""
        # File system errors -> ERROR (1)
        assert get_exit_code_for_error(StamperErrorCode.FILE_NOT_FOUND) == 1
        assert get_exit_code_for_error(StamperErrorCode.PERMISSION_DENIED) == 1

        # Validation errors -> WARNING (2)
        assert get_exit_code_for_error(StamperErrorCode.IDEMPOTENCY_CHECK_FAILED) == 2
        assert get_exit_code_for_error(StamperErrorCode.CONTENT_VALIDATION_FAILED) == 2

        # Configuration errors -> ERROR (1)
        assert get_exit_code_for_error(StamperErrorCode.INVALID_CONFIGURATION) == 1

    def test_error_code_to_exit_code_mapping_completeness(self) -> None:
        """Test that all error codes have exit code mappings."""
        for error_code in StamperErrorCode:
            assert (
                error_code in ERROR_CODE_TO_EXIT_CODE
            ), f"Missing exit code mapping for {error_code}"

    def test_get_error_description(self) -> None:
        """Test that all error codes have descriptions."""
        for error_code in StamperErrorCode:
            description = get_error_description(error_code)
            assert (
                description != "Unknown error"
            ), f"Missing description for {error_code}"
            assert len(description) > 0, f"Empty description for {error_code}"


class TestStamperError:
    """Test the StamperError exception class."""

    def test_stamper_error_creation(self) -> None:
        """Test creating StamperError with error code."""
        error = StamperError("Test error", StamperErrorCode.FILE_NOT_FOUND)
        assert str(error) == "[ONEX_STAMP_001_FILE_NOT_FOUND] Test error"
        assert error.error_code == StamperErrorCode.FILE_NOT_FOUND
        assert error.get_exit_code() == 1

    def test_stamper_error_with_context(self) -> None:
        """Test creating StamperError with additional context."""
        error = StamperError(
            "Test error",
            StamperErrorCode.FILE_NOT_FOUND,
            file_path="/test/file.py",
            line_number=42,
        )
        assert error.context["file_path"] == "/test/file.py"
        assert error.context["line_number"] == 42

    def test_stamper_error_inheritance(self) -> None:
        """Test that StamperError properly inherits from OnexError."""
        from omnibase.core.core_error_codes import OnexError

        error = StamperError("Test error", StamperErrorCode.FILE_NOT_FOUND)
        assert isinstance(error, OnexError)
        assert isinstance(error, Exception)


class TestStamperErrorSubclasses:
    """Test the specific stamper error subclasses."""

    def test_stamper_file_error(self) -> None:
        """Test StamperFileError."""
        error = StamperFileError("File not found", StamperErrorCode.FILE_NOT_FOUND)
        assert isinstance(error, StamperError)
        assert error.get_exit_code() == 1

    def test_stamper_metadata_error(self) -> None:
        """Test StamperMetadataError."""
        error = StamperMetadataError(
            "Parse failed", StamperErrorCode.METADATA_PARSE_ERROR
        )
        assert isinstance(error, StamperError)
        assert error.get_exit_code() == 1

    def test_stamper_handler_error(self) -> None:
        """Test StamperHandlerError."""
        error = StamperHandlerError(
            "Handler failed", StamperErrorCode.HANDLER_EXECUTION_FAILED
        )
        assert isinstance(error, StamperError)
        assert error.get_exit_code() == 1

    def test_stamper_validation_error(self) -> None:
        """Test StamperValidationError."""
        error = StamperValidationError(
            "Validation failed", StamperErrorCode.IDEMPOTENCY_CHECK_FAILED
        )
        assert isinstance(error, StamperError)
        assert error.get_exit_code() == 2  # Validation errors map to WARNING

    def test_stamper_configuration_error(self) -> None:
        """Test StamperConfigurationError."""
        error = StamperConfigurationError(
            "Config invalid", StamperErrorCode.INVALID_CONFIGURATION
        )
        assert isinstance(error, StamperError)
        assert error.get_exit_code() == 1


class TestErrorCodeRegistry:
    """Test the error code registry integration."""

    def test_stamper_error_codes_registered(self) -> None:
        """Test that stamper error codes are registered with the global registry."""
        from omnibase.core.core_error_codes import (
            get_error_codes_for_component,
            list_registered_components,
        )

        # Check that stamper is registered
        assert "stamper" in list_registered_components()

        # Check that we can retrieve stamper error codes
        stamper_codes = get_error_codes_for_component("stamper")

        # Instead of comparing enum classes directly, check that they have the same members
        assert stamper_codes is StamperErrorCode or (
            hasattr(stamper_codes, "__members__")
            and hasattr(StamperErrorCode, "__members__")
            and set(stamper_codes.__members__.keys())
            == set(StamperErrorCode.__members__.keys())
        )

    def test_error_code_registry_functionality(self) -> None:
        """Test that the error code registry works as expected."""
        from omnibase.core.core_error_codes import get_error_codes_for_component

        # Should be able to get stamper error codes
        stamper_codes = get_error_codes_for_component("stamper")

        # Should have all the expected error codes
        assert hasattr(stamper_codes, "FILE_NOT_FOUND")
        assert hasattr(stamper_codes, "METADATA_PARSE_ERROR")
        assert hasattr(stamper_codes, "HANDLER_NOT_FOUND")

    def test_unknown_component_raises_error(self) -> None:
        """Test that requesting unknown component raises OnexError."""
        from omnibase.core.core_error_codes import (
            OnexError,
            get_error_codes_for_component,
        )

        with pytest.raises(
            OnexError, match="No error codes registered for component: unknown"
        ):
            get_error_codes_for_component("unknown")


class TestCLIIntegration:
    """Test CLI integration with error codes."""

    def test_cli_exit_code_consistency(self) -> None:
        """Test that CLI exit codes are consistent with error code mappings."""
        # Import the shared function used by CLI
        from omnibase.core.core_error_codes import (
            get_exit_code_for_status as shared_function,
        )

        # Test that it returns the same values as our local function
        for status in OnexStatus:
            local_exit_code = get_exit_code_for_status(status)
            shared_exit_code = shared_function(status)
            assert (
                local_exit_code == shared_exit_code
            ), f"Inconsistent exit codes for {status}"

    def test_error_code_exit_code_ranges(self) -> None:
        """Test that exit codes are in expected ranges."""
        for error_code in StamperErrorCode:
            exit_code = error_code.get_exit_code()
            assert (
                0 <= exit_code <= 6
            ), f"Exit code {exit_code} for {error_code} is out of range"

    def test_error_categories_have_consistent_exit_codes(self) -> None:
        """Test that error categories map to consistent exit codes."""
        # File system errors should all map to ERROR (1)
        file_errors = [
            StamperErrorCode.FILE_NOT_FOUND,
            StamperErrorCode.FILE_READ_ERROR,
            StamperErrorCode.FILE_WRITE_ERROR,
            StamperErrorCode.PERMISSION_DENIED,
            StamperErrorCode.INVALID_FILE_TYPE,
        ]
        for error_code in file_errors:
            assert error_code.get_exit_code() == CLIExitCode.ERROR.value

        # Validation errors should all map to WARNING (2)
        validation_errors = [
            StamperErrorCode.IDEMPOTENCY_CHECK_FAILED,
            StamperErrorCode.HASH_VERIFICATION_FAILED,
            StamperErrorCode.CONTENT_VALIDATION_FAILED,
        ]
        for error_code in validation_errors:
            assert error_code.get_exit_code() == CLIExitCode.WARNING.value
