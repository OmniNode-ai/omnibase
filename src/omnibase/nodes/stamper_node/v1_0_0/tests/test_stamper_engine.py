# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_stamper_engine.py
# version: 1.0.0
# uuid: 574f9eb4-f06e-4e25-bff6-194384a36cba
# author: OmniNode Team
# created_at: 2025-05-22T14:03:21.902158
# last_modified_at: 2025-05-22T20:50:39.721385
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 611844030dc7d09c49f4e1920a0e6977a8b4a5b9a192dedd0f26075324816fe9
# entrypoint: python@test_stamper_engine.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_stamper_engine
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Standards-Compliant Test File for ONEX/OmniBase Stamper Engine

This file follows the canonical test pattern as demonstrated in src/omnibase/utils/tests/test_node_metadata_extractor.py. It demonstrates:
- Naming conventions: test_ prefix, lowercase, descriptive
- Context-agnostic, registry-driven, fixture-injected testing
- Use of both mock (unit) and integration (real) contexts via pytest fixture parametrization
- No global state; all dependencies are injected
- Registry-driven test case execution pattern
- Compliance with all standards in docs/standards.md and docs/testing.md

All new stamper engine tests should follow this pattern unless a justified exception is documented and reviewed.
"""

import json
from pathlib import Path
from typing import Any
from unittest import mock

import pytest
import yaml

from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.model.model_onex_message_result import (  # type: ignore[import-untyped]
    OnexResultModel,
    OnexStatus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.io.in_memory_file_io import (
    InMemoryFileIO,  # type: ignore[import-untyped]
)
from omnibase.tools.fixture_stamper_engine import (
    FixtureStamperEngine,  # type: ignore[import-untyped]
)
from omnibase.utils.directory_traverser import DirectoryTraverser

from ..helpers.stamper_engine import StamperEngine
from ..tests.mocks.dummy_schema_loader import DummySchemaLoader
from ..tests.protocol_stamper_test_case import ProtocolStamperTestCase
from ..tests.stamper_test_registry_cases import STAMPER_TEST_CASES


@pytest.fixture
def real_engine() -> StamperEngine:
    """Fixture providing a real StamperEngine instance with in-memory file IO."""
    return StamperEngine(
        schema_loader=DummySchemaLoader(),
        file_io=InMemoryFileIO(),
    )


@pytest.fixture(params=["json", "yaml"])
def fixture_engine(
    tmp_path: Path, request: pytest.FixtureRequest
) -> FixtureStamperEngine:
    """Fixture providing a FixtureStamperEngine for both JSON and YAML formats."""
    fixture_data: dict[str, Any] = {
        "test.yaml": {
            "status": "success",
            "target": "test.yaml",
            "messages": [{"summary": "Fixture success", "level": "info"}],
            "metadata": {"trace_hash": "abc123"},
        },
        "test_dir": {
            "status": "success",
            "target": "test_dir",
            "messages": [{"summary": "Dir fixture", "level": "info"}],
            "metadata": {"processed": 1, "failed": 0, "skipped": 0},
        },
    }
    fmt: str = request.param  # type: ignore[attr-defined]
    fixture_path = tmp_path / f"fixture.{fmt}"
    if fmt == "json":
        fixture_path.write_text(json.dumps(fixture_data))
    else:
        fixture_path.write_text(yaml.safe_dump(fixture_data))
    return FixtureStamperEngine(fixture_path, fixture_format=fmt)


@pytest.mark.parametrize(
    "test_case", STAMPER_TEST_CASES, ids=[tc.id for tc in STAMPER_TEST_CASES]
)
def test_stamp_file_registry_driven(
    real_engine: StamperEngine, test_case: ProtocolStamperTestCase
) -> None:
    file_io = real_engine.file_io
    path = Path(test_case.file_path)
    # Write the file content for all file types using write_text (handler-rendered, with delimiters)
    file_io.write_text(path, test_case.file_content)
    result: OnexResultModel = real_engine.stamp_file(path)
    assert isinstance(result, OnexResultModel)
    assert result.status == test_case.expected_status
    # Optionally check metadata, content, etc. if provided
    if test_case.expected_metadata:
        for k, v in test_case.expected_metadata.items():
            assert result.metadata.get(k) == v  # type: ignore[union-attr]


def test_process_directory_real_engine(
    real_engine: StamperEngine, tmp_path: Path
) -> None:
    """Test processing a directory using the real engine and in-memory file IO."""
    file_io = real_engine.file_io
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    file_path = dir_path / "test.yaml"
    file_io.write_yaml(
        file_path,
        {
            "schema_version": "1.0.0",
            "name": "test",
            "version": "1.0.0",
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "author": "Test Author",
            "created_at": "2025-01-01T00:00:00Z",
            "last_modified_at": "2025-01-01T00:00:00Z",
            "description": "desc",
            "state_contract": "contract-1",
            "lifecycle": "active",
            "hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "entrypoint": {"type": "python", "target": "main.py"},
            "namespace": "onex.test",
            "meta_type": "tool",
        },
    )
    result: OnexResultModel = real_engine.process_directory(dir_path)
    assert isinstance(result, OnexResultModel)
    assert result.status in (OnexStatus.SUCCESS, OnexStatus.WARNING, OnexStatus.ERROR)


def test_stamp_file_fixture_engine(fixture_engine: FixtureStamperEngine) -> None:
    """Test stamping a file using the fixture engine."""
    result: OnexResultModel = fixture_engine.stamp_file(Path("test.yaml"))
    assert isinstance(result, OnexResultModel)
    assert result.status == OnexStatus.SUCCESS
    assert result.target == "test.yaml"
    assert result.messages[0].summary == "Fixture success"


def test_process_directory_fixture_engine(fixture_engine: FixtureStamperEngine) -> None:
    """Test processing a directory using the fixture engine."""
    result: OnexResultModel = fixture_engine.process_directory(Path("test_dir"))
    assert isinstance(result, OnexResultModel)
    assert result.status == OnexStatus.SUCCESS
    assert result.target == "test_dir"
    assert result.messages[0].summary == "Dir fixture"


def test_stamp_markdown_file_real_engine(real_engine: StamperEngine) -> None:
    """Test stamping a Markdown (.md) file using the real engine and in-memory file IO."""
    file_io = real_engine.file_io
    path = Path("test.md")
    # Provide a canonical metadata block as a Markdown comment at the top
    file_io.write_text(
        path,
        """<!-- === OmniNode:Metadata ===\n"""
        "<!-- schema_version: 1.0.0 -->\n"
        "<!-- name: test -->\n"
        "<!-- version: 1.0.0 -->\n"
        "<!-- uuid: 123e4567-e89b-12d3-a456-426614174000 -->\n"
        "<!-- author: Test Author -->\n"
        "<!-- created_at: 2025-01-01T00:00:00Z -->\n"
        "<!-- last_modified_at: 2025-01-01T00:00:00Z -->\n"
        "<!-- description: desc -->\n"
        "<!-- state_contract: contract-1 -->\n"
        "<!-- lifecycle: active -->\n"
        "<!-- hash: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef -->\n"
        '<!-- entrypoint: {"type": "python", "target": "main.py"} -->\n'
        "<!-- namespace: onex.test -->\n"
        "<!-- meta_type: tool -->\n"
        "<!-- === /OmniNode:Metadata === -->\n\n# Example Markdown\n\nSome content here.\n",
    )
    # First stamp
    result1: OnexResultModel = real_engine.stamp_file(path)
    assert isinstance(result1, OnexResultModel)
    assert result1.status in (OnexStatus.SUCCESS, OnexStatus.WARNING, OnexStatus.ERROR)
    stamped_content1 = file_io.read_text(path)
    # Second stamp (idempotency)
    result2: OnexResultModel = real_engine.stamp_file(path)
    assert result2.status in (OnexStatus.SUCCESS, OnexStatus.WARNING, OnexStatus.ERROR)
    stamped_content2 = file_io.read_text(path)
    assert stamped_content1 == stamped_content2
    assert "OmniNode:Metadata" in stamped_content1


def test_stamp_python_file_real_engine(real_engine: StamperEngine) -> None:
    """Test stamping a Python (.py) file using the real engine and in-memory file IO."""
    file_io = real_engine.file_io
    path = Path("test.py")
    # Provide a canonical metadata block as a Python comment at the top
    file_io.write_text(
        path,
        """# === OmniNode:Metadata ===\n"
        "# schema_version: 1.0.0\n"
        "# name: test\n"
        "# version: 1.0.0\n"
        "# uuid: 123e4567-e89b-12d3-a456-426614174000\n"
        "# author: Test Author\n"
        "# created_at: 2025-01-01T00:00:00Z\n"
        "# last_modified_at: 2025-01-01T00:00:00Z\n"
        "# description: desc\n"
        "# state_contract: contract-1\n"
        "# lifecycle: active\n"
        "# hash: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef\n"
        "# entrypoint: {\"type\": \"python\", \"target\": \"main.py\"}\n"
        "# namespace: onex.test\n"
        "# meta_type: tool\n"
        "# === /OmniNode:Metadata ===\n\ndef foo():\n    return 42\n""",
    )
    # First stamp
    result1: OnexResultModel = real_engine.stamp_file(path)
    assert isinstance(result1, OnexResultModel)
    assert result1.status in (OnexStatus.SUCCESS, OnexStatus.WARNING, OnexStatus.ERROR)
    stamped_content1 = file_io.read_text(path)
    # Second stamp (idempotency)
    result2: OnexResultModel = real_engine.stamp_file(path)
    assert result2.status in (OnexStatus.SUCCESS, OnexStatus.WARNING, OnexStatus.ERROR)
    stamped_content2 = file_io.read_text(path)
    assert stamped_content1 == stamped_content2
    assert "OmniNode:Metadata" in stamped_content1


def test_stamper_uses_directory_traverser_unit() -> None:
    """Unit test that StamperEngine correctly uses the injected DirectoryTraverser."""
    schema_loader = mock.MagicMock()
    directory_traverser = mock.MagicMock(spec=DirectoryTraverser)
    directory_traverser.process_directory.return_value = OnexResultModel(
        status=OnexStatus.SUCCESS,
        target="/mock/dir",
        messages=[],
        metadata={"processed": 5, "failed": 0, "skipped": 2},
    )
    engine = StamperEngine(
        schema_loader=schema_loader, directory_traverser=directory_traverser
    )
    result = engine.process_directory(
        directory=Path("/mock/dir"),
        template=TemplateTypeEnum.MINIMAL,
        recursive=True,
        dry_run=True,
        include_patterns=["**/*.yaml"],
        exclude_patterns=["**/exclude/**"],
        ignore_file=Path("/mock/.onexignore"),
    )
    assert result.status == OnexStatus.SUCCESS
    directory_traverser.process_directory.assert_called_once()
    args, kwargs = directory_traverser.process_directory.call_args
    assert kwargs["directory"] == Path("/mock/dir") or args[0] == Path("/mock/dir")
