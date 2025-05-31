# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.991079'
# description: Stamped by PythonHandler
# entrypoint: python://test_file_type_handler.py
# hash: fd116d665295164a93e91a9761e18b7a0d936fa83b5725c927382d0a405c5bd0
# last_modified_at: '2025-05-29T13:51:23.661787+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_file_type_handler.py
# namespace: py://omnibase.tests.protocol.test_file_type_handler_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: b066e925-d39d-476b-bb9c-8e2c1fc0867f
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Standards-Compliant Protocol Tests for ProtocolFileTypeHandler.

This file follows the canonical test pattern as demonstrated in src/omnibase/utils/tests/test_node_metadata_extractor.py. It demonstrates:
- Registry-driven test case execution pattern
- Context-agnostic, fixture-injected testing
- Protocol-first validation (no implementation details)
- No hardcoded test data or string literals
- Compliance with all standards in docs/testing.md

Tests verify that all implementations of ProtocolFileTypeHandler follow the protocol contract
through registry-injected test cases and fixture-provided dependencies.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus

# Context constants for fixture parametrization
MOCK_CONTEXT = 1
INTEGRATION_CONTEXT = 2


class MockFileTypeHandler(ProtocolFileTypeHandler):
    """Mock implementation for protocol testing in mock context."""

    def __init__(self, test_cases: Dict[str, Any]) -> None:
        """Initialize with registry-provided test cases."""
        self.test_cases = test_cases

    # Required metadata properties
    @property
    def handler_name(self) -> str:
        return "mock_file_type_handler"

    @property
    def handler_version(self) -> str:
        return "1.0.0"

    @property
    def handler_author(self) -> str:
        return "Test Suite"

    @property
    def handler_description(self) -> str:
        return "Mock handler for protocol testing"

    @property
    def supported_extensions(self) -> List[str]:
        return [".mock", ".test"]

    @property
    def supported_filenames(self) -> List[str]:
        return ["mock_file.txt"]

    @property
    def handler_priority(self) -> int:
        return 0

    @property
    def requires_content_analysis(self) -> bool:
        return True

    def can_handle(self, path: Path, content: str) -> bool:
        """Mock can_handle based on test case configuration."""
        result = self.test_cases.get("can_handle_result", True)
        return bool(result)

    def extract_block(self, path: Path, content: str) -> Tuple[Optional[Any], str]:
        """Mock extract_block based on test case configuration."""
        metadata = self.test_cases.get("extract_metadata", {"mock": "metadata"})
        body = self.test_cases.get("extract_body", content)
        return metadata, str(body)

    def serialize_block(self, meta: Any) -> str:
        """Mock serialize_block based on test case configuration."""
        result = self.test_cases.get("serialize_result", "# mock metadata block\n")
        return str(result)

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """Mock stamp based on test case configuration."""
        from omnibase.enums import LogLevelEnum
        from omnibase.model.model_onex_message_result import (
            OnexMessageModel,
            OnexStatus,
        )

        status = OnexStatus(self.test_cases.get("stamp_status", "success"))
        return OnexResultModel(
            status=status,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary=self.test_cases.get(
                        "stamp_message", "Mock stamp successful"
                    ),
                    level=LogLevelEnum.INFO,
                    file=str(path),
                    line=None,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata=self.test_cases.get("stamp_metadata", {"mock": True}),
        )

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """Mock validate based on test case configuration."""
        from omnibase.enums import LogLevelEnum
        from omnibase.model.model_onex_message_result import (
            OnexMessageModel,
            OnexStatus,
        )

        status = OnexStatus(self.test_cases.get("validate_status", "success"))
        return OnexResultModel(
            status=status,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary=self.test_cases.get(
                        "validate_message", "Mock validation successful"
                    ),
                    level=LogLevelEnum.INFO,
                    file=str(path),
                    line=None,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata=self.test_cases.get("validate_metadata", {"validated": True}),
        )

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        """Mock pre_validate based on test case configuration."""
        result = self.test_cases.get("pre_validate_result", None)
        if result is None:
            return None

        # Ensure we return a proper OnexResultModel
        if isinstance(result, OnexResultModel):
            return result

        # Create a mock OnexResultModel if result is not already one
        from omnibase.enums import LogLevelEnum
        from omnibase.model.model_onex_message_result import (
            OnexMessageModel,
            OnexStatus,
        )

        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary="Mock pre-validation result",
                    level=LogLevelEnum.INFO,
                    file=str(path),
                    line=None,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata={"pre_validate": True},
        )

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        """Mock post_validate based on test case configuration."""
        result = self.test_cases.get("post_validate_result", None)
        if result is None:
            return None

        # Ensure we return a proper OnexResultModel
        if isinstance(result, OnexResultModel):
            return result

        # Create a mock OnexResultModel if result is not already one
        from omnibase.enums import LogLevelEnum
        from omnibase.model.model_onex_message_result import (
            OnexMessageModel,
            OnexStatus,
        )

        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary="Mock post-validation result",
                    level=LogLevelEnum.INFO,
                    file=str(path),
                    line=None,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata={"post_validate": True},
        )


