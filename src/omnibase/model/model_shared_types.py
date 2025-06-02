# This file is intentionally left empty after refactor. EntrypointBlock and all tool-related code have been moved to their own modules.

from typing import Any, Dict, Type

from pydantic import BaseModel, Field, RootModel, model_validator

from omnibase.model.model_node_metadata import FunctionTool


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


# ToolCollection and tool-related code removed; see model_tool_collection.py and model_function_tool.py for canonical definitions.
