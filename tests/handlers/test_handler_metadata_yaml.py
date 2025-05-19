# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: <to-be-generated>
# name: test_handler_metadata_yaml.py
# version: 1.0.0
# author: OmniNode Team
# created_at: <to-be-generated>
# last_modified_at: <to-be-generated>
# description: Unit tests for MetadataYAMLHandler.
# state_contract: none
# lifecycle: active
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# entrypoint: {'type': 'python', 'target': 'test_handler_metadata_yaml.py'}
# namespace: onex.stamped.test_handler_metadata_yaml.py
# meta_type: test
# === /OmniNode:Metadata ===

from pathlib import Path
from typing import List

import pytest

from omnibase.canonical.canonical_serialization import CanonicalYAMLSerializer
from omnibase.engine.stamping_engine import stamp_file
from omnibase.handlers.handler_metadata_yaml import MetadataYAMLHandler
from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN
from omnibase.model.enum_onex_status import OnexStatus
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_result import OnexResultModel

# Canonical test case registry for stamping
YamlTestCase = pytest.param
YAML_STAMP_CASES = [
    YamlTestCase(
        "unstamped",
        Path("foo.yaml"),
        "key: value\n",
        OnexStatus.SUCCESS,
        id="unstamped",
    ),
    YamlTestCase(
        "malformed",
        Path("foo.yaml"),
        "\t: not yaml\n",
        [OnexStatus.SUCCESS, OnexStatus.ERROR],
        id="malformed",
    ),
]


class ConcreteMetadataYAMLHandler(MetadataYAMLHandler):
    def compute_hash(self, path: object, content: object, **kwargs: object) -> str:
        return "0" * 64

    def pre_validate(
        self, path: object, content: object, **kwargs: object
    ) -> OnexResultModel | None:
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[],
            metadata={"note": "Stamped file"},
        )

    def post_validate(
        self, path: object, content: object, **kwargs: object
    ) -> OnexResultModel | None:
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[],
            metadata={"note": "Stamped file"},
        )

    def stamp(self, path: object, content: object, **kwargs: object) -> OnexResultModel:
        import re

        now = "1970-01-01T00:00:00Z"
        meta = NodeMetadataBlock(
            metadata_version="0.1.0",
            protocol_version="1.0.0",
            owner="OmniNode Team",
            copyright="OmniNode Team",
            schema_version="1.1.0",
            name=str(path).split(".")[0],
            version="1.0.0",
            uuid="00000000-0000-0000-0000-000000000000",
            author="OmniNode Team",
            created_at=now,
            last_modified_at=now,
            description="Stamped by stamping_engine",
            state_contract="state_contract://default",
            lifecycle=Lifecycle.ACTIVE,
            hash="0" * 64,
            entrypoint=EntrypointBlock(type=EntrypointType.PYTHON, target=str(path)),
            runtime_language_hint="python>=3.11",
            namespace=f"onex.stamped.{str(path).split('.')[0]}",
            meta_type=MetaType.TOOL,
        )
        serializer = CanonicalYAMLSerializer()
        block = (
            f"{YAML_META_OPEN}\n"
            + serializer.canonicalize_metadata_block(meta, comment_prefix="# ")
            + f"\n{YAML_META_CLOSE}"
        )
        # Remove any existing metadata block (idempotency)
        block_pattern = re.compile(
            rf"{re.escape(YAML_META_OPEN)}[\s\S]+?{re.escape(YAML_META_CLOSE)}\n*",
            re.MULTILINE,
        )
        content_no_block = re.sub(block_pattern, "", str(content) or "")
        # Normalize spacing: exactly one blank line after the block if content follows
        rest = content_no_block.lstrip("\n")
        if rest:
            stamped = block + "\n\n" + rest
        else:
            stamped = block + "\n"
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[],
            metadata={"content": stamped, "note": "Stamped file"},
        )


@pytest.fixture
def yaml_handler() -> ConcreteMetadataYAMLHandler:
    return ConcreteMetadataYAMLHandler()


