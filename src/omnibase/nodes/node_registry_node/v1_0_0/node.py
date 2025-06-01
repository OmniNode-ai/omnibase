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
from omnibase.enums import LogLevel, OnexStatus, NodeStatusEnum
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum, NodeAnnounceMetadataModel
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import OnexVersionLoader
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry
from omnibase.model.model_node_metadata import NodeMetadataBlock, IOBlock
from .introspection import NodeRegistryNodeIntrospection
from .models.state import NodeRegistryInputState, NodeRegistryOutputState, NodeRegistryEntry, NodeRegistryState
from omnibase.nodes.node_constants import NODE_ID, REGISTRY_ID, TRUST_STATE, TTL, REASON, METADATA_BLOCK, INPUTS, OUTPUTS, GRAPH_BINDING, ARG_ACTION, ARG_NODE_ID, ARG_INTROSPECT, ERR_MISSING_NODE_ID, ERR_NODE_NOT_FOUND, ERR_UNKNOWN_ACTION
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from .port_manager import PortManager
_COMPONENT_NAME = Path(__file__).stem


class NodeRegistryNode(EventDrivenNodeMixin):

    def __init__(self, node_id: str=NODE_ID, event_bus: Optional[
        ProtocolEventBus]=None, **kwargs):
        super().__init__(node_id=node_id, event_bus=event_bus, **kwargs)
        self.registry_state = NodeRegistryState()
        self.handler_registry = FileTypeHandlerRegistry(event_bus=get_event_bus(mode="bind"))
        self.port_manager = PortManager(event_bus=self.event_bus)
        # Sync port metadata on init
        self.registry_state.ports = self.port_manager.port_state
        if self.event_bus:
            self.event_bus.subscribe(lambda event: self.
                handle_node_announce(event) if getattr(event, 'event_type',
                None) == OnexEventTypeEnum.NODE_ANNOUNCE else None)

    def handle_node_announce(self, event):
        """Handle NODE_ANNOUNCE events and update registry. Expects event.metadata to be a NodeAnnounceMetadataModel (never a dict or other model)."""
        try:
            meta = event.metadata
            emit_log_event(LogLevel.TRACE, f"handle_node_announce: meta type={type(meta)}, meta={meta}", node_id=self.node_id, event_bus=self.event_bus)
            if not isinstance(meta, NodeAnnounceMetadataModel):
                raise TypeError("event.metadata must be a NodeAnnounceMetadataModel (protocol-pure), not a dict or other model.")
            announce = meta
            emit_log_event(LogLevel.TRACE, f"handle_node_announce: announce type={type(announce)}, announce={announce}", node_id=self.node_id, event_bus=self.event_bus)
            # Enforce node_id match unless proxying is explicitly documented
            if str(event.node_id) != str(announce.node_id):
                raise ValueError("event.node_id and metadata.node_id must match unless proxying is explicitly documented.")
            node_id = announce.node_id
            entry = NodeRegistryEntry(
                node_id=node_id,
                metadata_block=announce.metadata_block,
                status=announce.status,
                execution_mode=announce.execution_mode,
                inputs=announce.inputs,
                outputs=announce.outputs,
                graph_binding=announce.graph_binding,
                trust_state=announce.trust_state,
                ttl=announce.ttl,
                last_announce=str(announce.timestamp),
            )
            self.registry_state.registry[str(node_id)] = entry
            self.registry_state.last_updated = str(announce.timestamp)
            emit_log_event(LogLevel.TRACE, f"handle_node_announce: metadata_block.tools type={type(announce.metadata_block.tools)}, tools={getattr(announce.metadata_block.tools, 'root', announce.metadata_block.tools)}", node_id=self.node_id, event_bus=self.event_bus)
            # --- Tool registration logic ---
            tools = getattr(announce.metadata_block, "tools", None)
            if tools:
                merged = {**self.registry_state.tools.root, **tools.root}
                self.registry_state.tools = type(tools)(merged)
                emit_log_event(LogLevel.TRACE, f"handle_node_announce: after merge, registry_state.tools.root={self.registry_state.tools.root}", node_id=self.node_id, event_bus=self.event_bus)
                emit_log_event(LogLevel.INFO,
                    f"Registered {len(tools.root)} tool(s) from node_id={node_id}", node_id=self.node_id, event_bus=self.event_bus)
            emit_log_event(LogLevel.DEBUG,
                f'Accepted node_announce for node_id={node_id}', node_id=self.node_id, event_bus=self.event_bus)
            ack_event = OnexEvent(
                node_id=self.node_id,
                event_type=OnexEventTypeEnum.NODE_ANNOUNCE_ACCEPTED,
                metadata={
                    "node_id": node_id,
                    "status": NodeStatusEnum.ACCEPTED,
                    REGISTRY_ID: self.node_id,
                    TRUST_STATE: entry.trust_state,
                    TTL: entry.ttl
                }
            )
            if self.event_bus:
                self.event_bus.publish(ack_event)
        except Exception as exc:
            emit_log_event(LogLevel.TRACE,
                f'Exception in handle_node_announce: {repr(exc)} (type={type(exc)})', node_id=self.node_id, event_bus=self.event_bus)
            emit_log_event(LogLevel.ERROR,
                f'Rejected node_announce: {exc}', node_id=self.node_id,
                event_bus=self.event_bus)
            nack_event = OnexEvent(
                node_id=self.node_id,
                event_type=OnexEventTypeEnum.NODE_ANNOUNCE_REJECTED,
                metadata={
                    "node_id": getattr(event.metadata, 'node_id', None),
                    "status": NodeStatusEnum.REJECTED,
                    REASON: str(exc),
                    REGISTRY_ID: self.node_id
                }
            )
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

    def get_introspection(self) -> dict:
        """Get canonical introspection data for the node_registry node (instance method)."""
        from .introspection import NodeRegistryNodeIntrospection
        return NodeRegistryNodeIntrospection.get_introspection_response(self)

    # --- Port registration logic ---
    def allocate_port(self, request: 'PortRequestModel'):
        lease = self.port_manager.request_port(request)
        self.registry_state.ports = self.port_manager.port_state
        return lease

    def release_port(self, lease_id: str):
        result = self.port_manager.release_port(lease_id)
        self.registry_state.ports = self.port_manager.port_state
        return result


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
    emit_log_event(LogLevel.INFO, output.model_dump_json(indent=2),
        node_id=_COMPONENT_NAME, event_bus=self.event_bus)
    exit_code = get_exit_code_for_status(OnexStatus(output.status))
    sys.exit(exit_code)


def get_introspection() ->dict:
    """Get introspection data for the node_registry node (legacy global)."""
    # For backward compatibility, instantiate a node and return its introspection
    node = NodeRegistryNode()
    return node.get_introspection()


if __name__ == '__main__':
    main()
