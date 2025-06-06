from typing import Any, Optional

from pydantic import BaseModel, Field


class ModelKafkaEventBusOutputField(BaseModel):
    processed: Optional[str] = None
    integration: Optional[bool] = None
    backend: str
    custom: Optional[Any] = None
