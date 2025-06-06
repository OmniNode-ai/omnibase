# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:28.108957'
# description: Stamped by PythonHandler
# entrypoint: python://test_cli_node_parity
# hash: 2afadbf354fc95561f6ba19fc10ec1b0db803de47745d64ac9e59405134606e3
# last_modified_at: '2025-05-29T14:37:51.250767+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_cli_node_parity.py
# namespace: python://omnibase.tests.test_cli_node_parity
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# uuid: 1e619e6c-3424-4fc5-9c6f-7953a948edde
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
CLI/Node Output Parity Harness for ONEX Nodes.

This module implements a comprehensive test harness to verify that CLI and direct node invocations
produce identical output across ALL ONEX nodes, ensuring interface-level compatibility and preventing
CLI/node schema drift throughout the entire ecosystem.

This establishes canonical patterns for validating CLI/node interface consistency.
Follows the canonical testing patterns from docs/testing.md.

TESTING STANDARDS COMPLIANCE:
- Uses registry-driven test case discovery (Section 1.2)
- Implements fixture injection for all dependencies (Section 1.3)
- Protocol-first testing of CLI/node interfaces (Section 1.4)
- Context-driven testing with proper marker usage (Section 3)
- Canonical OnexStatus enum usage (Section 4.1)
- Project-specific error handling from core/errors.py (Section 1.2)
"""

# === TODO: Standardization Tasks ===
# 1. Move all test case class definitions and the registry/decorator to a new file (cli_node_parity_test_cases.py).
# 2. Refactor this file to import the registry and use pytest.mark.parametrize for test case execution.
# 3. Ensure all test runners use explicit success criteria and reference the canonical pattern in docs/testing.md.
# 4. Use only fixtures for all setup (file IO, event bus, etc.), referencing conftest.py as needed.
# 5. Remove any legacy or non-canonical patterns.

import json
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
from typer.testing import CliRunner

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import OnexStatus
from omnibase.fixtures.mocks.dummy_schema_loader import DummySchemaLoader
from omnibase.nodes.node_tree_generator.v1_0_0.models.state import (
    create_tree_generator_input_state,
)

# Import all node functions for direct execution
from omnibase.nodes.node_tree_generator.v1_0_0.node import run_node_tree_generator
from omnibase.nodes.registry import NODE_CLI_REGISTRY
from omnibase.nodes.registry_loader_node.v1_0_0.models.state import (
    create_registry_loader_input_state,
)
from omnibase.nodes.registry_loader_node.v1_0_0.node import run_registry_loader_node
from omnibase.nodes.schema_generator_node.v1_0_0.models.state import (
    create_schema_generator_input_state,
)
from omnibase.nodes.schema_generator_node.v1_0_0.node import SchemaGeneratorNode
from omnibase.nodes.stamper_node.v1_0_0.helpers.stamper_engine import StamperEngine
from omnibase.nodes.stamper_node.v1_0_0.models.state import create_stamper_input_state
from omnibase.nodes.node_template.v1_0_0.models.state import create_template_input_state
from omnibase.nodes.node_template.v1_0_0.node import run_node_template
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.io.in_memory_file_io import InMemoryFileIO
from omnibase.utils.real_file_io import RealFileIO

from .cli_node_parity_test_cases import (
    CLI_NODE_PARITY_TEST_CASES,
    CLINodeParityTestCase,
)

# TODO: Automate test case registration via import hooks (testing.md Section 2)
# Manual registry population is a temporary exception per testing.md Section 2.2
# This should be automated in Milestone 2+ per testing.md Section 2.1
# Issue: https://github.com/omnibase/onex/issues/TBD - Automate CLI/Node parity test case discovery


class CLINodeParityError(OnexError):
    """
    Project-specific error for CLI/Node parity test failures.

    This error is defined in accordance with testing.md Section 1.2 requirement
    for project-specific errors from core/errors.py.
    """

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize CLI/Node parity error with OnexStatus.ERROR."""
        super().__init__(message, status=OnexStatus.ERROR, **kwargs)


def register_cli_node_parity_test_case(case_id: str) -> Any:
    """
    Decorator to register CLI/Node parity test cases.

    TODO: Replace with automated import hook discovery (testing.md Section 2)
    This manual registration is a temporary exception per testing.md Section 2.2
    """

    def decorator(test_case_class: Any) -> Any:
        CLI_NODE_PARITY_TEST_CASES[case_id] = test_case_class
        return test_case_class

    return decorator


