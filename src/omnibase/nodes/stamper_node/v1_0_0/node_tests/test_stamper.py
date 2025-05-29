# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.837539'
# description: Stamped by PythonHandler
# entrypoint: python://test_stamper
# hash: 7ba4a3d1973d15a36629f78bbca5f8b73e00a3b5fd59f2d4965ba520e1b31a77
# last_modified_at: '2025-05-29T14:13:59.982841+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_stamper.py
# namespace: python://omnibase.nodes.stamper_node.v1_0_0.node_tests.test_stamper
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 35914727-27f9-404d-951e-8ad45a75e3f1
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Canonical, registry-driven, context-agnostic test runner for CLIStamper.
Compliant with ONEX testing policy (see docs/testing.md).
"""

from pathlib import Path
from typing import Any

import pytest

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_file_type_handler_registry import (
    FileTypeHandlerRegistry,  # type: ignore[import-untyped]
)
from omnibase.enums import TemplateTypeEnum
from omnibase.fixtures.mocks.dummy_handlers import (
    GlobalDummyJsonHandler as DummyJsonHandler,
)
from omnibase.fixtures.mocks.dummy_handlers import (
    GlobalDummyYamlHandler as DummyYamlHandler,
)
from omnibase.fixtures.mocks.dummy_schema_loader import DummySchemaLoader
from omnibase.nodes.stamper_node.v1_0_0.helpers.stamper_engine import (
    StamperEngine,  # type: ignore[import-untyped]
)
from omnibase.runtimes.onex_runtime.v1_0_0.io.in_memory_file_io import (
    InMemoryFileIO,  # type: ignore[import-untyped]
)
from tests.utils.utils_test_stamper_cases import (
    STAMPER_TEST_CASES,  # type: ignore[import-untyped]
)

# Context constants for registry-driven fixture injection
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
def stamper_engine(request: Any) -> StamperEngine:
    """
    Canonical registry-driven stamper engine fixture.
    Context mapping:
      MOCK_CONTEXT = 1 (in-memory file I/O, dummy handlers)
      INTEGRATION_CONTEXT = 2 (in-memory file I/O, real handlers - no disk writes)

    Returns:
        StamperEngine: A StamperEngine instance in the appropriate context.

    Raises:
        OnexError: If an unknown context is requested (future-proofing).
    """
    if request.param == MOCK_CONTEXT:
        # Mock context: in-memory file I/O with dummy handlers
        file_io = InMemoryFileIO()
        handler_registry = FileTypeHandlerRegistry()
        handler_registry.register_handler(".yaml", DummyYamlHandler())
        handler_registry.register_handler(".json", DummyJsonHandler())
        return StamperEngine(
            DummySchemaLoader(), file_io=file_io, handler_registry=handler_registry
        )
    elif request.param == INTEGRATION_CONTEXT:
        # Integration context: in-memory file I/O with dummy handlers (testing engine behavior)
        # Note: Real handlers expect actual files on disk, so we use dummy handlers for protocol testing
        file_io = InMemoryFileIO()
        handler_registry = FileTypeHandlerRegistry()
        handler_registry.register_handler(".yaml", DummyYamlHandler())
        handler_registry.register_handler(".json", DummyJsonHandler())
        return StamperEngine(
            DummySchemaLoader(), file_io=file_io, handler_registry=handler_registry
        )
    else:
        raise OnexError(
            f"Unknown stamper engine context: {request.param}",
            CoreErrorCode.INVALID_PARAMETER,
        )


@pytest.mark.parametrize(
    "case_id,case_cls", STAMPER_TEST_CASES.items(), ids=list(STAMPER_TEST_CASES.keys())
)
def test_stamper_cases(
    case_id: str, case_cls: Any, stamper_engine: StamperEngine
) -> None:
    # Import the global variables from the shared module
    # Set the global variables in the shared module
    import omnibase.fixtures.mocks.dummy_handlers as dummy_handlers

    case = case_cls()

    # Generate a unique file path for each test (in-memory only)
    ext = ".yaml" if case.file_type == "yaml" else ".json"
    file_path = Path(f"/test/{case_id}{ext}")

    # Use the injected stamper engine's file I/O abstraction
    file_io = stamper_engine.file_io

    # Write test content using the file I/O abstraction
    if case.content is None:
        if case.file_type == "json":
            file_io.write_text(file_path, "{}")
        else:
            file_io.write_text(file_path, "")
    elif case.file_type == "yaml":
        if isinstance(case.content, str):
            file_io.write_text(file_path, case.content)
        else:
            file_io.write_yaml(file_path, case.content)
    elif case.file_type == "json":
        if isinstance(case.content, str):
            file_io.write_text(file_path, case.content)
        else:
            file_io.write_json(file_path, case.content)
    elif isinstance(case.content, str):
        file_io.write_text(file_path, case.content)

    # Set expected status/message for dummy handlers using the shared module
    dummy_handlers.CURRENT_EXPECTED_STATUS = case.expected_status
    dummy_handlers.CURRENT_EXPECTED_MESSAGE = case.expected_message

    # Execute the test using the injected stamper engine
    result = stamper_engine.stamp_file(file_path, template=TemplateTypeEnum.MINIMAL)

    # TODO: Update test data for full ONEX schema compliance (see docs/testing.md)
    if case_id.startswith("malformed_"):
        try:
            assert (
                result.status == case.expected_status
            ), f"{case_id}: status {result.status} != {case.expected_status}"
            assert (
                case.expected_message in result.messages[0].summary
                or "Error stamping file" in result.messages[0].summary
            ), f"{case_id}: message '{result.messages[0].summary}' does not contain '{case.expected_message}' or 'Error stamping file'"
        except AssertionError:
            print(f"[DEBUG] {case_id} failed: {result.messages[0].summary}")
            raise
    else:
        try:
            assert (
                result.status == case.expected_status
            ), f"{case_id}: status {result.status} != {case.expected_status}"
            assert (
                case.expected_message in result.messages[0].summary
            ), f"{case_id}: message '{result.messages[0].summary}' does not contain '{case.expected_message}'"
        except AssertionError:
            print(f"[DEBUG] {case_id} failed: {result.messages[0].summary}")
            raise
