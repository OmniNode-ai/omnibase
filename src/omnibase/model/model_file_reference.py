from typing import Optional

from pydantic import BaseModel


class FileReferenceModel(BaseModel):
    path: str  # Use str for now; can be changed to Path if needed
    description: Optional[str] = None
