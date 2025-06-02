import atexit
import datetime
import hashlib
import inspect
import os
import threading
import time
from typing import Callable, List, Optional
import uuid

import zmq

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums.log_level import LogLevel
from omnibase.model.model_log_entry import LogContextModel
from omnibase.model.model_onex_event import OnexEvent
from omnibase.protocol.protocol_event_bus_types import (
    EventBusCredentialsModel,
    ProtocolEventBus,
)


class ZmqEventBus(ProtocolEventBus):
    """
    ZMQ-backed Event Bus using Unix domain sockets (ipc://) or TCP (tcp://) for cross-process event delivery.
    Implements ProtocolEventBus for protocol-pure ONEX eventing.
    Uses PUB/SUB pattern for event emission and subscription.

    mode: "bind" (publisher) or "connect" (subscriber)
    # TODO: Future: Add message persistence, authentication, multi-tenant support, and pluggable broker backends.
    """

    def __init__(
        self,
        socket_path: Optional[str] = None,
        credentials: Optional[EventBusCredentialsModel] = None,
        mode: str = "bind",
    ):
        self._bus_id = str(uuid.uuid4())
        self._waited_for_ready = False
        self.socket_path = socket_path or os.getenv(
            "ONEX_ZMQ_SOCKET", "/tmp/onex_eventbus_zmq.sock"
        )
        self.credentials = credentials
        self.mode = mode
        self._subscribers: List[Callable[[OnexEvent], None]] = []
        self._ctx = zmq.Context()
        self._pub = self._ctx.socket(zmq.PUB)
        self._sub_threads: List[threading.Thread] = []
        self._stop_event = threading.Event()
        # --- Handshake and ready file attributes must be set before any log events ---
        bind_addr = self._resolve_bind_addr(self.socket_path)
        self._handshake_timeout = float(os.getenv("ONEX_ZMQ_HANDSHAKE_TIMEOUT", "2.0"))
        if bind_addr.startswith("ipc://"):
            self._ready_file = f"/tmp/onex_zmq_ready_{hashlib.sha256(self.socket_path.encode()).hexdigest()[:8]}"
        else:
            self._ready_file = None
        # --- Robust socket file cleanup before bind (only for ipc) ---
        if self.mode == "bind":
            if bind_addr.startswith("ipc://"):
                ipc_path = bind_addr[len("ipc://") :]
                if ipc_path and ipc_path.startswith("/"):
                    try:
                        if os.path.exists(ipc_path):
                            os.unlink(ipc_path)
                    except Exception as e:
                        emit_log_event(
                            LogLevel.WARNING,
                            f"Failed to cleanup ZMQ socket file before bind: {e}",
                            context=LogContextModel(
                                timestamp=datetime.datetime.now(
                                    datetime.timezone.utc
                                ).isoformat(),
                                calling_module=__name__,
                                calling_function="__init__",
                                calling_line=inspect.currentframe().f_lineno,
                                event_bus_type="zmq",
                                operation="pre_bind_cleanup",
                                socket_path=self.socket_path,
                                process_id=os.getpid(),
                                mode=self.mode,
                            ),
                            event_bus=self,
                        )
            self._pub.bind(bind_addr)
            emit_log_event(
                LogLevel.INFO,
                f"ZmqEventBus publisher bound to {bind_addr} (mode={self.mode})",
                context=LogContextModel(
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    calling_module=__name__,
                    calling_function="__init__",
                    calling_line=inspect.currentframe().f_lineno,
                    event_bus_type="zmq",
                    operation="bind",
                    socket_path=self.socket_path,
                    bind_addr=bind_addr,
                    process_id=os.getpid(),
                    mode=self.mode,
                ),
                event_bus=self,
            )
            # Register atexit cleanup
            atexit.register(self.close)
            emit_log_event(
                LogLevel.INFO,
                f"ZmqEventBus sleeping 1.0s after PUB bind to ensure socket is ready (ZeroMQ pattern)",
                context=LogContextModel(
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    calling_module=__name__,
                    calling_function="__init__",
                    calling_line=inspect.currentframe().f_lineno,
                    event_bus_type="zmq",
                    operation="post_bind_sleep",
                    socket_path=self.socket_path,
                    bind_addr=bind_addr,
                    process_id=os.getpid(),
                    mode=self.mode,
                ),
                event_bus=self,
            )
            time.sleep(1.0)
        else:
            emit_log_event(
                LogLevel.INFO,
                f"ZmqEventBus subscriber initialized for connect to {bind_addr} (mode={self.mode})",
                context=LogContextModel(
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    calling_module=__name__,
                    calling_function="__init__",
                    calling_line=inspect.currentframe().f_lineno,
                    event_bus_type="zmq",
                    operation="subscriber_init",
                    socket_path=self.socket_path,
                    bind_addr=bind_addr,
                    process_id=os.getpid(),
                    mode=self.mode,
                ),
                event_bus=self,
            )

    def _resolve_bind_addr(self, socket_path: str) -> str:
        if socket_path.startswith("tcp://"):
            return socket_path
        elif socket_path.startswith("ipc://"):
            return socket_path
        elif socket_path.startswith("/"):
            return f"ipc://{socket_path}"
        else:
            raise ValueError(f"Unsupported ZMQ socket path: {socket_path}")

    def _wait_for_ready(self):
        if self._waited_for_ready:
            return
        start = time.time()
        while time.time() - start < self._handshake_timeout:
            if self._ready_file and os.path.exists(self._ready_file):
                emit_log_event(
                    LogLevel.INFO,
                    f"ZmqEventBus detected subscriber ready file: {self._ready_file}",
                    context=LogContextModel(
                        timestamp=datetime.datetime.now(
                            datetime.timezone.utc
                        ).isoformat(),
                        calling_module=__name__,
                        calling_function="_wait_for_ready",
                        calling_line=inspect.currentframe().f_lineno,
                        event_bus_type="zmq",
                        operation="handshake_ready",
                        socket_path=self.socket_path,
                        process_id=os.getpid(),
                    ),
                    event_bus=self,
                )
                self._waited_for_ready = True
                return
            time.sleep(0.05)
        emit_log_event(
            LogLevel.WARNING,
            f"ZmqEventBus did not detect subscriber ready file after {self._handshake_timeout}s: {self._ready_file}",
            context=LogContextModel(
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                calling_module=__name__,
                calling_function="_wait_for_ready",
                calling_line=inspect.currentframe().f_lineno,
                event_bus_type="zmq",
                operation="handshake_timeout",
                socket_path=self.socket_path,
                process_id=os.getpid(),
            ),
            event_bus=self,
        )
        self._waited_for_ready = True

    def close(self):
        """
        Cleanly shutdown all sockets, threads, and remove the socket file.
        """
        self._stop_event.set()
        for t in self._sub_threads:
            t.join(timeout=1)
        # Emit log event BEFORE closing sockets/context
        emit_log_event(
            LogLevel.INFO,
            "ZmqEventBus closed and cleaned up",
            context=LogContextModel(
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                calling_module=__name__,
                calling_function="close",
                calling_line=inspect.currentframe().f_lineno,
                event_bus_type="zmq",
                operation="close",
                socket_path=self.socket_path,
                process_id=os.getpid(),
            ),
            event_bus=self,
        )
        try:
            self._pub.close(linger=0)
        except Exception:
            pass
        try:
            self._ctx.term()
        except Exception:
            pass
        # Remove the socket file
        if self.socket_path and self.socket_path.startswith("/"):
            try:
                if os.path.exists(self.socket_path):
                    os.unlink(self.socket_path)
            except Exception:
                pass

    def publish(self, event: OnexEvent) -> None:
        self._wait_for_ready()
        # Inline event serialization for ZMQ transport (future: use a wrapper if needed)
        data = event.model_dump_json()
        emit_log_event(
            LogLevel.DEBUG,
            "ZmqEventBus publish called",
            context=LogContextModel(
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                calling_module=__name__,
                calling_function="publish",
                calling_line=inspect.currentframe().f_lineno,
                event_bus_type="zmq",
                operation="publish",
                event_type=getattr(event, "event_type", None),
                credentials_present=self.credentials is not None,
            ),
            event_bus=self,
        )
        self._pub.send_string(data)

    def subscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        """
        Start a background thread to receive events and invoke the callback.
        """

        def listen():
            sub = self._ctx.socket(zmq.SUB)
            connect_addr = self._resolve_bind_addr(self.socket_path)
            if self.mode == "connect":
                sub.connect(connect_addr)
                emit_log_event(
                    LogLevel.INFO,
                    f"ZmqEventBus subscriber thread connecting to {connect_addr} (mode={self.mode})",
                    context=LogContextModel(
                        timestamp=datetime.datetime.now(
                            datetime.timezone.utc
                        ).isoformat(),
                        calling_module=__name__,
                        calling_function="listen",
                        calling_line=inspect.currentframe().f_lineno,
                        event_bus_type="zmq",
                        operation="subscriber_thread_start",
                        socket_path=self.socket_path,
                        connect_addr=connect_addr,
                        process_id=os.getpid(),
                        thread_id=threading.get_ident(),
                        mode=self.mode,
                    ),
                    event_bus=self,
                )
            else:
                emit_log_event(
                    LogLevel.ERROR,
                    f"ZmqEventBus subscribe called in mode={self.mode}, expected 'connect' for subscriber.",
                    context=LogContextModel(
                        timestamp=datetime.datetime.now(
                            datetime.timezone.utc
                        ).isoformat(),
                        calling_module=__name__,
                        calling_function="listen",
                        calling_line=inspect.currentframe().f_lineno,
                        event_bus_type="zmq",
                        operation="subscriber_thread_error",
                        socket_path=self.socket_path,
                        connect_addr=connect_addr,
                        process_id=os.getpid(),
                        thread_id=threading.get_ident(),
                        mode=self.mode,
                    ),
                    event_bus=self,
                )
                return
            sub.setsockopt_string(zmq.SUBSCRIBE, "")
            # --- File-based readiness handshake: create ready file (only for ipc) ---
            if connect_addr.startswith("ipc://") and self._ready_file:
                try:
                    with open(self._ready_file, "w") as f:
                        f.write(f"ready {os.getpid()} {time.time()}\n")
                except Exception:
                    pass
            while not self._stop_event.is_set():
                try:
                    msg = sub.recv_string(flags=zmq.NOBLOCK)
                    # Directly parse OnexEvent (future: use a wrapper if needed)
                    event_obj = OnexEvent.model_validate_json(msg)
                    callback(event_obj)
                except zmq.Again:
                    continue
                except Exception as e:
                    emit_log_event(
                        LogLevel.ERROR,
                        f"ZmqEventBus subscriber error: {e}",
                        context=LogContextModel(
                            timestamp=datetime.datetime.now(
                                datetime.timezone.utc
                            ).isoformat(),
                            calling_module=__name__,
                            calling_function="listen",
                            calling_line=inspect.currentframe().f_lineno,
                            event_bus_type="zmq",
                            operation="subscriber_thread_error",
                            socket_path=self.socket_path,
                            connect_addr=connect_addr,
                            process_id=os.getpid(),
                            thread_id=threading.get_ident(),
                            mode=self.mode,
                        ),
                        event_bus=self,
                    )
            # --- Remove ready file on shutdown (only for ipc) ---
            if connect_addr.startswith("ipc://") and self._ready_file:
                try:
                    if os.path.exists(self._ready_file):
                        os.unlink(self._ready_file)
                except Exception:
                    pass

        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
        self._subscribers.append(callback)
        self._sub_threads.append(thread)
        emit_log_event(
            LogLevel.DEBUG,
            "ZmqEventBus subscribe called",
            context=LogContextModel(
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                calling_module=__name__,
                calling_function="subscribe",
                calling_line=inspect.currentframe().f_lineno,
                event_bus_type="zmq",
                operation="subscribe",
                subscriber_id=id(callback),
                credentials_present=self.credentials is not None,
                mode=self.mode,
            ),
            event_bus=self,
        )

    def unsubscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        # Not implemented: would require tracking and stopping the thread for this callback
        emit_log_event(
            LogLevel.WARNING,
            "ZmqEventBus unsubscribe called (not implemented)",
            context=LogContextModel(
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                calling_module=__name__,
                calling_function="unsubscribe",
                calling_line=inspect.currentframe().f_lineno,
                event_bus_type="zmq",
                operation="unsubscribe",
                subscriber_id=id(callback),
                credentials_present=self.credentials is not None,
            ),
            event_bus=self,
        )

    def clear(self) -> None:
        self._stop_event.set()
        for t in self._sub_threads:
            t.join(timeout=1)
        self._subscribers.clear()
        self._sub_threads.clear()
        emit_log_event(
            LogLevel.INFO,
            "ZmqEventBus clear called",
            context=LogContextModel(
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                calling_module=__name__,
                calling_function="clear",
                calling_line=inspect.currentframe().f_lineno,
                event_bus_type="zmq",
                operation="clear",
                credentials_present=self.credentials is not None,
            ),
            event_bus=self,
        )

    @property
    def bus_id(self) -> str:
        return self._bus_id
