from typing import Any, Dict
from omnibase.nodes.template_node.protocols.input_validation_tool_protocol import InputValidationToolProtocol
from omnibase.nodes.template_node.protocols.output_field_tool_protocol import OutputFieldTool
from omnibase.nodes.template_node.v1_0_0.tools.input.input_validation_tool import input_validation_tool
from omnibase.nodes.template_node.v1_0_0.tools.output.output_field_tool import compute_output_field

class TemplateNodeToolRegistry:
    """
    Minimal protocol-compliant tool registry for the template node.
    Allows swappable, pluggable tool implementations for input validation and output field computation.
    """
    def __init__(self):
        self._tools: Dict[str, Any] = {
            "input_validation_tool": input_validation_tool,
            "output_field_tool": compute_output_field,
        }

    def get_tool(self, name: str) -> Any:
        return self._tools[name]

    def register_tool(self, name: str, tool: Any):
        self._tools[name] = tool

# Singleton instance for use in the node
TEMPLATE_NODE_TOOL_REGISTRY = TemplateNodeToolRegistry()
