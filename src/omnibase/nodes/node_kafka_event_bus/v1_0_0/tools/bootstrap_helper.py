from aiokafka.errors import KafkaError
# TODO: Replace with AIOKafkaAdminClient when available in aiokafka
# from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import KafkaEventBusConfigModel
import logging
from typing import List, Dict, Any

logger = logging.getLogger("KafkaBootstrapHelper")

def bootstrap_kafka_cluster(config: KafkaEventBusConfigModel) -> Dict[str, Any]:
    """
    Bootstrap Kafka cluster for ONEX node:
    - Verifies broker availability
    - Checks for required topics (creates if missing)
    - Returns status and error info
    - Idempotent and safe to call multiple times
    """
    result = {
        "status": "ok",
        "errors": [],
        "created_topics": [],
        "existing_topics": [],
        "bootstrap_servers": config.bootstrap_servers,
        "topics": config.topics,
    }
    try:
        # TODO: Replace with aiokafka admin client when available
        # admin = KafkaAdminClient(bootstrap_servers=config.bootstrap_servers)
        existing_topics = set(admin.list_topics())
        result["existing_topics"] = list(existing_topics)
        topics_to_create = [
            NewTopic(name=topic, num_partitions=1, replication_factor=1)
            for topic in config.topics if topic not in existing_topics
        ]
        if topics_to_create:
            try:
                admin.create_topics(new_topics=topics_to_create, validate_only=False)
                result["created_topics"] = [t.name for t in topics_to_create]
                logger.info(f"Created topics: {result['created_topics']}")
            except TopicAlreadyExistsError:
                # Should not happen due to check, but safe to ignore
                pass
            except KafkaError as e:
                logger.error(f"Error creating topics: {e}")
                result["errors"].append(str(e))
        logger.info(f"Kafka bootstrap complete. Existing topics: {result['existing_topics']}")
    except NoBrokersAvailable as e:
        logger.error(f"Kafka broker not available: {e}")
        result["status"] = "error"
        result["errors"].append(f"No brokers available: {e}")
    except KafkaError as e:
        logger.error(f"Kafka error during bootstrap: {e}")
        result["status"] = "error"
        result["errors"].append(str(e))
    except Exception as e:
        logger.error(f"Unexpected error during Kafka bootstrap: {e}")
        result["status"] = "error"
        result["errors"].append(str(e))
    finally:
        try:
            admin.close()
        except Exception:
            pass
    return result 