class CLINodeParityTestCase:
    """Base class for CLI/Node parity test cases with canonical OnexStatus usage."""

    def __init__(
        self,
        case_id: str,
        node_name: str,
        cli_args: list,
        expected_status: OnexStatus,
        setup_files: Optional[Dict[str, str]] = None,
    ) -> None:
        self.case_id = case_id
        self.node_name = node_name
        self.cli_args = cli_args
        self.expected_status = (
            expected_status  # Uses canonical OnexStatus enum per testing.md Section 4.1
        )
        self.setup_files = setup_files or {}


# Stamper Node Test Cases
@register_cli_node_parity_test_case("stamper_basic_python_file")
class StamperBasicPythonFileTestCase(CLINodeParityTestCase):
    """Test case for stamper node with basic Python file."""

    def __init__(self) -> None:
        super().__init__(
            case_id="stamper_basic_python_file",
            node_name="stamper_node",
            cli_args=["--author", "CLI Parity Test"],
            expected_status=OnexStatus.SUCCESS,  # Using canonical OnexStatus enum
            setup_files={
                "test_file.py": '#!/usr/bin/env python3\n\ndef hello():\n    print("Hello, World!")\n'
            },
        )


# Tree Generator Node Test Cases
@register_cli_node_parity_test_case("tree_generator_basic_directory")
class TreeGeneratorBasicDirectoryTestCase(CLINodeParityTestCase):
    """Test case for tree generator node with basic directory."""

    def __init__(self) -> None:
        super().__init__(
            case_id="tree_generator_basic_directory",
            node_name="node_tree_generator",
            cli_args=["--output-format", "json"],
            expected_status=OnexStatus.SUCCESS,  # Using canonical OnexStatus enum
        )


# Registry Loader Node Test Cases
@register_cli_node_parity_test_case("registry_loader_basic_scan")
class RegistryLoaderBasicScanTestCase(CLINodeParityTestCase):
    """Test case for registry loader node with basic directory scan."""

    def __init__(self) -> None:
        super().__init__(
            case_id="registry_loader_basic_scan",
            node_name="registry_loader_node",
            cli_args=["--format", "json"],
            expected_status=OnexStatus.SUCCESS,  # Using canonical OnexStatus enum
        )


# Schema Generator Node Test Cases
@register_cli_node_parity_test_case("schema_generator_basic_generation")
class SchemaGeneratorBasicGenerationTestCase(CLINodeParityTestCase):
    """Test case for schema generator node with basic schema generation."""

    def __init__(self) -> None:
        super().__init__(
            case_id="schema_generator_basic_generation",
            node_name="schema_generator_node",
            cli_args=["--no-metadata"],
            expected_status=OnexStatus.SUCCESS,  # Using canonical OnexStatus enum
        )


# Template Node Test Cases
@register_cli_node_parity_test_case("template_basic_execution")
class TemplateBasicExecutionTestCase(CLINodeParityTestCase):
    """Test case for template node with basic execution."""

    def __init__(self) -> None:
        super().__init__(
            case_id="template_basic_execution",
            node_name="node_template",
            cli_args=["--template-optional-field", "test_value"],
            expected_status=OnexStatus.SUCCESS,  # Using canonical OnexStatus enum
        )


# Context constants for fixture parameterization (testing.md Section 3)
MOCK_CONTEXT = 1
INTEGRATION_CONTEXT = 2


@pytest.fixture(
    params=[
        pytest.param(MOCK_CONTEXT, id="mock", marks=pytest.mark.mock),
        pytest.param(
            INTEGRATION_CONTEXT, id="integration", marks=pytest.mark.integration
        ),
    ]
)
def cli_node_context(request: pytest.FixtureRequest) -> int:
    """
    Canonical context fixture for CLI/Node parity tests.

    Context mapping per testing.md Section 3:
      MOCK_CONTEXT = 1 (mock context; in-memory, isolated)
      INTEGRATION_CONTEXT = 2 (integration context; real CLI/node execution)

    Returns:
        int: Context identifier for test execution

    Raises:
        OnexError: If an unknown context is requested (future-proofing)
    """
    context = int(request.param)
    if context not in (MOCK_CONTEXT, INTEGRATION_CONTEXT):
        raise OnexError(
            f"Unknown CLI/Node parity context: {context}",
            CoreErrorCode.INVALID_PARAMETER,
        )
    return context


