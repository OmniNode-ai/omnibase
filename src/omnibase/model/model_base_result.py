from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from omnibase.model.model_base_error import BaseErrorModel

class BaseResultModel(BaseModel):
    exit_code: int
    success: bool
    errors: List[BaseErrorModel] = []
    metadata: Optional[Dict[str, Any]] = None 