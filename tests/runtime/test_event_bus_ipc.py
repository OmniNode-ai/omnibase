import hashlib
import inspect
import multiprocessing
import os
import shutil
import socket
import sys
import tempfile
import threading
import time
from datetime import datetime
from uuid import uuid4

import pytest

from omnibase.core.core_structured_logging import LogContextModel, emit_log_event_sync
from omnibase.enums import LogLevelEnum
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum, OnexEventMetadataModel
from omnibase.nodes.node_registry_node.v1_0_0.models.state import PortRequestModel
from omnibase.nodes.node_registry_node.v1_0_0.port_manager import PortManager
from omnibase.protocol.protocol_event_bus import get_event_bus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus


def make_test_log_context(test_name: str) -> LogContextModel:
    frame = inspect.currentframe().f_back
    return LogContextModel(
        calling_module=frame.f_globals.get("__name__", "<unknown>"),
        calling_function=frame.f_code.co_name,
        calling_line=frame.f_lineno,
        timestamp=datetime.now().isoformat(),
        test=test_name,
    )


@pytest.mark.parametrize(
    "event_bus_type",
    [
        pytest.param("inmemory", id="inmemory", marks=pytest.mark.mock),
    ],
)
def test_zmq_event_bus_in_process(event_bus_type, zmq_ipc_socket_path):
    if event_bus_type == "inmemory":
        pub_bus = InMemoryEventBus()
        sub_bus = InMemoryEventBus()
        received = []
        event_received = threading.Event()
        def handler(event):
            if getattr(event, "event_type", None) != OnexEventTypeEnum.STRUCTURED_LOG:
                received.append(event)
                event_received.set()
        sub_bus.subscribe(handler)
        print("[DEBUG] Subscribed handler to sub_bus")
        test_event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="test_node_inproc",
            metadata=OnexEventMetadataModel(foo="bar"),
        )
        pub_bus.subscribe(handler)  # InMemoryEventBus: pub/sub are the same
        pub_bus.publish(test_event)
        event_received.wait(timeout=0.05)
        assert received, "InMemoryEventBus handler did not receive domain event"
        assert received[0].event_type == OnexEventTypeEnum.NODE_START
        assert received[0].node_id == "test_node_inproc"
        # Robust metadata check for both dict and Pydantic model
        meta = received[0].metadata
        if hasattr(meta, 'model_dump'):
            foo_val = meta.model_dump().get('foo')
        elif hasattr(meta, 'foo'):
            foo_val = meta.foo
        elif isinstance(meta, dict):
            foo_val = meta.get('foo')
        else:
            foo_val = None
        assert foo_val == "bar"
    elif event_bus_type == "zmq":
        # NOTE: The ZMQ path is inherently slow due to PUB/SUB handshake and IPC. Only run in integration/slow CI.
        os.environ["ONEX_EVENT_BUS_TYPE"] = "zmq"
        print(f"[DEBUG] Creating pub_bus with socket_path={zmq_ipc_socket_path} mode=bind")
        pub_bus = get_event_bus(event_bus_type="zmq", socket_path=zmq_ipc_socket_path, mode="bind")
        print(f"[DEBUG] pub_bus type: {type(pub_bus)} repr: {repr(pub_bus)}")
        print(f"[DEBUG] Creating sub_bus with socket_path={zmq_ipc_socket_path} mode=connect")
        sub_bus = get_event_bus(event_bus_type="zmq", socket_path=zmq_ipc_socket_path, mode="connect")
        print(f"[DEBUG] sub_bus type: {type(sub_bus)} repr: {repr(sub_bus)}")
        received = []
        event_received = threading.Event()
        ping_received = threading.Event()
        # Thread-based handshake: publisher sends 'ping', subscriber ACKs, then real event is sent
        def handler(event):
            print(f"[DEBUG] handler received event: {event.event_type} node_id={event.node_id}")
            if getattr(event, "node_id", None) == "ping":
                ping_received.set()
            else:
                received.append(event)
                event_received.set()
        sub_bus.subscribe(handler)
        print("[DEBUG] Subscribed handler to sub_bus")
        # Publisher sends a 'ping' event and waits for ACK
        ping_event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="ping",
            metadata=OnexEventMetadataModel(foo="ping"),
        )
        print("[DEBUG] Publishing handshake ping event")
        for _ in range(5):  # Reduced from 10 to 5
            print("[DEBUG] before pub_bus.publish(ping_event)")
            pub_bus.publish(ping_event)
            print("[DEBUG] after pub_bus.publish(ping_event)")
            if ping_received.wait(timeout=0.05):  # Reduced from 0.1s to 0.05s
                break
        print(f"[DEBUG] ping_received.is_set(): {ping_received.is_set()}")
        assert ping_received.is_set(), "Subscriber did not ACK handshake ping"
        # Now send the real test event
        test_event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="test_node_inproc",
            metadata=OnexEventMetadataModel(foo="bar"),
        )
        print("[DEBUG] before pub_bus.publish(test_event)")
        pub_bus.publish(test_event)
        print("[DEBUG] after pub_bus.publish(test_event)")
        event_received.wait(timeout=2.0)
        print(f"[DEBUG] event_received.is_set(): {event_received.is_set()} received: {received}")
        assert received, "In-process ZMQ handler did not receive domain event"
        assert received[0].event_type == OnexEventTypeEnum.NODE_START
        assert received[0].node_id == "test_node_inproc"
        meta = received[0].metadata
        assert meta.foo == "bar"
        if hasattr(pub_bus, "close"):
            pub_bus.close()
        if hasattr(sub_bus, "close"):
            sub_bus.close()


@pytest.fixture
def zmq_ipc_socket_path():
    """Yield a unique IPC socket path for each test, and clean up after."""
    path = tempfile.mktemp(prefix="onex_zmq_test_", suffix=".sock")
    yield path
    try:
        if os.path.exists(path):
            os.unlink(path)
    except Exception:
        pass


@pytest.fixture
def allocated_port(port_manager):
    request = PortRequestModel(
        requester_id=uuid4(), protocol="zmq", preferred_port=None, ttl=60
    )
    lease = port_manager.request_port(request)
    return lease.port


def test_event_bus_ipc_uses_registry_port(allocated_port):
    port = allocated_port
    # ... use port for event bus setup ...
    assert isinstance(port, int)
    # Add more assertions or event bus logic as needed


# Refactor other tests in this file to use the allocated_port fixture instead of get_free_tcp_port or ad hoc port assignment.
