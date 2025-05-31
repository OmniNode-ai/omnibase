"""
NODE_REGISTRY: Main node implementation for node_registry_node.

Replace this docstring with a description of your node's functionality.
Update the function names, logic, and imports as needed.
"""
import sys
from pathlib import Path
from typing import Callable, Optional
from omnibase.core.core_error_codes import get_exit_code_for_status
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus, NodeStatusEnum
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import OnexVersionLoader
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry
from omnibase.model.model_node_metadata import NodeMetadataBlock, IOBlock
from .introspection import NodeRegistryNodeIntrospection
from .models.state import NodeRegistryInputState, NodeRegistryOutputState, NodeRegistryEntry, NodeRegistryState
from omnibase.nodes.node_constants import NODE_ID, REGISTRY_ID, TRUST_STATE, TTL, REASON, METADATA_BLOCK, INPUTS, OUTPUTS, GRAPH_BINDING, ARG_ACTION, ARG_NODE_ID, ARG_INTROSPECT, ERR_MISSING_NODE_ID, ERR_NODE_NOT_FOUND, ERR_UNKNOWN_ACTION
_COMPONENT_NAME = Path(__file__).stem


class NodeRegistryNode(EventDrivenNodeMixin):

    def __init__(self, node_id: str=NODE_ID, event_bus: Optional[
        ProtocolEventBus]=None, **kwargs):
        super().__init__(node_id=node_id, event_bus=event_bus, **kwargs)
        self.registry_state = NodeRegistryState()
        self.handler_registry = FileTypeHandlerRegistry(event_bus=InMemoryEventBus())
        if self.event_bus:
            self.event_bus.subscribe(lambda event: self.
                handle_node_announce(event) if getattr(event, 'event_type',
                None) == OnexEventTypeEnum.NODE_ANNOUNCE else None)

    def handle_node_announce(self, event):
        """Handle NODE_ANNOUNCE events and update registry."""
        try:
            meta = event.metadata or {}
            node_id = meta.get(NODE_ID)
            if node_id is None or not str(node_id).strip():
                raise ValueError(ERR_MISSING_NODE_ID)
            entry = NodeRegistryEntry(node_id=node_id, metadata_block=
                NodeMetadataBlock(**meta.get(METADATA_BLOCK, {})), status=
                meta.get('status', NodeStatusEnum.EPHEMERAL),
                execution_mode=meta.get('execution_mode', 'memory'), inputs
                =[IOBlock(**i) for i in meta.get(INPUTS, [])], outputs=[
                IOBlock(**o) for o in meta.get(OUTPUTS, [])], graph_binding
                =meta.get(GRAPH_BINDING), trust_state=meta.get(TRUST_STATE),
                ttl=meta.get(TTL), last_announce=str(event.timestamp))
            self.registry_state.registry[str(node_id)] = entry
            self.registry_state.last_updated = str(event.timestamp)
            emit_log_event(LogLevelEnum.DEBUG,
                f'Accepted node_announce for node_id={node_id}', node_id=
                self.node_id, event_bus=self._event_bus)
            ack_event = OnexEvent(node_id=self.node_id, event_type=
                OnexEventTypeEnum.NODE_ANNOUNCE_ACCEPTED, metadata={NODE_ID:
                node_id, 'status': NodeStatusEnum.ACCEPTED, REGISTRY_ID:
                self.node_id, TRUST_STATE: entry.trust_state, TTL: entry.ttl})
            if self.event_bus:
                self.event_bus.publish(ack_event)
        except Exception as exc:
            emit_log_event(LogLevelEnum.ERROR,
                f'Rejected node_announce: {exc}', node_id=self.node_id,
                event_bus=self.event_bus)
            nack_event = OnexEvent(node_id=self.node_id, event_type=
                OnexEventTypeEnum.NODE_ANNOUNCE_REJECTED, metadata={NODE_ID:
                meta.get(NODE_ID), 'status': NodeStatusEnum.REJECTED,
                REASON: str(exc), REGISTRY_ID: self.node_id})
            if self.event_bus:
                self.event_bus.publish(nack_event)

    @telemetry(node_name=NODE_ID, operation='run')
    def run(self, input_state: NodeRegistryInputState, output_state_cls:
        Optional[Callable[..., NodeRegistryOutputState]]=None,
        handler_registry: Optional[FileTypeHandlerRegistry]=None, event_bus:
        Optional[ProtocolEventBus]=None, **kwargs) ->NodeRegistryOutputState:
        if output_state_cls is None:
            output_state_cls = NodeRegistryOutputState
        self.emit_node_start({'input_state': input_state.model_dump()})
        try:
            if input_state.action == 'get_active_nodes':
                output = output_state_cls(version=input_state.version,
                    status='success', message='Registry state returned',
                    registry_json=self.registry_state.model_dump_json())
            elif input_state.action == 'get_node':
                node_id = input_state.node_id
                if not node_id or node_id not in self.registry_state.registry:
                    output = output_state_cls(version=input_state.version,
                        status='failure', message=ERR_NODE_NOT_FOUND.format
                        (node_id=node_id), registry_json=None)
                else:
                    entry = self.registry_state.registry[node_id]
                    output = output_state_cls(version=input_state.version,
                        status='success', message=
                        f'Node {node_id} info returned.', registry_json=
                        entry.model_dump_json())
            else:
                output = output_state_cls(version=input_state.version,
                    status='failure', message=ERR_UNKNOWN_ACTION.format(
                    action=input_state.action), registry_json=None)
            self.emit_node_success({'input_state': input_state.model_dump(),
                'output_state': output.model_dump()})
            return output
        except Exception as exc:
            self.emit_node_failure({'input_state': input_state.model_dump(),
                'error': str(exc)})
            raise


