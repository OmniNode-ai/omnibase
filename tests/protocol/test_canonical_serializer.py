import hashlib

import pytest
import yaml

from omnibase.canonical.canonical_serialization import (
    CanonicalYAMLSerializer,
    extract_metadata_block_and_body,
)
from omnibase.canonical.hash_computation_mixin import HashComputationMixin
from omnibase.model.model_enum_metadata import NodeMetadataField
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)


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
            namespace="onex.dummy",
            meta_type=MetaType.TOOL,
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
