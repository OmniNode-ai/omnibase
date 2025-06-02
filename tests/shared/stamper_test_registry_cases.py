# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.765460'
# description: Stamped by PythonHandler
# entrypoint: python://stamper_test_registry_cases
# hash: 0dc7d10a38ed15f422ac6527956c0f260ef83034c321b2d6700370d5699655b8
# last_modified_at: '2025-05-29T14:13:59.906706+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: stamper_test_registry_cases.py
# namespace: python://omnibase.nodes.stamper_node.v1_0_0.node_tests.stamper_test_registry_cases
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: b3e1afea-3cf6-4c22-b220-4545c2bd17f4
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Any, Optional

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import FileTypeEnum
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_message_result import OnexStatus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_markdown import (
    MarkdownHandler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import (
    MetadataYAMLHandler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_python import PythonHandler

from .protocol_stamper_test_case import ProtocolStamperTestCase

# Utility to build a fully populated NodeMetadataBlock


def build_metadata_block(name: str) -> NodeMetadataBlock:
    return NodeMetadataBlock(
        name=name,
        uuid="123e4567-e89b-12d3-a456-426614174000",
        author="Test Author",
        created_at="2025-01-01T00:00:00Z",
        last_modified_at="2025-01-01T00:00:00Z",
        description="desc",
        state_contract="contract-1",
        lifecycle=Lifecycle.ACTIVE,
        hash="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        entrypoint=EntrypointBlock(type="python", target="main.py"),
        namespace="omnibase.test",
        meta_type=MetaTypeEnum.TOOL,
        schema_version="1.0.0",
        version="1.0.0",
    )


# Canonical handlers
_yaml_handler = MetadataYAMLHandler(event_bus=InMemoryEventBus())
_md_handler = MarkdownHandler(event_bus=InMemoryEventBus())
_py_handler = PythonHandler(event_bus=InMemoryEventBus())


def render_content(meta_block: NodeMetadataBlock, file_type: FileTypeEnum) -> str:
    if file_type == FileTypeEnum.YAML:
        return _yaml_handler.serialize_block(meta_block)
    elif file_type == FileTypeEnum.MARKDOWN:
        return _md_handler.serialize_block(meta_block)
    elif file_type == FileTypeEnum.PYTHON:
        return _py_handler.serialize_block(meta_block)
    else:
        raise OnexError(
            f"Unsupported file type: {file_type}", CoreErrorCode.INVALID_PARAMETER
        )


# Registry-driven test cases
class RealStamperTestCase(ProtocolStamperTestCase):
    def __init__(
        self,
        id: str,
        file_type: FileTypeEnum,
        file_path: str,
        file_content: str,
        expected_status: OnexStatus,
        expected_metadata: Optional[Any] = None,
        description: Optional[str] = None,
    ) -> None:
        self.id = id
        self.file_type = file_type
        self.file_path = file_path
        self.file_content = file_content
        self.expected_status = expected_status
        self.expected_metadata = expected_metadata
        self.description = description


def get_stamper_test_cases(event_bus):
    cases = []
    # YAML
    meta_yaml = build_metadata_block("test_yaml")
    block_yaml = MetadataYAMLHandler(event_bus=event_bus).serialize_block(
        meta_yaml, event_bus=event_bus
    )
    cases.append(
        RealStamperTestCase(
            id="yaml_minimal_real",
            file_type=FileTypeEnum.YAML,
            file_path="test.yaml",
            file_content=block_yaml,
            expected_status=OnexStatus.SUCCESS,
            expected_metadata=None,
            description="Canonical YAML metadata block rendered by handler.",
        )
    )
    # Markdown
    meta_md = build_metadata_block("test_md")
    block_md = MarkdownHandler(event_bus=event_bus).serialize_block(
        meta_md, event_bus=event_bus
    )
    if not block_md.endswith("\n"):
        block_md += "\n"
    md_body = "\n# Example Markdown\nSome content here.\n"
    cases.append(
        RealStamperTestCase(
            id="markdown_minimal_real",
            file_type=FileTypeEnum.MARKDOWN,
            file_path="test.md",
            file_content=block_md + md_body,
            expected_status=OnexStatus.SUCCESS,
            expected_metadata=None,
            description="Canonical Markdown metadata block rendered by handler.",
        )
    )
    # Python
    meta_py = build_metadata_block("test_py")
    block_py = PythonHandler(event_bus=event_bus).serialize_block(
        meta_py, event_bus=event_bus
    )
    if not block_py.endswith("\n"):
        block_py += "\n"
    py_body = "\ndef foo():\n    return 42\n"
    cases.append(
        RealStamperTestCase(
            id="python_minimal_real",
            file_type=FileTypeEnum.PYTHON,
            file_path="test.py",
            file_content=block_py + py_body,
            expected_status=OnexStatus.SUCCESS,
            expected_metadata=None,
            description="Canonical Python metadata block rendered by handler.",
        )
    )
    return cases


def build_python_handler_test_case() -> ProtocolStamperTestCase:
    # TODO: Implement this function
    raise NotImplementedError("This function is not yet implemented")