def run_node_registry_node(input_state: NodeRegistryInputState, event_bus:
    Optional[ProtocolEventBus]=None, output_state_cls: Optional[Callable[
    ..., NodeRegistryOutputState]]=None, handler_registry: Optional[
    FileTypeHandlerRegistry]=None) ->NodeRegistryOutputState:
    node = NodeRegistryNode(event_bus=event_bus)
    return node.run(input_state, output_state_cls=output_state_cls,
        handler_registry=handler_registry)


def main() ->None:
    """
    NODE_REGISTRY: CLI entrypoint for standalone execution.

    Replace this with your node's CLI interface.
    Update the argument parser and logic as needed.
    """
    import argparse
    parser = argparse.ArgumentParser(description='Node Registry Node CLI')
    parser.add_argument(ARG_ACTION, type=str, nargs='?', help=
        "Action to perform: 'get_active_nodes', 'get_node'")
    parser.add_argument(ARG_NODE_ID, type=str, default=None, help=
        'Node ID for node-specific queries')
    parser.add_argument(ARG_INTROSPECT, action='store_true', help=
        'Display node contract and capabilities')
    args = parser.parse_args()
    if args.introspect:
        NodeRegistryNodeIntrospection.handle_introspect_command()
        return
    if not args.action:
        parser.error('action is required when not using --introspect')
    schema_version = OnexVersionLoader().get_onex_versions().schema_version
    input_state = NodeRegistryInputState(version=schema_version, action=
        args.action, node_id=args.node_id)
    output = run_node_registry_node(input_state)
    emit_log_event(LogLevelEnum.INFO, output.model_dump_json(indent=2),
        node_id=_COMPONENT_NAME, event_bus=self._event_bus)
    exit_code = get_exit_code_for_status(OnexStatus(output.status))
    sys.exit(exit_code)


def get_introspection() ->dict:
    """Get introspection data for the node_registry node."""
    return NodeRegistryNodeIntrospection.get_introspection_response(
        ).model_dump()


if __name__ == '__main__':
    main()
