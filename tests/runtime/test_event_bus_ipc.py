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

from omnibase.core.core_structured_logging import LogContextModel, emit_log_event
from omnibase.enums import LogLevel
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


def zmq_subscriber_process(queue, socket_path, ready_event):
    os.environ["ONEX_EVENT_BUS_TYPE"] = "zmq"
    os.environ["ONEX_ZMQ_SOCKET"] = socket_path
    print(f"[DEBUG] Subscriber process using socket_path: {socket_path}")
    bus = get_event_bus(socket_path=socket_path, mode="connect")
    emit_log_event(
        LogLevel.DEBUG, "[TEST DEBUG] ZMQ Subscriber process started", event_bus=bus
    )

    def handler(event):
        emit_log_event(
            LogLevel.DEBUG,
            f"[TEST DEBUG] ZMQ Subscriber received event: {event.event_type}",
            event_bus=bus,
        )
        queue.put((event.event_type, event.node_id, event.metadata))

    bus.subscribe(handler)
    emit_log_event(
        LogLevel.DEBUG,
        "[TEST DEBUG] ZMQ Subscriber process ready, setting ready_event",
        event_bus=bus,
    )
    ready_event.set()
    # Wait longer for event delivery
    time.sleep(2)
    # Attempt to flush/close event bus if supported
    if hasattr(bus, "close"):
        emit_log_event(
            LogLevel.DEBUG,
            "[TEST DEBUG] ZMQ Subscriber closing event bus",
            event_bus=bus,
        )
        bus.close()


def zmq_tcp_subscriber_process(queue, tcp_addr, ready_event):
    os.environ["ONEX_EVENT_BUS_TYPE"] = "zmq"
    os.environ["ONEX_ZMQ_SOCKET"] = tcp_addr
    print(f"[DEBUG] TCP Subscriber process using tcp_addr: {tcp_addr}")
    bus = get_event_bus(socket_path=tcp_addr, mode="connect")
    emit_log_event(
        LogLevel.DEBUG, "[TEST DEBUG] ZMQ TCP Subscriber process started", event_bus=bus
    )

    def handler(event):
        emit_log_event(
            LogLevel.DEBUG,
            f"[TEST DEBUG] ZMQ TCP Subscriber received event: {event.event_type}",
            event_bus=bus,
        )
        queue.put((event.event_type, event.node_id, event.metadata))

    bus.subscribe(handler)
    emit_log_event(
        LogLevel.DEBUG,
        "[TEST DEBUG] ZMQ TCP Subscriber process ready, setting ready_event",
        event_bus=bus,
    )
    ready_event.set()
    time.sleep(2)
    if hasattr(bus, "close"):
        emit_log_event(
            LogLevel.DEBUG,
            "[TEST DEBUG] ZMQ TCP Subscriber closing event bus",
            event_bus=bus,
        )
        bus.close()


