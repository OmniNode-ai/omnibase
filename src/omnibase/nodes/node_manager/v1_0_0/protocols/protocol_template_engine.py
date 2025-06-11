"""
Protocol for template engine tool for node_manager node.
Defines the interface for processing template files and replacing tokens.
"""
from pathlib import Path
from ..models.model_template_context import ModelTemplateContext, ModelRenderedTemplate
from typing import Protocol

class ProtocolTemplateEngine(Protocol):
    """
    Protocol for template engine tool for node_manager node.
    Implementations should provide methods for rendering templates and replacing tokens using strong types.
    """
    def render_template(self, template_path: Path, context: ModelTemplateContext) -> ModelRenderedTemplate:
        """
        Render a template file with the given context.
        Args:
            template_path (Path): The path to the template file to render.
            context (ModelTemplateContext): The context model for token replacement.
        Returns:
            ModelRenderedTemplate: The rendered template output model.
        """
        ... 