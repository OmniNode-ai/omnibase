# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_node.py
# version: 1.0.0
# uuid: 78d37ad6-56ab-4c7c-abeb-a701d87b6e93
# author: OmniNode Team
# created_at: 2025-05-22T14:03:21.901881
# last_modified_at: 2025-05-22T20:50:39.722188
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 367453987f7d43084e73c92c475eed36400a9583d2e52d442c2d0c68249244ed
# entrypoint: python@test_node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_node
# meta_type: tool
# === /OmniNode:Metadata ===


from enum import Enum
from pathlib import Path
from typing import List, Protocol

import pytest
from pydantic import BaseModel

from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.nodes.stamper_node.helpers.stamper_engine import StamperEngine
from omnibase.nodes.stamper_node.models.state import StamperInputState
from omnibase.nodes.stamper_node.node import run_stamper_node
from omnibase.runtime.events.event_bus_in_memory import InMemoryEventBus
from omnibase.runtime.handlers.handler_metadata_yaml import MetadataYAMLHandler
from omnibase.utils.directory_traverser import DirectoryTraverser
from omnibase.utils.in_memory_file_io import InMemoryFileIO

pytestmark = pytest.mark.node


class StamperInputCaseModel(BaseModel):
    __test__ = False  # Prevent pytest from collecting this as a test class
    file_path: str
    author: str
    version: str
    file_content: str  # Full canonical file content for the test


class ProtocolStamperTestCaseRegistry(Protocol):
    def all_cases(self) -> List[StamperInputCaseModel]: ...


def enum_to_str(obj):
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
        meta_model = NodeMetadataBlock(
            schema_version="0.1.0",
            name="fixture_test_node",
            version="1.0.0",
            uuid="f1e2d3c4-5678-4abc-9def-abcdefabcdef",
            author="FixtureBot",
            created_at=now,
            last_modified_at=now,
            description="Test fixture for ONEX node stamping.",
            state_contract="state_contract://stamper_node_contract.yaml",
            lifecycle=Lifecycle.DRAFT,
            hash="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            entrypoint=EntrypointBlock(
                type="python", target="src/omnibase/nodes/stamper_node/node.py"
            ),
            namespace="onex.nodes.stamper_node.fixture",
            meta_type=MetaType.TOOL,
            runtime_language_hint="python>=3.11",
            tags=["fixture", "test", "stamper"],
            protocols_supported=[],
            base_class=[],
            dependencies=[],
            environment=[],
            license="Apache-2.0",
        )
        file_content = MetadataYAMLHandler().serialize_block(meta_model)
        return [
            StamperInputCaseModel(
                file_path="test.yaml",
                author="FixtureBot",
                version="1.0.0",
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
    class DummySchemaLoader:
        def load_schema(self, *args, **kwargs):
            return {}

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
            payload={"input_state": input_state.model_dump()},
        )
    )
    event_bus.publish(
        OnexEvent(
            event_type=OnexEventTypeEnum.NODE_SUCCESS,
            node_id="stamper_node",
            payload={"output_state": result.model_dump()},
        )
    )
    event_types = [e.event_type for e in events]
    assert OnexEventTypeEnum.NODE_START in event_types
    assert OnexEventTypeEnum.NODE_SUCCESS in event_types


@pytest.mark.parametrize(
    "test_case", stamper_test_registry.all_cases(), ids=lambda case: case.file_path
)
def test_event_emission_failure(
    test_case: StamperInputCaseModel,
    monkeypatch: pytest.MonkeyPatch,
    real_engine: StamperEngine,
    in_memory_file_io: InMemoryFileIO,
) -> None:
    """Test event emission on failure using protocol-driven input and in-memory event bus."""
    in_memory_file_io.write_text(test_case.file_path, test_case.file_content)
    input_state = StamperInputState(
        file_path=test_case.file_path,
        author=test_case.author,
        version=test_case.version,
    )

    def fail_output(*args: object, **kwargs: object) -> None:
        raise RuntimeError("Simulated failure")

    events = []
    event_bus = InMemoryEventBus()
    event_bus.subscribe(lambda e: events.append(e))
    monkeypatch.setattr(
        "omnibase.nodes.stamper_node.node.StamperOutputState", fail_output
    )
    with pytest.raises(RuntimeError, match="Simulated failure"):
        run_stamper_node(input_state, event_bus=event_bus)
    event_types = [e.event_type for e in events]
    assert event_types[0] == OnexEventTypeEnum.NODE_START
    assert event_types[-1] == OnexEventTypeEnum.NODE_FAILURE


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
    assert stamped_content1 == stamped_content2
    assert result1.status == result2.status


# TODO: Integrate protocol registry and context-parametrized fixture per docs/testing.md
# TODO: Add more comprehensive tests after real logic is migrated
