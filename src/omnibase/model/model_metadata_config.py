from pydantic import BaseModel, Extra
from typing import Optional

class MetadataConfigModel(BaseModel, extra=Extra.allow):
    # Example config fields; add more as needed
    timeout: Optional[int] = None
    retries: Optional[int] = None
    enable_cache: Optional[bool] = None
    custom_settings: Optional[dict] = None
    # Arbitrary extra fields allowed for extensibility 