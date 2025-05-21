# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: main.py
# version: 1.0.0
# uuid: 2a1b3c4d-5678-4abc-9def-1234567890cd
# author: OmniNode Team
# created_at: 2025-06-10T12:00:00Z
# last_modified_at: 2025-06-10T12:00:00Z
# description: Canonical entrypoint for the ONEX stamper node.
# state_contract: state_contract://stamper_node_contract.yaml
# lifecycle: draft
# hash: <TO_BE_COMPUTED>
# entrypoint: {'type': 'python', 'target': 'src/main.py'}
# runtime_language_hint: python>=3.11
# namespace: omnibase.nodes.stamper_node
# meta_type: tool
# === /OmniNode:Metadata ===

import logging
from pathlib import Path
from typing import List, Optional, Literal

from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader
from omnibase.protocol.protocol_stamper_engine import ProtocolStamperEngine
from omnibase.runtime.filesystem.directory_traverser import DirectoryTraverser
from omnibase.runtime.io.in_memory_file_io import InMemoryFileIO
from omnibase.runtime.utils.onex_version_loader import OnexVersionLoader

from omnibase.nodes.stamper_node.src.helpers.handlers.handler_registry import FileTypeHandlerRegistry
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.runtime.events.event_bus_in_memory import InMemoryEventBus
from omnibase.runtime.protocol.protocol_event_bus import ProtocolEventBus

logger = logging.getLogger(__name__)

class StamperEngine(ProtocolStamperEngine):
    MAX_FILE_SIZE = 5 * 1024 * 1024

    def __init__(
        self,
        schema_loader: ProtocolSchemaLoader,
        directory_traverser: Optional[DirectoryTraverser] = None,
        file_io: Optional[InMemoryFileIO] = None,
        handler_registry: Optional[FileTypeHandlerRegistry] = None,
    ) -> None:
        self.schema_loader = schema_loader
        self.directory_traverser = directory_traverser or DirectoryTraverser()
        self.file_io = file_io or InMemoryFileIO()
        logger = logging.getLogger("omnibase.nodes.stamper_node.engine")
        if handler_registry is None:
            handler_registry = FileTypeHandlerRegistry()
            handler_registry.register_all_handlers()
        self.handler_registry = handler_registry
        logger.debug(
            f"StamperEngine initialized with handled extensions: {self.handler_registry.handled_extensions()}"
        )

    def stamp_file(
        self,
        path: Path,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
        author: str = "OmniNode Team",
        **kwargs: object,
    ) -> OnexResultModel:
        # ... migrate logic from stamper_engine.py, update for modular helpers ...
        pass  # TODO: Complete migration

    def process_directory(
        self,
        directory: Path,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        recursive: bool = True,
        dry_run: bool = False,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        ignore_file: Optional[Path] = None,
        author: str = "OmniNode Team",
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
    ) -> OnexResultModel:
        # ... migrate logic from stamper_engine.py, update for modular helpers ...
        pass  # TODO: Complete migration


# TODO: Add ONEX node entrypoint function (input_state -> output_state)

import sys
from typing import Any, Dict

from pydantic import BaseModel

# Remove commented stub imports
from .models.state import StamperInputState, StamperOutputState


def run_stamper_node(input_state: StamperInputState, event_bus: ProtocolEventBus = None) -> StamperOutputState:
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
    node_id = "stamper_node"  # Could be parameterized or read from metadata
    # Emit NODE_START
    event_bus.publish(OnexEvent(
        event_type=OnexEventTypeEnum.NODE_START,
        node_id=node_id,
        metadata={"input_state": input_state.model_dump()}
    ))
    try:
        # TODO: Migrate and refactor logic from stamper_engine.py
        # For now, return a stub output
        output = StamperOutputState(
            version=input_state.version,
            status="success",
            message=f"Stub: would stamp file {input_state.file_path} as {input_state.author}",
        )
        # Emit NODE_SUCCESS
        event_bus.publish(OnexEvent(
            event_type=OnexEventTypeEnum.NODE_SUCCESS,
            node_id=node_id,
            metadata={
                "input_state": input_state.model_dump(),
                "output_state": output.model_dump(),
            }
        ))
        return output
    except Exception as exc:
        # Emit NODE_FAILURE
        event_bus.publish(OnexEvent(
            event_type=OnexEventTypeEnum.NODE_FAILURE,
            node_id=node_id,
            metadata={
                "input_state": input_state.model_dump(),
                "error": str(exc),
            }
        ))
        raise


def main():
    """CLI entrypoint for standalone execution."""
    import argparse
    from omnibase.runtime.utils.onex_version_loader import OnexVersionLoader

    parser = argparse.ArgumentParser(description="ONEX Stamper Node CLI")
    parser.add_argument("file_path", type=str, help="Path to file to stamp")
    parser.add_argument(
        "--author", type=str, default="OmniNode Team", help="Author name"
    )
    args = parser.parse_args()
    schema_version = OnexVersionLoader().get_onex_versions().schema_version
    input_state = StamperInputState(file_path=args.file_path, author=args.author, version=schema_version)
    # Use default event bus for CLI
    output = run_stamper_node(input_state)
    print(output.json(indent=2))


if __name__ == "__main__":
    main()
