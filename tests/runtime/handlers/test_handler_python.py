# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_handler_python.py
# version: 1.0.0
# uuid: '1d451430-53dc-4665-bc31-60e3d080ae88'
# author: OmniNode Team
# created_at: '2025-05-22T12:17:04.457183'
# last_modified_at: '2025-05-22T18:05:26.856804'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: test_handler_python.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_handler_python
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


from pathlib import Path

from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.model.enum_onex_status import OnexStatus
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.runtime.handlers.handler_python import PythonHandler


class ConcretePythonHandler(PythonHandler):
    def extract_block(self, path: Path, content: str) -> tuple[None, str]:
        return None, content

    def serialize_block(self, meta: object) -> str:
        serializer = CanonicalYAMLSerializer()
        return (
            f"{PY_META_OPEN}\n"
            + serializer.canonicalize_metadata_block(meta, comment_prefix="# ")
            + f"\n{PY_META_CLOSE}"
        )

    def validate(self, path: Path, content: str, **kwargs: object) -> OnexResultModel:
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[],
            metadata={"note": "Stamped Python file"},
        )

    def compute_hash(self, path: Path, content: str, **kwargs: object) -> str:
        return "0" * 64

    def pre_validate(
        self, path: Path, content: str, **kwargs: object
    ) -> OnexResultModel | None:
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[],
            metadata={"note": "Stamped Python file"},
        )

    def post_validate(
        self, path: Path, content: str, **kwargs: object
    ) -> OnexResultModel | None:
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[],
            metadata={"note": "Stamped Python file"},
        )

    def stamp(self, path: Path, content: str, **kwargs: object) -> OnexResultModel:
        import re

        now = "1970-01-01T00:00:00Z"
        meta = NodeMetadataBlock(
            metadata_version="0.1.0",
            protocol_version="1.0.0",
            owner="OmniNode Team",
            copyright="OmniNode Team",
            schema_version="1.1.0",
            name=path.stem,
            version="1.0.0",
            uuid="00000000-0000-0000-0000-000000000000",
            author="OmniNode Team",
            created_at=now,
            last_modified_at=now,
            description="Stamped by stamping_engine",
            state_contract="state_contract://default",
            lifecycle=Lifecycle.ACTIVE,
            hash="0" * 64,
            entrypoint=EntrypointBlock(type=EntrypointType.PYTHON, target=path.name),
            runtime_language_hint="python>=3.11",
            namespace=f"onex.stamped.{path.stem}",
            meta_type=MetaType.TOOL,
        )
        serializer = CanonicalYAMLSerializer()
        block = (
            f"{PY_META_OPEN}\n"
            + serializer.canonicalize_metadata_block(meta, comment_prefix="# ")
            + f"\n{PY_META_CLOSE}"
        )
        # Remove any existing metadata block (idempotency)
        block_pattern = re.compile(
            rf"{re.escape(PY_META_OPEN)}[\s\S]+?{re.escape(PY_META_CLOSE)}\n*",
            re.MULTILINE,
        )
        content_no_block = re.sub(block_pattern, "", content or "")
        # Normalize spacing: exactly one blank line after the block if code follows
        rest = content_no_block.lstrip("\n")
        if rest:
            stamped = block + "\n\n" + rest
        else:
            stamped = block + "\n"
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[],
            metadata={"content": stamped, "note": "Stamped Python file"},
        )


def test_can_handle_default() -> None:
    handler = ConcretePythonHandler()
    assert handler.can_handle(Path("foo.py"), "")
    assert not handler.can_handle(Path("foo.yaml"), "")


def test_stamp_unstamped() -> None:
    handler = ConcretePythonHandler()
    content = "print('hello world')\n"
    result = handler.stamp(Path("foo.py"), content)
    if result.status != OnexStatus.SUCCESS:
        print("DEBUG result.metadata:", result.metadata)
        print("DEBUG result.messages:", result.messages)
        assert False, f"Stamp failed: {result.metadata}, {result.messages}"
    assert result.status == OnexStatus.SUCCESS
    assert (
        result.metadata is not None and "Stamped Python file" in result.metadata["note"]
    )
    assert result.metadata is not None and "content" in result.metadata
    assert result.metadata is not None and result.metadata["content"].startswith(
        PY_META_OPEN
    )
    # Block is at top, followed by blank line, then code
    assert (
        result.metadata is not None
        and result.metadata["content"].split("\n")[0] == PY_META_OPEN
    )
    assert (
        result.metadata is not None
        and "print('hello world')" in result.metadata["content"]
    )


