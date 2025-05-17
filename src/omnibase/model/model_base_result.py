from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from omnibase.model.model_base_error import BaseErrorModel


class BaseResultModel(BaseModel):
    exit_code: int
    success: bool
    errors: List[BaseErrorModel] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
