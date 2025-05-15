from pydantic import BaseModel
from typing import Optional

class DocLinkModel(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None 