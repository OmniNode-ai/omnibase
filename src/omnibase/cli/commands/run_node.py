import argparse

from omnibase.runtime.events.event_bus_in_memory import InMemoryEventBus
from omnibase.runtime.node_runner import NodeRunner


def main():
    """
    Canonical CLI entrypoint for `onex run <node>`.
    Parses arguments, instantiates event bus and node runner, and executes the node.
    TODO: Implement real node loading and event bus selection.
    """
    parser = argparse.ArgumentParser(description="Run an ONEX node and emit events.")
    parser.add_argument("node", type=str, help="Node name to execute")
    parser.add_argument(
        "--args", nargs=argparse.REMAINDER, help="Arguments to pass to the node"
    )
    args = parser.parse_args()

    # TODO: Load the actual node callable by name
    def stub_node(*node_args, **node_kwargs):
        print(f"Stub node executed with args: {node_args}, kwargs: {node_kwargs}")
        return {"status": "success"}

    event_bus = InMemoryEventBus()
    runner = NodeRunner(stub_node, event_bus, node_id=args.node)
    result = runner.run(*(args.args or []))
    print(f"Node result: {result}")
    # TODO: Print or log emitted events if needed


if __name__ == "__main__":
    main()
