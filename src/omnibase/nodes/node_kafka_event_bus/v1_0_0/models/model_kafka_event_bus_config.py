from pydantic import BaseModel, Field
from typing import List, Optional

class ModelKafkaEventBusConfig(BaseModel):
    """
    Configuration model for KafkaEventBus.
    Defines all required connection, topic, and security options for ONEX Kafka event bus nodes.
    Sensitive fields (e.g., sasl_password, ssl_keyfile) should be injected via environment variables or a secrets manager, not hardcoded in config files or code.
    """
    bootstrap_servers: List[str] = Field(..., description="List of Kafka bootstrap servers (host:port)")
    topics: List[str] = Field(..., description="List of Kafka topics to use for event bus communication")
    security_protocol: Optional[str] = Field(
        default=None, description="Kafka security protocol (e.g., PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL)"
    )
    sasl_mechanism: Optional[str] = Field(
        default=None, description="SASL mechanism if using SASL authentication (e.g., PLAIN, SCRAM-SHA-256)"
    )
    sasl_username: Optional[str] = Field(default=None, description="SASL username for authentication")
    sasl_password: Optional[str] = Field(default=None, description="SASL password for authentication")
    client_id: Optional[str] = Field(default=None, description="Kafka client ID for diagnostics")
    group_id: Optional[str] = Field(default=None, description="Kafka consumer group ID")
    partitions: Optional[int] = Field(default=None, description="Number of partitions for topic creation (if applicable)")
    replication_factor: Optional[int] = Field(default=None, description="Replication factor for topic creation (if applicable)")
    acks: Optional[str] = Field(default="all", description="Kafka producer acknowledgment policy (e.g., 'all', '1', '0')")
    enable_auto_commit: Optional[bool] = Field(default=True, description="Enable auto-commit for Kafka consumer")
    auto_offset_reset: Optional[str] = Field(default="earliest", description="Offset reset policy (earliest/latest)")
    ssl_cafile: Optional[str] = Field(default=None, description="Path to CA file for TLS (if using SSL/SASL_SSL)")
    ssl_certfile: Optional[str] = Field(default=None, description="Path to client certificate file for TLS (if using SSL/SASL_SSL)")
    ssl_keyfile: Optional[str] = Field(default=None, description="Path to client key file for TLS (if using SSL/SASL_SSL)")
    # Add more fields as needed for advanced Kafka features 

    @classmethod
    def default(cls) -> "ModelKafkaEventBusConfig":
        """
        Returns a canonical default config for development, testing, and CLI fallback use.
        """
        return cls(
            bootstrap_servers=["localhost:9092"],
            topics=["onex-default"],
            group_id="onex-default-group",
            security_protocol="PLAINTEXT",
            # Add other required fields with safe defaults as needed
        ) 