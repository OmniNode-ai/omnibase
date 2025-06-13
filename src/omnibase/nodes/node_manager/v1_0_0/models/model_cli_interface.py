from pydantic import BaseModel
from typing import List, Dict, Any


class CliParameterModel(BaseModel):
    """Represents a CLI parameter"""
    name: str
    type: str
    description: str
    required: bool
    default: Any = None
    help_text: str


class CliInterfaceModel(BaseModel):
    """Represents CLI interface metadata from contract"""
    command_name: str
    description: str
    parameters: List[CliParameterModel]
    examples: List[str] 