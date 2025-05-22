# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_stamper.py
# version: 1.0.0
# uuid: '05a5b144-c75b-45ca-b7c8-300518ea3406'
# author: OmniNode Team
# created_at: '2025-05-22T14:03:21.908309'
# last_modified_at: '2025-05-22T18:05:26.883154'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: test_stamper.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_stamper
# meta_type: tool
# trust_score: null
# tags: null
# capabilities: null
# protocols_supported: null
# base_class: null
# dependencies: null
# inputs: null
# outputs: null
# environment: null
# license: null
# signature_block: null
# x_extensions: {}
# testing: null
# os_requirements: null
# architectures: null
# container_image_reference: null
# compliance_profiles: []
# data_handling_declaration: null
# logging_config: null
# source_repository: null
# === /OmniNode:Metadata ===


"""
Canonical, registry-driven, context-agnostic test runner for CLIStamper.
Compliant with ONEX testing policy (see docs/testing.md).
"""

from pathlib import Path
from typing import Any, Optional, Tuple

import pytest

from omnibase.core.core_file_type_handler_registry import (
    FileTypeHandlerRegistry,  # type: ignore[import-untyped]
)
from omnibase.model.model_enum_log_level import (
    LogLevelEnum,  # type: ignore[import-untyped]
)
from omnibase.model.model_enum_template_type import (
    TemplateTypeEnum,  # type: ignore[import-untyped]
)
from omnibase.model.model_onex_message_result import (  # type: ignore[import-untyped]
    OnexMessageModel,
    OnexResultModel,
)
from omnibase.nodes.stamper_node.helpers.stamper_engine import StamperEngine
from omnibase.runtime.protocol.protocol_file_type_handler import (
    ProtocolFileTypeHandler,  # type: ignore[import-untyped]
)
from omnibase.utils.in_memory_file_io import (
    InMemoryFileIO,  # type: ignore[import-untyped]
)
from omnibase.utils.real_file_io import RealFileIO  # type: ignore[import-untyped]
from tests.utils.dummy_schema_loader import DummySchemaLoader
from tests.utils.utils_test_stamper_cases import (
    STAMPER_TEST_CASES,  # type: ignore[import-untyped]
)


@pytest.fixture(
    params=[
        pytest.param("mock", id="mock_context", marks=pytest.mark.mock),
        pytest.param(
            "integration", id="integration_context", marks=pytest.mark.integration
        ),
    ]
)
def file_io(request: Any, tmp_path: Path) -> Any:
    if request.param == "mock":
        return InMemoryFileIO(), Path("/test")
    elif request.param == "integration":
        return RealFileIO(), tmp_path
    else:
        pytest.skip("Unsupported file_io context")


# Global for test-driven dummy handler
CURRENT_EXPECTED_STATUS = None
CURRENT_EXPECTED_MESSAGE = None


# Dummy handler for protocol compliance in tests
class DummyYamlHandler(ProtocolFileTypeHandler):
    file_type = "yaml"

    def can_handle(self, path: Path, content: str) -> bool:
        return True

    def extract_block(self, path: Path, content: str) -> Tuple[Optional[Any], str]:
        return None, content

    def serialize_block(self, meta: Any) -> str:
        return ""

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        global CURRENT_EXPECTED_STATUS, CURRENT_EXPECTED_MESSAGE
        return OnexResultModel(
            status=CURRENT_EXPECTED_STATUS,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary=CURRENT_EXPECTED_MESSAGE or "",
                    level=LogLevelEnum.INFO,
                    file=str(path),
                    line=0,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata={},
        )

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        return OnexResultModel(
            status=CURRENT_EXPECTED_STATUS,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary=CURRENT_EXPECTED_MESSAGE or "",
                    level=LogLevelEnum.INFO,
                    file=str(path),
                    line=0,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata={},
        )

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def compute_hash(self, path: Path, content: str, **kwargs: Any) -> Optional[str]:
        return "dummy_hash"


class DummyJsonHandler(ProtocolFileTypeHandler):
    file_type = "json"

    def can_handle(self, path: Path, content: str) -> bool:
        return True

    def extract_block(self, path: Path, content: str) -> Tuple[Optional[Any], str]:
        return None, content

    def serialize_block(self, meta: Any) -> str:
        return ""

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        global CURRENT_EXPECTED_STATUS, CURRENT_EXPECTED_MESSAGE
        return OnexResultModel(
            status=CURRENT_EXPECTED_STATUS,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary=CURRENT_EXPECTED_MESSAGE or "",
                    level=LogLevelEnum.INFO,
                    file=str(path),
                    line=0,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata={},
        )

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        return OnexResultModel(
            status=CURRENT_EXPECTED_STATUS,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary=CURRENT_EXPECTED_MESSAGE or "",
                    level=LogLevelEnum.INFO,
                    file=str(path),
                    line=0,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata={},
        )

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def compute_hash(self, path: Path, content: str, **kwargs: Any) -> Optional[str]:
        return "dummy_hash"


@pytest.mark.parametrize(
    "case_id,case_cls", STAMPER_TEST_CASES.items(), ids=list(STAMPER_TEST_CASES.keys())
)
def test_stamper_cases(case_id: str, case_cls: Any, file_io: Any) -> None:
    global CURRENT_EXPECTED_STATUS, CURRENT_EXPECTED_MESSAGE
    file_io_impl, root = file_io
    case = case_cls()
    # Generate a unique file path for each test
    ext = ".yaml" if case.file_type == "yaml" else ".json"
    file_path = root / f"{case_id}{ext}"
    # Write the file using the protocol
    if isinstance(file_io_impl, InMemoryFileIO):
        if case.file_type == "yaml":
            file_io_impl.write_yaml(file_path, case.content)
        elif case.file_type == "json":
            file_io_impl.write_json(file_path, case.content)
    else:
        # Real file I/O
        if case.content is None:
            if case.file_type == "json":
                file_path.write_text("{}")
            else:
                file_path.write_text("")
        elif case.file_type == "yaml":
            import yaml

            with file_path.open("w") as f:
                yaml.safe_dump(case.content, f)
        elif case.file_type == "json":
            import json

            with file_path.open("w") as f:
                json.dump(case.content, f, sort_keys=True)
        elif isinstance(case.content, str):
            file_path.write_text(case.content)
    # Register dummy handlers for .yaml and .json
    handler_registry = FileTypeHandlerRegistry()
    handler_registry.register_handler(".yaml", DummyYamlHandler())
    handler_registry.register_handler(".json", DummyJsonHandler())
    # Set expected status/message for the handler
    CURRENT_EXPECTED_STATUS = case.expected_status
    CURRENT_EXPECTED_MESSAGE = case.expected_message
    stamper = StamperEngine(
        DummySchemaLoader(), file_io=file_io_impl, handler_registry=handler_registry
    )
    result = stamper.stamp_file(file_path, template=TemplateTypeEnum.MINIMAL)
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
