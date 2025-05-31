from typing import Dict, Type, Any
from pydantic import BaseModel, Field, RootModel, model_validator

class EntrypointBlock(BaseModel):
    type: str
    target: str  # Always the filename stem (no extension)
    # No URI string logic, only type/target

    @classmethod
    def from_uri(cls, uri: str) -> "EntrypointBlock":
        """
        Parse a URI string (e.g., 'python://main') into type/target and return EntrypointBlock.
        The target is always the filename stem (no extension).
        """
        if "://" not in uri:
            raise ValueError(f"Invalid entrypoint URI: {uri}")
        type_, target = uri.split("://", 1)
        return cls(type=type_, target=target)

    def to_uri(self) -> str:
        """
        Return the entrypoint as a URI string (e.g., 'python://main') for display/CLI only.
        The target is always the filename stem (no extension).
        """
        return f"{self.type}://{self.target}"

class ToolCollection(RootModel[Dict[str, Any]]):
    """
    Collection of function tools for ONEX metadata blocks.
    Canonical type for the 'tools' field in NodeMetadataBlock and ProjectMetadataBlock.
    Protocol-compatible with a ToolCollection (not a dict[str, Any]):
      - Serializes to a flat mapping in YAML/JSON (no extra nesting)
      - Accepts both dict and ToolCollection on deserialization
    Provides utility methods for dict conversion and validation.
    Uses Pydantic RootModel for v2+ compatibility.
    """
    @model_validator(mode="after")
    def check_function_names(self):
        for name in self.root:
            if not name.isidentifier():
                raise ValueError(f"Invalid function name: {name}")
        return self 