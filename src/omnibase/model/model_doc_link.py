from typing import Optional

from pydantic import BaseModel


class DocLinkModel(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
