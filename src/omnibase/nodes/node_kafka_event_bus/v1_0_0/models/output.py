from pydantic import BaseModel, Field
from typing import Optional, Any

class NodeKafkaEventBusOutputField(BaseModel):
    processed: Optional[str] = None
    integration: Optional[bool] = None
    backend: str
    custom: Optional[Any] = None 