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
from omnibase.enums import LogLevel, NodeStatusEnum, OnexStatus
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.model.model_node_metadata import IOBlock, NodeMetadataBlock
from omnibase.model.model_onex_event import (
    NodeAnnounceMetadataModel,
    OnexEvent,
    OnexEventTypeEnum,
)
from omnibase.nodes.node_constants import (
    ARG_ACTION,
    ARG_INTROSPECT,
    ARG_NODE_ID,
    ERR_MISSING_NODE_ID,
    ERR_NODE_NOT_FOUND,
    ERR_UNKNOWN_ACTION,
    GRAPH_BINDING,
    INPUTS,
    METADATA_BLOCK,
    NODE_ID,
    OUTPUTS,
    REASON,
    REGISTRY_ID,
    TRUST_STATE,
    TTL,
)
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)

from .introspection import NodeRegistryNodeIntrospection
from .models.state import (
    NodeRegistryEntry,
    NodeRegistryInputState,
    NodeRegistryOutputState,
    NodeRegistryState,
    ToolProxyInvocationRequest,
    ToolProxyInvocationResponse,
)
from .port_manager import PortManager
from omnibase.model.model_log_entry import LogContextModel

_COMPONENT_NAME = Path(__file__).stem


class NodeRegistryNode(EventDrivenNodeMixin):

    def __init__(
        self,
        node_id: str = NODE_ID,
        event_bus: Optional[ProtocolEventBus] = None,
        **kwargs,
    ):
        super().__init__(node_id=node_id, event_bus=event_bus, **kwargs)
        emit_log_event(LogLevel.DEBUG, f"[NODE] NodeRegistryNode initialized with event_bus.bus_id={self.event_bus.bus_id}", node_id=node_id, event_bus=self.event_bus)
        self.registry_state = NodeRegistryState()
        self.handler_registry = FileTypeHandlerRegistry(
            event_bus=get_event_bus(mode="bind")
        )
        self.port_manager = PortManager(event_bus=self.event_bus)
        # Sync port metadata on init
        self.registry_state.ports = self.port_manager.port_state
        if self.event_bus:
            self.event_bus.subscribe(
                lambda event: (
                    self.handle_node_announce(event)
                    if getattr(event, "event_type", None)
                    == OnexEventTypeEnum.NODE_ANNOUNCE
                    else None
                )
            )
            # --- Tool discovery event handler ---
            self.event_bus.subscribe(self._handle_tool_discovery_request)
            # --- Proxy tool invocation event handler ---
            self.event_bus.subscribe(self._handle_tool_proxy_invoke)

    def handle_node_announce(self, event):
        emit_log_event(LogLevel.DEBUG, f"[NODE] handle_node_announce: event_bus.bus_id={self.event_bus.bus_id}", node_id=self.node_id, event_bus=self.event_bus)
        """Handle NODE_ANNOUNCE events and update registry. Expects event.metadata to be a NodeAnnounceMetadataModel (never a dict or other model)."""
        try:
            meta = event.metadata
            emit_log_event(
                LogLevel.TRACE,
                f"handle_node_announce: meta type={type(meta)}, meta={meta}",
                node_id=self.node_id,
                event_bus=self.event_bus,
            )
            if not isinstance(meta, NodeAnnounceMetadataModel):
                raise TypeError(
                    "event.metadata must be a NodeAnnounceMetadataModel (protocol-pure), not a dict or other model."
                )
            announce = meta
            emit_log_event(
                LogLevel.TRACE,
                f"handle_node_announce: announce type={type(announce)}, announce={announce}",
                node_id=self.node_id,
                event_bus=self.event_bus,
            )
            # Enforce node_id match unless proxying is explicitly documented
            if str(event.node_id) != str(announce.node_id):
                raise ValueError(
                    "event.node_id and metadata.node_id must match unless proxying is explicitly documented."
                )
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
            emit_log_event(
                LogLevel.TRACE,
                f"handle_node_announce: metadata_block.tools type={type(announce.metadata_block.tools)}, tools={getattr(announce.metadata_block.tools, 'root', announce.metadata_block.tools)}",
                node_id=self.node_id,
                event_bus=self.event_bus,
            )
            # --- Tool registration logic ---
            tools = getattr(announce.metadata_block, "tools", None)
            if tools:
                merged = {**self.registry_state.tools.root, **tools.root}
                self.registry_state.tools = type(tools)(merged)
                emit_log_event(
                    LogLevel.TRACE,
                    f"handle_node_announce: after merge, registry_state.tools.root={self.registry_state.tools.root}",
                    node_id=self.node_id,
                    event_bus=self.event_bus,
                )
                emit_log_event(
                    LogLevel.INFO,
                    f"Registered {len(tools.root)} tool(s) from node_id={node_id}",
                    node_id=self.node_id,
                    event_bus=self.event_bus,
                )
            emit_log_event(
                LogLevel.DEBUG,
                f"Accepted node_announce for node_id={node_id}",
                node_id=self.node_id,
                event_bus=self.event_bus,
            )
            ack_event = OnexEvent(
                node_id=self.node_id,
                event_type=OnexEventTypeEnum.NODE_ANNOUNCE_ACCEPTED,
                metadata={
                    "node_id": node_id,
                    "status": NodeStatusEnum.ACCEPTED,
                    REGISTRY_ID: self.node_id,
                    TRUST_STATE: entry.trust_state,
                    TTL: entry.ttl,
                },
            )
            if self.event_bus:
                self.event_bus.publish(ack_event)
        except Exception as exc:
            emit_log_event(
                LogLevel.TRACE,
                f"Exception in handle_node_announce: {repr(exc)} (type={type(exc)})",
                node_id=self.node_id,
                event_bus=self.event_bus,
            )
            emit_log_event(
                LogLevel.ERROR,
                f"Rejected node_announce: {exc}",
                node_id=self.node_id,
                event_bus=self.event_bus,
            )
            nack_event = OnexEvent(
                node_id=self.node_id,
                event_type=OnexEventTypeEnum.NODE_ANNOUNCE_REJECTED,
                metadata={
                    "node_id": getattr(event.metadata, "node_id", None),
                    "status": NodeStatusEnum.REJECTED,
                    REASON: str(exc),
                    REGISTRY_ID: self.node_id,
                },
            )
            if self.event_bus:
                self.event_bus.publish(nack_event)

    def _handle_tool_discovery_request(self, event):
        emit_log_event(LogLevel.DEBUG, f"[NODE] _handle_tool_discovery_request: event_bus.bus_id={self.event_bus.bus_id}", node_id=self.node_id, event_bus=self.event_bus)
        """Handle TOOL_DISCOVERY_REQUEST events and respond with all registered tools."""
        if getattr(event, "event_type", None) != OnexEventTypeEnum.TOOL_DISCOVERY_REQUEST:
            return
        try:
            correlation_id = getattr(event, "correlation_id", None)
            tools = self.registry_state.tools.model_dump()
            emit_log_event(
                LogLevel.INFO,
                f"Received TOOL_DISCOVERY_REQUEST, responding with {len(tools)} tools.",
                node_id=self.node_id,
                event_bus=self.event_bus,
                context=LogContextModel(correlation_id=correlation_id),
            )
            response_event = OnexEvent(
                node_id=self.node_id,
                event_type=OnexEventTypeEnum.TOOL_DISCOVERY_RESPONSE,
                correlation_id=correlation_id,
                metadata={"tools": tools},
            )
            if self.event_bus:
                self.event_bus.publish(response_event)
        except Exception as exc:
            emit_log_event(
                LogLevel.ERROR,
                f"Failed to handle TOOL_DISCOVERY_REQUEST: {exc}",
                node_id=self.node_id,
                event_bus=self.event_bus,
                context=LogContextModel(correlation_id=getattr(event, "correlation_id", None)),
            )

    def _make_log_context(self, correlation_id=None):
        import inspect
        from datetime import datetime
        frame = inspect.currentframe().f_back
        return LogContextModel(
            calling_module=frame.f_globals.get("__name__", "<unknown>"),
            calling_function=frame.f_code.co_name,
            calling_line=frame.f_lineno,
            timestamp=datetime.utcnow().isoformat() + "Z",
            node_id=self.node_id,
            correlation_id=correlation_id,
        )

    def _handle_tool_proxy_invoke(self, event):
        emit_log_event(LogLevel.DEBUG, f"[NODE] _handle_tool_proxy_invoke: event_bus.bus_id={self.event_bus.bus_id}", node_id=self.node_id, event_bus=self.event_bus)
        from .models.state import ToolProxyInvocationRequest, ToolProxyInvocationResponse
        from omnibase.enums import OnexStatus
        from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
        emit_log_event(
            LogLevel.DEBUG,
            f"DEBUG: _handle_tool_proxy_invoke called for event_type={getattr(event, 'event_type', None)} correlation_id={getattr(event, 'correlation_id', None)}",
            node_id=self.node_id,
            event_bus=self.event_bus,
            context=self._make_log_context(getattr(event, 'correlation_id', None)),
        )
        try:
            if getattr(event, "event_type", None) != OnexEventTypeEnum.TOOL_PROXY_INVOKE:
                return
            correlation_id = getattr(event, "correlation_id", None)
            req = event.metadata
            if not isinstance(req, ToolProxyInvocationRequest):
                emit_log_event(
                    LogLevel.ERROR,
                    f"TOOL_PROXY_INVOKE: metadata is not ToolProxyInvocationRequest: {type(req)}",
                    node_id=self.node_id,
                    event_bus=self.event_bus,
                    context=self._make_log_context(correlation_id),
                )
                # Emit rejected event
                self.event_bus.publish(
                    OnexEvent(
                        node_id=self.node_id,
                        event_type=OnexEventTypeEnum.TOOL_PROXY_REJECTED,
                        correlation_id=correlation_id,
                        metadata=ToolProxyInvocationResponse(
                            status=OnexStatus.REJECTED,
                            error_code="INVALID_REQUEST",
                            error_message="metadata must be ToolProxyInvocationRequest",
                            correlation_id=correlation_id,
                            tool_name=getattr(req, "tool_name", ""),
                        ),
                    )
                )
                return
            # Validate tool existence
            tool = self.registry_state.tools.root.get(req.tool_name)
            if not tool:
                emit_log_event(
                    LogLevel.ERROR,
                    f"TOOL_PROXY_INVOKE: tool '{req.tool_name}' not found in registry",
                    node_id=self.node_id,
                    event_bus=self.event_bus,
                    context=self._make_log_context(correlation_id),
                )
                self.event_bus.publish(
                    OnexEvent(
                        node_id=self.node_id,
                        event_type=OnexEventTypeEnum.TOOL_PROXY_REJECTED,
                        correlation_id=correlation_id,
                        metadata=ToolProxyInvocationResponse(
                            status=OnexStatus.REJECTED,
                            error_code="TOOL_NOT_FOUND",
                            error_message=f"Tool '{req.tool_name}' not found in registry",
                            correlation_id=correlation_id,
                            tool_name=req.tool_name,
                        ),
                    )
                )
                return
            # (Stub) Accept and emit TOOL_PROXY_ACCEPTED
            emit_log_event(
                LogLevel.INFO,
                f"TOOL_PROXY_INVOKE: accepted for tool '{req.tool_name}'",
                node_id=self.node_id,
                event_bus=self.event_bus,
                context=self._make_log_context(correlation_id),
            )
            self.event_bus.publish(
                OnexEvent(
                    node_id=self.node_id,
                    event_type=OnexEventTypeEnum.TOOL_PROXY_ACCEPTED,
                    correlation_id=correlation_id,
                    metadata=ToolProxyInvocationResponse(
                        status=OnexStatus.ACCEPTED,
                        correlation_id=correlation_id,
                        tool_name=req.tool_name,
                    ),
                )
            )
            # (Stub) Immediately emit TOOL_PROXY_RESULT with a placeholder result
            self.event_bus.publish(
                OnexEvent(
                    node_id=self.node_id,
                    event_type=OnexEventTypeEnum.TOOL_PROXY_RESULT,
                    correlation_id=correlation_id,
                    metadata=ToolProxyInvocationResponse(
                        status=OnexStatus.SUCCESS,
                        result={"message": f"Stub result for tool '{req.tool_name}'"},
                        correlation_id=correlation_id,
                        tool_name=req.tool_name,
                        provider_node_id=self.node_id,
                    ),
                )
            )
        except Exception as exc:
            emit_log_event(
                LogLevel.ERROR,
                f"Exception in _handle_tool_proxy_invoke: {exc}",
                node_id=self.node_id,
                event_bus=self.event_bus,
                context=self._make_log_context(getattr(event, "correlation_id", None)),
            )
            self.event_bus.publish(
                OnexEvent(
                    node_id=self.node_id,
                    event_type=OnexEventTypeEnum.TOOL_PROXY_ERROR,
                    correlation_id=getattr(event, "correlation_id", None),
                    metadata=ToolProxyInvocationResponse(
                        status=OnexStatus.ERROR,
                        error_code="INTERNAL_ERROR",
                        error_message=str(exc),
                        correlation_id=getattr(event, "correlation_id", None),
                        tool_name=getattr(getattr(event, "metadata", None), "tool_name", ""),
                    ),
                )
            )

    @telemetry(node_name=NODE_ID, operation="run")
    def run(
        self,
        input_state: NodeRegistryInputState,
        output_state_cls: Optional[Callable[..., NodeRegistryOutputState]] = None,
        handler_registry: Optional[FileTypeHandlerRegistry] = None,
        event_bus: Optional[ProtocolEventBus] = None,
        **kwargs,
    ) -> NodeRegistryOutputState:
        if output_state_cls is None:
            output_state_cls = NodeRegistryOutputState
        self.emit_node_start({"input_state": input_state.model_dump()})
        try:
            if input_state.action == "get_active_nodes":
                output = output_state_cls(
                    version=input_state.version,
                    status="success",
                    message="Registry state returned",
                    registry_json=self.registry_state.model_dump_json(),
                )
            elif input_state.action == "get_node":
                node_id = input_state.node_id
                if not node_id or node_id not in self.registry_state.registry:
                    output = output_state_cls(
                        version=input_state.version,
                        status="failure",
                        message=ERR_NODE_NOT_FOUND.format(node_id=node_id),
                        registry_json=None,
                    )
                else:
                    entry = self.registry_state.registry[node_id]
                    output = output_state_cls(
                        version=input_state.version,
                        status="success",
                        message=f"Node {node_id} info returned.",
                        registry_json=entry.model_dump_json(),
                    )
            else:
                output = output_state_cls(
                    version=input_state.version,
                    status="failure",
                    message=ERR_UNKNOWN_ACTION.format(action=input_state.action),
                    registry_json=None,
                )
            self.emit_node_success(
                {
                    "input_state": input_state.model_dump(),
                    "output_state": output.model_dump(),
                }
            )
            return output
        except Exception as exc:
            self.emit_node_failure(
                {"input_state": input_state.model_dump(), "error": str(exc)}
            )
            raise

    def get_introspection(self) -> dict:
        """Get canonical introspection data for the node_registry node (instance method)."""
        from .introspection import NodeRegistryNodeIntrospection

        return NodeRegistryNodeIntrospection.get_introspection_response(self)

    # --- Port registration logic ---
    def allocate_port(self, request: "PortRequestModel"):
        lease = self.port_manager.request_port(request)
        self.registry_state.ports = self.port_manager.port_state
        return lease

    def release_port(self, lease_id: str):
        result = self.port_manager.release_port(lease_id)
        self.registry_state.ports = self.port_manager.port_state
        return result