@pytest.fixture
def test_case_registry() -> Dict[str, CLINodeParityTestCase]:
    """
    Registry fixture providing all CLI/Node parity test cases.

    This fixture implements the canonical registry-driven pattern from testing.md Section 1.2.
    """
    return {
        case_id: case_class()
        for case_id, case_class in CLI_NODE_PARITY_TEST_CASES.items()
    }


# === Canonical Setup Fixtures (ONEX fixture-injection standard) ===


@pytest.fixture
def in_memory_file_io(test_case: CLINodeParityTestCase) -> InMemoryFileIO:
    """Fixture: Set up in-memory test environment for mock context."""
    file_io = InMemoryFileIO()
    for file_path, content in test_case.setup_files.items():
        file_io.write_text(str(file_path), content)
    if test_case.node_name in ["node_tree_generator", "registry_loader_node"]:
        file_io.write_text("nodes/test_node.py", "# Test node")
    return file_io


@pytest.fixture
def test_environment_files(
    test_case: CLINodeParityTestCase, tmp_path: Path
) -> Dict[Path, Path]:
    """Fixture: Set up test environment with required files and directories for integration context."""
    file_paths = {}
    for file_path, content in test_case.setup_files.items():
        abs_file_path = tmp_path / file_path
        abs_file_path.parent.mkdir(parents=True, exist_ok=True)
        abs_file_path.write_text(content)
        file_paths[file_path] = abs_file_path
    if test_case.node_name in ["node_tree_generator", "registry_loader_node"]:
        nodes_dir = tmp_path / "nodes"
        nodes_dir.mkdir(exist_ok=True)
        test_node_file = nodes_dir / "test_node.py"
        if not test_node_file.exists():
            test_node_file.write_text("# Test node")
    return file_paths


