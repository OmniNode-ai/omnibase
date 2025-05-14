#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: run_validators
# namespace: omninode.tools.run_validators
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:55+00:00
# last_modified_at: 2025-04-27T18:12:55+00:00
# entrypoint: run_validators.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""run_validators.py
containers.foundation.src.foundation.script.validate.run_validators.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Placeholder for DI container import (replace with actual Foundation DI import)
from foundation.di.di_container import DIContainer
from foundation.script.validate.config.config_manager import ConfigurationManager
from foundation.script.validate.common.common_validator_utils import get_staged_files
from foundation.model.model_validate import ValidationResult
from foundation.script.validate.validate_registry import ValidatorRegistry

# NOTE: This orchestrator interacts ONLY with the registry. Direct validator imports are forbidden per standards and validator_refactor_checklist.yaml.

# Mapping from validator name to file extension(s) or filter function
VALIDATOR_FILE_FILTERS = {
    # Python validators
    "absolute_imports": lambda f: f.endswith(".py"),
    "env_secrets": lambda f: f.endswith(
        (
            ".py",
            ".env",
            ".yaml",
            ".yml",
            ".json",
            ".toml",
            ".ini",
            ".conf",
            ".sh",
            ".bash",
            ".zsh",
            "Dockerfile",
            "docker-compose.yml",
        )
    ),
    "security": lambda f: f.endswith(".py"),
    "code_quality": lambda f: f.endswith(".py"),
    "test_coverage": lambda f: f.endswith(".py"),
    "logger_extra": lambda f: f.endswith(".py"),
    "style": lambda f: f.endswith(".py"),
    "naming_convention": lambda f: True,  # Apply to all files
    # YAML/metadata validators
    "metadata_block": lambda f: f.endswith((".yaml", ".yml")),
    "profile_schema": lambda f: f.endswith((".yaml", ".yml")),
    "container_yaml": lambda f: f.endswith(("container.yaml", "container.yml")),
    # Docker/compose validators
    "dockerfile": lambda f: f.endswith("Dockerfile"),
    "compose": lambda f: f.endswith(("docker-compose.yml", "docker-compose.yaml")),
    # Add more as needed
}


# --- CLI Argument Parsing ---
def parse_args():
    parser = argparse.ArgumentParser(description="Run code and configuration validators.")
    parser.add_argument("--validators", type=str, help="Comma-separated list of validator names to run (default: all)")
    parser.add_argument("--group", type=str, help="Validator group/profile to run (e.g., quality, security, ci)")
    parser.add_argument("--target", type=str, help="Target path or container to validate (default: project root)")
    parser.add_argument("--config", type=str, help="Path to config override JSON/YAML file")
    parser.add_argument(
        "--output", type=str, default="text", choices=["text", "json", "html", "sarif"], help="Output format"
    )
    parser.add_argument("--auto-fix", action="store_true", help="Enable auto-fix mode (where supported)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed, but make no changes")
    parser.add_argument("--max-workers", type=int, default=4, help="Max parallel validator executions")
    parser.add_argument("--describe", action="store_true", help="Describe available validators and exit")
    parser.add_argument("--list", action="store_true", help="List all available validators and exit")
    parser.add_argument("--version", action="store_true", help="Show validator orchestrator version and exit")
    parser.add_argument("--staged", action="store_true", help="Only validate staged files (for pre-commit)")
    parser.add_argument("--compliant-only", action="store_true", help="Run only validators that are compliant with the new standards (for refactor phase)")
    return parser.parse_args()


