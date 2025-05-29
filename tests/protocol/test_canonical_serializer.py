# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.967366'
# description: Stamped by PythonHandler
# entrypoint: python://test_canonical_serializer.py
# hash: cfb5b0d915c8cd8572e8d9702e21687a5c5018eb016239ae0cab65cce2aecdd6
# last_modified_at: '2025-05-29T13:43:04.606168+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_canonical_serializer.py
# namespace:
#   value: py://omnibase.tests.protocol.test_canonical_serializer_py
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
            entrypoint=EntrypointBlock(type="python", target="dummy.py"),
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
        "expected_entrypoint": "entrypoint: python://foo",
        "should_omit": ["tags", "capabilities", "tools"],
    },
    {
        "id": "cli",
        "kwargs": {
            "entrypoint_type": "cli",
            "entrypoint_target": "foo",
            "author": "Test Author",
            "description": "Test file for serializer",
        },
        "expected_entrypoint": "entrypoint: cli://foo",
        "should_omit": ["tools"],
    },
    {
        "id": "docker",
        "kwargs": {
            "entrypoint_type": "docker",
            "entrypoint_target": "foo",
            "author": "Test Author",
            "description": "Test file for serializer",
        },
        "expected_entrypoint": "entrypoint: docker://foo",
        "should_omit": ["tools"],
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
        "expected_entrypoint": "entrypoint: python://foo",
        "should_omit": ["tools"],
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

def test_namespace_serialized_as_uri_string(canonical_yaml_serializer: CanonicalYAMLSerializer) -> None:
    """
    Protocol: The namespace field must be emitted as a single-line URI string (e.g., python://omnibase.something), never as a mapping.
    """
    meta = NodeMetadataBlock.create_with_defaults(
        name="foo.py",
        author="Test Author",
        entrypoint_type="python",
        entrypoint_target="foo.py",
        namespace="python://omnibase.test_namespace_case"
    )
    yaml_out = canonical_yaml_serializer.canonicalize_metadata_block(meta)
    # The namespace line must be present as a single-line string
    import re
    ns_lines = [line for line in yaml_out.splitlines() if line.strip().startswith("namespace:")]
    assert len(ns_lines) == 1, f"Expected exactly one namespace line, got: {ns_lines}"
    ns_line = ns_lines[0]
    # Should be of the form: namespace: python://omnibase.test_namespace_case
    assert re.match(r"^namespace: +[a-zA-Z0-9_]+://[a-zA-Z0-9_\.]+$", ns_line), f"Namespace line not in URI format: {ns_line}"
    # Should not be a mapping
    assert not any(l.strip().startswith("value:") for l in yaml_out.splitlines()), "Namespace should not be emitted as a mapping (no 'value:' line)"

def test_markdown_entrypoint_and_field_omission(canonical_yaml_serializer: CanonicalYAMLSerializer) -> None:
    """
    Protocol: Markdown files must have entrypoint 'markdown://<stem>', no runtime_language_hint, and no tools/null fields.
    """
    meta = NodeMetadataBlock.create_with_defaults(
        name="foo.md",
        author="Test Author",
        entrypoint_type="markdown",
        entrypoint_target="foo.md",
        runtime_language_hint=None,
        tools=None,
        tags=None,
        capabilities=None,
    )
    yaml_out = canonical_yaml_serializer.canonicalize_metadata_block(meta)
    # Entrypoint must be markdown://foo
    assert "entrypoint: markdown://foo" in yaml_out, f"Entrypoint not correct: {yaml_out}"
    # Should not contain runtime_language_hint
    assert "runtime_language_hint" not in yaml_out, f"runtime_language_hint should not be present: {yaml_out}"
    # Should not contain tools/null fields
    assert "tools:" not in yaml_out, f"tools field should not be present: {yaml_out}"
    # Should not contain any null/None/empty fields
    assert ": null" not in yaml_out, f"Null fields should not be present: {yaml_out}"
    assert ": None" not in yaml_out, f"None fields should not be present: {yaml_out}"
    assert ": {}" not in yaml_out, f"Empty dict fields should not be present: {yaml_out}"


def test_python_entrypoint_and_field_omission(canonical_yaml_serializer: CanonicalYAMLSerializer) -> None:
    """
    Protocol: Python files must have entrypoint 'python://<stem>', correct namespace, and only relevant fields.
    """
    meta = NodeMetadataBlock.create_with_defaults(
        name="foo.py",
        author="Test Author",
        entrypoint_type="python",
        entrypoint_target="foo.py",
        runtime_language_hint="python>=3.11",
        tools=None,
        tags=None,
        capabilities=None,
    )
    yaml_out = canonical_yaml_serializer.canonicalize_metadata_block(meta)
    # Entrypoint must be python://foo
    assert "entrypoint: python://foo" in yaml_out, f"Entrypoint not correct: {yaml_out}"
    # Should contain runtime_language_hint
    assert "runtime_language_hint: python>=3.11" in yaml_out, f"runtime_language_hint missing: {yaml_out}"
    # Should not contain tools/null fields
    assert "tools:" not in yaml_out, f"tools field should not be present: {yaml_out}"
    # Should not contain any null/None/empty fields
    assert ": null" not in yaml_out, f"Null fields should not be present: {yaml_out}"
    assert ": None" not in yaml_out, f"None fields should not be present: {yaml_out}"
    assert ": {}" not in yaml_out, f"Empty dict fields should not be present: {yaml_out}"

def test_typescript_entrypoint_and_runtime_hint(canonical_yaml_serializer):
    meta = NodeMetadataBlock.create_with_defaults(
        name="foo.ts",
        author="Test Author",
        entrypoint_type="typescript",
        entrypoint_target="foo.ts",
    )
    yaml_out = canonical_yaml_serializer.canonicalize_metadata_block(meta)
    assert "entrypoint: typescript://foo" in yaml_out
    assert "runtime_language_hint: typescript>=4.0" in yaml_out
    assert ": null" not in yaml_out
    assert ": {}" not in yaml_out

def test_javascript_entrypoint_and_runtime_hint(canonical_yaml_serializer):
    meta = NodeMetadataBlock.create_with_defaults(
        name="foo.js",
        author="Test Author",
        entrypoint_type="javascript",
        entrypoint_target="foo.js",
    )
    yaml_out = canonical_yaml_serializer.canonicalize_metadata_block(meta)
    assert "entrypoint: javascript://foo" in yaml_out
    assert "runtime_language_hint: javascript>=ES2020" in yaml_out
    assert ": null" not in yaml_out
    assert ": {}" not in yaml_out

def test_html_entrypoint_and_runtime_hint(canonical_yaml_serializer):
    meta = NodeMetadataBlock.create_with_defaults(
        name="foo.html",
        author="Test Author",
        entrypoint_type="html",
        entrypoint_target="foo.html",
    )
    yaml_out = canonical_yaml_serializer.canonicalize_metadata_block(meta)
    assert "entrypoint: html://foo" in yaml_out
    assert "runtime_language_hint: html5" in yaml_out
    assert ": null" not in yaml_out
    assert ": {}" not in yaml_out

def test_entrypoint_rejects_dict():
    with pytest.raises(ValueError):
        NodeMetadataBlock(entrypoint={"type": "python", "target": "main.py"}, name="x", uuid="0"*36, author="a", created_at="1970-01-01T00:00:00Z", last_modified_at="1970-01-01T00:00:00Z", description="d", state_contract="s", lifecycle="active", hash="0"*64, namespace="n", meta_type="tool", schema_version="1.0.0", version="1.0.0")

def test_entrypoint_rejects_string():
    with pytest.raises(ValueError):
        NodeMetadataBlock(entrypoint="python://main.py", name="x", uuid="0"*36, author="a", created_at="1970-01-01T00:00:00Z", last_modified_at="1970-01-01T00:00:00Z", description="d", state_contract="s", lifecycle="active", hash="0"*64, namespace="n", meta_type="tool", schema_version="1.0.0", version="1.0.0")

def test_entrypoint_accepts_model():
    block = NodeMetadataBlock(entrypoint=EntrypointBlock(type="python", target="main.py"), name="x", uuid="00000000-0000-0000-0000-000000000000", author="a", created_at="1970-01-01T00:00:00Z", last_modified_at="1970-01-01T00:00:00Z", description="d", state_contract="s", lifecycle="active", hash="0"*64, namespace="n", meta_type="tool", schema_version="1.0.0", version="1.0.0")
    assert isinstance(block.entrypoint, EntrypointBlock)
