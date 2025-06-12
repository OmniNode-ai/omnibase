"""
Kafka Event Bus – Event Replay Policy

- On reconnection or restart, the Kafka consumer resumes from the last committed offset (using Kafka's consumer group mechanism).
- If the offset is lost or reset, consumption starts from the configured offset reset policy (typically 'earliest' for replay, or 'latest' for only new events).
- Events are retained in Kafka topics for a configurable period (e.g., 7 days) to allow for replay.
- Event handlers must be idempotent to avoid side effects from replayed events.
- In degraded (in-memory) mode, replay is not possible; only live events are processed.
- The node logs when a replay occurs and how many events are replayed (future enhancement: add explicit replay metrics/logs).

Event Keying and Partitioning Strategy:
- Kafka messages are keyed by correlation_id (if present), else node_id, else a default.
- This ensures all events for a given correlation or node are routed to the same partition, preserving order.
- For dev/CI, a single partition is sufficient; for production, use multiple partitions for scalability.
"""

import asyncio
import json
import logging
import random
import string
import typing
from typing import Any, Callable, Optional, List, Dict

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from kafka.admin import KafkaAdminClient
from pydantic import BaseModel

from omnibase.enums.log_level import LogLevelEnum
from omnibase.model.model_onex_event import OnexEvent
from omnibase.model.model_event_bus_config import ModelEventBusConfig
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context
from omnibase.nodes.node_kafka_event_bus.constants import NODE_KAFKA_EVENT_BUS_ID
from ..error_codes import NodeKafkaEventBusNodeErrorCode
from omnibase.core.core_errors import OnexError
from omnibase.nodes.node_logger.protocols.protocol_logger_emit_log_event import ProtocolLoggerEmitLogEvent
from omnibase.nodes.node_logger.v1_0_0.tools.tool_logger_emit_log_event import ToolLoggerEmitLogEvent

if typing.TYPE_CHECKING:
    from omnibase.protocol.protocol_event_bus import ProtocolEventBus


class KafkaHealthCheckResult(BaseModel):
    connected: bool
    error: str = None


