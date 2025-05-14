# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_dispatch
# namespace: omninode.tools.validate_dispatch
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:58+00:00
# last_modified_at: 2025-04-27T18:12:58+00:00
# entrypoint: validate_dispatch.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

import logging
from pathlib import Path

from foundation.protocol.protocol_logger import ProtocolLogger
from foundation.script.validate.python.python_validate_file_filters import VALIDATOR_FILE_FILTERS


def run_validators(
    validator_names,
    registry,
    config,
    target,
    staged_files,
    args,
    di_container=None,
    logger: ProtocolLogger = None,
):
    logger = logger or logging.getLogger(__name__)
    results = []
    for name in validator_names:
        validator_cls = registry.get(name)
        if not validator_cls:
            logger.warning(f"Validator '{name}' not found in registry.")
            continue
        validator = (
            di_container.resolve(validator_cls) if di_container else validator_cls()
        )
        validator_config = config["validators"].get(name, {})
        logger.info(f"Running validator: {name}")
        try:
            if staged_files:
                file_filter = VALIDATOR_FILE_FILTERS.get(name, lambda f: True)
                filtered_files = [
                    file for file in staged_files if file_filter(str(file))
                ]
                if not filtered_files:
                    logger.warning(
                        f"No applicable files for validator {name}. Skipping."
                    )
                    continue
                for file in filtered_files:
                    try:
                        result = validator.validate(Path(file), config=validator_config)
                        logger.info(
                            f"Validator {name} finished for {file}. Valid: {getattr(result, 'is_valid', getattr(result, 'get', lambda k: None)('is_valid'))}"
                        )
                        if hasattr(result, "errors") and result.errors:
                            logger.error(
                                f"Errors for {name} on {file}: {result.errors}"
                            )
                        elif isinstance(result, dict) and result.get("errors"):
                            logger.error(
                                f"Errors for {name} on {file}: {result['errors']}"
                            )
                    except Exception as ve:
                        logger.warning(
                            f"Validator {name} could not process {file}: {ve}"
                        )
                result = None
            else:
                result = validator.validate(target, config=validator_config)
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
        if args.auto_fix and hasattr(validator, "fix"):
            if args.dry_run:
                logger.info(
                    f"[DRY RUN] Would auto-fix issues for {name} (not making changes)"
                )
            else:
                logger.info(f"Auto-fixing issues for {name}")
        results.append((name, result))
    return results
