# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node.py
# version: 1.0.0
# uuid: 2df37627-d790-48bb-aabb-099b07e367f2
# author: OmniNode Team
# created_at: 2025-05-22T12:17:04.399436
# last_modified_at: 2025-05-22T20:50:39.717456
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 1789dd9797b246cf0958c85db3e9e7aa3309855477aa6bf8e64603a52fd411f4
# entrypoint: python@node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.node
# meta_type: tool
# === /OmniNode:Metadata ===


import logging
from pathlib import Path
from typing import Optional

from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtime.events.event_bus_in_memory import InMemoryEventBus
from omnibase.runtime.utils.onex_version_loader import OnexVersionLoader

from .helpers.stamper_engine import StamperEngine
from .models.state import StamperInputState, StamperOutputState
from .tests.mocks.dummy_schema_loader import DummySchemaLoader

logger = logging.getLogger(__name__)


def run_stamper_node(
    input_state: StamperInputState, event_bus: Optional[ProtocolEventBus] = None
) -> StamperOutputState:
    """
    Canonical ONEX node entrypoint for stamping metadata blocks into files.
    Emits NODE_START, NODE_SUCCESS, NODE_FAILURE events.
    Args:
        input_state: StamperInputState (must include version)
        event_bus: ProtocolEventBus (optional, defaults to InMemoryEventBus)
    Returns:
        StamperOutputState (version matches input_state.version)
    """
    if event_bus is None:
        event_bus = InMemoryEventBus()
    node_id = "stamper_node"
    event_bus.publish(
        OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id=node_id,
            metadata={"input_state": input_state.model_dump()},
        )
    )
    try:
        # Instantiate the canonical engine
        engine = StamperEngine(
            schema_loader=DummySchemaLoader(),
        )  # TODO: Inject real schema_loader if needed
        # Call the real stamping logic
        result = engine.stamp_file(
            Path(input_state.file_path), author=input_state.author
        )
        # Map OnexResultModel to StamperOutputState
        output = StamperOutputState(
            version=input_state.version,
            status=(
                result.status.value
                if hasattr(result.status, "value")
                else str(result.status)
            ),
            message=str(
                result.messages[0].summary
                if result.messages
                else (result.metadata.get("note") if result.metadata else "No message")
            ),  # Ensure message is always a str
        )
        event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_SUCCESS,
                node_id=node_id,
                metadata={
                    "input_state": input_state.model_dump(),
                    "output_state": output.model_dump(),
                },
            )
        )
        return output
    except Exception as exc:
        event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_FAILURE,
                node_id=node_id,
                metadata={
                    "input_state": input_state.model_dump(),
                    "error": str(exc),
                },
            )
        )
        raise


def main() -> None:
    """CLI entrypoint for standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(description="ONEX Stamper Node CLI")
    parser.add_argument("file_path", type=str, help="Path to file to stamp")
    parser.add_argument(
        "--author", type=str, default="OmniNode Team", help="Author name"
    )
    args = parser.parse_args()
    schema_version = OnexVersionLoader().get_onex_versions().schema_version
    input_state = StamperInputState(
        file_path=args.file_path, author=args.author, version=schema_version
    )
    # Use default event bus for CLI
    output = run_stamper_node(input_state)
    print(output.json(indent=2))


if __name__ == "__main__":
    main()