# --- Main Orchestration Logic ---
def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)
    args = parse_args()
    registry = ValidatorRegistry()
    di_container = DIContainer()
    config_manager = ConfigurationManager()

    if args.version:
        logger.info("Validator Orchestrator v2.0 (Registry+DI)")
        sys.exit(0)

    if args.list:
        logger.info("Available Validators:")
        for meta in registry.list_metadata():
            logger.info(
                f"- {meta['name']} (v{meta['version']}) [{meta.get('group', 'default')}] - {meta.get('description', '')}"
            )
        sys.exit(0)

    if args.describe:
        logger.info("Validator Descriptions:")
        for meta in registry.list_metadata():
            logger.info(
                f"\n{meta['name']} (v{meta['version']}) [{meta.get('group', 'default')}]:\n  {meta.get('description', '')}"
            )
            # Optionally call describe() if available
        sys.exit(0)

    # Compliant-only mode: restrict to compliant validators
    compliant_validators = [""]  # Update as more become compliant
    
    if getattr(args, "compliant_only", False):
        validator_names = compliant_validators
    elif args.validators:
        validator_names = [v.strip() for v in args.validators.split(",")]
    elif args.group:
        validator_names = [meta["name"] for meta in registry.list_metadata() if meta.get("group") == args.group]
    else:
        validator_names = [meta["name"] for meta in registry.list_metadata()]

    # Load config (with optional override)
    config = config_manager.default_config
    if args.config:
        # See https://github.com/OmniNode-ai/ai-dev/issues/144 - Support YAML as well as JSON for config override
        with open(args.config) as f:
            override = json.load(f)
        config_manager._merge_configs(config, override)

    # Determine target(s)
    staged_files = []
    if getattr(args, "staged", False):
        logger.info("[STAGED MODE] Validating only staged files.")
        staged_files = get_staged_files()
        if not staged_files:
            logger.info("No staged files to validate. Exiting.")
            sys.exit(0)
    target = Path(args.target) if args.target else Path.cwd()

    # Run validators (sequential for now; parallel execution is a future enhancement)
    results = []
    for name in validator_names:
        validator_cls = registry.get(name)
        if not validator_cls:
            logger.warning(f"Validator '{name}' not found in registry.")
            continue
        validator = di_container.resolve(validator_cls)
        validator_config = config["validators"].get(name, {})
        logger.info(f"Running validator: {name}")
        try:
            if staged_files:
                # Filter files for this validator
                file_filter = VALIDATOR_FILE_FILTERS.get(name, lambda f: True)
                filtered_files = [file for file in staged_files if file_filter(str(file))]
                if not filtered_files:
                    logger.warning(f"No applicable files for validator {name}. Skipping.")
                    continue
                for file in filtered_files:
                    try:
                        result = validator.validate(Path(file), config=validator_config)
                        logger.info(
                            f"Validator {name} finished for {file}. Valid: {getattr(result, 'is_valid', getattr(result, 'get', lambda k: None)('is_valid'))}"
                        )
                        if hasattr(result, "errors") and result.errors:
                            logger.error(f"Errors for {name} on {file}: {result.errors}")
                        elif isinstance(result, dict) and result.get("errors"):
                            logger.error(f"Errors for {name} on {file}: {result['errors']}")
                    except Exception as ve:
                        logger.warning(f"Validator {name} could not process {file}: {ve}")
                result = None
            else:
                result = validator.validate(target, config=validator_config)
                if not isinstance(result, ValidationResult):
                    logger.error(f"[!] Validator {validator.get_name()} did not return a ValidationResult for {target}. Got: {type(result)}")
                    # Optionally, create a failed ValidationResult
                    result = ValidationResult(is_valid=False, errors=[f"Non-compliant return type: {type(result)}"], warnings=[], suggestions=[], metadata={}, version=None)
                logger.info(
                    f"Validator {name} finished. Valid: {getattr(result, 'is_valid', getattr(result, 'get', lambda k: None)('is_valid'))}"
                )
                if hasattr(result, "errors") and result.errors:
                    logger.error(f"Errors for {name}: {result.errors}")
                elif isinstance(result, dict) and result.get("errors"):
                    logger.error(f"Errors for {name}: {result['errors']}")
        except Exception as e:
            logger.exception(f"Exception while running validator {name}: {e}")
            result = None
        # Auto-fix/dry-run stub
        if args.auto_fix and hasattr(validator, "fix"):
            if args.dry_run:
                logger.info(f"[DRY RUN] Would auto-fix issues for {name} (not making changes)")
            else:
                logger.info(f"Auto-fixing issues for {name}")
        results.append((name, result))

    # Output results
    if args.output == "json":
        logger.info(json.dumps({name: result.model_dump() if result else None for name, result in results}, indent=2))
    elif args.output == "text":
        for name, result in results:
            logger.info(f"\n=== {name} ===")
            if result:
                logger.info(f"Valid: {result.is_valid}")
                if result.errors:
                    logger.error("Errors:")
                    for err in result.errors:
                        logger.error(f"- {err}")
                if result.warnings:
                    logger.warning("Warnings:")
                    for warn in result.warnings:
                        logger.warning(f"- {warn}")
            else:
                logger.error("No result returned (exception or failure)")
    else:
        logger.warning(f"Output format '{args.output}' not yet implemented.")


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()