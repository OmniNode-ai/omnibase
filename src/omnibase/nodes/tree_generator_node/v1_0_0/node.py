# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node.py
# version: 1.0.0
# uuid: 4f13e6e3-84de-4e5d-8579-f90f3dd41a16
# author: OmniNode Team
# created_at: 2025-05-24T09:29:37.987105
# last_modified_at: 2025-05-24T13:39:57.890138
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5aa9aa96ef80b9158d340ef33ab4819ec2ceeb1f608b2696a9363af138181e5c
# entrypoint: python@node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.node
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Tree Generator Node - Generates .onextree manifest files from directory structure analysis.

This node scans the omnibase directory structure to discover all versioned artifacts
(nodes, CLI tools, runtimes, adapters, contracts, packages) and generates a canonical
.onextree manifest file that describes the project structure.
"""

import logging
import sys
from pathlib import Path
from typing import Callable, Optional

from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)

from .helpers.tree_validator import OnextreeValidator

# Import helpers and state models with fallback for different execution contexts
try:
    from .helpers.tree_generator_engine import TreeGeneratorEngine
    from .models.state import TreeGeneratorInputState, TreeGeneratorOutputState
except ImportError:
    # Fallback for direct execution
    # Add current directory to path for relative imports
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    from helpers.tree_generator_engine import TreeGeneratorEngine  # type: ignore
    from models.state import (  # type: ignore
        TreeGeneratorInputState,
        TreeGeneratorOutputState,
    )

logger = logging.getLogger(__name__)


def run_tree_generator_node(
    input_state: TreeGeneratorInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., TreeGeneratorOutputState]] = None,
) -> TreeGeneratorOutputState:
    """
    Canonical ONEX node entrypoint for generating .onextree manifest files.
    Emits NODE_START, NODE_SUCCESS, NODE_FAILURE events.
    Args:
        input_state: TreeGeneratorInputState (must include version)
        event_bus: ProtocolEventBus (optional, defaults to InMemoryEventBus)
        output_state_cls: Optional callable to construct output state (for testing/mocking)
    Returns:
        TreeGeneratorOutputState (version matches input_state.version)
    """
    if event_bus is None:
        event_bus = InMemoryEventBus()
    if output_state_cls is None:
        output_state_cls = TreeGeneratorOutputState
    node_id = "tree_generator_node"
    event_bus.publish(
        OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id=node_id,
            metadata={"input_state": input_state.model_dump()},
        )
    )
    try:
        # Instantiate the canonical engine
        engine = TreeGeneratorEngine()
        # Call the real tree generation logic
        result = engine.generate_tree(
            root_directory=input_state.root_directory,
            output_path=input_state.output_path,
            output_format=input_state.output_format,
            include_metadata=input_state.include_metadata,
        )
        # Map OnexResultModel to output_state_cls
        metadata = result.metadata or {}
        output = output_state_cls(
            version=input_state.version,
            status=(
                result.status.value
                if hasattr(result.status, "value")
                else str(result.status)
            ),
            message=str(
                metadata.get("error")
                if result.status.value == "failure"
                else f"Successfully generated .onextree manifest at {metadata.get('manifest_path', 'unknown')}"
            ),
            manifest_path=metadata.get("manifest_path"),
            artifacts_discovered=metadata.get("artifacts_discovered"),
            validation_results=metadata.get("validation_results"),
            tree_structure=metadata.get("tree_structure"),
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

    parser = argparse.ArgumentParser(description="ONEX Tree Generator Node CLI")
    parser.add_argument(
        "--root-directory",
        type=str,
        help="Root directory to scan for artifacts",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        help="Output path for .onextree file (default: <root>/.onextree)",
    )
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["yaml", "json"],
        default="yaml",
        help="Output format for manifest file",
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Skip metadata validation",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate .onextree file against directory",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    args = parser.parse_args()

    if args.validate:
        validator = OnextreeValidator(verbose=args.verbose)
        onextree_path = (
            Path(args.output_path)
            if args.output_path
            else Path(args.root_directory) / ".onextree"
        )
        result = validator.validate_onextree_file(
            onextree_path=onextree_path,
            root_directory=Path(args.root_directory),
        )
        validator.print_results(result)
        sys.exit(validator.get_exit_code(result))
    else:
        # Generation mode
        schema_version = OnexVersionLoader().get_onex_versions().schema_version
        input_state = TreeGeneratorInputState(
            version=schema_version,
            root_directory=args.root_directory,
            output_path=args.output_path,
            output_format=args.output_format,
            include_metadata=not args.no_metadata,
        )
        # Use default event bus for CLI
        output = run_tree_generator_node(input_state)
        print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
