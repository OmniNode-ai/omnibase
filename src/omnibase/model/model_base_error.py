from pydantic import BaseModel

class BaseErrorModel(BaseModel):
    message: str
    code: str = "unknown"
    details: str = "" 