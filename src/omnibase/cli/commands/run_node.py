# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: run_node.py
# version: 1.0.0
# uuid: bf1b62fa-a11a-4c39-a582-bbd77d63190d
# author: OmniNode Team
# created_at: 2025-05-22T14:05:21.442415
# last_modified_at: 2025-05-22T20:21:24.989970
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 05994e6c182b403283b2a09e6b12d13131c92664e62296e110273e9bb0a60903
# entrypoint: python@run_node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.run_node
# meta_type: tool
# === /OmniNode:Metadata ===


import argparse
import importlib
import logging
from typing import Any, Callable, Dict

from omnibase.runtime.events.event_bus_in_memory import InMemoryEventBus

# Node registry: maps node name to (module, function, cli_adapter)
NODE_REGISTRY: Dict[str, tuple[str, str, Any]] = {
    "stamper_node": (
        "omnibase.nodes.stamper_node.node",
        "run_stamper_node",
        "omnibase.nodes.stamper_node.helpers.stamper_node_cli_adapter.StamperNodeCliAdapter",
    ),
    # Add more nodes here as needed
}

logger = logging.getLogger("onex.run_node")


def main() -> None:
    """
    Canonical CLI entrypoint for `onex run <node>`.
    Dynamically loads and runs the requested node using its CLI adapter.
    """
    parser = argparse.ArgumentParser(description="Run an ONEX node and emit events.")
    parser.add_argument("node", type=str, help="Node name to execute")
    parser.add_argument(
        "--args", nargs=argparse.REMAINDER, help="Arguments to pass to the node"
    )
    args = parser.parse_args()

    node_name = args.node
    node_info = NODE_REGISTRY.get(node_name)
    if not node_info:
        logger.error(f"Unknown node: {node_name}")
        print(
            f"Error: Unknown node '{node_name}'. Available: {list(NODE_REGISTRY.keys())}"
        )
        exit(1)
    module_name, func_name, adapter_path = node_info
    try:
        module = importlib.import_module(module_name)
        node_func: Callable = getattr(module, func_name)
        # Dynamically import the adapter class
        adapter_module_path, adapter_class_name = adapter_path.rsplit(".", 1)
        adapter_module = importlib.import_module(adapter_module_path)
        adapter_class = getattr(adapter_module, adapter_class_name)
        cli_adapter = adapter_class()
    except Exception as e:
        logger.error(f"Failed to import node or adapter {node_name}: {e}")
        print(f"Error: Failed to import node or adapter '{node_name}': {e}")
        exit(1)

    node_args = args.args or []
    # Use the adapter to build the input state
    try:
        input_state = cli_adapter.parse_cli_args(node_args)
    except Exception as e:
        logger.error(f"Failed to parse CLI args for {node_name}: {e}")
        print(f"Error: Failed to parse CLI args for '{node_name}': {e}")
        exit(1)
    event_bus = InMemoryEventBus()
    try:
        result = node_func(input_state, event_bus=event_bus)
    except TypeError:
        result = node_func(input_state)
    # Print result as JSON if possible
    try:
        from pydantic import BaseModel

        if isinstance(result, BaseModel):
            # Pydantic v2: use model_dump_json; v1: use json()
            if hasattr(result, "model_dump_json"):
                print(result.model_dump_json(indent=2))
            else:
                print(result.json(indent=2))
        else:
            print(str(result))
    except ImportError:
        print(str(result))
    # TODO: Print or log emitted events if needed


if __name__ == "__main__":
    main()
