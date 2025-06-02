# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.588637'
# description: Stamped by PythonHandler
# entrypoint: python://test_handler_markdown
# hash: b5760522f3d42ef5b4b1f2a761b08648221485e009d44b5f260a26c0a475456a
# last_modified_at: '2025-05-29T14:14:00.751467+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_handler_markdown.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.runtime_tests.handler_tests.test_handler_markdown
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 4d6245a0-4026-4be9-81cf-94bc58d4e021
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

import pytest
from pydantic import BaseModel

from omnibase.enums import NodeMetadataField
from omnibase.metadata.metadata_constants import MD_META_CLOSE, MD_META_OPEN
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


# Canonical test case model and registry for Markdown handler
class HandlerTestCaseModel(BaseModel):
    desc: str
    path: Path
    meta_model: NodeMetadataBlock
    block: str
    content: str


class ProtocolHandlerTestCaseRegistry(Protocol):
    def all_cases(self) -> list[HandlerTestCaseModel]: ...


class CanonicalMarkdownHandlerTestCaseRegistry:
    """Canonical protocol-driven registry for Markdown handler test cases."""

    def __init__(
        self, serializer: CanonicalYAMLSerializer, meta_open: str, meta_close: str
    ):
        self.serializer = serializer
        self.meta_open = meta_open
        self.meta_close = meta_close

    def all_cases(self) -> list[HandlerTestCaseModel]:
        meta_model = NodeMetadataBlock.create_with_defaults(
            name="canonical_test.md",
            author="TestBot",
            entrypoint_type="markdown",
            entrypoint_target="canonical_test",
            description="Canonical test block.",
            meta_type="tool",
        )
        # Emit a single HTML comment block with YAML inside (no '---' document markers)
        yaml_block = self.serializer.canonicalize_metadata_block(
            meta_model, comment_prefix=""
        )
        if yaml_block.startswith("---\n"):
            yaml_block = yaml_block[4:]
        if yaml_block.endswith("...\n"):
            yaml_block = yaml_block[:-4]
        block = f"{self.meta_open}\n{yaml_block}{self.meta_close}"
        content = block + "\n# Body content\n"
        return [
            HandlerTestCaseModel(
                desc="canonical_minimal",
                path=Path("canonical.md"),
                meta_model=meta_model,
                block=block,
                content=content,
            ),
        ]


@pytest.fixture
def serializer() -> CanonicalYAMLSerializer:
    return CanonicalYAMLSerializer()


@pytest.fixture
def markdown_handler() -> MarkdownHandler:
    return MarkdownHandler()


@pytest.fixture
def canonical_markdown_handler_registry(
    serializer,
) -> CanonicalMarkdownHandlerTestCaseRegistry:
    return CanonicalMarkdownHandlerTestCaseRegistry(
        serializer, MD_META_OPEN, MD_META_CLOSE
    )


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(c, id=c.desc)
        for c in CanonicalMarkdownHandlerTestCaseRegistry(
            CanonicalYAMLSerializer(), MD_META_OPEN, MD_META_CLOSE
        ).all_cases()
    ],
)
def test_round_trip_extraction_and_serialization(
    case: HandlerTestCaseModel, markdown_handler: MarkdownHandler
):
    handler = markdown_handler
    block_obj = handler.extract_block(case.path, case.content)
    if isinstance(block_obj, tuple):
        meta_model = block_obj[0]
    else:
        meta_model = block_obj.metadata
    assert meta_model is not None, f"Failed to extract block for {case.desc}"
    reserialized = handler.serialize_block(meta_model)
    block_obj2 = handler.extract_block(case.path, reserialized)
    if isinstance(block_obj2, tuple):
        meta_model2 = block_obj2[0]
    else:
        meta_model2 = block_obj2.metadata
    assert (
        meta_model2 is not None
    ), f"Failed to extract block after round-trip for {case.desc}"
    assert (
        meta_model.model_dump() == meta_model2.model_dump()
    ), f"Model mismatch after round-trip for {case.desc}"


def test_protocol_fields_on_stamped_markdown(
    markdown_handler: MarkdownHandler, tmp_path
):
    """
    Protocol: Stamped Markdown file must have correct entrypoint, namespace, and no runtime_language_hint/tools/null fields.
    """
    test_file = tmp_path / "protocol_test.md"
    content = """# Protocol Test\n\nkey: value\n"""
    result = markdown_handler.stamp(test_file, content)
    assert result.status in (
        OnexStatus.SUCCESS,
        OnexStatus.WARNING,
    ), f"Stamping failed: {result.messages}"
    stamped_content = result.metadata["content"]
    import re

    import yaml

    # Extract YAML block from inside the HTML comment block
    block = re.search(
        rf"{MD_META_OPEN}\n(.*?)(?:\n)?{MD_META_CLOSE}", stamped_content, re.DOTALL
    )
    assert block, "No metadata block found"
    meta = yaml.safe_load(block.group(1))
    # Entrypoint must be markdown://protocol_test
    if meta[NodeMetadataField.ENTRYPOINT.value] != "markdown://protocol_test":
        print("[DEBUG] Full stamped_content:\n", stamped_content)
        print("[DEBUG] Parsed meta:\n", meta)
    assert (
        meta[NodeMetadataField.ENTRYPOINT.value] == "markdown://protocol_test"
    ), f"Entrypoint incorrect: {meta[NodeMetadataField.ENTRYPOINT.value]}"
    # Namespace must start with markdown://
    assert str(meta[NodeMetadataField.NAMESPACE.value]).startswith(
        "markdown://"
    ), f"Namespace incorrect: {meta[NodeMetadataField.NAMESPACE.value]}"
    # runtime_language_hint must be absent
    assert (
        NodeMetadataField.RUNTIME_LANGUAGE_HINT.value not in meta
    ), "runtime_language_hint should be omitted for Markdown"
    # No tools/null fields
    assert (
        NodeMetadataField.TOOLS.value not in meta
    ), "tools field should not be present"
    # No legacy/mapping formats
    assert not isinstance(
        meta[NodeMetadataField.ENTRYPOINT.value], dict
    ), "Entrypoint should not be a mapping"
    assert not isinstance(
        meta[NodeMetadataField.NAMESPACE.value], dict
    ), "Namespace should not be a mapping"
    # No null/empty fields
    for k, v in meta.items():
        assert v not in (None, "", [], {}), f"Field {k} is null/empty: {v}"
