from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SchemaModel(BaseModel):
    """
    Minimal Pydantic model for ONEX JSON schema files.
    Includes canonical fields and is extensible for M1+.
    """

    schema_uri: Optional[str] = Field(None, alias="$schema")
    title: Optional[str] = None
    type: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    required: Optional[List[str]] = None
    # TODO: Add more fields and validation logic in M1+
