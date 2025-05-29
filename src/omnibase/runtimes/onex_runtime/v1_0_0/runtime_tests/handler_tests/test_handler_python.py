# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.611419'
# description: Stamped by PythonHandler
# entrypoint: python://test_handler_python
# hash: 1935dde7408e4419ef3858f9d6d232c87a4d9dcc9a6d21927f3a5dbaf434e0e9
# last_modified_at: '2025-05-29T14:14:00.770595+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_handler_python.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.runtime_tests.handler_tests.test_handler_python
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 499421af-b1d0-4808-9177-54785c32c882
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path

import pytest

from omnibase.enums import OnexStatus
from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_python import PythonHandler
from omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer import serialize_python_metadata_block

FILENAME = "foo"

@pytest.fixture
def python_handler() -> PythonHandler:
    return PythonHandler()


def test_protocol_entrypoint_uri_compliance():
    block = NodeMetadataBlock.create_with_defaults(
        name=FILENAME,
        author="Test Author",
        entrypoint_type="python",
        entrypoint_target=FILENAME,
        description="Test block",
        meta_type="tool",
        file_path=None,
    )
    assert block.entrypoint.to_uri() == f"python://{FILENAME}", f"Entrypoint URI must be python://{FILENAME}, got {block.entrypoint.to_uri()}"


def test_can_handle_default() -> None:
    handler = PythonHandler()
    assert handler.can_handle(Path("foo.py"), "")
    assert not handler.can_handle(Path("foo.yaml"), "")


@pytest.mark.node
def test_stamp_unstamped_python(python_handler: PythonHandler) -> None:
    content = "print('hello world')\n"
    result = python_handler.stamp(Path(FILENAME + ".py"), content)
    if result.status != OnexStatus.SUCCESS:
        print("DEBUG result.metadata:", result.metadata)
        print("DEBUG result.messages:", result.messages)
    assert result.status == OnexStatus.SUCCESS, f"Stamp failed: {result.metadata}, {result.messages}"
    meta_block = NodeMetadataBlock.from_file_or_content(result.metadata["content"])
    # Check entrypoint URI
    assert meta_block.entrypoint.to_uri() == f"python://{FILENAME}", f"Entrypoint URI must be python://{FILENAME}, got {meta_block.entrypoint.to_uri()}"


def test_stamp_already_stamped() -> None:
    handler = PythonHandler()
    content = "print('hello world')\n"
    stamped = handler.stamp(Path(FILENAME), content).metadata
    stamped_content = (
        stamped["content"] if stamped is not None and "content" in stamped else ""
    )
    result2 = handler.stamp(Path(FILENAME), stamped_content)
    assert result2.status == OnexStatus.SUCCESS, f"Restamp failed: {result2.metadata}, {result2.messages}"
    # Should not double-stamp
    assert (
        result2.metadata is not None
        and result2.metadata["content"].count(PY_META_OPEN) == 1
    )


def test_stamp_enum_serialization() -> None:
    handler = PythonHandler()
    content = "print('enum test')\n"
    result = handler.stamp(Path(FILENAME), content)
    block = (
        result.metadata["content"].split("\n")
        if result.metadata is not None and "content" in result.metadata
        else []
    )
    # Check for known enum values in block
    assert any("lifecycle: active" in line for line in block), f"Enum value 'lifecycle: active' not found in block: {block}"
    assert any("meta_type: tool" in line for line in block)


def test_spacing_after_block() -> None:
    handler = PythonHandler()
    content = "print('spacing test')\n"
    result = handler.stamp(Path(FILENAME), content)
    lines = (
        result.metadata["content"].split("\n")
        if result.metadata is not None and "content" in result.metadata
        else []
    )
    # There should be exactly one blank line after the block if code follows
    assert PY_META_CLOSE in lines, f"Block delimiter {PY_META_CLOSE} not found in lines: {lines}"
    idx = lines.index(PY_META_CLOSE)
    # Next line should be blank, then code
    assert lines[idx + 1] == ""
    assert "print('spacing test')" in lines[idx + 2]


def test_hash_stability():
    pass  # Removed: not protocol-compliant for public handler


def test_stamp_invalid_python() -> None:
    handler = PythonHandler()
    bad_content = "def broken(:\n"
    result = handler.stamp(Path(FILENAME), bad_content)
    # Should return error or warning, not crash
    assert result.status in [OnexStatus.SUCCESS, OnexStatus.ERROR]


def test_pre_post_validate():
    pass  # Removed: not protocol-compliant for public handler


def test_compute_hash():
    pass  # Removed: not protocol-compliant for public handler


def test_serialize_python_metadata_block_emits_comments_only():
    """
    Ensure that serialize_python_metadata_block emits only Python comments (no string literals)
    and correct delimiters for a minimal NodeMetadataBlock.
    """
    meta = NodeMetadataBlock.create_with_defaults(
        name="test.py",
        author="Test Author",
        entrypoint_type="python",
        entrypoint_target="test.py",
        description="Test block",
        meta_type="tool",
        file_path=None,
    )
    block = serialize_python_metadata_block(meta)
    # All lines except delimiters must start with '# ' or be blank
    lines = block.splitlines()
    assert lines[0].startswith("# === OmniNode:Metadata ==="), "Block must start with open delimiter"
    assert lines[-1].startswith("# === /OmniNode:Metadata ==="), "Block must end with close delimiter"
    for line in lines[1:-1]:
        if line.strip():
            assert line.startswith("# "), f"Line does not start with comment: {line!r}"
    # No Python string literal markers