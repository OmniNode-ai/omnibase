from typing import List, Optional
from pydantic import BaseModel, Field

class DispatchParamModel(BaseModel):
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (e.g., dict, str, int)")
    description: Optional[str] = Field(None, description="Parameter description")

class DispatchReturnModel(BaseModel):
    type: str = Field(..., description="Return type (e.g., dict, str, int)")
    description: Optional[str] = Field(None, description="Return value description")

class DispatchActionModel(BaseModel):
    id: str = Field(..., description="Action identifier")
    description: Optional[str] = Field(None, description="Action description")
    params: List[DispatchParamModel] = Field(default_factory=list, description="List of parameters for the action")
    returns: DispatchReturnModel = Field(..., description="Return value model for the action")

class DispatchTableModel(BaseModel):
    actions: List[DispatchActionModel] = Field(default_factory=list, description="List of available dispatch actions") 