def run_node_registry_node(
    input_state: NodeRegistryInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., NodeRegistryOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> NodeRegistryOutputState:
    node = NodeRegistryNode(event_bus=event_bus)
    return node.run(
        input_state,
        output_state_cls=output_state_cls,
        handler_registry=handler_registry,
    )


def main() -> None:
    """
    NODE_REGISTRY: CLI entrypoint for standalone execution.

    Replace this with your node's CLI interface.
    Update the argument parser and logic as needed.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Node Registry Node CLI")
    parser.add_argument(
        ARG_ACTION,
        type=str,
        nargs="?",
        help="Action to perform: 'get_active_nodes', 'get_node'",
    )
    parser.add_argument(
        ARG_NODE_ID, type=str, default=None, help="Node ID for node-specific queries"
    )
    parser.add_argument(
        ARG_INTROSPECT,
        action="store_true",
        help="Display node contract and capabilities",
    )
    args = parser.parse_args()
    if args.introspect:
        NodeRegistryNodeIntrospection.handle_introspect_command()
        return
    if not args.action:
        parser.error("action is required when not using --introspect")
    schema_version = OnexVersionLoader().get_onex_versions().schema_version
    input_state = NodeRegistryInputState(
        version=schema_version, action=args.action, node_id=args.node_id
    )
    output = run_node_registry_node(input_state)
    emit_log_event(
        LogLevel.INFO,
        output.model_dump_json(indent=2),
        node_id=_COMPONENT_NAME,
        event_bus=self.event_bus,
    )
    exit_code = get_exit_code_for_status(OnexStatus(output.status))
    sys.exit(exit_code)


def get_introspection() -> dict:
    """Get introspection data for the node_registry node (legacy global)."""
    # For backward compatibility, instantiate a node and return its introspection
    node = NodeRegistryNode()
    return node.get_introspection()


if __name__ == "__main__":
    main()
