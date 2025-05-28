# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: stamper_test_registry_cases.py
# version: 1.0.0
# uuid: b3e1afea-3cf6-4c22-b220-4545c2bd17f4
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.765460
# last_modified_at: 2025-05-28T17:20:05.684336
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 1a42ac9c1b93fd81ef9cfdb75cdb31e5e08f5825f2c4f8f5ecf5b3cf70fee80e
# entrypoint: python@stamper_test_registry_cases.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.stamper_test_registry_cases
# meta_type: tool
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
        entrypoint=EntrypointBlock(type=EntrypointType.PYTHON, target="main.py"),
        namespace="omnibase.test",
        meta_type=MetaTypeEnum.TOOL,
        schema_version="1.0.0",
        version="1.0.0",
    )


# Canonical handlers
_yaml_handler = MetadataYAMLHandler()
_md_handler = MarkdownHandler()
_py_handler = PythonHandler()


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


STAMPER_TEST_CASES = []

# YAML
meta_yaml = build_metadata_block("test_yaml")
block_yaml = MetadataYAMLHandler().serialize_block(meta_yaml)
STAMPER_TEST_CASES.append(
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
block_md = MarkdownHandler().serialize_block(meta_md)
if not block_md.endswith("\n"):
    block_md += "\n"
md_body = "\n# Example Markdown\nSome content here.\n"
STAMPER_TEST_CASES.append(
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
block_py = PythonHandler().serialize_block(meta_py)
if not block_py.endswith("\n"):
    block_py += "\n"
py_body = "\ndef foo():\n    return 42\n"
STAMPER_TEST_CASES.append(
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
# Add negative/malformed test cases as explicit exceptions below, with clear comments.


def build_python_handler_test_case() -> ProtocolStamperTestCase:
    # TODO: Implement this function
    raise NotImplementedError("This function is not yet implemented")