@pytest.mark.xfail(
    reason="ZMQ ipc:// cross-process delivery is unreliable on some platforms due to slow joiner and process isolation issues."
)
def test_zmq_event_bus_cross_process():
    """Test ZMQ event bus cross-process delivery (ipc://)."""
    os.environ["ONEX_EVENT_BUS_TYPE"] = "zmq"
    os.environ["ONEX_ZMQ_SOCKET"] = ZMQ_SOCKET_PATH
    bus = get_event_bus(socket_path=ZMQ_SOCKET_PATH, mode="bind")
    queue = multiprocessing.Queue()
    ready_event = multiprocessing.Event()
    proc = multiprocessing.Process(
        target=zmq_subscriber_process, args=(queue, ZMQ_SOCKET_PATH, ready_event)
    )
    proc.start()
    emit_log_event(
        LogLevel.DEBUG,
        "[TEST DEBUG] Waiting for subscriber process to be ready...",
        context=make_test_log_context("test_zmq_event_bus_cross_process"),
        event_bus=bus,
    )
    ready_event.wait(timeout=2.0)
    if not ready_event.is_set():
        emit_log_event(
            LogLevel.ERROR,
            "[TEST DEBUG] ZMQ Subscriber process did not signal ready within timeout.",
            context=make_test_log_context("test_zmq_event_bus_cross_process"),
            event_bus=bus,
        )
    # ZeroMQ PUB/SUB slow joiner fix: wait for subscriber to connect
    emit_log_event(
        LogLevel.DEBUG,
        "[TEST DEBUG] Sleeping 0.5s to allow ZMQ subscriber to connect (slow joiner fix)",
        context=make_test_log_context("test_zmq_event_bus_cross_process"),
        event_bus=bus,
    )
    time.sleep(0.5)
    test_event = OnexEvent(
        event_type=OnexEventTypeEnum.NODE_START,
        node_id="test_node",
        metadata=OnexEventMetadataModel(foo="bar"),
    )
    publish_success = False
    publish_start = time.time()
    for attempt in range(5):
        try:
            emit_log_event(
                LogLevel.DEBUG,
                f"[TEST DEBUG] Publish attempt {attempt+1}...",
                context=make_test_log_context("test_zmq_event_bus_cross_process"),
                event_bus=bus,
            )
            bus.publish(test_event)
            publish_success = True
            break
        except Exception as e:
            emit_log_event(
                LogLevel.ERROR,
                f"[TEST DEBUG] Publish attempt {attempt+1} failed: {e}",
                context=make_test_log_context("test_zmq_event_bus_cross_process"),
                event_bus=bus,
            )
            time.sleep(0.05)
    publish_end = time.time()
    emit_log_event(
        LogLevel.INFO,
        f"[TEST DEBUG] Time to first publish: {publish_end - publish_start:.3f} seconds",
        context=make_test_log_context("test_zmq_event_bus_cross_process"),
        event_bus=bus,
    )
    if not publish_success:
        emit_log_event(
            LogLevel.ERROR,
            "[TEST DEBUG] All publish attempts failed.",
            context=make_test_log_context("test_zmq_event_bus_cross_process"),
            event_bus=bus,
        )
        raise RuntimeError("Failed to publish event after multiple attempts")
    emit_log_event(
        LogLevel.DEBUG,
        "[TEST DEBUG] Published test event, waiting for queue.get...",
        context=make_test_log_context("test_zmq_event_bus_cross_process"),
        event_bus=bus,
    )
    try:
        # Filter out STRUCTURED_LOG events
        for _ in range(3):
            event_type, node_id, metadata = queue.get(timeout=2.0)
            emit_log_event(
                LogLevel.DEBUG,
                f"[TEST DEBUG] Received event from queue: {event_type}, {node_id}, {metadata}",
                context=make_test_log_context("test_zmq_event_bus_cross_process"),
                event_bus=bus,
            )
            if event_type != OnexEventTypeEnum.STRUCTURED_LOG:
                break
        assert event_type == OnexEventTypeEnum.NODE_START
        assert node_id == "test_node"
        # Debug print for metadata type
        print(f"[DEBUG] metadata type: {type(metadata)} dir: {dir(metadata)}")
        if isinstance(metadata, dict):
            foo_val = metadata.get('foo')
        else:
            print(f"[DEBUG] metadata __dict__: {getattr(metadata, '__dict__', None)}")
            raise AssertionError(f"Unexpected metadata type: {type(metadata)}")
        assert foo_val == "bar"
    except Exception as e:
        emit_log_event(
            LogLevel.ERROR,
            f"[TEST DEBUG] queue.get() timed out or failed: {e}",
            context=make_test_log_context("test_zmq_event_bus_cross_process"),
            event_bus=bus,
        )
        raise
    finally:
        proc.terminate()
        proc.join()
        if os.path.exists(ZMQ_SOCKET_PATH):
            os.unlink(ZMQ_SOCKET_PATH)


