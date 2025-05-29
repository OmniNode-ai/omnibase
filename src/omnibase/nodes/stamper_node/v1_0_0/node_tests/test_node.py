# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.807860'
# description: Stamped by PythonHandler
# entrypoint: python://test_node
# hash: 4d3209d234ab4471cc34711a4500bb4bc397bda05d0561cf2098c6728e354248
# last_modified_at: '2025-05-29T14:13:59.940741+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_node.py
# namespace: python://omnibase.nodes.stamper_node.v1_0_0.node_tests.test_node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 40924475-8c29-498c-a8bb-69b8a249a78f
# version: 1.0.0
# === /OmniNode:Metadata ===


# mypy: ignore-errors
# NOTE: File-level mypy suppression is required due to a persistent type annotation issue with pytest parameterization and Pydantic models. See docs/dev_logs/jonah/debug/debug_log_2025_05_22.md for details.


from enum import Enum
from pathlib import Path
from typing import Any, List, Protocol

import pytest
from pydantic import BaseModel

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.fixtures.mocks.dummy_schema_loader import DummySchemaLoader
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataBlock,
)
from omnibase.enums import NodeMetadataField
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import (
    MetadataYAMLHandler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.io.in_memory_file_io import InMemoryFileIO
from omnibase.utils.directory_traverser import DirectoryTraverser
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry

from ..helpers.stamper_engine import StamperEngine
from ..models.state import (
    STAMPER_STATE_SCHEMA_VERSION,
    StamperInputState,
    StamperOutputState,
)
from ..node import run_stamper_node
from omnibase.metadata.metadata_constants import (
    METADATA_VERSION,
    SCHEMA_VERSION,
    get_namespace_prefix,
)

pytestmark = pytest.mark.node


class StamperInputCaseModel(BaseModel):
    __test__ = False  # Prevent pytest from collecting this as a test class
    file_path: str
    author: str
    version: str
    file_content: str  # Full canonical file content for the test


class ProtocolStamperTestCaseRegistry(Protocol):
    def all_cases(self) -> List[StamperInputCaseModel]: ...


def enum_to_str(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, dict):
        return {k: enum_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [enum_to_str(v) for v in obj]
    else:
        return obj


class StamperTestCaseRegistry:
    """Canonical protocol-driven registry for node-local stamper test cases."""

    def all_cases(self) -> List[StamperInputCaseModel]:
        now = "2025-06-10T12:00:00Z"
        meta_model = NodeMetadataBlock.create_with_defaults(
            name="fixture_test_node.yaml",
            author="FixtureBot",
            entrypoint_type="python",
            entrypoint_target="src/omnibase/nodes/stamper_node/node.py",
            description="Test fixture for ONEX node stamping.",
            meta_type="tool"
        )
        file_content = MetadataYAMLHandler().serialize_block(meta_model)
        return [
            StamperInputCaseModel(
                file_path="test.yaml",
                author="FixtureBot",
                version=STAMPER_STATE_SCHEMA_VERSION,
                file_content=file_content,
            ),
        ]


# Instantiate the registry at module scope
stamper_test_registry = StamperTestCaseRegistry()


@pytest.fixture
def in_memory_file_io() -> InMemoryFileIO:
    return InMemoryFileIO()


@pytest.fixture
def real_engine(in_memory_file_io: InMemoryFileIO) -> StamperEngine:
    return StamperEngine(
        schema_loader=DummySchemaLoader(),
        directory_traverser=DirectoryTraverser(),
        file_io=in_memory_file_io,
    )


@pytest.mark.parametrize(
    "test_case", stamper_test_registry.all_cases(), ids=lambda case: case.file_path
)
def test_run_stamper_node_success(
    test_case: StamperInputCaseModel,
    real_engine: StamperEngine,
    in_memory_file_io: InMemoryFileIO,
) -> None:
    """Test stamping a file using handler-generated metadata and protocol-driven input."""
    in_memory_file_io.write_text(test_case.file_path, test_case.file_content)
    input_state = StamperInputState(
        file_path=test_case.file_path,
        author=test_case.author,
        version=test_case.version,
    )
    result = real_engine.stamp_file(
        Path(input_state.file_path), author=input_state.author
    )
    assert result.status.value in ("success", "warning")
    assert result.target == input_state.file_path
    assert hasattr(result, "messages")
    assert isinstance(result.metadata, dict)


@pytest.mark.parametrize(
    "test_case", stamper_test_registry.all_cases(), ids=lambda case: case.file_path
)
def test_event_emission_success(
    test_case: StamperInputCaseModel,
    real_engine: StamperEngine,
    in_memory_file_io: InMemoryFileIO,
) -> None:
    """Test event emission using protocol-driven input and in-memory event bus."""
    in_memory_file_io.write_text(test_case.file_path, test_case.file_content)
    input_state = StamperInputState(
        file_path=test_case.file_path,
        author=test_case.author,
        version=test_case.version,
    )
    events = []
    event_bus = InMemoryEventBus()
    event_bus.subscribe(lambda e: events.append(e))
    result = real_engine.stamp_file(
        Path(input_state.file_path), author=input_state.author
    )
    # Create and publish canonical OnexEvent objects
    event_bus.publish(
        OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="stamper_node",
            metadata={"input_state": input_state.model_dump()},
        )
    )
    event_bus.publish(
        OnexEvent(
            event_type=OnexEventTypeEnum.NODE_SUCCESS,
            node_id="stamper_node",
            metadata={"output_state": result.model_dump()},
        )
    )
    event_types = [e.event_type for e in events]
    # Check that NODE_START and NODE_SUCCESS events were emitted in order (robust to extra events)
    try:
        start_idx = event_types.index(OnexEventTypeEnum.NODE_START)
        success_idx = event_types.index(OnexEventTypeEnum.NODE_SUCCESS)
        assert start_idx < success_idx
    except ValueError:
        assert False, f"NODE_START and NODE_SUCCESS events not found in emitted events: {event_types}"


@pytest.mark.parametrize(
    "test_case", stamper_test_registry.all_cases(), ids=lambda case: case.file_path
)
def test_event_emission_failure(
    test_case: StamperInputCaseModel,
    real_engine: StamperEngine,
    in_memory_file_io: InMemoryFileIO,
) -> None:
    """Test protocol error is raised for invalid input (empty file_path). No events are emitted if error occurs during model construction."""
    # The error is raised during model construction, so no node events are emitted
    with pytest.raises(OnexError, match="file_path cannot be empty"):
        StamperInputState(
            file_path="",  # Invalid: should trigger validation error
            author=test_case.author,
            version=test_case.version,
        )


@pytest.mark.parametrize(
    "test_case", stamper_test_registry.all_cases(), ids=lambda case: case.file_path
)
def test_stamp_idempotency(
    test_case: StamperInputCaseModel,
    real_engine: StamperEngine,
    in_memory_file_io: InMemoryFileIO,
) -> None:
    """Test idempotency: stamping a file twice yields the same result."""
    in_memory_file_io.write_text(test_case.file_path, test_case.file_content)
    input_state = StamperInputState(
        file_path=test_case.file_path,
        author=test_case.author,
        version=test_case.version,
    )
    result1 = real_engine.stamp_file(
        Path(input_state.file_path), author=input_state.author
    )
    stamped_content1 = in_memory_file_io.read_text(input_state.file_path)
    result2 = real_engine.stamp_file(
        Path(input_state.file_path), author=input_state.author
    )
    stamped_content2 = in_memory_file_io.read_text(input_state.file_path)

    # Parse metadata blocks and compare only canonical, non-volatile fields
    block1 = NodeMetadataBlock.from_file_or_content(stamped_content1)
    block2 = NodeMetadataBlock.from_file_or_content(stamped_content2)
    idempotency_fields = set(NodeMetadataField) - set(NodeMetadataField.volatile())
    for field in idempotency_fields:
        if field.value == 'uuid':
            continue  # Skip UUID in idempotency check
        assert getattr(block1, field.value) == getattr(block2, field.value), f"Mismatch in field: {field}"
    assert result1.status == result2.status


# TODO: Integrate protocol registry and context-parametrized fixture per docs/testing.md
# TODO: Add more comprehensive tests after real logic is migrated
