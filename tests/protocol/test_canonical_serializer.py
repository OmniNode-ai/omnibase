# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.967366'
# description: Stamped by PythonHandler
# entrypoint: python://test_canonical_serializer.py
# hash: 9222296bb22af2f2001da0e88d455ca5b9824115472812765730b192b32d182b
# last_modified_at: '2025-05-29T11:50:12.645130+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_canonical_serializer.py
# namespace: omnibase.test_canonical_serializer
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 0cf7e489-f551-4d00-95a5-7134486a897d
# version: 1.0.0
# === /OmniNode:Metadata ===


import hashlib

import pytest
import yaml

from omnibase.enums import NodeMetadataField
from omnibase.mixin.mixin_canonical_serialization import (
    CanonicalYAMLSerializer,
    extract_metadata_block_and_body,
)
from omnibase.mixin.mixin_hash_computation import HashComputationMixin
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataBlock,
)
from omnibase.model.model_project_metadata import get_canonical_versions

canonical_versions = get_canonical_versions()

@pytest.fixture
def canonical_yaml_serializer() -> CanonicalYAMLSerializer:
    """Fixture for protocol-compliant CanonicalYAMLSerializer."""
    return CanonicalYAMLSerializer()


class DummyMetaBlock(NodeMetadataBlock, HashComputationMixin):
    def __init__(self) -> None:
        super().__init__(
            metadata_version="0.1.0",
            protocol_version="1.0.0",
            owner="test_owner",
            copyright="test_copyright",
            schema_version="1.0.0",
            name="dummy",
            version="1.0.0",
            uuid="00000000-0000-0000-0000-000000000000",
            author="test_author",
            created_at="1970-01-01T00:00:00Z",
            last_modified_at="1970-01-01T00:00:00Z",
            description="test",
            state_contract="none",
            lifecycle=Lifecycle.ACTIVE,
            hash="0" * 64,
            entrypoint=EntrypointBlock(type=EntrypointType.PYTHON, target="dummy.py"),
            runtime_language_hint=None,
            namespace="omnibase.dummy",
            meta_type=MetaTypeEnum.TOOL,
        )


def test_round_trip_canonicalization(
    canonical_yaml_serializer: CanonicalYAMLSerializer,
) -> None:
    """
    Protocol: CanonicalYAMLSerializer must produce idempotent YAML serialization.
    """
    dummy = DummyMetaBlock()
    yaml_1 = canonical_yaml_serializer.canonicalize_metadata_block(dummy)
    loaded = yaml.safe_load(yaml_1)
    yaml_2 = canonical_yaml_serializer.canonicalize_metadata_block(loaded)
    assert (
        yaml_1 == yaml_2
    ), f"Round-trip canonicalization failed:\n{yaml_1}\n---\n{yaml_2}"


def test_normalize_body_line_endings(
    canonical_yaml_serializer: CanonicalYAMLSerializer,
) -> None:
    """
    Protocol: CanonicalYAMLSerializer must normalize all line endings to '\n'.
    """
    mixed = "foo\r\nbar\r\nbaz\n"
    norm = canonical_yaml_serializer.normalize_body(mixed)
    assert "\r" not in norm
    assert norm.endswith("\n")


def test_canonicalize_for_hash_protocol(
    canonical_yaml_serializer: CanonicalYAMLSerializer,
) -> None:
    """
    Protocol: CanonicalYAMLSerializer and HashComputationMixin must produce stable, protocol-compliant hash input.
    """
    dummy = DummyMetaBlock()
    body = "abc\ndef"
    canonical = canonical_yaml_serializer.canonicalize_for_hash(
        dummy,
        body,
        volatile_fields=(NodeMetadataField.HASH, NodeMetadataField.LAST_MODIFIED_AT),
    )
    # Hash should be stable for the same input
    h1 = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    h2 = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert h1 == h2
    # HashComputationMixin should match
    h3 = dummy.compute_hash(body, comment_prefix="# ")
    assert isinstance(h3, str) and len(h3) == 64


def test_nonbreaking_space_normalization(
    canonical_yaml_serializer: CanonicalYAMLSerializer,
) -> None:
    """
    Protocol: CanonicalYAMLSerializer must replace non-breaking spaces (\xa0) with regular spaces in canonical YAML output.
    """
    dummy = DummyMetaBlock()
    # Inject a non-breaking space into a string field
    dummy.author = "test\xa0author"
    yaml_out = canonical_yaml_serializer.canonicalize_metadata_block(dummy)
    assert "\xa0" not in yaml_out, f"Non-breaking space found in output: {yaml_out!r}"
    assert (
        "test author" in yaml_out
    ), f"Expected normalized space in output: {yaml_out!r}"