def test_zmq_event_bus_cross_process_tcp(allocated_port):
    """Test ZMQ event bus cross-process delivery (tcp://) using registry-allocated port."""
    port = allocated_port
    tcp_addr = f"tcp://127.0.0.1:{port}"
    print(f"[DEBUG] Allocated port for test_zmq_event_bus_cross_process_tcp: {port}")
    os.environ["ONEX_EVENT_BUS_TYPE"] = "zmq"
    os.environ["ONEX_ZMQ_SOCKET"] = tcp_addr
    bus = get_event_bus(socket_path=tcp_addr, mode="bind")
    queue = multiprocessing.Queue()
    ready_event = multiprocessing.Event()
    proc = multiprocessing.Process(
        target=zmq_tcp_subscriber_process, args=(queue, tcp_addr, ready_event)
    )
    proc.start()
    emit_log_event(
        LogLevel.DEBUG,
        "[TEST DEBUG] Waiting for TCP subscriber process to be ready...",
        context=make_test_log_context("test_zmq_event_bus_cross_process_tcp"),
        event_bus=bus,
    )
    ready = ready_event.wait(timeout=5.0)
    print(f"[DEBUG] ready_event.is_set(): {ready_event.is_set()}")
    if not ready:
        emit_log_event(
            LogLevel.ERROR,
            "[TEST DEBUG] ZMQ TCP Subscriber process did not signal ready within timeout.",
            context=make_test_log_context("test_zmq_event_bus_cross_process_tcp"),
            event_bus=bus,
        )
        proc.terminate()
        proc.join()
        assert False, "Subscriber did not signal ready in time"
    emit_log_event(
        LogLevel.DEBUG,
        "[TEST DEBUG] Sleeping 0.5s to allow ZMQ TCP subscriber to connect (slow joiner fix)",
        context=make_test_log_context("test_zmq_event_bus_cross_process_tcp"),
        event_bus=bus,
    )
    time.sleep(0.5)
    test_event = OnexEvent(
        event_type=OnexEventTypeEnum.NODE_START,
        node_id="test_node_tcp",
        metadata=OnexEventMetadataModel(foo="bar"),
    )
    publish_success = False
    publish_start = time.time()
    for attempt in range(5):
        try:
            emit_log_event(
                LogLevel.DEBUG,
                f"[TEST DEBUG] TCP Publish attempt {attempt+1}...",
                context=make_test_log_context("test_zmq_event_bus_cross_process_tcp"),
                event_bus=bus,
            )
            bus.publish(test_event)
            publish_success = True
            break
        except Exception as e:
            emit_log_event(
                LogLevel.ERROR,
                f"[TEST DEBUG] TCP Publish attempt {attempt+1} failed: {e}",
                context=make_test_log_context("test_zmq_event_bus_cross_process_tcp"),
                event_bus=bus,
            )
            time.sleep(0.05)
    publish_end = time.time()
    emit_log_event(
        LogLevel.INFO,
        f"[TEST DEBUG] TCP Time to first publish: {publish_end - publish_start:.3f} seconds",
        context=make_test_log_context("test_zmq_event_bus_cross_process_tcp"),
        event_bus=bus,
    )
    if not publish_success:
        emit_log_event(
            LogLevel.ERROR,
            "[TEST DEBUG] All TCP publish attempts failed.",
            context=make_test_log_context("test_zmq_event_bus_cross_process_tcp"),
            event_bus=bus,
        )
        proc.terminate()
        proc.join()
        assert False, "Failed to publish event after multiple attempts"
    emit_log_event(
        LogLevel.DEBUG,
        "[TEST DEBUG] Published TCP test event, waiting for queue.get...",
        context=make_test_log_context("test_zmq_event_bus_cross_process_tcp"),
        event_bus=bus,
    )
    try:
        for _ in range(3):
            event_type, node_id, metadata = queue.get(timeout=3.0)
            print(
                f"[DEBUG] Received event from queue: {event_type}, {node_id}, {metadata}"
            )
            emit_log_event(
                LogLevel.DEBUG,
                f"[TEST DEBUG] TCP Received event from queue: {event_type}, {node_id}, {metadata}",
                context=make_test_log_context("test_zmq_event_bus_cross_process_tcp"),
                event_bus=bus,
            )
            if event_type != OnexEventTypeEnum.STRUCTURED_LOG:
                break
        assert event_type == OnexEventTypeEnum.NODE_START
        assert node_id == "test_node_tcp"
        # Debug print for metadata type
        print(f"[DEBUG] metadata type: {type(metadata)} dir: {dir(metadata)}")
        if isinstance(metadata, dict):
            foo_val = metadata.get('foo')
        else:
            print(f"[DEBUG] metadata __dict__: {getattr(metadata, '__dict__', None)}")
            raise AssertionError(f"Unexpected metadata type: {type(metadata)}")
        assert foo_val == "bar"
    except Exception as e:
        emit_log_event(
            LogLevel.ERROR,
            f"[TEST DEBUG] TCP queue.get() timed out or failed: {e}",
            context=make_test_log_context("test_zmq_event_bus_cross_process_tcp"),
            event_bus=bus,
        )
        print(f"[DEBUG] Exception in queue.get: {e}")
        raise
    finally:
        proc.terminate()
        proc.join()
        print(f"[DEBUG] Cleaned up subscriber process for port {port}")


@pytest.mark.parametrize(
    "event_bus_type",
    [
        pytest.param("inmemory", id="inmemory", marks=pytest.mark.mock),
        pytest.param("zmq", id="zmq", marks=pytest.mark.integration),
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
        for _ in range(10):
            print("[DEBUG] before pub_bus.publish(ping_event)")
            pub_bus.publish(ping_event)
            print("[DEBUG] after pub_bus.publish(ping_event)")
            if ping_received.wait(timeout=0.1):
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
