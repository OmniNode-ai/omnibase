import datetime
import uuid
from uuid import uuid4

import pytest
from pydantic.errors import PydanticUserError

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import OnexStatus
from omnibase.fixtures.port_manager_fixtures import event_bus, port_manager
from omnibase.model.model_entrypoint import EntrypointBlock
from omnibase.model.model_function_tool import (
    FunctionLanguageEnum,
    FunctionTool,
    ToolTypeEnum,
)
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_onex_event import (
    OnexEvent,
    OnexEventMetadataModel,
    OnexEventTypeEnum,
)
from omnibase.model.model_tool_collection import ToolCollection
from omnibase.nodes.node_registry_node.v1_0_0.models.port_usage import PortUsageEntry
from omnibase.nodes.node_registry_node.v1_0_0.models.state import (
    PortRequestModel,
    ToolProxyInvocationRequest,
    ToolProxyInvocationResponse,
)
from omnibase.nodes.node_registry_node.v1_0_0.node import NodeRegistryNode
from omnibase.nodes.node_registry_node.v1_0_0.port_manager import PortManager
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)


def test_port_allocation_success(port_manager):
    requester_id = uuid4()
    request = PortRequestModel(
        requester_id=requester_id, protocol="kafka", preferred_port=None, ttl=60
    )
    lease = port_manager.request_port(request)
    assert lease.assigned_to == str(requester_id)
    assert lease.protocol == "kafka"
    assert lease.status == "active"
    assert int(lease.port) in port_manager.port_usage_map.ports


def test_port_collision_avoidance(port_manager):
    # Placeholder: Will test that two requests for the same port do not collide
    # when logic is implemented
    pass


def test_lease_expiration_stub(port_manager):
    # Placeholder: Will test lease expiration logic when implemented
    pass


def test_introspection_returns_state(port_manager):
    state = port_manager.introspect_ports()
    assert hasattr(state, "ports")
    assert isinstance(state.ports, dict)


def test_port_allocation_emits_event(port_manager, event_bus):
    events = []
    event_bus.subscribe(lambda e: events.append(e))
    requester_id = uuid4()
    request = PortRequestModel(
        requester_id=requester_id, protocol="kafka", preferred_port=50010, ttl=60
    )
    port_manager.request_port(request)
    assert any(
        e.event_type == OnexEventTypeEnum.STRUCTURED_LOG
        and getattr(e.metadata, "status", None) == "allocated"
        for e in events
    )
    found = [
        e
        for e in events
        if e.metadata and getattr(e.metadata, "status", None) == "allocated"
    ]
    assert found
    event = found[0]
    assert event.metadata.input_state["lease"]["port"] == 50010
    assert getattr(event.metadata, "status", None) == "allocated"
    assert f"Port 50010 allocated to {requester_id}" in event.metadata.result_summary


def test_port_allocation_updates_usage_map(port_manager):
    requester_id = uuid4()
    request = PortRequestModel(
        requester_id=requester_id, protocol="kafka", preferred_port=50001, ttl=60
    )
    lease = port_manager.request_port(request)
    assert lease.port == 50001
    assert lease.assigned_to == str(requester_id)
    assert 50001 in port_manager.port_usage_map.ports
    entry = port_manager.port_usage_map.ports[50001]
    assert entry.node_id == requester_id
    assert entry.protocol == "kafka"
    assert entry.status == "active"


def test_port_allocation_collision(port_manager):
    requester1 = uuid4()
    requester2 = uuid4()
    req1 = PortRequestModel(
        requester_id=requester1, protocol="kafka", preferred_port=50002, ttl=60
    )
    req2 = PortRequestModel(
        requester_id=requester2, protocol="kafka", preferred_port=50002, ttl=60
    )
    port_manager.request_port(req1)
    with pytest.raises(OnexError) as excinfo:
        port_manager.request_port(req2)
    assert excinfo.value.error_code == CoreErrorCode.RESOURCE_EXHAUSTED


def test_port_release_removes_from_usage_map(port_manager):
    requester_id = uuid4()
    request = PortRequestModel(
        requester_id=requester_id, protocol="kafka", preferred_port=50003, ttl=60
    )
    lease = port_manager.request_port(request)
    assert 50003 in port_manager.port_usage_map.ports
    result = port_manager.release_port(lease.lease_id)
    assert result is True
    assert 50003 not in port_manager.port_usage_map.ports
    assert lease.lease_id not in port_manager.port_state.ports


