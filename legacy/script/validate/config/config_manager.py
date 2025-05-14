#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# schema_version: 1.0.0
# name: config_manager
# namespace: omninode.tools.config_manager
# meta_type: model
# version: 0.1.0
# author: OmniNode Team
# owner: jonah@omninode.ai
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-05-02T18:46:08+00:00
# last_modified_at: 2025-05-02T18:46:08+00:00
# entrypoint: config_manager.py
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""config.py containers.foundation.src.foundation.script.validate.config.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

import jsonschema

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Manages validator configurations."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the configuration manager.

        Args:
            config_dir: Directory containing configuration files
        """
        # Always use scripts/validation/config/ as the config directory
        self.config_dir = config_dir or Path(__file__).parent
        self.schema = self._load_schema()
        self.default_config = self._load_default_config()

    def _load_schema(self) -> Dict:
        """Load the configuration schema.

        Returns:
            Dict: The schema definition
        """
        schema_path = self.config_dir / "schema.json"
        try:
            with open(schema_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading schema: {e}")
            return {}

    def _load_default_config(self) -> Dict:
        """Load the default configuration.

        Returns:
            Dict: The default configuration
        """
        config_path = self.config_dir / "default_config.json"
        try:
            with open(config_path) as f:
                config = json.load(f)
            self.validate_config(config)
            return config
        except Exception as e:
            logger.error(f"Error loading default config: {e}")
            return {"validators": {}, "global": {}}

    def validate_config(self, config: Dict) -> bool:
        """Validate a configuration against the schema.

        Args:
            config: Configuration to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            jsonschema.validate(instance=config, schema=self.schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            return False

    def load_config(
        self, config_path: Optional[Path] = None, validator_name: Optional[str] = None
    ) -> Dict:
        """Load and validate a configuration.

        Args:
            config_path: Path to configuration file
            validator_name: Optional validator name to get specific config

        Returns:
            Dict: The loaded and validated configuration
        """
        # Start with default config
        config = self.default_config.copy()

        # Load custom config if provided
        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    custom_config = json.load(f)
                if self.validate_config(custom_config):
                    # Deep merge configurations
                    self._merge_configs(config, custom_config)
            except Exception as e:
                logger.error(f"Error loading custom config: {e}")

        # Return specific validator config if requested
        if validator_name:
            return {
                "validators": {
                    validator_name: config["validators"].get(validator_name, {})
                },
                "global": config["global"],
            }

        return config

    def _merge_configs(self, base: Dict, override: Dict):
        """Deep merge two configuration dicts.

        Args:
            base: The base configuration
            override: The override configuration
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value

    def get_validator_config(
        self, validator_name: str, config: Optional[Dict] = None
    ) -> Dict:
        """Get configuration for a specific validator.

        Args:
            validator_name: Name of the validator
            config: Optional full configuration

        Returns:
            Dict: Configuration for the validator
        """
        if config is None:
            config = self.default_config

        return {
            "validators": {
                validator_name: config["validators"].get(validator_name, {})
            },
            "global": config["global"],
        }

    def is_validator_enabled(
        self, validator_name: str, config: Optional[Dict] = None
    ) -> bool:
        """Check if a validator is enabled.

        Args:
            validator_name: Name of the validator
            config: Optional configuration to check

        Returns:
            bool: True if enabled, False otherwise
        """
        if config is None:
            config = self.default_config

        validator_config = config["validators"].get(validator_name, {})
        return validator_config.get("enabled", True)

    def get_validator_rules(
        self, validator_name: str, config: Optional[Dict] = None
    ) -> Dict:
        """Get rules for a specific validator.

        Args:
            validator_name: Name of the validator
            config: Optional configuration to check

        Returns:
            Dict: Rules for the validator
        """
        if config is None:
            config = self.default_config

        validator_config = config["validators"].get(validator_name, {})
        return validator_config.get("rules", {})

    def get_global_config(self, config: Optional[Dict] = None) -> Dict:
        """Get global configuration.

        Args:
            config: Optional configuration to check

        Returns:
            Dict: Global configuration
        """
        if config is None:
            config = self.default_config

        return config["global"]