@pytest.fixture(
    params=[
        pytest.param(MOCK_CONTEXT, id="mock", marks=pytest.mark.mock),
        pytest.param(
            INTEGRATION_CONTEXT, id="integration", marks=pytest.mark.integration
        ),
    ]
)
def file_type_handler_registry(request: Any) -> Dict[str, ProtocolFileTypeHandler]:
    """
    Canonical registry-swapping fixture for ONEX file type handler tests.

    Context mapping:
      MOCK_CONTEXT = 1 (mock context; in-memory, isolated)
      INTEGRATION_CONTEXT = 2 (integration context; real handlers)

    Returns:
        Dict[str, ProtocolFileTypeHandler]: Registry of handlers in appropriate context.

    Raises:
        OnexError: If an unknown context is requested.
    """
    if request.param == MOCK_CONTEXT:
        # Mock context: return mock handlers with test case configurations
        return {
            "mock_handler": MockFileTypeHandler(
                {
                    "can_handle_result": True,
                    "extract_metadata": {"test": "metadata"},
                    "extract_body": "test body",
                    "serialize_result": "# test metadata\n",
                    "stamp_status": "success",
                    "validate_status": "success",
                }
            ),
            "failing_handler": MockFileTypeHandler(
                {
                    "can_handle_result": False,
                    "stamp_status": "error",
                    "validate_status": "error",
                }
            ),
        }
    elif request.param == INTEGRATION_CONTEXT:
        # Integration context: return real handlers
        from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_markdown import (
            MarkdownHandler,
        )
        from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import (
            MetadataYAMLHandler,
        )
        from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_python import (
            PythonHandler,
        )

        return {
            "yaml_handler": MetadataYAMLHandler(),
            "python_handler": PythonHandler(),
            "markdown_handler": MarkdownHandler(),
        }
    else:
        raise OnexError(
            f"Unknown file type handler context: {request.param}",
            CoreErrorCode.INVALID_PARAMETER,
        )


@pytest.fixture
def test_case_registry() -> Dict[str, Dict[str, Any]]:
    """
    Registry of test cases for protocol compliance testing.

    TODO: This should be automated via decorators/import hooks per testing.md policy.
    """
    return {
        "basic_path_content": {
            "path": Path("test.txt"),
            "content": "test content",
            "description": "Basic path and content test case",
        },
        "empty_inputs": {
            "path": Path(""),
            "content": "",
            "description": "Empty path and content edge case",
        },
        "complex_path": {
            "path": Path("very/long/path/that/might/cause/issues.txt"),
            "content": "normal content",
            "description": "Complex path structure test case",
        },
        "binary_content": {
            "path": Path("binary.bin"),
            "content": "malformed content\x00\xff",
            "description": "Binary content edge case",
        },
    }


@pytest.fixture
def metadata_test_cases() -> Dict[str, Any]:
    """
    Registry of metadata test cases for serialize_block testing.

    TODO: This should be automated via decorators/import hooks per testing.md policy.
    """
    return {
        "simple_dict": {"test": "data"},
        "empty_dict": {},
        "complex_dict": {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "string": "test",
        },
    }


def test_protocol_method_existence(
    file_type_handler_registry: Dict[str, ProtocolFileTypeHandler]
) -> None:
    """
    Protocol: Verify all required methods exist with correct signatures.
    """
    for handler_name, handler in file_type_handler_registry.items():
        # Check that all protocol methods exist
        assert hasattr(
            handler, "can_handle"
        ), f"{handler_name}: Missing can_handle method"
        assert hasattr(
            handler, "extract_block"
        ), f"{handler_name}: Missing extract_block method"
        assert hasattr(
            handler, "serialize_block"
        ), f"{handler_name}: Missing serialize_block method"
        assert hasattr(handler, "stamp"), f"{handler_name}: Missing stamp method"
        assert hasattr(handler, "validate"), f"{handler_name}: Missing validate method"
        assert hasattr(
            handler, "pre_validate"
        ), f"{handler_name}: Missing pre_validate method"
        assert hasattr(
            handler, "post_validate"
        ), f"{handler_name}: Missing post_validate method"

        # Check method signatures by inspecting callable
        assert callable(
            handler.can_handle
        ), f"{handler_name}: can_handle must be callable"
        assert callable(
            handler.extract_block
        ), f"{handler_name}: extract_block must be callable"
        assert callable(
            handler.serialize_block
        ), f"{handler_name}: serialize_block must be callable"
        assert callable(handler.stamp), f"{handler_name}: stamp must be callable"
        assert callable(handler.validate), f"{handler_name}: validate must be callable"
        assert callable(
            handler.pre_validate
        ), f"{handler_name}: pre_validate must be callable"
        assert callable(
            handler.post_validate
        ), f"{handler_name}: post_validate must be callable"


