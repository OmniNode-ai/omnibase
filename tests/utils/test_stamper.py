"""
Canonical, registry-driven, context-agnostic test runner for CLIStamper.
Compliant with ONEX testing policy (see docs/testing.md).
"""
import pytest
from pathlib import Path
from omnibase.tools.stamper_engine import StamperEngine
from omnibase.utils.in_memory_file_io import InMemoryFileIO
from omnibase.utils.real_file_io import RealFileIO
from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.schema.loader import SchemaLoader
from tests.utils.utils_test_stamper_cases import STAMPER_TEST_CASES

@pytest.fixture(params=[
    pytest.param("mock", id="mock_context", marks=pytest.mark.mock),
    pytest.param("integration", id="integration_context", marks=pytest.mark.integration),
])
def file_io(request, tmp_path):
    if request.param == "mock":
        return InMemoryFileIO(), Path("/test")
    elif request.param == "integration":
        return RealFileIO(), tmp_path
    else:
        pytest.skip("Unsupported file_io context")

@pytest.mark.parametrize("case_id,case_cls", STAMPER_TEST_CASES.items(), ids=list(STAMPER_TEST_CASES.keys()))
def test_stamper_cases(case_id, case_cls, file_io):
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
    stamper = StamperEngine(SchemaLoader(), file_io=file_io_impl)
    result = stamper.stamp_file(file_path, template=TemplateTypeEnum.MINIMAL)
    # TODO: Update test data for full ONEX schema compliance (see docs/testing.md)
    if case_id.startswith("malformed_"):
        assert result.status == case.expected_status, f"{case_id}: status {result.status} != {case.expected_status}"
        assert (
            case.expected_message in result.messages[0].summary or
            "Error stamping file" in result.messages[0].summary
        ), f"{case_id}: message '{result.messages[0].summary}' does not contain '{case.expected_message}' or 'Error stamping file'"
    else:
        assert result.status == case.expected_status, f"{case_id}: status {result.status} != {case.expected_status}"
        assert case.expected_message in result.messages[0].summary, f"{case_id}: message '{result.messages[0].summary}' does not contain '{case.expected_message}'" 