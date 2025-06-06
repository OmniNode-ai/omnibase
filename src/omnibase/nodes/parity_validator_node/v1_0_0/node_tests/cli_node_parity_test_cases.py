"""
Canonical CLI/Node Parity Test Cases for Parity Validator Node

- All test case classes and the registry/decorator are defined here.
- This file is imported by test_cli_node_parity.py for registry-driven, parameterized test execution.
- Follows the canonical pattern in docs/testing.md section 4.1.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from omnibase.core.core_error_codes import OnexError
from omnibase.enums import NodeNameEnum, OnexStatus

from ..node_constants import (
    CLI_ARG_AUTHOR,
    CLI_ARG_FORMAT,
    CLI_ARG_NO_METADATA,
    CLI_ARG_OUTPUT_FORMAT,
    CLI_AUTHOR_CLI_PARITY_TEST,
    OUTPUT_FORMAT_JSON,
)

# Canonical protocol-facing test constants (see docs/testing.md, section 4.4)
TEST_FILE_PY_NAME = Path("test_file.py")
TEST_FILE_PY_CONTENT = (
    '#!/usr/bin/env python3\n\ndef hello():\n    print("Hello, World!")\n'
)

# Registry for CLI/Node parity test cases
CLI_NODE_PARITY_TEST_CASES: Dict[str, Any] = {}


def register_cli_node_parity_test_case(case_id: str) -> Any:
    """
    Decorator to register CLI/Node parity test cases.
    """

    def decorator(test_case_class: Any) -> Any:
        CLI_NODE_PARITY_TEST_CASES[case_id] = test_case_class
        return test_case_class

    return decorator


class CLINodeParityError(OnexError):
    """
    Project-specific error for CLI/Node parity test failures.
    """

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, status=OnexStatus.ERROR, **kwargs)


class CLINodeParityTestCase:
    """Base class for CLI/Node parity test cases with canonical OnexStatus usage."""

    def __init__(
        self,
        case_id: str,
        node_name: NodeNameEnum,
        cli_args: list,
        expected_status: OnexStatus,
        setup_files: Optional[Dict[Path, str]] = None,  # ONEX: Use Path for file keys
    ) -> None:
        self.case_id = case_id
        self.node_name = node_name
        self.cli_args = cli_args
        self.expected_status = expected_status
        self.setup_files = setup_files or {}


# Stamper Node Test Cases
@register_cli_node_parity_test_case("stamper_basic_python_file")
class StamperBasicPythonFileTestCase(CLINodeParityTestCase):
    """Test case for stamper node with basic Python file."""

    def __init__(self) -> None:
        super().__init__(
            case_id="stamper_basic_python_file",
            node_name=NodeNameEnum.STAMPER_NODE,
            cli_args=[CLI_ARG_AUTHOR, CLI_AUTHOR_CLI_PARITY_TEST],
            expected_status=OnexStatus.SUCCESS,
            setup_files={TEST_FILE_PY_NAME: TEST_FILE_PY_CONTENT},
        )


# Tree Generator Node Test Cases
@register_cli_node_parity_test_case("tree_generator_basic_directory")
class TreeGeneratorBasicDirectoryTestCase(CLINodeParityTestCase):
    """Test case for tree generator node with basic directory."""

    def __init__(self) -> None:
        super().__init__(
            case_id="tree_generator_basic_directory",
            node_name=NodeNameEnum.TREE_GENERATOR_NODE,
            cli_args=[CLI_ARG_OUTPUT_FORMAT, OUTPUT_FORMAT_JSON],
            expected_status=OnexStatus.SUCCESS,
        )


# Registry Loader Node Test Cases
@register_cli_node_parity_test_case("registry_loader_basic_scan")
class RegistryLoaderBasicScanTestCase(CLINodeParityTestCase):
    """Test case for registry loader node with basic directory scan."""

    def __init__(self) -> None:
        super().__init__(
            case_id="registry_loader_basic_scan",
            node_name=NodeNameEnum.REGISTRY_LOADER_NODE,
            cli_args=[CLI_ARG_FORMAT, OUTPUT_FORMAT_JSON],
            expected_status=OnexStatus.SUCCESS,
        )


# Schema Generator Node Test Cases
@register_cli_node_parity_test_case("schema_generator_basic_generation")
class SchemaGeneratorBasicGenerationTestCase(CLINodeParityTestCase):
    """Test case for schema generator node with basic schema generation."""

    def __init__(self) -> None:
        super().__init__(
            case_id="schema_generator_basic_generation",
            node_name=NodeNameEnum.SCHEMA_GENERATOR_NODE,
            cli_args=[CLI_ARG_NO_METADATA],
            expected_status=OnexStatus.SUCCESS,
        )


# Template Node Test Cases
@register_cli_node_parity_test_case("template_basic_execution")
class TemplateBasicExecutionTestCase(CLINodeParityTestCase):
    """Test case for template node with basic execution."""

    def __init__(self) -> None:
        super().__init__(
            case_id="template_basic_execution",
            node_name=NodeNameEnum.TEMPLATE_NODE,
            cli_args=[],
            expected_status=OnexStatus.SUCCESS,
        )