def test_port_usage_map_introspection(port_manager):
    requester_id = uuid4()
    request = PortRequestModel(
        requester_id=requester_id, protocol="kafka", preferred_port=50004, ttl=60
    )
    port_manager.request_port(request)
    usage_map = port_manager.introspect_port_usage()
    assert 50004 in usage_map.ports
    entry = usage_map.ports[50004]
    assert entry.node_id == requester_id
    assert entry.protocol == "kafka"
    assert entry.status == "active"


def test_port_release_emits_event(port_manager, event_bus):
    events = []
    event_bus.subscribe(lambda e: events.append(e))
    requester_id = uuid4()
    request = PortRequestModel(
        requester_id=requester_id, protocol="kafka", preferred_port=50011, ttl=60
    )
    lease = port_manager.request_port(request)
    port_manager.release_port(lease.lease_id)
    assert any(
        e.event_type == OnexEventTypeEnum.STRUCTURED_LOG
        and getattr(e.metadata, "status", None) == "released"
        for e in events
    )
    found = [
        e
        for e in events
        if e.metadata and getattr(e.metadata, "status", None) == "released"
    ]
    assert found
    event = found[0]
    assert getattr(event.metadata, "status", None) == "released"
    assert f"Port lease {lease.lease_id} released" in event.metadata.result_summary


def test_registry_node_introspection_response():
    node = NodeRegistryNode()
    response = node.get_introspection()
    required_fields = [
        "node_metadata",
        "contract",
        "ports",
        "event_buses",
        "port_usage",
        "registry",
        "trust_status",
    ]
    missing = [f for f in required_fields if f not in response]
    assert (
        not missing
    ), f"Missing fields in introspection response: {missing}\nFull response: {response}"
    # Optionally, check that node_metadata and contract have expected keys
    assert isinstance(response["node_metadata"], dict)
    assert isinstance(response["contract"], dict)
    # Print for debug if test fails
    if missing:
        print("Introspection response:", response)


def test_registry_state_tracks_port_metadata():
    from uuid import uuid4

    from omnibase.nodes.node_registry_node.v1_0_0.models.state import PortRequestModel
    from omnibase.nodes.node_registry_node.v1_0_0.node import NodeRegistryNode

    node = NodeRegistryNode()
    requester_id = uuid4()
    request = PortRequestModel(
        requester_id=requester_id, protocol="kafka", preferred_port=50020, ttl=60
    )
    lease = node.allocate_port(request)
    # Registry state should match port manager state
    assert node.registry_state.ports == node.port_manager.port_state
    # Introspection should include the port lease
    response = node.get_introspection()
    ports = response.get("ports", {}).get("ports", {})
    found = any(str(lease.lease_id) == k for k in ports.keys())
    assert found, f"Lease {lease.lease_id} not found in introspection ports: {ports}"


def test_registry_node_introspection_includes_tools():
    node = NodeRegistryNode()
    response = node.get_introspection()
    assert (
        "tools" in response
    ), f"tools field missing in introspection: {response.keys()}"
    assert isinstance(
        response["tools"], dict
    ), f"tools field is not a dict: {type(response['tools'])}"


