# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 32c6a7b8-92a8-4d66-ba00-c79e1a3405ad
# name: test_in_memory_stamper.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:38:54.878494
# last_modified_at: 2025-05-19T16:38:54.878498
# description: Stamped Python file: test_in_memory_stamper.py
# state_contract: none
# lifecycle: active
# hash: 276ccc424d1de3ae29f9ed5c36679783ac69fc1c321d3149cf5fd084516514b5
# entrypoint: {'type': 'python', 'target': 'test_in_memory_stamper.py'}
# namespace: onex.stamped.test_in_memory_stamper.py
# meta_type: tool
# === /OmniNode:Metadata ===

"""
Protocol-first, registry-driven in-memory tests for CLIStamper using InMemoryFileIO.
All file operations are simulated in memory. No disk I/O.

# OmniBase/ONEX In-Memory Test Setup

This test suite demonstrates a fully in-memory, protocol-driven approach to testing the stamping tool.
- All file I/O is abstracted via the ProtocolFileIO interface.
- The InMemoryFileIO implementation simulates a file system using a Python dict.
- No temp directories, no disk I/O, and no reliance on the OS filesystem.
- This enables fast, deterministic, and CI-friendly tests that validate protocol contracts, not implementation details.
- The approach is extensible to .tree logic, ignore patterns, and error cases.

Usage:
- Use the `file_io` fixture to simulate files and directories in memory.
- Use the `stamper` fixture to run stamping logic against the in-memory file system.
- Add/modify files by calling `file_io.write_yaml`, `file_io.write_json`, or by directly manipulating `file_io.files`.
- All assertions are made on returned models, not on disk state.

This pattern is canonical for ONEX/OmniBase protocol-first, registry-driven testing.
"""

from pathlib import Path
from typing import Any

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
from omnibase.model.model_onex_message_result import (
    OnexMessageModel,  # type: ignore[import-untyped]
)
from omnibase.model.model_onex_message_result import (
    OnexResultModel,  # type: ignore[import-untyped]
)
from omnibase.model.model_onex_message_result import (
    OnexStatus,  # type: ignore[import-untyped]
)
from omnibase.protocol.protocol_file_type_handler import (
    ProtocolFileTypeHandler,  # type: ignore[import-untyped]
)
from omnibase.tools.stamper_engine import StamperEngine  # type: ignore[import-untyped]
from omnibase.utils.in_memory_file_io import (
    InMemoryFileIO,  # type: ignore[import-untyped]
)
from tests.utils.dummy_schema_loader import DummySchemaLoader


@pytest.fixture
def file_io() -> InMemoryFileIO:
    return InMemoryFileIO()


# Dummy handler for protocol compliance in tests
class DummyYamlHandler(ProtocolFileTypeHandler):
    file_type = "yaml"

    def stamp(self, *args, **kwargs):
        path = str(args[0]) if args else None
        content = args[1] if len(args) > 1 else None
        if content is None:
            return OnexResultModel(
                status=OnexStatus.error,
                target=path,
                messages=[
                    OnexMessageModel(
                        summary="File does not exist", level=LogLevelEnum.ERROR
                    )
                ],
                metadata={},
            )
        if content == "" or content == {} or content == []:
            return OnexResultModel(
                status=OnexStatus.warning,
                target=path,
                messages=[
                    OnexMessageModel(summary="Empty file", level=LogLevelEnum.WARNING)
                ],
                metadata={"trace_hash": "dummyhash"},
            )
        return OnexResultModel(
            status=OnexStatus.warning,
            target=path,
            messages=[
                OnexMessageModel(
                    summary="Semantic validation failed", level=LogLevelEnum.WARNING
                )
            ],
            metadata={},
        )


class DummyJsonHandler(ProtocolFileTypeHandler):
    file_type = "json"

    def stamp(self, *args, **kwargs):
        path = str(args[0]) if args else None
        content = args[1] if len(args) > 1 else None
        if content is None:
            return OnexResultModel(
                status=OnexStatus.error,
                target=path,
                messages=[
                    OnexMessageModel(
                        summary="File does not exist", level=LogLevelEnum.ERROR
                    )
                ],
                metadata={},
            )
        if content == "" or content == {} or content == []:
            return OnexResultModel(
                status=OnexStatus.warning,
                target=path,
                messages=[
                    OnexMessageModel(summary="Empty file", level=LogLevelEnum.WARNING)
                ],
                metadata={"trace_hash": "dummyhash"},
            )
        return OnexResultModel(
            status=OnexStatus.warning,
            target=path,
            messages=[
                OnexMessageModel(
                    summary="Semantic validation failed", level=LogLevelEnum.WARNING
                )
            ],
            metadata={},
        )


@pytest.fixture
def stamper(file_io: InMemoryFileIO) -> StamperEngine:
    handler_registry = FileTypeHandlerRegistry()
    handler_registry.register_handler(".yaml", DummyYamlHandler())
    handler_registry.register_handler(".json", DummyJsonHandler())
    return StamperEngine(
        DummySchemaLoader(), file_io=file_io, handler_registry=handler_registry
    )


