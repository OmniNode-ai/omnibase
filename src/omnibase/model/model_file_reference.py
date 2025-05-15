from pydantic import BaseModel
from typing import Optional

class FileReferenceModel(BaseModel):
    path: str  # Use str for now; can be changed to Path if needed
    description: Optional[str] = None 