def test_registry_node_aggregates_tools_from_node_announce():
    import datetime
    from uuid import uuid4

    from omnibase.model.model_node_metadata import NodeMetadataBlock
    from omnibase.model.model_onex_event import (
        NodeAnnounceMetadataModel,
        OnexEvent,
        OnexEventTypeEnum,
    )
    from omnibase.nodes.node_registry_node.v1_0_0.node import NodeRegistryNode

    # Create a node with a tool in its metadata block
    tool_name = "example_tool"
    tool_def = FunctionTool(
        type=ToolTypeEnum.FUNCTION,
        language=FunctionLanguageEnum.PYTHON,
        line=1,
        description="A test tool",
        inputs=["x"],
        outputs=["y"],
        error_codes=[],
        side_effects=[],
    )
    metadata_block = NodeMetadataBlock(
        name="test_node",
        uuid=str(uuid4()),
        inputs=[],
        outputs=[],
        tools=ToolCollection({tool_name: tool_def}),
        metadata_version="1.0.0",
        schema_version="1.0.0",
        author="Test",
        created_at=datetime.datetime.utcnow().isoformat(),
        last_modified_at=datetime.datetime.utcnow().isoformat(),
        hash="0" * 64,
        entrypoint=EntrypointBlock(type="python", target="test.test_node.main"),
        namespace="python://test.test_node",
        meta_type="tool",
    )
    announce = NodeAnnounceMetadataModel(
        node_id=str(uuid4()),
        metadata_block=metadata_block,
        status="ephemeral",
        execution_mode="memory",
        inputs=[],
        outputs=[],
        schema_version="1.0.0",
        timestamp=datetime.datetime.utcnow(),
    )
    event_bus = InMemoryEventBus()

    def print_log_events(event):
        if getattr(event, "event_type", None) == OnexEventTypeEnum.STRUCTURED_LOG:
            print(
                f"[LOG] {getattr(event.metadata, 'message', '') if event.metadata else ''}"
            )

    event_bus.subscribe(print_log_events)
    node = NodeRegistryNode(event_bus=event_bus)
    event = OnexEvent(
        node_id=announce.node_id,
        event_type=OnexEventTypeEnum.NODE_ANNOUNCE,
        metadata=announce,
    )
    node.handle_node_announce(event)
    # The tool should now be in the registry's global tools
    assert (
        tool_name in node.registry_state.tools.root
    ), f"Tool {tool_name} not found in registry tools: {node.registry_state.tools.root.keys()}"
    # Introspection should also include the tool
    response = node.get_introspection()
    assert (
        tool_name in response["tools"]
    ), f"Tool {tool_name} not found in introspection tools: {response['tools'].keys()}"


def test_tool_proxy_invoke_success(event_bus):
    """Test TOOL_PROXY_INVOKE for a registered tool emits ACCEPTED and RESULT events."""
    import uuid

    from omnibase.model.model_function_tool import (
        FunctionLanguageEnum,
        FunctionTool,
        ToolTypeEnum,
    )
    from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
    from omnibase.model.model_tool_collection import ToolCollection
    from omnibase.nodes.node_registry_node.v1_0_0.models.state import (
        ToolProxyInvocationRequest,
    )

    # Collect emitted events
    events = []
    # Register a tool in the registry node
    node = NodeRegistryNode(event_bus=event_bus)
    tool_name = "test_tool"
    tool = FunctionTool(
        type=ToolTypeEnum.FUNCTION,
        language=FunctionLanguageEnum.PYTHON,
        line=1,
        description="Test tool",
        inputs=["x"],
        outputs=["y"],
        error_codes=[],
        side_effects=[],
    )
    node.registry_state.tools = ToolCollection({tool_name: tool})

    def collector(e):
        print(
            f"[TEST COLLECTOR] event_type={getattr(e, 'event_type', None)}, correlation_id={getattr(e, 'correlation_id', None)}"
        )
        events.append(e)

    event_bus.subscribe(collector)

    correlation_id = str(uuid.uuid4())
    req = ToolProxyInvocationRequest(
        tool_name=tool_name,
        arguments={"x": 1},
        correlation_id=correlation_id,
    )
    event = OnexEvent(
        node_id="test_client",
        event_type=OnexEventTypeEnum.TOOL_PROXY_INVOKE,
        correlation_id=correlation_id,
        metadata=req,
    )
    event_bus.publish(event)

    # Check for ACCEPTED and RESULT events
    accepted = [
        e for e in events if e.event_type == OnexEventTypeEnum.TOOL_PROXY_ACCEPTED
    ]
    result = [e for e in events if e.event_type == OnexEventTypeEnum.TOOL_PROXY_RESULT]
    assert accepted, "No TOOL_PROXY_ACCEPTED event emitted"
    assert result, "No TOOL_PROXY_RESULT event emitted"
    assert accepted[0].metadata.tool_name == tool_name
    assert accepted[0].correlation_id == correlation_id
    assert result[0].metadata.tool_name == tool_name
    assert result[0].correlation_id == correlation_id
    assert result[0].metadata.status.value == "success"


