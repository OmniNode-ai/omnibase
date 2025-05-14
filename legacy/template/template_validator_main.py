# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "template_validator_main"
# namespace: "omninode.tools.template_validator_main"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:31+00:00"
# last_modified_at: "2025-05-05T13:00:31+00:00"
# entrypoint: "template_validator_main.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Canonical TemplateValidator for validating all template types (container, dockerfile, compose, config, docs).
Migrated from src/foundation/templates/validator.py (2025-04-25).
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import toml
import yaml
from foundation.template.template_base_abc import BaseTemplate

# NOTE: If a registry is needed, import or implement it here.
# from foundation.templates.registry import get_template


class TemplateValidator:
    """Validator for all template types."""

    def __init__(self):
        self.errors: List[str] = []

    def validate_template(
        self,
        template: BaseTemplate,
        instance: Union[str, Dict],
        container_path: Optional[Union[str, Path]] = None,
    ) -> Tuple[bool, List[str]]:
        if container_path:
            errors = template.validate(instance, container_path)
        else:
            errors = template.validate(instance)
        return len(errors) == 0, errors

    def validate_project_config(
        self, config_file: Union[str, Path]
    ) -> Tuple[bool, List[str]]:
        if isinstance(config_file, str):
            config_file = Path(config_file)
        if not config_file.exists():
            return False, [f"Config file not found: {config_file}"]
        if config_file.suffix in (".toml",):
            try:
                data = toml.load(config_file)
            except Exception as e:
                return False, [f"TOML parse error: {e}"]
        elif config_file.suffix in (".yaml", ".yml"):
            try:
                with open(config_file, "r") as f:
                    data = yaml.safe_load(f)
            except Exception as e:
                return False, [f"YAML parse error: {e}"]
        else:
            return False, [f"Unsupported config file type: {config_file.suffix}"]
        # Here you would validate 'data' against a schema or template
        # For now, just return success if parsed
        return True, []


def validate_project_config(config_file: Union[str, Path]) -> Tuple[bool, List[str]]:
    """Convenience function to validate a project configuration file."""
    return TemplateValidator().validate_project_config(config_file)