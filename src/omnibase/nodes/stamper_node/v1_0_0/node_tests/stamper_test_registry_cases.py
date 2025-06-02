# === OmniNode:Metadata ===
# This file has been moved to tests/shared/stamper_test_registry_cases.py
# It is now an import-only stub for backward compatibility.
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
from tests.shared.stamper_test_registry_cases import (
    RealStamperTestCase,
    get_stamper_test_cases,
)

from .protocol_stamper_test_case import ProtocolStamperTestCase

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


def build_python_handler_test_case() -> ProtocolStamperTestCase:
    # TODO: Implement this function
    raise NotImplementedError("This function is not yet implemented")