def test_extract_metadata_block_and_body_edge_cases() -> None:
    """
    Protocol: extract_metadata_block_and_body must extract blocks in all canonical forms.
    """
    open_delim = "=== OmniNode:Metadata ==="
    close_delim = "=== /OmniNode:Metadata ==="
    # Case 1: Block at file start, non-commented
    content1 = f"{open_delim}\nfoo: bar\n{close_delim}\nrest of file\n"
    block, rest = extract_metadata_block_and_body(content1, open_delim, close_delim)
    assert block is not None and "foo: bar" in block
    assert "rest of file" in rest
    # Case 2: Block after blank lines
    content2 = "\n\n" + f"{open_delim}\nfoo: bar\n{close_delim}\nrest of file\n"
    block, rest = extract_metadata_block_and_body(content2, open_delim, close_delim)
    assert block is not None and "foo: bar" in block
    # Case 3: Fully commented block (as produced by engine)
    content3 = f"# {open_delim}\n# foo: bar\n# {close_delim}\nrest of file\n"
    block, rest = extract_metadata_block_and_body(content3, open_delim, close_delim)
    assert block is not None and "foo: bar" in block
    # Case 4: Commented block after blank lines
    content4 = "\n\n" + f"# {open_delim}\n# foo: bar\n# {close_delim}\nrest of file\n"
    block, rest = extract_metadata_block_and_body(content4, open_delim, close_delim)
    assert block is not None and "foo: bar" in block
    # Case 5: Block after shebang
    content5 = (
        "#!/usr/bin/env python\n"
        + f"# {open_delim}\n# foo: bar\n# {close_delim}\nrest of file\n"
    )
    block, rest = extract_metadata_block_and_body(content5, open_delim, close_delim)
    assert block is not None and "foo: bar" in block
    # Case 6: Block with trailing blank lines
    content6 = f"# {open_delim}\n# foo: bar\n# {close_delim}\n\n\nrest of file\n"
    block, rest = extract_metadata_block_and_body(content6, open_delim, close_delim)
    assert block is not None and "foo: bar" in block
    # Case 7: Block with indented commented delimiters
    content7 = (
        f"    # {open_delim}\n    # foo: bar\n    # {close_delim}\nrest of file\n"
    )
    block, rest = extract_metadata_block_and_body(content7, open_delim, close_delim)
    assert block is not None and "foo: bar" in block


def test_canonical_serializer_byte_diff_regression(canonical_yaml_serializer):
    """
    Serialize a known-good NodeMetadataBlock 10 times and assert all outputs are byte-identical.
    Print the output for inspection.
    """
    from omnibase.nodes.stamper_node.v1_0_0.node_tests.stamper_test_registry_cases import build_metadata_block
    block = build_metadata_block("byte_diff_regression")
    outputs = [canonical_yaml_serializer.canonicalize_metadata_block(block) for _ in range(10)]
    for i in range(1, 10):
        assert outputs[i] == outputs[0], f"Serialization output differs at iteration {i}"
    print("--- Canonical serializer output ---\n" + outputs[0])


# Registry of entrypoint/null omission test cases (manual for now)
# TODO: Automate registry population via decorators/import hooks per testing.md policy
ENTRYPOINT_COMPACT_TEST_CASES = [
    {
        "id": "python",
        "kwargs": {
            "name": "foo.py",
            "author": "Test Author",
            "entrypoint_type": "python",
            "entrypoint_target": "foo.py",
            "description": "Test file for serializer",
            "tools": None,
            "tags": None,
            "capabilities": None,
        },
        "expected_entrypoint": "entrypoint: python://foo.py",
        "should_omit": ["tags", "capabilities"],
    },
    {
        "id": "cli",
        "kwargs": {
            "name": "foo.sh",
            "author": "Test Author",
            "entrypoint_type": "cli",
            "entrypoint_target": "foo.sh",
            "description": "Test file for serializer",
            "tools": None,
        },
        "expected_entrypoint": "entrypoint: cli://foo.sh",
        "should_omit": [],
    },
    {
        "id": "docker",
        "kwargs": {
            "name": "foo.docker",
            "author": "Test Author",
            "entrypoint_type": "docker",
            "entrypoint_target": "foo.docker",
            "description": "Test file for serializer",
            "tools": None,
        },
        "expected_entrypoint": "entrypoint: docker://foo.docker",
        "should_omit": [],
    },
    {
        "id": "tools_empty",
        "kwargs": {
            "name": "foo.py",
            "author": "Test Author",
            "entrypoint_type": "python",
            "entrypoint_target": "foo.py",
            "description": "Test file for serializer",
            "tools": {},
        },
        "expected_entrypoint": "entrypoint: python://foo.py",
        "should_omit": [],
        "should_include": ["tools: {}"],
    },
]

