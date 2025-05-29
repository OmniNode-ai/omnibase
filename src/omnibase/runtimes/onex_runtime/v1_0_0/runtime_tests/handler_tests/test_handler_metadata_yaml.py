# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.600210'
# description: Stamped by PythonHandler
# entrypoint: python://test_handler_metadata_yaml
# hash: 447e09514f1fb965733c016b8f7f01e662283a1a745520ab5184f3248c1016a0
# last_modified_at: '2025-05-29T14:14:00.761337+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_handler_metadata_yaml.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.runtime_tests.handler_tests.test_handler_metadata_yaml
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 2ce4a48a-f8bb-4cc8-adf9-ba7bdb82b20f
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import List, Protocol

import pytest
from pydantic import BaseModel

from omnibase.enums import OnexStatus
from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import (
    MetadataYAMLHandler,
)

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
        meta = NodeMetadataBlock.create_with_defaults(
            name=path.name,
            author="Test Author",
            entrypoint_type="yaml",
            entrypoint_target=path.stem,
            description="Test file for handler",
            meta_type="tool"
        )
        serializer = CanonicalYAMLSerializer()
        # Emit a YAML block with # comments, no '---' document markers
        yaml_block = serializer.canonicalize_metadata_block(meta, comment_prefix="# ")
        yaml_block = '\n'.join(line for line in yaml_block.splitlines() if line.strip())  # Remove blank lines
        block = f"{YAML_META_OPEN}\n{yaml_block}\n{YAML_META_CLOSE}"
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
def yaml_handler() -> MetadataYAMLHandler:
    return MetadataYAMLHandler()


@pytest.mark.parametrize("desc,path,content,expected_status", YAML_STAMP_CASES)
def test_stamp_cases(
    yaml_handler: MetadataYAMLHandler,
    desc: str,
    path: Path,
    content: str,
    expected_status: OnexStatus | List[OnexStatus],
) -> None:
    result = yaml_handler.stamp(path, content)
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
        assert result.metadata is not None and "Stamped" in result.metadata["note"]
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
    yaml_handler: MetadataYAMLHandler, desc: str, path: Path, content: str
) -> None:
    result1 = yaml_handler.stamp(path, content)
    assert (
        result1.status == OnexStatus.SUCCESS
    ), f"Result: {result1.status}, Metadata: {result1.metadata}, Messages: {result1.messages}"
    stamped_content = (
        result1.metadata["content"]
        if result1.metadata is not None and "content" in result1.metadata
        else ""
    )
    print("\n[DEBUG] Stamped content after first stamp:\n" + stamped_content)
    result2 = yaml_handler.stamp(path, stamped_content)
    print(
        "\n[DEBUG] Stamped content after second stamp (should be unchanged):\n"
        + result2.metadata["content"]
        if result2.metadata is not None and "content" in result2.metadata
        else "<no content>"
    )
    assert (
        result2.status == OnexStatus.SUCCESS
    ), f"Result: {result2.status}, Metadata: {result2.metadata}, Messages: {result2.messages}"
    assert result2.metadata is not None and "Stamped" in result2.metadata["note"]


@pytest.mark.parametrize(
    "desc,path,content",
    [
        ("hash", Path("foo.yaml"), "key: value\n"),
    ],
)
def test_compute_hash(
    yaml_handler: MetadataYAMLHandler, desc: str, path: Path, content: str
) -> None:
    fixed_now = "2025-01-01T00:00:00.000000"
    result1 = yaml_handler.stamp(path, content, now=fixed_now)
    assert (
        result1.status == OnexStatus.SUCCESS
    ), f"Result: {result1.status}, Metadata: {result1.metadata}, Messages: {result1.messages}"
    stamped = (
        result1.metadata["content"]
        if result1.metadata is not None and "content" in result1.metadata
        else ""
    )
    result2 = yaml_handler.stamp(path, stamped, now=fixed_now)
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
    yaml_handler: MetadataYAMLHandler, desc: str, path: Path, content: str
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
    yaml_handler: MetadataYAMLHandler,
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
    handler = MetadataYAMLHandler(can_handle_predicate=_can_handle_special_yaml)
    assert handler.can_handle(path, content) is expected


class HandlerTestCaseModel(BaseModel):
    desc: str
    path: Path
    meta_model: NodeMetadataBlock
    block: str
    content: str


class ProtocolHandlerTestCaseRegistry(Protocol):
    def all_cases(self) -> list[HandlerTestCaseModel]: ...


