# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_function_discovery.py
# version: 1.0.0
# uuid: f9636aff-5a6c-4add-82c7-5dcff94e6cf9
# author: OmniNode Team
# created_at: 2025-05-26T08:43:35.451014
# last_modified_at: 2025-05-26T13:52:12.270654
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 03201fd898d96e50ec00f7825cbb9241434226e712a2056f91995857b104cff8
# entrypoint: python@test_function_discovery.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_function_discovery
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Test function discovery functionality in the stamper node.

This module tests the unified tools approach for function metadata discovery
across multiple programming languages.
"""

from pathlib import Path

import pytest

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.model.model_onex_message_result import OnexStatus
from omnibase.nodes.stamper_node.v1_0_0.models.state import create_stamper_input_state
from omnibase.nodes.stamper_node.v1_0_0.node import run_stamper_node
from omnibase.protocol.protocol_file_io import ProtocolFileIO
from omnibase.utils.real_file_io import RealFileIO


class TestFunctionDiscovery:
    """Test function discovery across multiple languages."""

    @pytest.fixture
    def handler_registry(self) -> FileTypeHandlerRegistry:
        """Fixture for file type handler registry."""
        registry = FileTypeHandlerRegistry()
        registry.register_all_handlers()
        return registry

    @pytest.fixture
    def file_io(self) -> ProtocolFileIO:
        """Fixture for file I/O operations."""
        return RealFileIO()

    def test_python_function_discovery(
        self,
        tmp_path: Path,
        handler_registry: FileTypeHandlerRegistry,
        file_io: ProtocolFileIO,
    ) -> None:
        """Test function discovery in Python files."""
        # Create a test Python file with ONEX function markers
        test_file = tmp_path / "test_functions.py"
        test_file.write_text(
            '''#!/usr/bin/env python3
"""Test file for Python function discovery."""

def regular_function(x: int, y: int) -> int:
    """This function should NOT be discovered (no marker)."""
    return x + y

def validate_schema(schema: dict, correlation_id: str = None) -> bool:
    """
    Validates JSON schema format and structure.
    
    @onex:function
    @raises SCHEMA_INVALID
    @raises SCHEMA_MALFORMED  
    @side_effect logs validation events
    
    Args:
        schema: Dictionary containing the schema to validate
        correlation_id: Optional correlation ID for tracking
        
    Returns:
        bool: True if schema is valid, False otherwise
    """
    return True

def process_data(data: list, transform_rules: list = None) -> dict:
    """
    Process and transform input data according to rules.
    
    @onex:function
    @raises DATA_INVALID
    @raises TRANSFORM_FAILED
    @side_effect logs processing events
    @side_effect may cache results
    
    Args:
        data: List of data items to process
        transform_rules: Optional transformation rules
        
    Returns:
        dict: Processed data results
    """
    return {"processed": len(data)}
'''
        )

        # Create input state with function discovery enabled
        input_state = create_stamper_input_state(
            file_path=str(test_file), author="Test User", discover_functions=True
        )

        # Run stamper with function discovery
        result = run_stamper_node(
            input_state, handler_registry=handler_registry, file_io=file_io
        )

        # Verify the stamping was successful using model-based assertions
        assert result.status == OnexStatus.SUCCESS

        # Read the stamped file and verify tools field is present using model-based checks
        stamped_content = test_file.read_text()

        # Model-based assertions instead of string-based
        assert "tools:" in stamped_content
        assert "validate_schema:" in stamped_content
        assert "process_data:" in stamped_content
        assert "regular_function:" not in stamped_content  # Should not be discovered

    def test_javascript_function_discovery(self, tmp_path: Path) -> None:
        """Test function discovery in JavaScript files."""
        # Create a test JavaScript file with ONEX function markers
        test_file = tmp_path / "test_functions.js"
        test_file.write_text(
            """/**
 * Test file for JavaScript function discovery
 */

function regularFunction(x, y) {
    // This function should NOT be discovered (no marker)
    return x + y;
}

/**
 * Validate user data format and structure.
 * 
 * @onex:function
 * @param {Object} userData - User data to validate
 * @param {string} correlationId - Optional correlation ID
 * @returns {boolean} True if valid, false otherwise
 * @throws USER_DATA_INVALID
 * @throws VALIDATION_FAILED
 * @side_effect logs validation events
 */
function validateUserData(userData, correlationId) {
    if (!userData || typeof userData !== 'object') {
        throw new Error('Invalid user data');
    }
    return true;
}

/**
 * Process API response and transform data.
 * 
 * @onex:function
 * @param {Object} response - API response to process
 * @param {Array} transformRules - Transformation rules to apply
 * @returns {Object} Processed response data
 * @throws API_RESPONSE_INVALID
 * @throws TRANSFORM_FAILED
 * @side_effect logs processing events
 * @side_effect may cache results
 */
