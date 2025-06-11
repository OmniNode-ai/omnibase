import asyncio
import threading
from .tool_kafka_event_bus import KafkaEventBus

class SyncKafkaEventBus:
    def __init__(self, config):
        self._async_bus = KafkaEventBus(config)
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()
        # Connect asynchronously
        fut = asyncio.run_coroutine_threadsafe(self._async_bus.connect(), self._loop)
        fut.result()  # Wait for connection

    def publish(self, event):
        fut = asyncio.run_coroutine_threadsafe(self._async_bus.publish_async(event), self._loop)
        return fut.result()

    def subscribe(self, callback):
        fut = asyncio.run_coroutine_threadsafe(self._async_bus.subscribe_async(callback), self._loop)
        return fut.result()

    def close(self):
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join() 