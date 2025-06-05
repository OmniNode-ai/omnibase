from pydantic import BaseModel, Field

class ModelKafkaEventBusBootstrapResult(BaseModel):
    """
    Result model for Kafka event bus bootstrap operations (canonical, ONEX-compliant).
    """
    status: str = Field(..., description="Bootstrap status, e.g. 'ok' or 'error'.")
    message: str = Field(..., description="Human-readable message about the bootstrap result.")
    # Add more fields as needed (e.g., error_code, details) 