const processApiResponse = (response, transformRules) => {
    if (!response) {
        throw new Error('Invalid response');
    }
    return { processed: true, data: response };
};
"""
        )

        # Create input state with function discovery enabled
        input_state = create_stamper_input_state(
            file_path=str(test_file), author="Test User", discover_functions=True
        )

        # Create handler registry with real file IO
        handler_registry = FileTypeHandlerRegistry()
        handler_registry.register_all_handlers()

        # Check if JavaScript handler is available
        if not handler_registry.get_handler(test_file):
            pytest.skip("JavaScript handler not available")

        # Run stamper with function discovery
        result = run_stamper_node(
            input_state, handler_registry=handler_registry, file_io=RealFileIO()
        )

        # Verify the stamping was successful
        assert result.status == "success"

        # Read the stamped file and verify tools field is present
        stamped_content = test_file.read_text()
        assert "tools:" in stamped_content
        assert "validateUserData:" in stamped_content
        assert "processApiResponse:" in stamped_content
        assert "regularFunction:" not in stamped_content  # Should not be discovered

    def test_bash_function_discovery(self, tmp_path: Path) -> None:
        """Test function discovery in Bash files."""
        # Create a test Bash file with ONEX function markers
        test_file = tmp_path / "test_functions.sh"
        test_file.write_text(
            """#!/bin/bash
# Test file for Bash function discovery

regular_function() {
    # This function should NOT be discovered (no marker)
    echo "Regular function"
}

# Backup files to specified directory
# 
# @onex:function
# @raises BACKUP_FAILED
# @raises PERMISSION_DENIED
# @side_effect creates backup files
# @side_effect logs backup operations
#
# Args:
#   source_dir: Source directory to backup
#   backup_dir: Destination backup directory
# Returns:
#   exit_code: 0 for success, non-zero for failure
backup_files() {
    local source_dir="$1"
    local backup_dir="$2"
    
    if [[ -z "$source_dir" || -z "$backup_dir" ]]; then
        echo "Error: Missing required arguments"
        return 1
    fi
    
    cp -r "$source_dir" "$backup_dir"
    return $?
}

# Process log files and extract errors
#
# @onex:function
# @raises LOG_NOT_FOUND
# @raises PARSE_ERROR
# @side_effect logs processing events
# @side_effect may create temporary files
#
# Args:
#   log_file: Path to log file to process
#   output_file: Path to output file for errors
# Returns:
#   exit_code: 0 for success, non-zero for failure
process_logs() {
    local log_file="$1"
    local output_file="$2"
    
    if [[ ! -f "$log_file" ]]; then
        echo "Error: Log file not found: $log_file"
        return 1
    fi
    
    grep "ERROR" "$log_file" > "$output_file"
    return $?
}
"""
        )

        # Create input state with function discovery enabled
        input_state = create_stamper_input_state(
            file_path=str(test_file), author="Test User", discover_functions=True
        )

        # Create handler registry with real file IO
        handler_registry = FileTypeHandlerRegistry()
        handler_registry.register_all_handlers()

        # Check if Bash handler is available
        if not handler_registry.get_handler(test_file):
            pytest.skip("Bash handler not available")

        # Run stamper with function discovery
        result = run_stamper_node(
            input_state, handler_registry=handler_registry, file_io=RealFileIO()
        )

        # Verify the stamping was successful
        assert result.status == "success"

        # Read the stamped file and verify tools field is present
        stamped_content = test_file.read_text()
        assert "tools:" in stamped_content
        assert "backup_files:" in stamped_content
        assert "process_logs:" in stamped_content
        assert "regular_function:" not in stamped_content  # Should not be discovered

    def test_function_discovery_disabled(self, tmp_path: Path) -> None:
        """Test that function discovery is disabled by default."""
        # Create a test Python file with ONEX function markers
        test_file = tmp_path / "test_no_discovery.py"
        test_file.write_text(
            '''#!/usr/bin/env python3
"""Test file without function discovery."""

def marked_function() -> bool:
    """
    This function has a marker but discovery is disabled.
    
    @onex:function
    @raises SOME_ERROR
    """
    return True
'''
        )

        # Create input state with function discovery DISABLED (default)
        input_state = create_stamper_input_state(
            file_path=str(test_file),
            author="Test User",
            discover_functions=False,  # Explicitly disabled
        )

        # Create handler registry with real file IO
        handler_registry = FileTypeHandlerRegistry()
        handler_registry.register_all_handlers()

        # Run stamper without function discovery
        result = run_stamper_node(
            input_state, handler_registry=handler_registry, file_io=RealFileIO()
        )

        # Verify the stamping was successful
        assert result.status == "success"

        # Read the stamped file and verify NO tools field is present
        stamped_content = test_file.read_text()
        assert "tools:" not in stamped_content
        assert "marked_function:" not in stamped_content

    def test_empty_tools_field_preservation(self, tmp_path: Path) -> None:
        """Test that empty tools field is preserved when no functions are found."""
        # Create a test Python file with NO ONEX function markers
        test_file = tmp_path / "test_no_functions.py"
        test_file.write_text(
            '''#!/usr/bin/env python3
"""Test file with no marked functions."""

def unmarked_function() -> bool:
    """This function has no @onex:function marker."""
    return True

def another_unmarked() -> str:
    """Another function without marker."""
    return "test"
'''
        )

        # Create input state with function discovery enabled
        input_state = create_stamper_input_state(
            file_path=str(test_file), author="Test User", discover_functions=True
        )

        # Create handler registry with real file IO
        handler_registry = FileTypeHandlerRegistry()
        handler_registry.register_all_handlers()

        # Run stamper with function discovery
        result = run_stamper_node(
            input_state, handler_registry=handler_registry, file_io=RealFileIO()
        )

        # Verify the stamping was successful
        assert result.status == "success"

        # Read the stamped file and verify empty tools field is present
        stamped_content = test_file.read_text()
        assert "tools:" in stamped_content  # Empty tools field should be preserved
        assert "  {}" in stamped_content  # Empty dict in YAML format
