import pytest
from pathlib import Path
from omnibase.protocol.protocol_stamper_engine import ProtocolStamperEngine
from omnibase.tools.stamper_engine import StamperEngine
from omnibase.tools.fixture_stamper_engine import FixtureStamperEngine
from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.model.model_onex_message_result import OnexStatus, OnexResultModel
from omnibase.schema.loader import SchemaLoader
from omnibase.utils.directory_traverser import DirectoryTraverser
from omnibase.utils.in_memory_file_io import InMemoryFileIO
import tempfile
import json
import yaml

@pytest.fixture
def real_engine():
    return StamperEngine(
        schema_loader=SchemaLoader(),
        directory_traverser=DirectoryTraverser(),
        file_io=InMemoryFileIO(),
    )

@pytest.fixture(params=["json", "yaml"])
def fixture_engine(tmp_path, request):
    # Create a fixture file for both formats
    fixture_data = {
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
    fmt = request.param
    fixture_path = tmp_path / f"fixture.{fmt}"
    if fmt == "json":
        fixture_path.write_text(json.dumps(fixture_data))
    else:
        fixture_path.write_text(yaml.safe_dump(fixture_data))
    return FixtureStamperEngine(fixture_path, fixture_format=fmt)

def test_stamp_file_real_engine(real_engine):
    # Simulate writing a valid file in memory
    file_io = real_engine.file_io
    path = Path("test.yaml")
    file_io.write_yaml(path, {"schema_version": "1.0.0", "name": "test", "version": "1.0.0", "uuid": "123e4567-e89b-12d3-a456-426614174000", "author": "Test Author", "created_at": "2025-01-01T00:00:00Z", "last_modified_at": "2025-01-01T00:00:00Z", "description": "desc", "state_contract": "contract-1", "lifecycle": "active", "hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef", "entrypoint": {"type": "python", "target": "main.py"}, "namespace": "onex.test", "meta_type": "tool"})
    result = real_engine.stamp_file(path)
    assert isinstance(result, OnexResultModel)
    assert result.status in (OnexStatus.success, OnexStatus.warning, OnexStatus.error)

def test_process_directory_real_engine(real_engine, tmp_path):
    # Simulate a directory with one valid file
    file_io = real_engine.file_io
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    file_path = dir_path / "test.yaml"
    file_io.write_yaml(file_path, {"schema_version": "1.0.0", "name": "test", "version": "1.0.0", "uuid": "123e4567-e89b-12d3-a456-426614174000", "author": "Test Author", "created_at": "2025-01-01T00:00:00Z", "last_modified_at": "2025-01-01T00:00:00Z", "description": "desc", "state_contract": "contract-1", "lifecycle": "active", "hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef", "entrypoint": {"type": "python", "target": "main.py"}, "namespace": "onex.test", "meta_type": "tool"})
    result = real_engine.process_directory(dir_path)
    assert isinstance(result, OnexResultModel)
    assert result.status in (OnexStatus.success, OnexStatus.warning, OnexStatus.error)

def test_stamp_file_fixture_engine(fixture_engine):
    result = fixture_engine.stamp_file(Path("test.yaml"))
    assert isinstance(result, OnexResultModel)
    assert result.status == OnexStatus.success
    assert result.target == "test.yaml"
    assert result.messages[0].summary == "Fixture success"

def test_process_directory_fixture_engine(fixture_engine):
    result = fixture_engine.process_directory(Path("test_dir"))
    assert isinstance(result, OnexResultModel)
    assert result.status == OnexStatus.success
    assert result.target == "test_dir"
    assert result.messages[0].summary == "Dir fixture" 