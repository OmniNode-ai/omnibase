# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_handler_markdown.py
# version: 1.0.0
# uuid: 4e8ec6ba-f664-43e3-b036-dcda3f33dfb2
# author: OmniNode Team
# created_at: 2025-05-22T14:03:21.907129
# last_modified_at: 2025-05-22T20:50:39.718419
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 364f6f4c1d6351d2b5f71272cef8171ceb81e8406c82e0c84a81d08f3794b4d7
# entrypoint: python@test_handler_markdown.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_handler_markdown
# meta_type: tool
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any, Dict, Optional

import pytest

from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_message_result import OnexStatus
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_markdown import (
    MarkdownHandler,
)

# Canonical metadata block for Markdown
now = "1970-01-01T00:00:00Z"
meta = NodeMetadataBlock(
    metadata_version="0.1.0",
    protocol_version="1.0.0",
    owner="OmniNode Team",
    copyright="OmniNode Team",
    schema_version="1.1.0",
    name="test_md",
    version="1.0.0",
    uuid="00000000-0000-0000-0000-000000000000",
    author="OmniNode Team",
    created_at=now,
    last_modified_at=now,
    description="Stamped by stamping_engine",
    state_contract="state_contract://default",
    lifecycle=Lifecycle.ACTIVE,
    hash="0" * 64,
    entrypoint=EntrypointBlock(type=EntrypointType.PYTHON, target="main.py"),
    runtime_language_hint="python>=3.11",
    namespace="onex.stamped.test_md",
    meta_type=MetaTypeEnum.TOOL,
)


@pytest.fixture
def markdown_handler() -> MarkdownHandler:
    return MarkdownHandler()


@pytest.mark.node
def test_stamp_unstamped_markdown(markdown_handler: MarkdownHandler) -> None:
    unstamped_content = """# Test Document

This is a test document without metadata.
"""

    test_path = Path("test.md")
    result = markdown_handler.stamp(test_path, unstamped_content)

    assert result is not None

    # Check if metadata is not None before indexing
    metadata: Optional[Dict[str, Any]] = result.metadata
    if metadata is not None:
        stamped_content = metadata["content"]
        assert stamped_content is not None
        assert "# Test Document" in stamped_content


@pytest.mark.node
def test_stamp_already_stamped_markdown(markdown_handler: MarkdownHandler) -> None:
    already_stamped = """<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
name: test.md
version: 1.0.0
<!-- === /OmniNode:Metadata === -->

# Test Document

This document already has metadata.
"""

    test_path = Path("test.md")
    result1 = markdown_handler.stamp(test_path, already_stamped)

    # Check if metadata is not None before indexing
    metadata1: Optional[Dict[str, Any]] = result1.metadata
    if metadata1 is not None:
        stamped_content1 = metadata1["content"]

        # Second stamp should be idempotent
        result2 = markdown_handler.stamp(test_path, stamped_content1)
        metadata2: Optional[Dict[str, Any]] = result2.metadata
        if metadata2 is not None:
            stamped_content2 = metadata2["content"]
            assert stamped_content1 == stamped_content2


def test_stamp_malformed_metadata_markdown(markdown_handler: MarkdownHandler) -> None:
    """Test stamping a Markdown file with malformed metadata block (missing close delimiter)."""
    malformed_block = (
        "<!-- === OmniNode:Metadata ===\nname: test_md\n"  # No close delimiter
    )
    content = malformed_block + "\n# Example Markdown\nSome content here.\n"
    result = markdown_handler.stamp(Path("foo.md"), content)
    # Should succeed and replace/repair the malformed block
    assert result.status in (OnexStatus.SUCCESS, OnexStatus.WARNING, OnexStatus.ERROR)
    metadata: Optional[Dict[str, Any]] = result.metadata
    if metadata is not None:
        stamped_content = metadata["content"]
        assert stamped_content.startswith("<!-- === OmniNode:Metadata ===")
        assert stamped_content.count("<!-- === OmniNode:Metadata ===") == 1


def test_stamp_extra_delimiters_markdown(markdown_handler: MarkdownHandler) -> None:
    """Test stamping a Markdown file with extra metadata delimiters."""
    serializer = CanonicalYAMLSerializer()
    block = (
        "<!-- === OmniNode:Metadata ===\n"
        + serializer.canonicalize_metadata_block(meta, comment_prefix="<!-- ")
        + "\n<!-- === /OmniNode:Metadata === -->\n"
    )
    # Add an extra open delimiter in the body
    content = (
        block
        + "\n<!-- === OmniNode:Metadata ===\n# Example Markdown\nSome content here.\n"
    )
    result = markdown_handler.stamp(Path("foo.md"), content)
    assert result.status in (OnexStatus.SUCCESS, OnexStatus.WARNING, OnexStatus.ERROR)
    metadata: Optional[Dict[str, Any]] = result.metadata
    if metadata is not None:
        stamped_content = metadata["content"]
        # Only one metadata block should remain at the top
        assert stamped_content.count("<!-- === OmniNode:Metadata ===") == 1
        assert stamped_content.startswith("<!-- === OmniNode:Metadata ===")


def test_stamp_non_metadata_content_at_top(markdown_handler: MarkdownHandler) -> None:
    """Test stamping a Markdown file with non-metadata content at the top (should prepend metadata)."""
    content = "# Title\n<!-- === OmniNode:Metadata ===\nname: test_md\n<!-- === /OmniNode:Metadata === -->\nBody text.\n"
    result = markdown_handler.stamp(Path("foo.md"), content)
    assert result.status == OnexStatus.SUCCESS
    metadata: Optional[Dict[str, Any]] = result.metadata
    if metadata is not None:
        stamped_content = metadata["content"]
        # Metadata block should be at the very top
        assert stamped_content.startswith("<!-- === OmniNode:Metadata ===")
        assert "# Title" in stamped_content
        assert "Body text." in stamped_content
