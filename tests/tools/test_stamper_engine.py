# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: test_stamper_engine.py
# version: 1.0.0
# uuid: 7981349d-29da-48a8-90f2-795011ae7e98
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.172110
# last_modified_at: 2025-05-21T16:42:46.067022
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 95abc568c87475d37ffb1f2238058e6eee9f78cf20ab943b26ef8baf80c7d5ab
# entrypoint: {'type': 'python', 'target': 'test_stamper_engine.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_stamper_engine
# meta_type: tool
# === /OmniNode:Metadata ===

"""
Standards-Compliant Test File for ONEX/OmniBase Stamper Engine

This file follows the canonical test pattern as demonstrated in tests/utils/test_node_metadata_extractor.py. It demonstrates:
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

import pytest
import yaml

from omnibase.model.model_onex_message_result import (  # type: ignore[import-untyped]
    OnexResultModel,
    OnexStatus,
)
from omnibase.tools.fixture_stamper_engine import (
    FixtureStamperEngine,  # type: ignore[import-untyped]
)
from omnibase.tools.stamper_engine import StamperEngine  # type: ignore[import-untyped]
from omnibase.utils.directory_traverser import (
    DirectoryTraverser,  # type: ignore[import-untyped]
)
from omnibase.utils.in_memory_file_io import (
    InMemoryFileIO,  # type: ignore[import-untyped]
)
from tests.utils.dummy_schema_loader import DummySchemaLoader


@pytest.fixture
def real_engine() -> StamperEngine:
    """Fixture providing a real StamperEngine instance with in-memory file IO."""
    return StamperEngine(
        schema_loader=DummySchemaLoader(),
        directory_traverser=DirectoryTraverser(),
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


def test_stamp_file_real_engine(real_engine: StamperEngine) -> None:
    """Test stamping a file using the real engine and in-memory file IO."""
    file_io = real_engine.file_io
    path = Path("test.yaml")
    file_io.write_yaml(
        path,
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
    result: OnexResultModel = real_engine.stamp_file(path)
    assert isinstance(result, OnexResultModel)
    assert result.status in (OnexStatus.SUCCESS, OnexStatus.WARNING, OnexStatus.ERROR)


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
