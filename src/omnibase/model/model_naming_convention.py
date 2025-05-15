from pydantic import BaseModel

class NamingConventionResultModel(BaseModel):
    valid: bool
    reason: str = "" 