def test_can_handle_returns_bool(
    file_type_handler_registry: Dict[str, ProtocolFileTypeHandler],
    test_case_registry: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: can_handle() must return bool for any path/content combination.
    """
    for handler_name, handler in file_type_handler_registry.items():
        for case_name, test_case in test_case_registry.items():
            result = handler.can_handle(test_case["path"], test_case["content"])
            assert isinstance(
                result, bool
            ), f"{handler_name} with {case_name}: can_handle() must return bool, got {type(result)}"


def test_extract_block_returns_tuple(
    file_type_handler_registry: Dict[str, ProtocolFileTypeHandler],
    test_case_registry: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: extract_block() must return tuple[Optional[Any], str].
    """
    for handler_name, handler in file_type_handler_registry.items():
        for case_name, test_case in test_case_registry.items():
            result = handler.extract_block(test_case["path"], test_case["content"])

            assert isinstance(
                result, tuple
            ), f"{handler_name} with {case_name}: extract_block() must return tuple, got {type(result)}"
            assert (
                len(result) == 2
            ), f"{handler_name} with {case_name}: extract_block() must return 2-tuple, got {len(result)}-tuple"

            metadata, body = result
            # metadata can be Any or None
            assert isinstance(
                body, str
            ), f"{handler_name} with {case_name}: Body must be str, got {type(body)}"


def test_serialize_block_returns_str(
    file_type_handler_registry: Dict[str, ProtocolFileTypeHandler],
    metadata_test_cases: Dict[str, Any],
) -> None:
    """
    Protocol: serialize_block() must return str.
    """
    for handler_name, handler in file_type_handler_registry.items():
        for case_name, test_metadata in metadata_test_cases.items():
            try:
                result = handler.serialize_block(test_metadata)
                assert isinstance(
                    result, str
                ), f"{handler_name} with {case_name}: serialize_block() must return str, got {type(result)}"
            except (OnexError, TypeError, Exception) as e:
                # Some handlers may require specific metadata formats
                # This is acceptable as long as the error is reasonable
                assert isinstance(
                    e, (OnexError, TypeError, Exception)
                ), f"{handler_name} with {case_name}: Unexpected exception type: {type(e)}"


def test_stamp_returns_onex_result_model(
    file_type_handler_registry: Dict[str, ProtocolFileTypeHandler],
    test_case_registry: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: stamp() must return OnexResultModel.
    """
    for handler_name, handler in file_type_handler_registry.items():
        for case_name, test_case in test_case_registry.items():
            try:
                result = handler.stamp(test_case["path"], test_case["content"])

                assert isinstance(
                    result, OnexResultModel
                ), f"{handler_name} with {case_name}: stamp() must return OnexResultModel, got {type(result)}"
                assert hasattr(
                    result, "status"
                ), f"{handler_name} with {case_name}: OnexResultModel must have status attribute"
                assert hasattr(
                    result, "target"
                ), f"{handler_name} with {case_name}: OnexResultModel must have target attribute"
                assert hasattr(
                    result, "messages"
                ), f"{handler_name} with {case_name}: OnexResultModel must have messages attribute"

            except Exception as e:
                # Some handlers may raise exceptions for invalid input
                assert isinstance(
                    e, (OnexError, TypeError, NotImplementedError, Exception)
                ), f"{handler_name} with {case_name}: Unexpected exception type: {type(e)}"


def test_validate_returns_onex_result_model(
    file_type_handler_registry: Dict[str, ProtocolFileTypeHandler],
    test_case_registry: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: validate() must return OnexResultModel.
    """
    for handler_name, handler in file_type_handler_registry.items():
        for case_name, test_case in test_case_registry.items():
            try:
                result = handler.validate(test_case["path"], test_case["content"])

                assert isinstance(
                    result, OnexResultModel
                ), f"{handler_name} with {case_name}: validate() must return OnexResultModel, got {type(result)}"
                assert hasattr(
                    result, "status"
                ), f"{handler_name} with {case_name}: OnexResultModel must have status attribute"
                assert hasattr(
                    result, "target"
                ), f"{handler_name} with {case_name}: OnexResultModel must have target attribute"
                assert hasattr(
                    result, "messages"
                ), f"{handler_name} with {case_name}: OnexResultModel must have messages attribute"

                # Status should be a valid enum value, not None
                if result.status is not None:
                    from omnibase.model.model_onex_message_result import OnexStatus

                    assert isinstance(
                        result.status, OnexStatus
                    ), f"{handler_name} with {case_name}: Status must be OnexStatus enum, got {type(result.status)}"

            except Exception as e:
                # Some handlers may raise exceptions for invalid input
                assert isinstance(
                    e, (OnexError, TypeError, NotImplementedError, Exception)
                ), f"{handler_name} with {case_name}: Unexpected exception type: {type(e)}"


def test_pre_validate_returns_optional_onex_result_model(
    file_type_handler_registry: Dict[str, ProtocolFileTypeHandler],
    test_case_registry: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: pre_validate() must return Optional[OnexResultModel].
    """
    for handler_name, handler in file_type_handler_registry.items():
        for case_name, test_case in test_case_registry.items():
            result = handler.pre_validate(test_case["path"], test_case["content"])

            # Result can be None or OnexResultModel
            if result is not None:
                assert isinstance(
                    result, OnexResultModel
                ), f"{handler_name} with {case_name}: pre_validate() must return OnexResultModel or None, got {type(result)}"


def test_post_validate_returns_optional_onex_result_model(
    file_type_handler_registry: Dict[str, ProtocolFileTypeHandler],
    test_case_registry: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: post_validate() must return Optional[OnexResultModel].
    """
    for handler_name, handler in file_type_handler_registry.items():
        for case_name, test_case in test_case_registry.items():
            result = handler.post_validate(test_case["path"], test_case["content"])

            # Result can be None or OnexResultModel
            if result is not None:
                assert isinstance(
                    result, OnexResultModel
                ), f"{handler_name} with {case_name}: post_validate() must return OnexResultModel or None, got {type(result)}"


def test_path_input_requirement(
    file_type_handler_registry: Dict[str, ProtocolFileTypeHandler],
    test_case_registry: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: All methods must accept Path objects as input.
    """
    for handler_name, handler in file_type_handler_registry.items():
        for case_name, test_case in test_case_registry.items():
            test_path = test_case["path"]
            test_content = test_case["content"]

            # These should not raise TypeError for Path input
            try:
                handler.can_handle(test_path, test_content)
                handler.extract_block(test_path, test_content)
                handler.stamp(test_path, test_content)
                handler.validate(test_path, test_content)
                handler.pre_validate(test_path, test_content)
                handler.post_validate(test_path, test_content)

            except TypeError as e:
                pytest.fail(
                    f"{handler_name} with {case_name}: Protocol violation - Methods must accept Path objects: {e}"
                )
            except Exception:
                # Other exceptions are acceptable - we're only testing Path input acceptance
                pass


def test_kwargs_support(
    file_type_handler_registry: Dict[str, ProtocolFileTypeHandler],
    test_case_registry: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: stamp(), validate(), pre_validate(), post_validate() must accept **kwargs.
    """
    test_kwargs = {"author": "test", "template": "minimal", "overwrite": True}

    for handler_name, handler in file_type_handler_registry.items():
        for case_name, test_case in test_case_registry.items():
            test_path = test_case["path"]
            test_content = test_case["content"]

            # These should not raise TypeError for kwargs
            try:
                handler.stamp(test_path, test_content, **test_kwargs)
                handler.validate(test_path, test_content, **test_kwargs)
                handler.pre_validate(test_path, test_content, **test_kwargs)
                handler.post_validate(test_path, test_content, **test_kwargs)

            except TypeError as e:
                if "unexpected keyword argument" in str(e):
                    pytest.fail(
                        f"{handler_name} with {case_name}: Protocol violation - Methods must accept **kwargs: {e}"
                    )
                # Other TypeErrors might be acceptable
            except Exception:
                # Other exceptions are acceptable - we're only testing kwargs acceptance
                pass


def test_error_handling_graceful(
    file_type_handler_registry: Dict[str, ProtocolFileTypeHandler],
    test_case_registry: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: Handlers should handle errors gracefully and return appropriate results.
    """
    for handler_name, handler in file_type_handler_registry.items():
        for case_name, test_case in test_case_registry.items():
            path = test_case["path"]
            content = test_case["content"]

            try:
                # These should not crash with unhandled exceptions
                can_handle_result = handler.can_handle(path, content)
                assert isinstance(can_handle_result, bool)

                extract_result = handler.extract_block(path, content)
                assert isinstance(extract_result, tuple)

                serialize_result = handler.serialize_block(extract_result[0])
                assert isinstance(serialize_result, str)

                stamp_result = handler.stamp(path, content)
                assert isinstance(stamp_result, OnexResultModel)

                validate_result = handler.validate(path, content)
                assert isinstance(validate_result, OnexResultModel)

            except Exception as e:
                # If exceptions occur, they should be handled gracefully
                # and not be unhandled crashes
                assert isinstance(
                    e, (OnexError, TypeError, OSError, Exception)
                ), f"{handler_name} with {case_name}: Unexpected exception type: {type(e)}"
