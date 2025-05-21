from pydantic import BaseModel

class StamperInputState(BaseModel):
    """Input state contract for the stamper node (node-local).

    version: Schema version for input state (must be injected at construction).
    """
    version: str
    file_path: str
    author: str = "OmniNode Team"
    # Add more fields as needed

class StamperOutputState(BaseModel):
    """Output state contract for the stamper node (node-local).

    version: Schema version for output state (must be injected at construction).
    """
    version: str
    status: str
    message: str
    # Add more fields as needed 