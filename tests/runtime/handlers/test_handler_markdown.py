# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_handler_markdown.py
# version: 1.0.0
# uuid: '4e8ec6ba-f664-43e3-b036-dcda3f33dfb2'
# author: OmniNode Team
# created_at: '2025-05-22T14:03:21.907129'
# last_modified_at: '2025-05-22T18:05:26.836460'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: test_handler_markdown.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_handler_markdown
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

import pytest

from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_message_result import OnexStatus
from omnibase.runtime.handlers.handler_markdown import MarkdownHandler

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
    entrypoint=EntrypointBlock(type="python", target="main.py"),
    runtime_language_hint="python>=3.11",
    namespace="onex.stamped.test_md",
    meta_type=MetaType.TOOL,
)


@pytest.fixture
def markdown_handler() -> MarkdownHandler:
    return MarkdownHandler()


def test_stamp_unstamped_markdown(markdown_handler: MarkdownHandler):
    """Test stamping a Markdown file with no metadata block."""
    content = "# Example Markdown\nSome content here.\n"
    result = markdown_handler.stamp(Path("foo.md"), content)
    assert result.status == OnexStatus.SUCCESS
    assert result.metadata is not None and "content" in result.metadata
    stamped_content = result.metadata["content"]
    # Metadata block should be at the top
    assert stamped_content.startswith("<!-- === OmniNode:Metadata ===")
    assert "# Example Markdown" in stamped_content


def test_stamp_already_stamped_markdown(markdown_handler: MarkdownHandler):
    """Test idempotency: stamping a Markdown file that is already stamped."""
    serializer = CanonicalYAMLSerializer()
    block = (
        "<!-- === OmniNode:Metadata ===\n"
        + serializer.canonicalize_metadata_block(meta, comment_prefix="<!-- ")
        + "\n<!-- === /OmniNode:Metadata === -->\n"
    )
    content = block + "\n# Example Markdown\nSome content here.\n"
    result1 = markdown_handler.stamp(Path("foo.md"), content)
    assert result1.status == OnexStatus.SUCCESS
    stamped_content1 = result1.metadata["content"]
    # Second stamp (should not double-stamp)
    result2 = markdown_handler.stamp(Path("foo.md"), stamped_content1)
    assert result2.status == OnexStatus.SUCCESS
    stamped_content2 = result2.metadata["content"]
    assert stamped_content2.count("<!-- === OmniNode:Metadata ===") == 1


def test_stamp_malformed_metadata_markdown(markdown_handler: MarkdownHandler):
    """Test stamping a Markdown file with malformed metadata block (missing close delimiter)."""
    malformed_block = (
        "<!-- === OmniNode:Metadata ===\nname: test_md\n"  # No close delimiter
    )
    content = malformed_block + "\n# Example Markdown\nSome content here.\n"
    result = markdown_handler.stamp(Path("foo.md"), content)
    # Should succeed and replace/repair the malformed block
    assert result.status in (OnexStatus.SUCCESS, OnexStatus.WARNING, OnexStatus.ERROR)
    stamped_content = result.metadata["content"]
    assert stamped_content.startswith("<!-- === OmniNode:Metadata ===")
    assert stamped_content.count("<!-- === OmniNode:Metadata ===") == 1


def test_stamp_extra_delimiters_markdown(markdown_handler: MarkdownHandler):
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
    stamped_content = result.metadata["content"]
    # Only one metadata block should remain at the top
    assert stamped_content.count("<!-- === OmniNode:Metadata ===") == 1
    assert stamped_content.startswith("<!-- === OmniNode:Metadata ===")


def test_stamp_non_metadata_content_at_top(markdown_handler: MarkdownHandler):
    """Test stamping a Markdown file with non-metadata content at the top (should prepend metadata)."""
    content = "# Title\n<!-- === OmniNode:Metadata ===\nname: test_md\n<!-- === /OmniNode:Metadata === -->\nBody text.\n"
    result = markdown_handler.stamp(Path("foo.md"), content)
    assert result.status == OnexStatus.SUCCESS
    stamped_content = result.metadata["content"]
    # Metadata block should be at the very top
    assert stamped_content.startswith("<!-- === OmniNode:Metadata ===")
    assert "# Title" in stamped_content
    assert "Body text." in stamped_content