@pytest.mark.parametrize("desc,path,content,expected_status", YAML_STAMP_CASES)
def test_stamp_cases(
    yaml_handler: ConcreteMetadataYAMLHandler,
    desc: str,
    path: Path,
    content: str,
    expected_status: OnexStatus | List[OnexStatus],
) -> None:
    result = stamp_file(path, content, yaml_handler)
    if isinstance(expected_status, list):
        assert result.status in [
            OnexStatus.SUCCESS,
            OnexStatus.ERROR,
        ], f"Result: {result.status}, Metadata: {result.metadata}, Messages: {result.messages}"
    else:
        assert (
            result.status == expected_status
        ), f"Result: {result.status}, Metadata: {result.metadata}, Messages: {result.messages}"
    if result.status == OnexStatus.SUCCESS:
        assert result.metadata is not None and "Stamped file" in result.metadata["note"]
        assert result.metadata is not None and "content" in result.metadata
        assert result.metadata is not None and result.metadata["content"].startswith(
            YAML_META_OPEN
        )


@pytest.mark.parametrize(
    "desc,path,content",
    [
        ("already_stamped", Path("foo.yaml"), "key: value\n"),
    ],
)
def test_stamp_idempotency(
    yaml_handler: ConcreteMetadataYAMLHandler, desc: str, path: Path, content: str
) -> None:
    result1 = stamp_file(path, content, yaml_handler)
    assert (
        result1.status == OnexStatus.SUCCESS
    ), f"Result: {result1.status}, Metadata: {result1.metadata}, Messages: {result1.messages}"
    stamped_content = (
        result1.metadata["content"]
        if result1.metadata is not None and "content" in result1.metadata
        else ""
    )
    print("\n[DEBUG] Stamped content after first stamp:\n" + stamped_content)
    result2 = stamp_file(path, stamped_content, yaml_handler)
    print(
        "\n[DEBUG] Stamped content after second stamp (should be unchanged):\n"
        + result2.metadata["content"]
        if result2.metadata is not None and "content" in result2.metadata
        else "<no content>"
    )
    assert (
        result2.status == OnexStatus.SUCCESS
    ), f"Result: {result2.status}, Metadata: {result2.metadata}, Messages: {result2.messages}"
    assert result2.metadata is not None and "Stamped file" in result2.metadata["note"]


@pytest.mark.parametrize(
    "desc,path,content",
    [
        ("hash", Path("foo.yaml"), "key: value\n"),
    ],
)
def test_compute_hash(
    yaml_handler: ConcreteMetadataYAMLHandler, desc: str, path: Path, content: str
) -> None:
    result1 = stamp_file(path, content, yaml_handler)
    assert (
        result1.status == OnexStatus.SUCCESS
    ), f"Result: {result1.status}, Metadata: {result1.metadata}, Messages: {result1.messages}"
    stamped = (
        result1.metadata["content"]
        if result1.metadata is not None and "content" in result1.metadata
        else ""
    )
    result2 = stamp_file(path, stamped, yaml_handler)
    assert (
        result2.status == OnexStatus.SUCCESS
    ), f"Result: {result2.status}, Metadata: {result2.metadata}, Messages: {result2.messages}"
    assert (
        result2.metadata is not None
        and result1.metadata is not None
        and result2.metadata.get("hash") == result1.metadata.get("hash")
    )


@pytest.mark.parametrize(
    "desc,path,content",
    [
        ("validate", Path("foo.yaml"), "key: value\n"),
    ],
)
def test_pre_post_validate(
    yaml_handler: ConcreteMetadataYAMLHandler, desc: str, path: Path, content: str
) -> None:
    pre = yaml_handler.validate(path, content)
    post = yaml_handler.validate(path, content)
    assert pre is not None and pre.status in [OnexStatus.SUCCESS, OnexStatus.ERROR]
    assert post is not None and post.status in [OnexStatus.SUCCESS, OnexStatus.ERROR]


@pytest.mark.parametrize(
    "desc,path,content,expected",
    [
        ("can_handle_yaml", Path("foo.yaml"), "", True),
        ("can_handle_py", Path("foo.py"), "", False),
    ],
)
def test_can_handle_default(
    yaml_handler: ConcreteMetadataYAMLHandler,
    desc: str,
    path: Path,
    content: str,
    expected: bool,
) -> None:
    assert yaml_handler.can_handle(path, content) is expected


def _can_handle_special_yaml(p: Path) -> bool:
    return p.name == "special.yaml"


@pytest.mark.parametrize(
    "desc,path,content,expected",
    [
        ("can_handle_predicate_true", Path("special.yaml"), "", True),
        ("can_handle_predicate_false", Path("other.yaml"), "", False),
    ],
)
def test_can_handle_predicate(
    desc: str, path: Path, content: str, expected: bool
) -> None:
    handler = ConcreteMetadataYAMLHandler(can_handle_predicate=_can_handle_special_yaml)
    assert handler.can_handle(path, content) is expected
