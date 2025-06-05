from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import ModelKafkaEventBusConfig
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.model_kafka_event_bus_bootstrap_result import ModelKafkaEventBusBootstrapResult
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync
from omnibase.nodes.node_kafka_event_bus.protocols.tool_bootstrap_protocol import ToolBootstrapProtocol
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError, TopicAlreadyExistsError, NoBrokersAvailable

class ToolBootstrap(ToolBootstrapProtocol):
    """
    Protocol-compliant bootstrap tool for the Kafka event bus node.
    Usage:
        result = tool_bootstrap.bootstrap_kafka_cluster(config)
    """
    def bootstrap_kafka_cluster(self, config: ModelKafkaEventBusConfig) -> ModelKafkaEventBusBootstrapResult:
        emit_log_event_sync(LogLevelEnum.INFO, "[tool_bootstrap] Kafka bootstrap called.")
        admin = None
        try:
            admin = KafkaAdminClient(bootstrap_servers=config.bootstrap_servers)
            existing_topics = set(admin.list_topics())
            topics_to_create = [
                NewTopic(name=topic, num_partitions=1, replication_factor=1)
                for topic in config.topics if topic not in existing_topics
            ]
            created_topics = []
            if topics_to_create:
                try:
                    admin.create_topics(new_topics=topics_to_create, validate_only=False)
                    created_topics = [t.name for t in topics_to_create]
                    emit_log_event_sync(LogLevelEnum.INFO, f"[tool_bootstrap] Created topics: {created_topics}")
                except TopicAlreadyExistsError:
                    pass
                except KafkaError as e:
                    emit_log_event_sync(LogLevelEnum.ERROR, f"[tool_bootstrap] Error creating topics: {e}")
                    return ModelKafkaEventBusBootstrapResult(status="error", message=f"Error creating topics: {e}")
            emit_log_event_sync(LogLevelEnum.INFO, f"[tool_bootstrap] Kafka bootstrap complete. Existing topics: {list(existing_topics)}")
            return ModelKafkaEventBusBootstrapResult(status="ok", message=f"Bootstrap complete. Created: {created_topics}, Existing: {list(existing_topics)}")
        except NoBrokersAvailable as e:
            emit_log_event_sync(LogLevelEnum.ERROR, f"[tool_bootstrap] Kafka broker not available: {e}")
            return ModelKafkaEventBusBootstrapResult(status="error", message=f"No brokers available: {e}")
        except KafkaError as e:
            emit_log_event_sync(LogLevelEnum.ERROR, f"[tool_bootstrap] Kafka error during bootstrap: {e}")
            return ModelKafkaEventBusBootstrapResult(status="error", message=f"Kafka error: {e}")
        except Exception as e:
            emit_log_event_sync(LogLevelEnum.ERROR, f"[tool_bootstrap] Unexpected error during Kafka bootstrap: {e}")
            return ModelKafkaEventBusBootstrapResult(status="error", message=f"Unexpected error: {e}")
        finally:
            try:
                if admin:
                    admin.close()
            except Exception:
                pass

# Singleton instance
tool_bootstrap = ToolBootstrap() 