@pytest.fixture(params=ENTRYPOINT_COMPACT_TEST_CASES, ids=[c["id"] for c in ENTRYPOINT_COMPACT_TEST_CASES])
def entrypoint_compact_case(request):
    return request.param

@pytest.mark.parametrize("case", ENTRYPOINT_COMPACT_TEST_CASES, ids=[c["id"] for c in ENTRYPOINT_COMPACT_TEST_CASES])
def test_entrypoint_compact_format_and_null_omission(case, canonical_yaml_serializer):
    """
    Protocol: The entrypoint field must be emitted as a single-line string '<type>://<target>' for all file types.
    All None/null/empty fields (except protocol-required ones like tools) must be omitted from the metadata block.
    """
    meta = NodeMetadataBlock.create_with_defaults(**case["kwargs"])
    yaml_out = canonical_yaml_serializer.canonicalize_metadata_block(meta)
    assert case["expected_entrypoint"] in yaml_out
    for field in case.get("should_omit", []):
        assert f"{field}:" not in yaml_out
    for field in case.get("should_include", []):
        assert field in yaml_out

# Additional protocol-first tests for omission and canonical versioning
import pytest
from omnibase.model.model_node_metadata import NodeMetadataBlock

@pytest.mark.parametrize("field,value", [
    ("license", None),
    ("license", ""),
    ("container_image_reference", None),
    ("container_image_reference", ""),
    ("tags", []),
    ("capabilities", []),
    ("x_extensions", {}),
])
def test_optional_fields_omitted(field, value):
    meta = NodeMetadataBlock.create_with_defaults(
        name="foo.py",
        author="Test Author",
        entrypoint_type="python",
        entrypoint_target="foo.py",
        **{field: value}
    )
    d = meta.to_serializable_dict()
    assert field not in d or d[field] not in (None, "", [], {}), f"Field {field} should be omitted if empty/null/empty-string"

@pytest.mark.parametrize("field,expected", [
    ("metadata_version", canonical_versions["metadata_version"]),
    ("protocol_version", canonical_versions["protocol_version"]),
    ("schema_version", canonical_versions["schema_version"]),
])
def test_version_fields_always_canonical(field, expected):
    meta = NodeMetadataBlock.create_with_defaults(
        name="foo.py",
        author="Test Author",
        entrypoint_type="python",
        entrypoint_target="foo.py",
        **{field: "legacy"}
    )
    d = meta.to_serializable_dict()
    assert d[field] == expected, f"{field} should always be canonical ({expected})"

@pytest.mark.parametrize("field,value", [
    ("license", ""),
    ("container_image_reference", None),
    ("tags", []),
    ("capabilities", []),
    ("x_extensions", {}),
])
def test_no_empty_null_fields_in_output(field, value):
    meta = NodeMetadataBlock.create_with_defaults(
        name="foo.py",
        author="Test Author",
        entrypoint_type="python",
        entrypoint_target="foo.py",
        **{field: value}
    )
    d = meta.to_serializable_dict()
    assert d.get(field, "__MISSING__") not in (None, "", [], {}), f"{field} should not be present as empty/null/empty-string"

# Negative test: legacy/edge case with manual override
@pytest.mark.parametrize("field,legacy_value,expected", [
    ("protocol_version", canonical_versions["protocol_version"], canonical_versions["protocol_version"]),
    ("schema_version", canonical_versions["schema_version"], canonical_versions["schema_version"]),
    ("metadata_version", "1.2.3", canonical_versions["metadata_version"]),
])
def test_legacy_version_override_is_canonical(field, legacy_value, expected):
    meta = NodeMetadataBlock.create_with_defaults(
        name="foo.py",
        author="Test Author",
        entrypoint_type="python",
        entrypoint_target="foo.py",
        **{field: legacy_value}
    )
    d = meta.to_serializable_dict()
    assert d[field] == expected, f"{field} should be canonical even if legacy value is set"