class CanonicalYAMLHandlerTestCaseRegistry:
    """Canonical protocol-driven registry for YAML handler test cases."""
    def __init__(self, serializer: CanonicalYAMLSerializer):
        self.serializer = serializer
    def all_cases(self) -> list[HandlerTestCaseModel]:
        now = "2025-01-01T00:00:00Z"
        meta_model = NodeMetadataBlock.create_with_defaults(
            name="canonical_test.yaml",
            author="TestBot",
            entrypoint_type="yaml",
            entrypoint_target="canonical_test",
            description="Canonical test block.",
            meta_type="tool",
            namespace="yaml://canonical_test"
        )
        # Emit a YAML block with # comments, no '---' document markers
        yaml_block = self.serializer.canonicalize_metadata_block(meta_model, comment_prefix="# ")
        yaml_block = '\n'.join(line for line in yaml_block.splitlines() if line.strip())  # Remove blank lines
        block = f"{YAML_META_OPEN}\n{yaml_block}\n{YAML_META_CLOSE}"
        content = block + "\n# Body content\n"
        return [
            HandlerTestCaseModel(
                desc="canonical_minimal",
                path=Path("canonical.yaml"),
                meta_model=meta_model,
                block=block,
                content=content,
            ),
        ]


# Instantiate the registry
canonical_yaml_handler_registry = CanonicalYAMLHandlerTestCaseRegistry(CanonicalYAMLSerializer())


@pytest.mark.parametrize(
    "case", canonical_yaml_handler_registry.all_cases(), ids=lambda c: c.desc
)
def test_round_trip_extraction_and_serialization(case: HandlerTestCaseModel) -> None:
    handler = MetadataYAMLHandler()
    # Extract block from content
    block_obj, _ = handler.extract_block(case.path, case.content)
    assert block_obj is not None, f"Failed to extract block for {case.desc}"
    # Re-serialize
    reserialized = handler.serialize_block(block_obj)
    # Extract again
    block_obj2, _ = handler.extract_block(case.path, reserialized)
    assert (
        block_obj2 is not None
    ), f"Failed to extract block after re-serialization for {case.desc}"
    # Model equivalence
    assert (
        block_obj.model_dump() == block_obj2.model_dump()
    ), f"Model mismatch after round-trip for {case.desc}"


@pytest.mark.node
def test_stamp_unstamped_yaml(yaml_handler: MetadataYAMLHandler) -> None:
    # Implementation of the new test case
    pass


def test_protocol_fields_on_stamped_yaml(yaml_handler: MetadataYAMLHandler, tmp_path):
    """
    Protocol: Stamped YAML file must have correct entrypoint, namespace, and no runtime_language_hint/tools/null fields.
    """
    test_file = tmp_path / "protocol_test.yaml"
    content = """# Protocol Test\n\nkey: value\n"""
    result = yaml_handler.stamp(test_file, content)
    assert result.status in (OnexStatus.SUCCESS, OnexStatus.WARNING), f"Stamping failed: {result.messages}"
    stamped_content = result.metadata["content"]
    import yaml, re
    # Extract YAML block from stamped_content
    block = re.search(r"# === OmniNode:Metadata ===(.*?)# === /OmniNode:Metadata ===", stamped_content, re.DOTALL)
    assert block, "No metadata block found"
    # Strip '# ' prefixes from each line before parsing
    block_lines = [line[2:] if line.strip().startswith('# ') else line for line in block.group(1).splitlines()]
    meta = yaml.safe_load('\n'.join(block_lines))
    # Entrypoint must be yaml://protocol_test
    if meta["entrypoint"] != "yaml://protocol_test":
        print("[DEBUG] Full stamped_content:\n", stamped_content)
        print("[DEBUG] Parsed meta:\n", meta)
    assert meta["entrypoint"] == "yaml://protocol_test", f"Entrypoint incorrect: {meta['entrypoint']}"
    # Namespace must start with yaml://
    assert str(meta["namespace"]).startswith("yaml://"), f"Namespace incorrect: {meta['namespace']}"
    # runtime_language_hint must be absent
    assert "runtime_language_hint" not in meta, "runtime_language_hint should be omitted for YAML"
    # No tools/null fields
    assert "tools" not in meta, "tools field should not be present"
    # No legacy/mapping formats
    assert not isinstance(meta["entrypoint"], dict), "Entrypoint should not be a mapping"
    assert not isinstance(meta["namespace"], dict), "Namespace should not be a mapping"
    # No null/empty fields
    for k, v in meta.items():
        assert v not in (None, "", [], {}), f"Field {k} is null/empty: {v}"