class KafkaEventBus:
    """
    Canonical Async Kafka Event Bus implementation for ONEX.
    Implements ProtocolEventBus and emits OnexEvent objects.
    Uses ModelEventBusConfig for all configuration.
    Only async methods are supported; sync methods are not implemented.
    """

    def __init__(self, config: ModelEventBusConfig, logger_tool: ProtocolLoggerEmitLogEvent = None):
        self.config = config
        self.producer = None
        self.consumer = None
        self.logger = logging.getLogger("KafkaEventBus")
        self.bootstrap_servers = config.bootstrap_servers
        self.topics = config.topics
        rand_suffix = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )
        self.group_id = f"{config.group_id}-{rand_suffix}"
        self.connected = False
        self.fallback_bus = None  # InMemoryEventBus for degraded mode
        self.logger_tool = logger_tool or ToolLoggerEmitLogEvent()
        self.logger_tool.emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[KafkaEventBus] (async) Producer/consumer instantiated for this instance only (id={id(self)})",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID),
        )
        self.logger_tool.emit_log_event_sync(
            LogLevelEnum.INFO,
            "[KafkaEventBus] Only async methods are available (publish_async, subscribe_async, etc.)",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID),
        )

    async def connect(self, correlation_id: Optional[str] = None):
        from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync, make_log_context
        emit_log_event_sync(LogLevelEnum.DEBUG, f"[KafkaEventBus] connect() called", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID, correlation_id=correlation_id))
        try:
            from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
            loop = asyncio.get_event_loop()
            self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers, loop=loop)
            await self.producer.start()
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                loop=loop
            )
            await self.consumer.start()
            self.connected = True
            emit_log_event_sync(LogLevelEnum.INFO, f"[KafkaEventBus] Connected to Kafka at {self.bootstrap_servers}", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID, correlation_id=correlation_id))
        except Exception as e:
            emit_log_event_sync(LogLevelEnum.ERROR, f"[KafkaEventBus] connect() failed: {e}", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID, correlation_id=correlation_id))
            self.connected = False

    async def publish(self, message: bytes, key: Optional[bytes] = None):
        """
        Async: Publish a message to the Kafka topic. Delegate to fallback bus in degraded mode.
        - Uses correlation_id (if present) or node_id as the Kafka message key for partitioning.
        """
        if not self.connected:
            if self.fallback_bus:
                return await self.fallback_bus.publish(message)
            self.logger.warning(
                f"KafkaEventBus in degraded mode: publish() is a no-op (no broker connected). Message not sent. [ErrorCode: {NodeKafkaEventBusNodeErrorCode.BACKEND_UNAVAILABLE.value}]"
            )
            return
        if not self.producer:
            raise OnexError(NodeKafkaEventBusNodeErrorCode.BACKEND_UNAVAILABLE, "Kafka producer not connected. Call connect() first.")
        try:
            # Extract key from message if not provided
            if key is None:
                try:
                    event = json.loads(message)
                    key_val = (
                        event.get("correlation_id") or event.get("node_id") or "default"
                    )
                    key = str(key_val).encode()
                except Exception:
                    key = b"default"
            await self.producer.send_and_wait(self.topics[0], message, key=key)
            self.logger.info(f"Published message to {self.topics}")
        except KafkaError as e:
            self.logger.error(f"Kafka publish failed: {e} [ErrorCode: {NodeKafkaEventBusNodeErrorCode.MESSAGE_PUBLISH_FAILED.value}]")
            raise OnexError(NodeKafkaEventBusNodeErrorCode.MESSAGE_PUBLISH_FAILED, "Failed to publish message to Kafka.")

    async def subscribe(self, on_message: Callable[[Any], None]):
        """Async: Subscribe to the Kafka topic and process messages with the given callback. Delegate to fallback bus in degraded mode."""
        if not self.connected:
            if self.fallback_bus:
                return await self.fallback_bus.subscribe(on_message)
            self.logger.warning(
                "KafkaEventBus in degraded mode: subscribe() is a no-op (no broker connected)."
            )
            return
        if not self.consumer:
            raise OnexError(NodeKafkaEventBusNodeErrorCode.BACKEND_UNAVAILABLE, "Kafka consumer not connected. Call connect() with group_id.")
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[KafkaEventBus] Starting async subscribe loop for topics: {self.topics}, group_id: {self.group_id}",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID),
        )
        async for msg in self.consumer:
            try:
                event = OnexEvent.parse_raw(msg.value)
                if asyncio.iscoroutinefunction(on_message):
                    await on_message(event)
                else:
                    on_message(event)
            except Exception as cb_exc:
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"[KafkaEventBus] Exception in event handler callback: {cb_exc}",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID),
                )

    async def close(self):
        """
        Properly close all Kafka resources with comprehensive error handling.
        Ensures no resource leaks occur even if individual cleanup operations fail.
        """
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            "[KafkaEventBus] Starting close() - cleaning up producer and consumer",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
        )
        
        # Handle fallback bus first
        if not self.connected and self.fallback_bus:
            try:
                await self.fallback_bus.close()
                emit_log_event_sync(
                    LogLevelEnum.DEBUG,
                    "[KafkaEventBus] Fallback bus closed successfully",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
            except Exception as e:
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"[KafkaEventBus] Error closing fallback bus: {e}",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
            return
        
        # Close producer with proper error handling
        if self.producer:
            try:
                emit_log_event_sync(
                    LogLevelEnum.DEBUG,
                    f"[KafkaEventBus] Stopping producer (id: {id(self.producer)})",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
                await self.producer.stop()
                emit_log_event_sync(
                    LogLevelEnum.DEBUG,
                    "[KafkaEventBus] Producer stopped successfully",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
            except Exception as e:
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"[KafkaEventBus] Error stopping producer: {e}",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
            finally:
                self.producer = None
        
        # Close consumer with proper error handling
        if self.consumer:
            try:
                emit_log_event_sync(
                    LogLevelEnum.DEBUG,
                    f"[KafkaEventBus] Stopping consumer (id: {id(self.consumer)})",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
                await self.consumer.stop()
                emit_log_event_sync(
                    LogLevelEnum.DEBUG,
                    "[KafkaEventBus] Consumer stopped successfully",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
            except Exception as e:
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"[KafkaEventBus] Error stopping consumer: {e}",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
            finally:
                self.consumer = None
        
        # Update connection state
        self.connected = False
        
        # Allow time for background tasks to complete
        try:
            await asyncio.sleep(0.1)
        except Exception:
            pass  # Ignore sleep errors
        
        emit_log_event_sync(
            LogLevelEnum.INFO,
            "[KafkaEventBus] All Kafka connections closed successfully",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
        )

    async def cleanup_resources(self) -> dict:
        """
        Advanced cleanup of Kafka resources including consumer groups and topics.
        Returns a summary of cleanup operations performed.
        """
        cleanup_summary = {
            "connections_closed": False,
            "consumer_groups_deleted": [],
            "topics_deleted": [],
            "errors": []
        }
        
        try:
            # Close existing connections first
            await self.close()
            cleanup_summary["connections_closed"] = True
            
            # Initialize admin client for cleanup operations
            admin_client = AIOKafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id="onex-cleanup-client"
            )
            await admin_client.start()
            
            try:
                # List and delete consumer groups that match our group prefix
                groups_metadata = await admin_client.list_consumer_groups()
                target_groups = []
                
                for group_metadata in groups_metadata:
                    group_id = group_metadata.group_id
                    # Delete groups that start with our configured group_id prefix
                    base_group_id = self.config.group_id.split('-')[0] if '-' in self.config.group_id else self.config.group_id
                    if group_id.startswith(base_group_id):
                        target_groups.append(group_id)
                
                if target_groups:
                    await admin_client.delete_consumer_groups(target_groups)
                    cleanup_summary["consumer_groups_deleted"] = target_groups
                    emit_log_event_sync(
                        LogLevelEnum.INFO,
                        f"[KafkaEventBus] Deleted consumer groups: {target_groups}",
                        make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                    )
                
                # Optionally delete test topics (only if they match test patterns)
                topics_metadata = await admin_client.list_topics()
                test_topics = []
                
                for topic_name in topics_metadata.topics:
                    # Only delete topics that are clearly test topics
                    if any(pattern in topic_name.lower() for pattern in ['test', 'onex_test', 'temp', 'cleanup']):
                        test_topics.append(topic_name)
                
                if test_topics:
                    await admin_client.delete_topics(test_topics)
                    cleanup_summary["topics_deleted"] = test_topics
                    emit_log_event_sync(
                        LogLevelEnum.INFO,
                        f"[KafkaEventBus] Deleted test topics: {test_topics}",
                        make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                    )
                
            finally:
                await admin_client.close()
            
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[KafkaEventBus] Cleanup completed: {cleanup_summary}",
                make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
            )
            
        except Exception as e:
            error_msg = f"Cleanup error: {e}"
            cleanup_summary["errors"].append(error_msg)
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[KafkaEventBus] {error_msg}",
                make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
            )
        
        return cleanup_summary

    async def list_consumer_groups(self) -> List[Dict[str, Any]]:
        """List all consumer groups with detailed information."""
        try:
            admin_client = AIOKafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id="onex-list-groups-client"
            )
            await admin_client.start()
            
            try:
                groups_metadata = await admin_client.list_consumer_groups()
                groups_info = []
                
                for group_metadata in groups_metadata:
                    group_info = {
                        "group_id": group_metadata.group_id,
                        "group_type": group_metadata.group_type,
                        "state": group_metadata.state,
                        "protocol_type": group_metadata.protocol_type,
                        "is_current_group": group_metadata.group_id == self.group_id
                    }
                    groups_info.append(group_info)
                
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[KafkaEventBus] Listed {len(groups_info)} consumer groups",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
                
                return groups_info
                
            finally:
                await admin_client.close()
            
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[KafkaEventBus] Failed to list consumer groups: {e}",
                make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
            )
            return []

    async def delete_consumer_group(self, group_id: str) -> bool:
        """Delete a specific consumer group."""
        try:
            admin_client = AIOKafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id="onex-delete-group-client"
            )
            await admin_client.start()
            
            try:
                await admin_client.delete_consumer_groups([group_id])
                
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[KafkaEventBus] Successfully deleted consumer group: {group_id}",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
                return True
                
            finally:
                await admin_client.close()
            
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[KafkaEventBus] Failed to delete consumer group {group_id}: {e}",
                make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
            )
            return False

    async def list_topics(self) -> List[Dict[str, Any]]:
        """List all topics with detailed information."""
        try:
            admin_client = AIOKafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id="onex-list-topics-client"
            )
            await admin_client.start()
            
            try:
                topics_metadata = await admin_client.list_topics()
                topics_info = []
                
                for topic_name, topic_metadata in topics_metadata.topics.items():
                    topic_info = {
                        "topic_name": topic_name,
                        "partition_count": len(topic_metadata.partitions),
                        "is_internal": topic_metadata.is_internal,
                        "partitions": [
                            {
                                "partition_id": partition.partition,
                                "leader": partition.leader,
                                "replicas": partition.replicas,
                                "isr": partition.isr
                            }
                            for partition in topic_metadata.partitions.values()
                        ]
                    }
                    topics_info.append(topic_info)
                
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[KafkaEventBus] Listed {len(topics_info)} topics",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
                
                return topics_info
                
            finally:
                await admin_client.close()
            
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[KafkaEventBus] Failed to list topics: {e}",
                make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
            )
            return []

    async def delete_topic(self, topic_name: str) -> bool:
        """Delete a specific topic."""
        try:
            admin_client = AIOKafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id="onex-delete-topic-client"
            )
            await admin_client.start()
            
            try:
                await admin_client.delete_topics([topic_name])
                
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[KafkaEventBus] Successfully deleted topic: {topic_name}",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
                return True
                
            finally:
                await admin_client.close()
            
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[KafkaEventBus] Failed to delete topic {topic_name}: {e}",
                make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
            )
            return False

    async def create_topic(self, topic_name: str, num_partitions: int = 1, replication_factor: int = 1) -> bool:
        """Create a new topic with specified configuration."""
        try:
            admin_client = AIOKafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id="onex-create-topic-client"
            )
            await admin_client.start()
            
            try:
                new_topic = NewTopic(
                    name=topic_name,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor
                )
                
                await admin_client.create_topics([new_topic])
                
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[KafkaEventBus] Successfully created topic: {topic_name} (partitions: {num_partitions}, replication: {replication_factor})",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
                )
                return True
                
            finally:
                await admin_client.close()
            
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[KafkaEventBus] Failed to create topic {topic_name}: {e}",
                make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
            )
            return False

    async def health_check(self) -> KafkaHealthCheckResult:
        """Async health check: try to connect to Kafka broker and return status."""
        from aiokafka.errors import KafkaConnectionError

        try:
            producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
            await producer.start()
            await producer.stop()
            return KafkaHealthCheckResult(connected=True)
        except KafkaConnectionError as e:
            return KafkaHealthCheckResult(connected=False, error=str(e))
        except Exception as e:
            return KafkaHealthCheckResult(connected=False, error=str(e))

    # --- Protocol-compliant async methods ---
    async def publish_async(self, event: OnexEvent) -> None:
        # Serialize event to bytes and publish
        message = event.model_dump_json().encode()
        if not self.connected:
            emit_log_event_sync(LogLevelEnum.WARNING, f"[KafkaEventBus] publish_async: not connected, fallback or no-op", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
            if self.fallback_bus:
                await self.fallback_bus.publish_async(event)
            else:
                self.logger.warning("KafkaEventBus in degraded mode: publish_async() is a no-op (no broker connected). Message not sent.")
            return
        if not self.producer:
            emit_log_event_sync(LogLevelEnum.ERROR, f"[KafkaEventBus] publish_async: producer not connected", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
            raise OnexError(NodeKafkaEventBusNodeErrorCode.BACKEND_UNAVAILABLE, "Kafka producer not connected. Call connect() first.")
        try:
            # Extract key from event
            key_val = getattr(event, "correlation_id", None) or getattr(event, "node_id", None) or "default"
            key = str(key_val).encode()
            await self.producer.send_and_wait(self.topics[0], message, key=key)
            emit_log_event_sync(LogLevelEnum.INFO, f"[KafkaEventBus] Published message to {self.topics}", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
        except KafkaError as e:
            emit_log_event_sync(LogLevelEnum.ERROR, f"[KafkaEventBus] Kafka publish failed: {e}", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
            self.logger.error(f"Kafka publish failed: {e}")
            raise

    async def subscribe_async(self, callback: Callable[[OnexEvent], None]) -> None:
        from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync, make_log_context
        emit_log_event_sync(LogLevelEnum.DEBUG, f"[KafkaEventBus] subscribe_async called. Connected: {self.connected}, Consumer: {self.consumer}", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
        if not self.connected:
            emit_log_event_sync(LogLevelEnum.WARNING, f"[KafkaEventBus] subscribe_async: not connected, fallback or no-op", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
            if self.fallback_bus:
                await self.fallback_bus.subscribe_async(callback)
            else:
                self.logger.warning("KafkaEventBus in degraded mode: subscribe_async() is a no-op (no broker connected).")
            return
        if not self.consumer:
            emit_log_event_sync(LogLevelEnum.ERROR, f"[KafkaEventBus] subscribe_async: consumer not connected", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
            raise OnexError(NodeKafkaEventBusNodeErrorCode.BACKEND_UNAVAILABLE, "Kafka consumer not connected. Call connect() with group_id.")
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[KafkaEventBus] Starting async subscribe loop for topics: {self.topics}, group_id: {self.group_id}",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID),
        )
        async for msg in self.consumer:
            try:
                emit_log_event_sync(LogLevelEnum.DEBUG, f"[KafkaEventBus] Received message: {msg}", context=make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID))
                event = OnexEvent.parse_raw(msg.value)
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as cb_exc:
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"[KafkaEventBus] Exception in event handler callback: {cb_exc}",
                    make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID),
                )

    async def unsubscribe_async(self, callback: Callable[[OnexEvent], None]) -> None:
        # Not implemented for Kafka (would require consumer group management)
        raise OnexError(NodeKafkaEventBusNodeErrorCode.UNSUPPORTED_OPERATION, "unsubscribe_async is not implemented for KafkaEventBus.")

    @property
    def bus_id(self) -> str:
        return f"kafka:{self.bootstrap_servers}:{self.group_id}"


# TODO: Add partitioning, ack, error handling, and advanced features as per checklist.