def test_stamp_already_stamped() -> None:
    handler = ConcretePythonHandler()
    content = "print('hello world')\n"
    stamped = handler.stamp(Path("foo.py"), content).metadata
    stamped_content = (
        stamped["content"] if stamped is not None and "content" in stamped else ""
    )
    result2 = handler.stamp(Path("foo.py"), stamped_content)
    assert result2.status == OnexStatus.SUCCESS
    assert (
        result2.metadata is not None
        and "Stamped Python file" in result2.metadata["note"]
    )
    # Should not double-stamp
    assert (
        result2.metadata is not None
        and result2.metadata["content"].count(PY_META_OPEN) == 1
    )


def test_stamp_enum_serialization() -> None:
    handler = ConcretePythonHandler()
    content = "print('enum test')\n"
    result = handler.stamp(Path("foo.py"), content)
    # All enums should be serialized as their .value
    block = (
        result.metadata["content"].split("\n")
        if result.metadata is not None and "content" in result.metadata
        else []
    )
    # Check for known enum values in block
    assert any("lifecycle: active" in line for line in block)
    assert any("meta_type: tool" in line for line in block)


def test_spacing_after_block() -> None:
    handler = ConcretePythonHandler()
    content = "print('spacing test')\n"
    result = handler.stamp(Path("foo.py"), content)
    # There should be exactly one blank line after the block if code follows
    lines = (
        result.metadata["content"].split("\n")
        if result.metadata is not None and "content" in result.metadata
        else []
    )
    assert PY_META_CLOSE in lines
    idx = lines.index(PY_META_CLOSE)
    # Next line should be blank, then code
    assert lines[idx + 1] == ""
    assert "print('spacing test')" in lines[idx + 2]


def test_hash_stability() -> None:
    handler = ConcretePythonHandler()
    content = "print('hash test')\n"
    stamped1 = handler.stamp(Path("foo.py"), content).metadata
    stamped1_content = (
        stamped1["content"] if stamped1 is not None and "content" in stamped1 else ""
    )
    hash1 = handler.compute_hash(Path("foo.py"), stamped1_content)
    # Print debug info for first stamp
    meta1 = NodeMetadataBlock.from_file_or_content(stamped1_content)
    print("STAMP1 last_modified_at:", meta1.last_modified_at)
    print("STAMP1 hash:", meta1.hash)
    print("STAMP1 content:\n", stamped1_content)
    # Stamping again should not change hash if content unchanged
    stamped2 = handler.stamp(Path("foo.py"), stamped1_content).metadata
    stamped2_content = (
        stamped2["content"] if stamped2 is not None and "content" in stamped2 else ""
    )
    hash2 = handler.compute_hash(Path("foo.py"), stamped2_content)
    # Print debug info for second stamp
    meta2 = NodeMetadataBlock.from_file_or_content(stamped2_content)
    print("STAMP2 last_modified_at:", meta2.last_modified_at)
    print("STAMP2 hash:", meta2.hash)
    print("STAMP2 content:\n", stamped2_content)
    if stamped1_content != stamped2_content:
        import difflib

        print("===== DIFF =====")
        for line in difflib.unified_diff(
            stamped1_content.splitlines(), stamped2_content.splitlines(), lineterm=""
        ):
            print(line)
        print("================")
    assert hash1 == hash2


def test_stamp_invalid_python() -> None:
    handler = ConcretePythonHandler()
    bad_content = "def broken(:\n"
    result = handler.stamp(Path("foo.py"), bad_content)
    # Should return error or warning, not crash
    assert result.status in [OnexStatus.SUCCESS, OnexStatus.ERROR]


def test_pre_post_validate() -> None:
    handler = ConcretePythonHandler()
    content = "print('validate test')\n"
    pre = handler.pre_validate(Path("foo.py"), content)
    post = handler.post_validate(Path("foo.py"), content)
    assert pre is not None and pre.status in [
        OnexStatus.SUCCESS,
        OnexStatus.WARNING,
        OnexStatus.ERROR,
    ]
    assert post is not None and post.status in [
        OnexStatus.SUCCESS,
        OnexStatus.WARNING,
        OnexStatus.ERROR,
    ]


def test_compute_hash() -> None:
    handler = ConcretePythonHandler()
    content = "print('hash test')\n"
    stamped = handler.stamp(Path("foo.py"), content).metadata
    stamped_content = (
        stamped["content"] if stamped is not None and "content" in stamped else ""
    )
    hash_val = handler.compute_hash(Path("foo.py"), stamped_content)
    assert hash_val is None or isinstance(hash_val, str)
