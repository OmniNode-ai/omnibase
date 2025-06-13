from pydantic import BaseModel


class ErrorCodeMetadataModel(BaseModel):
    """Represents error code metadata with enhanced information"""
    code: str
    number: int
    description: str
    exit_code: int
    category: str 