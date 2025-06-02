from typing import Any, Dict

from pydantic import RootModel, model_validator

from omnibase.model.model_function_tool import FunctionTool


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

    @model_validator(mode="before")
    @classmethod
    def coerce_tool_values(cls, data):
        if isinstance(data, dict):
            new_data = {}
            for k, v in data.items():
                if isinstance(v, dict):
                    new_data[k] = FunctionTool.from_serializable_dict(v)
                else:
                    new_data[k] = v
            return new_data
        if isinstance(data, ToolCollection):
            return data.root
        return data

    @model_validator(mode="after")
    def check_function_names(self):
        for name in self.root:
            if not name.isidentifier():
                raise ValueError(f"Invalid function name: {name}")
        return self