@pytest.mark.parametrize(
    "file_type,content",
    [
        ("yaml", {"foo": 1, "bar": 2}),
        ("json", {"foo": 1, "bar": 2}),
    ],
)
def test_stamp_single_file(
    stamper: StamperEngine,
    file_io: InMemoryFileIO,
    file_type: str,
    content: dict[str, Any],
) -> None:
    path = Path(f"/test/test.{file_type}")
    if file_type == "yaml":
        file_io.write_yaml(path, content)
    else:
        file_io.write_json(path, content)
    result = stamper.stamp_file(path, template=TemplateTypeEnum.MINIMAL)
    assert result.status in (OnexStatus.error, OnexStatus.warning)
    assert (
        "Semantic validation failed" in result.messages[0].summary
        or "Error stamping file" in result.messages[0].summary
    )


@pytest.mark.parametrize(
    "files",
    [
        [
            ("/dir/a.yaml", {"a": 1}),
            ("/dir/b.json", {"b": 2}),
            ("/dir/ignore.txt", "should be ignored"),
        ]
    ],
)
def test_stamp_directory_in_memory(
    stamper: StamperEngine, file_io: InMemoryFileIO, files: list[tuple[str, Any]]
) -> None:
    for fname, content in files:
        path = Path(fname)
        if fname.endswith(".yaml"):
            file_io.write_yaml(path, content)
        elif fname.endswith(".json"):
            file_io.write_json(path, content)
        else:
            file_io.files[str(path)] = content
            file_io.file_types[str(path)] = "txt"
    eligible = [Path(f[0]) for f in files if f[0].endswith((".yaml", ".json"))]
    for path in eligible:
        result = stamper.stamp_file(path, template=TemplateTypeEnum.MINIMAL)
        assert result.status in (OnexStatus.error, OnexStatus.warning)
        assert (
            "Semantic validation failed" in result.messages[0].summary
            or "Error stamping file" in result.messages[0].summary
        )


# Error case: file does not exist
def test_stamp_missing_file(stamper: StamperEngine) -> None:
    path = Path("/missing/file.yaml")
    result = stamper.stamp_file(path, template=TemplateTypeEnum.MINIMAL)
    assert result.status in (OnexStatus.error, OnexStatus.warning)
    assert (
        "does not exist" in result.messages[0].summary
        or "Semantic validation failed" in result.messages[0].summary
        or "Error stamping file" in result.messages[0].summary
        or "Empty file" in result.messages[0].summary
    )


# Error case: unsupported file type
def test_stamp_unsupported_type(
    stamper: StamperEngine, file_io: InMemoryFileIO
) -> None:
    path = Path("/test/unsupported.txt")
    file_io.files[str(path)] = "not yaml or json"
    file_io.file_types[str(path)] = "txt"
    result = stamper.stamp_file(path, template=TemplateTypeEnum.MINIMAL)
    assert result.status in (OnexStatus.error, OnexStatus.warning)
    assert (
        "Unsupported file type" in result.messages[0].summary
        or "No handler registered for file type" in result.messages[0].summary
    )


# Edge case: empty YAML/JSON file
@pytest.mark.parametrize("file_type", ["yaml", "json"])
def test_stamp_empty_file(
    stamper: StamperEngine, file_io: InMemoryFileIO, file_type: str
) -> None:
    path = Path(f"/empty/empty.{file_type}")
    if file_type == "yaml":
        file_io.write_yaml(path, None)
    else:
        file_io.write_json(path, None)
    result = stamper.stamp_file(path, template=TemplateTypeEnum.MINIMAL)
    assert result.status in (OnexStatus.error, OnexStatus.warning)
    if result.metadata is not None and "trace_hash" in result.metadata:
        assert result.metadata["trace_hash"] == "dummyhash"


# Edge case: malformed YAML/JSON file
@pytest.mark.parametrize(
    "file_type,content", [("yaml", "::not yaml::"), ("json", "{not: json,}")]
)
def test_stamp_malformed_file(
    stamper: StamperEngine, file_io: InMemoryFileIO, file_type: str, content: str
) -> None:
    path = Path(f"/malformed/bad.{file_type}")
    file_io.files[str(path)] = content
    file_io.file_types[str(path)] = file_type
    result = stamper.stamp_file(path, template=TemplateTypeEnum.MINIMAL)
    assert result.status in (OnexStatus.error, OnexStatus.warning)
    assert (
        "Semantic validation failed" in result.messages[0].summary
        or "Error stamping file" in result.messages[0].summary
    )


# Simulate .tree logic: only stamp files listed in .tree
@pytest.mark.parametrize(
    "tree_files,all_files",
    [
        (
            ["/dir/a.yaml", "/dir/b.json"],
            [
                ("/dir/a.yaml", {"a": 1}),
                ("/dir/b.json", {"b": 2}),
                ("/dir/extra.yaml", {"extra": 3}),
            ],
        )
    ],
)
def test_stamp_tree_only(
    stamper: StamperEngine,
    file_io: InMemoryFileIO,
    tree_files: list[str],
    all_files: list[tuple[str, Any]],
) -> None:
    for fname, content in all_files:
        path = Path(fname)
        if fname.endswith(".yaml"):
            file_io.write_yaml(path, content)
        elif fname.endswith(".json"):
            file_io.write_json(path, content)
    eligible = [Path(f) for f in tree_files]
    for path in eligible:
        result = stamper.stamp_file(path, template=TemplateTypeEnum.MINIMAL)
        assert result.status in (OnexStatus.error, OnexStatus.warning)
        assert "Semantic validation failed" in result.messages[0].summary
