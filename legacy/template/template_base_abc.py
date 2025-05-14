# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "template_base_abc"
# namespace: "omninode.tools.template_base_abc"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:31+00:00"
# last_modified_at: "2025-05-05T13:00:31+00:00"
# entrypoint: "template_base_abc.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ABC']
# base_class: ['ABC']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Canonical abstract base class for all templates.
Migrated from src/foundation/templates/base.py (2025-04-25).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Union


class BaseTemplate(ABC):
    """Base class for all templates.
    This class defines the interface that all templates must implement. Each template
    must provide methods for:
    - Generating template output
    - Validating instances against the template
    - Generating markdown documentation
    """

    @abstractmethod
    def generate(self) -> Union[str, Dict]:
        """Generate the template output.
        Returns:
            Union[str, Dict]: The generated template content, either as a string
            for file content or a dictionary for complex structures.
        """
        pass

    @abstractmethod
    def validate(self, instance: Union[str, Dict]) -> List[str]:
        """Validate an instance against the template.
        Args:
            instance: The instance to validate, either as a string for file content
                     or a dictionary for complex structures.
        Returns:
            List[str]: A list of validation errors. Empty list if validation passes.
        """
        pass

    @abstractmethod
    def to_markdown(self) -> str:
        """Generate markdown documentation for the template.
        Returns:
            str: Markdown formatted documentation describing the template.
        """
        pass