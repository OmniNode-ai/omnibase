# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: output_format
# namespace: omninode.tools.output_format
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:00+00:00
# last_modified_at: 2025-04-27T18:13:00+00:00
# entrypoint: output_format.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

import json
import logging


def output_results(results, args):
    logger = logging.getLogger(__name__)
    if args.output == "json":
        logger.info(
            json.dumps(
                {
                    name: result.model_dump() if result else None
                    for name, result in results
                },
                indent=2,
            )
        )
    elif args.output == "text":
        for name, result in results:
            logger.info(f"\n=== {name} ===")
            if result:
                logger.info(f"Valid: {result.is_valid}")
                if hasattr(result, "errors") and result.errors:
                    logger.error("Errors:")
                    for e in result.errors:
                        if hasattr(e, "type") and hasattr(e, "message"):
                            # Structured ValidationIssue
                            loc = f"{e.file or ''}" + (f":{e.line}" if e.line else "")
                            logger.error(f"- [{e.type.upper()}] {loc} {e.message}")
                        else:
                            logger.error(f"- {e}")
                if hasattr(result, "warnings") and result.warnings:
                    logger.warning("Warnings:")
                    for w in result.warnings:
                        if hasattr(w, "type") and hasattr(w, "message"):
                            loc = f"{w.file or ''}" + (f":{w.line}" if w.line else "")
                            logger.warning(f"- [{w.type.upper()}] {loc} {w.message}")
                        else:
                            logger.warning(f"- {w}")
            else:
                logger.error("No result returned (exception or failure)")
    else:
        logger.warning(f"Output format '{args.output}' not yet implemented.")
