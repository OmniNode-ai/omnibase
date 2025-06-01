import pytest
from uuid import uuid4
from omnibase.nodes.node_registry_node.v1_0_0.port_manager import PortManager
from omnibase.nodes.node_registry_node.v1_0_0.models.state import PortRequestModel
from omnibase.nodes.node_registry_node.v1_0_0.models.port_usage import PortUsageEntry
from omnibase.core.core_error_codes import OnexError, CoreErrorCode
from omnibase.model.model_onex_event import OnexEventTypeEnum, OnexEvent, OnexEventMetadataModel
from omnibase.fixtures.port_manager_fixtures import event_bus, port_manager
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_function_tool import FunctionTool, ToolTypeEnum, FunctionLanguageEnum
from omnibase.model.model_tool_collection import ToolCollection
import datetime

def test_port_allocation_success(port_manager):
    requester_id = uuid4()
    request = PortRequestModel(
        requester_id=requester_id,
        protocol="zmq",
        preferred_port=None,
        ttl=60
    )
    lease = port_manager.request_port(request)
    assert lease.assigned_to == str(requester_id)
    assert lease.protocol == "zmq"
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
        requester_id=requester_id,
        protocol="zmq",
        preferred_port=50010,
        ttl=60
    )
    port_manager.request_port(request)
    assert any(e.event_type == OnexEventTypeEnum.STRUCTURED_LOG and e.metadata.status == "allocated" for e in events)
    found = [e for e in events if e.metadata and e.metadata.status == "allocated"]
    assert found
    event = found[0]
    assert event.metadata.input_state["lease"]["port"] == 50010
    assert event.metadata.status == "allocated"
    assert f"Port 50010 allocated to {requester_id}" in event.metadata.result_summary

def test_port_allocation_updates_usage_map(port_manager):
    requester_id = uuid4()
    request = PortRequestModel(
        requester_id=requester_id,
        protocol="zmq",
        preferred_port=50001,
        ttl=60
    )
    lease = port_manager.request_port(request)
    assert lease.port == 50001
    assert lease.assigned_to == str(requester_id)
    assert 50001 in port_manager.port_usage_map.ports
    entry = port_manager.port_usage_map.ports[50001]
    assert entry.node_id == requester_id
    assert entry.protocol == "zmq"
    assert entry.status == "active"

def test_port_allocation_collision(port_manager):
    requester1 = uuid4()
    requester2 = uuid4()
    req1 = PortRequestModel(
        requester_id=requester1,
        protocol="zmq",
        preferred_port=50002,
        ttl=60
    )
    req2 = PortRequestModel(
        requester_id=requester2,
        protocol="zmq",
        preferred_port=50002,
        ttl=60
    )
    port_manager.request_port(req1)
    with pytest.raises(OnexError) as excinfo:
        port_manager.request_port(req2)
    assert excinfo.value.error_code == CoreErrorCode.RESOURCE_EXHAUSTED

def test_port_release_removes_from_usage_map(port_manager):
    requester_id = uuid4()
    request = PortRequestModel(
        requester_id=requester_id,
        protocol="zmq",
        preferred_port=50003,
        ttl=60
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
        requester_id=requester_id,
        protocol="zmq",
        preferred_port=50004,
        ttl=60
    )
    port_manager.request_port(request)
    usage_map = port_manager.introspect_port_usage()
    assert 50004 in usage_map.ports
    entry = usage_map.ports[50004]
    assert entry.node_id == requester_id
    assert entry.protocol == "zmq"
    assert entry.status == "active"

def test_port_release_emits_event(port_manager, event_bus):
    events = []
    event_bus.subscribe(lambda e: events.append(e))
    requester_id = uuid4()
    request = PortRequestModel(
        requester_id=requester_id,
        protocol="zmq",
        preferred_port=50011,
        ttl=60
    )
    lease = port_manager.request_port(request)
    port_manager.release_port(lease.lease_id)
    assert any(e.event_type == OnexEventTypeEnum.STRUCTURED_LOG and e.metadata.status == "released" for e in events)
    found = [e for e in events if e.metadata and e.metadata.status == "released"]
    assert found
    event = found[0]
    assert event.metadata.status == "released"
    assert f"Port lease {lease.lease_id} released" in event.metadata.result_summary

def test_registry_node_introspection_response():
    from omnibase.nodes.node_registry_node.v1_0_0.node import NodeRegistryNode
    node = NodeRegistryNode()
    response = node.get_introspection()
    required_fields = [
        "node_metadata", "contract", "ports", "event_buses", "port_usage", "registry", "trust_status"
    ]
    missing = [f for f in required_fields if f not in response]
    assert not missing, f"Missing fields in introspection response: {missing}\nFull response: {response}"
    # Optionally, check that node_metadata and contract have expected keys
    assert isinstance(response["node_metadata"], dict)
    assert isinstance(response["contract"], dict)
    # Print for debug if test fails
    if missing:
        print("Introspection response:", response)

def test_registry_state_tracks_port_metadata():
    from omnibase.nodes.node_registry_node.v1_0_0.node import NodeRegistryNode
    from omnibase.nodes.node_registry_node.v1_0_0.models.state import PortRequestModel
    from uuid import uuid4
    node = NodeRegistryNode()
    requester_id = uuid4()
    request = PortRequestModel(
        requester_id=requester_id,
        protocol="zmq",
        preferred_port=50020,
        ttl=60
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
    from omnibase.nodes.node_registry_node.v1_0_0.node import NodeRegistryNode
    node = NodeRegistryNode()
    response = node.get_introspection()
    assert "tools" in response, f"tools field missing in introspection: {response.keys()}"
    assert isinstance(response["tools"], dict), f"tools field is not a dict: {type(response['tools'])}"

def test_registry_node_aggregates_tools_from_node_announce():
    from omnibase.nodes.node_registry_node.v1_0_0.node import NodeRegistryNode
    from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum, NodeAnnounceMetadataModel
    from omnibase.model.model_node_metadata import NodeMetadataBlock
    from uuid import uuid4
    import datetime
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
        side_effects=[]
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
        hash="0"*64,
        entrypoint="python://test.test_node.main",
        namespace="python://test.test_node",
        meta_type="tool"
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
    node = NodeRegistryNode()
    event = OnexEvent(
        node_id=announce.node_id,
        event_type=OnexEventTypeEnum.NODE_ANNOUNCE,
        metadata=OnexEventMetadataModel(**announce.model_dump())
    )
    node.handle_node_announce(event)
    # The tool should now be in the registry's global tools
    assert tool_name in node.registry_state.tools.root, f"Tool {tool_name} not found in registry tools: {node.registry_state.tools.root.keys()}"
    # Introspection should also include the tool
    response = node.get_introspection()
    assert tool_name in response["tools"], f"Tool {tool_name} not found in introspection tools: {response['tools'].keys()}" 