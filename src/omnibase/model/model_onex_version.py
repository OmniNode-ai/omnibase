from pydantic import BaseModel


class OnexVersionInfo(BaseModel):
    """
    Canonical Pydantic model for ONEX version information.
    Fields:
        metadata_version (str): The metadata schema version.
        protocol_version (str): The protocol version.
        schema_version (str): The schema version.
    """

    metadata_version: str
    protocol_version: str
    schema_version: str