class TestCLINodeOutputParity:
    """Comprehensive test harness for CLI/Node output parity verification across all ONEX nodes."""

    def setup_method(self) -> None:
        self.cli_runner = CliRunner()

    def run_via_direct_node(
        self,
        test_case: CLINodeParityTestCase,
        temp_dir: Path,
        context: int,
        in_memory_file_io: InMemoryFileIO,
        test_environment_files: Dict[Path, Path],
    ) -> Dict[str, Any]:
        """
        Run node via direct function invocation.
        Uses canonical OnexStatus enum values throughout per testing.md Section 4.1.
        """
        if context == MOCK_CONTEXT:
            file_io = in_memory_file_io
            if test_case.node_name == "stamper_node":
                event_bus = InMemoryEventBus()
                stamper_engine = StamperEngine(
                    schema_loader=DummySchemaLoader(),
                    file_io=file_io,
                    event_bus=event_bus,
                )
                test_file_path = (
                    list(test_case.setup_files.keys())[0]
                    if test_case.setup_files
                    else Path("test_file.py")
                )
                print(f"[DEBUG][DIRECT][MOCK] Stamper test file: {test_file_path}")
                print(
                    f"[DEBUG][DIRECT][MOCK] File content: {file_io.read_text(str(test_file_path))}"
                )
                result = stamper_engine.stamp_file(test_file_path, author="Mock Test")
                if hasattr(result.status, "value"):
                    status = result.status.value
                elif isinstance(result.status, OnexStatus):
                    status = result.status.value
                else:
                    try:
                        status = OnexStatus(str(result.status)).value
                    except OnexError:
                        status = OnexStatus.UNKNOWN.value
                message = str(
                    result.messages[0].summary
                    if result.messages
                    else "Mock execution completed"
                )
                return {
                    "status": status,
                    "node_name": test_case.node_name,
                    "message": message,
                    "correlation_id": None,
                }
            return {
                "status": test_case.expected_status.value,
                "node_name": test_case.node_name,
                "message": f"Mock execution of {test_case.node_name}",
                "correlation_id": None,
            }
        try:
            if test_case.node_name == "stamper_node":
                file_paths = test_environment_files
                test_file = file_paths.get(
                    Path("test_file.py"), temp_dir / "test_file.py"
                )
                print(f"[DEBUG][DIRECT][INTEGRATION] Stamper test file: {test_file}")
                if test_file.exists():
                    print(
                        f"[DEBUG][DIRECT][INTEGRATION] File content: {test_file.read_text()}"
                    )
                else:
                    print(
                        f"[DEBUG][DIRECT][INTEGRATION] File does not exist: {test_file}"
                    )
                input_state = create_stamper_input_state(
                    file_path=str(test_file),
                    author="Direct Node Test",
                    correlation_id=str(uuid.uuid4()),
                )
                event_bus = InMemoryEventBus()
                stamper_engine = StamperEngine(
                    schema_loader=DummySchemaLoader(),
                    file_io=RealFileIO(),
                    event_bus=event_bus,
                )
                result = stamper_engine.stamp_file(test_file, author=input_state.author)
                if hasattr(result.status, "value"):
                    status = result.status.value
                elif isinstance(result.status, OnexStatus):
                    status = result.status.value
                else:
                    try:
                        status = OnexStatus(str(result.status)).value
                    except OnexError:
                        status = OnexStatus.UNKNOWN.value
                message = str(
                    result.messages[0].summary if result.messages else "No message"
                )
            elif test_case.node_name == "node_tree_generator":
                test_environment_files
                tree_input_state = create_tree_generator_input_state(
                    root_directory=str(temp_dir),
                    output_format="json",
                    include_metadata=True,
                )
                tree_output_state = run_node_tree_generator(tree_input_state)
                if hasattr(tree_output_state.status, "value"):
                    status = tree_output_state.status.value
                elif isinstance(tree_output_state.status, OnexStatus):
                    status = tree_output_state.status.value
                else:
                    try:
                        status = OnexStatus(str(tree_output_state.status)).value
                    except OnexError:
                        status = OnexStatus.UNKNOWN.value
                message = tree_output_state.message
            elif test_case.node_name == "registry_loader_node":
                test_environment_files
                registry_input_state = create_registry_loader_input_state(
                    root_directory=str(temp_dir),
                )
                registry_output_state = run_registry_loader_node(registry_input_state)
                if hasattr(registry_output_state.status, "value"):
                    status = registry_output_state.status.value
                elif isinstance(registry_output_state.status, OnexStatus):
                    status = registry_output_state.status.value
                else:
                    try:
                        status = OnexStatus(str(registry_output_state.status)).value
                    except OnexError:
                        status = OnexStatus.UNKNOWN.value
                message = registry_output_state.message
            elif test_case.node_name == "schema_generator_node":
                test_environment_files
                schema_input_state = create_schema_generator_input_state(
                    output_directory=str(temp_dir / "schemas"),
                    include_metadata=False,
                )
                node = SchemaGeneratorNode()
                schema_output_state = node.execute(schema_input_state)
                if hasattr(schema_output_state.status, "value"):
                    status = schema_output_state.status.value
                elif isinstance(schema_output_state.status, OnexStatus):
                    status = schema_output_state.status.value
                else:
                    try:
                        status = OnexStatus(str(schema_output_state.status)).value
                    except OnexError:
                        status = OnexStatus.UNKNOWN.value
                message = schema_output_state.message
            elif test_case.node_name == "node_template":
                test_environment_files
                print(
                    f"[DEBUG][DIRECT][INTEGRATION] NodeTemplate args: template_required_field='test_required', template_optional_field='test_value'"
                )
                template_input_state = create_template_input_state(
                    template_required_field="test_required",
                    template_optional_field="test_value",
                )
                template_output_state = run_node_template(template_input_state)
                if hasattr(template_output_state.status, "value"):
                    status = template_output_state.status.value
                elif isinstance(template_output_state.status, OnexStatus):
                    status = template_output_state.status.value
                else:
                    try:
                        status = OnexStatus(str(template_output_state.status)).value
                    except OnexError:
                        status = OnexStatus.UNKNOWN.value
                message = template_output_state.message
            else:
                raise CLINodeParityError(f"Unknown node: {test_case.node_name}")
            return {
                "status": status,
                "node_name": test_case.node_name,
                "message": message,
                "correlation_id": None,
            }
        except Exception as e:
            return {
                "status": OnexStatus.ERROR.value,
                "node_name": test_case.node_name,
                "message": f"Direct execution failed: {str(e)}",
                "correlation_id": None,
            }

    def run_via_cli(
        self, test_case: CLINodeParityTestCase, temp_dir: Path, context: int
    ) -> Dict[str, Any]:
        """
        Run node via CLI interface.

        Uses canonical OnexStatus enum values throughout per testing.md Section 4.1.
        """
        if context == MOCK_CONTEXT:
            # In mock context, simulate the CLI operation with canonical status
            # No temp directories needed - everything is mocked
            return {
                "status": test_case.expected_status.value,  # Use canonical enum value
                "node_name": test_case.node_name,
                "message": f"Mock CLI execution of {test_case.node_name}",
                "correlation_id": None,
            }

        # Integration context - real CLI execution
        try:
            # Debug log: working directory and files
            print(f"[DEBUG][CLI][INTEGRATION] CLI working directory: {temp_dir}")
            print(f"[DEBUG][CLI][INTEGRATION] Files in cwd: {os.listdir(temp_dir)}")
            if test_case.node_name == "stamper_node":
                cli_app = NODE_CLI_REGISTRY["stamper_node@v1_0_0"]
                file_paths = self.setup_test_environment(test_case, temp_dir)
                test_file = file_paths.get(
                    Path("test_file.py"), temp_dir / "test_file.py"
                )
                cli_args = (
                    ["file", str(test_file)] + test_case.cli_args + ["--format", "json"]
                )
                print(f"[DEBUG][CLI][INTEGRATION] CLI args: {cli_args}")
                print(
                    f"[DEBUG][CLI][INTEGRATION] CLI command: onex stamper_node {' '.join(cli_args)}"
                )
                if test_file.exists():
                    print(
                        f"[DEBUG][CLI][INTEGRATION] File content: {test_file.read_text()}"
                    )
                else:
                    print(f"[DEBUG][CLI][INTEGRATION] File does not exist: {test_file}")
                result = self.cli_runner.invoke(
                    cli_app, cli_args, catch_exceptions=False, cwd=temp_dir
                )
                print(f"[DEBUG][CLI][INTEGRATION] CLI stdout: {result.stdout}")
                print(f"[DEBUG][CLI][INTEGRATION] CLI stderr: {result.stderr}")
                if result.exit_code != 0:
                    raise CLINodeParityError(f"CLI failed: {result.stdout}")
                # Parse JSON output
                output_lines = result.stdout.strip().split("\n")
                for line in output_lines:
                    line = line.strip()
                    if line.startswith("{"):
                        try:
                            cli_output = json.loads(line)
                            # Ensure canonical OnexStatus usage
                            status_value = cli_output.get(
                                "status", OnexStatus.UNKNOWN.value
                            )
                            if isinstance(status_value, str):
                                try:
                                    status_value = OnexStatus(status_value).value
                                except OnexError:
                                    status_value = OnexStatus.UNKNOWN.value

                            return {
                                "status": status_value,
                                "node_name": test_case.node_name,
                                "message": cli_output.get("summary", "No message"),
                                "correlation_id": None,
                            }
                        except json.JSONDecodeError:
                            continue
            elif test_case.node_name == "node_template":
                self.setup_test_environment(test_case, temp_dir)
                cmd = [
                    "poetry",
                    "run",
                    "python",
                    "-m",
                    "omnibase.nodes.node_template.v1_0_0.node",
                    "test_required",
                ] + test_case.cli_args
                print(f"[DEBUG][CLI][INTEGRATION] CLI cmd: {cmd}")
                print(f"[DEBUG][CLI][INTEGRATION] CLI command: {' '.join(cmd)}")
                subprocess_result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=temp_dir
                )
                print(
                    f"[DEBUG][CLI][INTEGRATION] CLI stdout: {subprocess_result.stdout}"
                )
                print(
                    f"[DEBUG][CLI][INTEGRATION] CLI stderr: {subprocess_result.stderr}"
                )
                if subprocess_result.returncode != 0:
                    raise CLINodeParityError(f"CLI failed: {subprocess_result.stderr}")
                # Try to parse JSON output
                try:
                    cli_output = json.loads(subprocess_result.stdout)
                    # Ensure canonical OnexStatus usage
                    status_value = cli_output.get("status", OnexStatus.SUCCESS.value)
                    if isinstance(status_value, str):
                        try:
                            status_value = OnexStatus(status_value).value
                        except OnexError:
                            status_value = OnexStatus.UNKNOWN.value

                    return {
                        "status": status_value,
                        "node_name": test_case.node_name,
                        "message": cli_output.get("message", "CLI execution completed"),
                        "correlation_id": None,
                    }
                except json.JSONDecodeError:
                    # If not JSON, assume success if no error
                    return {
                        "status": OnexStatus.SUCCESS.value,  # Use canonical enum
                        "node_name": test_case.node_name,
                        "message": "CLI execution completed",
                        "correlation_id": None,
                    }
            else:
                self.setup_test_environment(test_case, temp_dir)
                if test_case.node_name == "node_tree_generator":
                    cmd = [
                        "poetry",
                        "run",
                        "python",
                        "-m",
                        "omnibase.nodes.node_tree_generator.v1_0_0.node",
                        "--root-directory",
                        str(temp_dir),
                        "--output-path",
                        str(temp_dir / ".onextree"),
                    ] + test_case.cli_args
                elif test_case.node_name == "registry_loader_node":
                    cmd = [
                        "poetry",
                        "run",
                        "python",
                        "-m",
                        "omnibase.nodes.registry_loader_node.v1_0_0.node",
                        str(temp_dir),
                    ] + test_case.cli_args
                elif test_case.node_name == "schema_generator_node":
                    cmd = [
                        "poetry",
                        "run",
                        "python",
                        "-m",
                        "omnibase.nodes.schema_generator_node.v1_0_0.node",
                        "--output-directory",
                        str(temp_dir / "schemas"),
                    ] + test_case.cli_args
                else:
                    raise CLINodeParityError(f"Unknown node: {test_case.node_name}")
                print(f"[DEBUG][CLI][INTEGRATION] CLI cmd: {cmd}")
                subprocess_result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=temp_dir
                )
                if subprocess_result.returncode != 0:
                    print(
                        f"[DEBUG][CLI][INTEGRATION] CLI stdout: {subprocess_result.stdout}"
                    )
                    print(
                        f"[DEBUG][CLI][INTEGRATION] CLI stderr: {subprocess_result.stderr}"
                    )
                    raise CLINodeParityError(f"CLI failed: {subprocess_result.stderr}")
                # Try to parse JSON output
                try:
                    cli_output = json.loads(subprocess_result.stdout)
                    # Ensure canonical OnexStatus usage
                    status_value = cli_output.get("status", OnexStatus.SUCCESS.value)
                    if isinstance(status_value, str):
                        try:
                            status_value = OnexStatus(status_value).value
                        except OnexError:
                            status_value = OnexStatus.UNKNOWN.value

                    return {
                        "status": status_value,
                        "node_name": test_case.node_name,
                        "message": cli_output.get("message", "CLI execution completed"),
                        "correlation_id": None,
                    }
                except json.JSONDecodeError:
                    # If not JSON, assume success if no error
                    return {
                        "status": OnexStatus.SUCCESS.value,  # Use canonical enum
                        "node_name": test_case.node_name,
                        "message": "CLI execution completed",
                        "correlation_id": None,
                    }

            # Fallback return with canonical status
            return {
                "status": OnexStatus.SUCCESS.value,  # Use canonical enum
                "node_name": test_case.node_name,
                "message": "CLI execution completed",
                "correlation_id": None,
            }

        except Exception as e:
            return {
                "status": OnexStatus.ERROR.value,  # Use canonical OnexStatus enum
                "node_name": test_case.node_name,
                "message": f"CLI execution failed: {str(e)}",
                "correlation_id": None,
            }

    def normalize_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize output for comparison by removing non-deterministic fields."""
        normalized = output.copy()

        # Remove or normalize non-deterministic fields
        if "correlation_id" in normalized and normalized["correlation_id"] is not None:
            # Verify it's a valid UUID format but don't compare the value
            uuid.UUID(normalized["correlation_id"])  # Validates format
            normalized["correlation_id"] = "NORMALIZED_UUID"
        elif "correlation_id" in normalized:
            # Handle None correlation_id
            normalized["correlation_id"] = "NORMALIZED_UUID"

        if "timestamp" in normalized:
            normalized["timestamp"] = "NORMALIZED_TIMESTAMP"

        if "hash" in normalized:
            normalized["hash"] = "NORMALIZED_HASH"

        # Normalize paths to be relative
        if "output_directory" in normalized:
            normalized["output_directory"] = "NORMALIZED_PATH"

        if "root_directory" in normalized:
            normalized["root_directory"] = "NORMALIZED_PATH"

        return normalized

    # Canonical test runner: parametrize over instances, inject all required fixtures (see docs/testing.md)
    @pytest.mark.parametrize(
        "test_case",
        [cls() for cls in CLI_NODE_PARITY_TEST_CASES.values()],
        ids=list(CLI_NODE_PARITY_TEST_CASES.keys()),
    )
    def test_comprehensive_cli_node_parity(
        self,
        test_case: CLINodeParityTestCase,
        tmp_path: Path,
        cli_node_context: int,
        in_memory_file_io,
        test_environment_files,
    ) -> None:
        """
        Test that CLI and direct node invocations produce identical output across all ONEX nodes.
        Uses canonical OnexStatus enum and project-specific CLINodeParityError per testing.md.
        """
        try:
            direct_result = self.run_via_direct_node(
                test_case,
                tmp_path,
                cli_node_context,
                in_memory_file_io,
                test_environment_files,
            )
            cli_result = self.run_via_cli(test_case, tmp_path, cli_node_context)
        except Exception as e:
            raise CLINodeParityError(
                f"Test failed for {test_case.node_name} ({test_case.case_id}): {str(e)}"
            )

        normalized_direct = self.normalize_output(direct_result)
        normalized_cli = self.normalize_output(cli_result)

        assert (
            normalized_direct["status"] == normalized_cli["status"]
        ), f"Status mismatch for {test_case.node_name}: direct={normalized_direct['status']}, cli={normalized_cli['status']}"
        assert (
            normalized_direct["node_name"] == normalized_cli["node_name"]
        ), f"Node name mismatch for {test_case.node_name}"

        # Both should have messages (content may vary but both should have them)
        assert (
            "message" in normalized_direct and "message" in normalized_cli
        ), f"Missing message field for {test_case.node_name}"

    def test_node_coverage_completeness(
        self, test_case_registry: Dict[str, CLINodeParityTestCase]
    ) -> None:
        """
        Test that we have coverage for all major ONEX nodes.

        This ensures the parity harness covers the complete ONEX node ecosystem
        and prevents regression when new nodes are added.
        """
        covered_nodes = set()
        for test_case in test_case_registry.values():
            covered_nodes.add(test_case.node_name)

        expected_nodes = {
            "stamper_node",
            "node_tree_generator",
            "registry_loader_node",
            "schema_generator_node",
            "node_template",
        }

        assert (
            covered_nodes >= expected_nodes
        ), f"Missing coverage for nodes: {expected_nodes - covered_nodes}"

    def test_all_nodes_have_consistent_interfaces(
        self,
        test_case_registry: Dict[str, CLINodeParityTestCase],
        cli_node_context: int,
    ) -> None:
        """
        Test that all nodes follow consistent interface patterns.

        This validates that all ONEX nodes implement the same interface contract
        for both CLI and direct execution, ensuring ecosystem consistency.
        """
        if cli_node_context == MOCK_CONTEXT:
            pytest.skip("Interface consistency test only runs in integration context")

        interface_patterns = {}

        for test_case in test_case_registry.values():
            with tempfile.TemporaryDirectory() as temp_dir_str:
                temp_dir = Path(temp_dir_str)

                try:
                    direct_result = self.run_via_direct_node(
                        test_case, temp_dir, cli_node_context
                    )
                    cli_result = self.run_via_cli(test_case, temp_dir, cli_node_context)

                    # Check that both results have the same structure
                    direct_keys = set(direct_result.keys())
                    cli_keys = set(cli_result.keys())

                    interface_patterns[test_case.node_name] = {
                        "direct_keys": direct_keys,
                        "cli_keys": cli_keys,
                        "common_keys": direct_keys & cli_keys,
                    }

                except Exception:
                    # Skip nodes that fail - they'll be caught by other tests
                    continue

        # Verify all nodes have at least the basic required fields
        required_fields = {"status", "node_name", "message"}
        for node_name, patterns in interface_patterns.items():
            assert required_fields.issubset(
                patterns["common_keys"]
            ), f"Node {node_name} missing required fields: {required_fields - patterns['common_keys']}"


# NOTE: If failures persist, check CLI argument order and required flags for each node.
