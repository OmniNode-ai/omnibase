from typing import Any, Dict, Optional

from pydantic import BaseModel


class MetadataConfigModel(BaseModel):
    # Example config fields; add more as needed
    timeout: Optional[int] = None
    retries: Optional[int] = None
    enable_cache: Optional[bool] = None
    custom_settings: Optional[Dict[str, Any]] = None  # Arbitrary settings, extensible
    # Arbitrary extra fields allowed for extensibility
    model_config = {"extra": "allow"}