def test_tool_proxy_invoke_tool_not_found(event_bus):
    """Test TOOL_PROXY_INVOKE for a non-existent tool emits TOOL_PROXY_REJECTED with TOOL_NOT_FOUND."""
    import uuid

    from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
    from omnibase.nodes.node_registry_node.v1_0_0.models.state import (
        ToolProxyInvocationRequest,
    )

    events = []
    node = NodeRegistryNode(event_bus=event_bus)

    def collector(e):
        print(
            f"[TEST COLLECTOR] event_type={getattr(e, 'event_type', None)}, correlation_id={getattr(e, 'correlation_id', None)}"
        )
        events.append(e)

    event_bus.subscribe(collector)
    correlation_id = str(uuid.uuid4())
    req = ToolProxyInvocationRequest(
        tool_name="missing_tool",
        arguments={},
        correlation_id=correlation_id,
    )
    event = OnexEvent(
        node_id="test_client",
        event_type=OnexEventTypeEnum.TOOL_PROXY_INVOKE,
        correlation_id=correlation_id,
        metadata=req,
    )
    event_bus.publish(event)
    rejected = [
        e for e in events if e.event_type == OnexEventTypeEnum.TOOL_PROXY_REJECTED
    ]
    assert rejected, "No TOOL_PROXY_REJECTED event emitted"
    assert rejected[0].metadata.error_code == "TOOL_NOT_FOUND"
    assert rejected[0].correlation_id == correlation_id


def test_tool_proxy_invoke_invalid_request(event_bus):
    """Test TOOL_PROXY_INVOKE with invalid metadata emits TOOL_PROXY_REJECTED with INVALID_REQUEST."""
    import uuid

    from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum

    events = []
    node = NodeRegistryNode(event_bus=event_bus)

    def collector(e):
        print(
            f"[TEST COLLECTOR] event_type={getattr(e, 'event_type', None)}, correlation_id={getattr(e, 'correlation_id', None)}"
        )
        events.append(e)

    event_bus.subscribe(collector)
    correlation_id = str(uuid.uuid4())
    # Send a request with metadata that is not a ToolProxyInvocationRequest
    event = OnexEvent(
        node_id="test_client",
        event_type=OnexEventTypeEnum.TOOL_PROXY_INVOKE,
        correlation_id=correlation_id,
        metadata={"foo": "bar"},
    )
    event_bus.publish(event)
    rejected = [
        e for e in events if e.event_type == OnexEventTypeEnum.TOOL_PROXY_REJECTED
    ]
    assert rejected, "No TOOL_PROXY_REJECTED event emitted"
    assert rejected[0].metadata.error_code == "INVALID_REQUEST"
    assert rejected[0].correlation_id == correlation_id


def test_discover_tools_returns_tool_collection(event_bus):
    node = NodeRegistryNode(event_bus=event_bus)
    # Register a tool
    tool_name = "test_tool"
    node.registry_state.tools.root[tool_name] = object()  # stub, not type-checked here
    tools = node.discover_tools()
    assert isinstance(tools, ToolCollection)
    assert tool_name in tools.root


def test_proxy_invoke_tool_success(event_bus):
    node = NodeRegistryNode(event_bus=event_bus)
    tool_name = "test_tool"
    node.registry_state.tools.root[tool_name] = object()  # stub
    req = ToolProxyInvocationRequest(
        tool_name=tool_name, arguments={}, correlation_id=str(uuid.uuid4())
    )
    resp = node.proxy_invoke_tool(req)
    assert isinstance(resp, ToolProxyInvocationResponse)
    assert resp.status == OnexStatus.SUCCESS
    assert resp.tool_name == tool_name
    assert "Stub result" in resp.result["message"]


def test_proxy_invoke_tool_not_found(event_bus):
    node = NodeRegistryNode(event_bus=event_bus)
    req = ToolProxyInvocationRequest(
        tool_name="missing_tool", arguments={}, correlation_id=str(uuid.uuid4())
    )
    resp = node.proxy_invoke_tool(req)
    assert resp.status == OnexStatus.ERROR
    assert resp.error_code == "TOOL_NOT_FOUND"


def test_proxy_invoke_tool_provider_not_found(event_bus):
    node = NodeRegistryNode(event_bus=event_bus)
    tool_name = "test_tool"
    # No node registered with this provider_node_id
    req = ToolProxyInvocationRequest(
        tool_name=tool_name,
        arguments={},
        correlation_id=str(uuid.uuid4()),
        provider_node_id="fake-node-id",
    )
    resp = node.proxy_invoke_tool(req)
    assert resp.status == OnexStatus.ERROR
    assert resp.error_code == "PROVIDER_NOT_FOUND"
