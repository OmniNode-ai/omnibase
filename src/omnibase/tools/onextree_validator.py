# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: onextree_validator.py
# version: 1.0.0
# uuid: e6d4804e-9c76-4cef-a466-fb65dde48cd4
# author: OmniNode Team
# created_at: 2025-05-24T12:13:14.580067
# last_modified_at: 2025-05-24T16:13:22.364802
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 56c3d54f5558d6bf46129f3b7ae7b890131cdfb0e4621b7171f76a7fc200a12c
# entrypoint: python@onextree_validator.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.onextree_validator
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
ONEX Tree Validator - CLI wrapper for node-local validator logic using canonical models and protocol.
"""
import argparse
import sys
from pathlib import Path

import yaml

from omnibase.core.structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.nodes.tree_generator_node.v1_0_0.helpers.tree_validator import (
    OnextreeValidator,
)

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


def main() -> None:
    """
    CLI entrypoint for .onextree validator. Outputs canonical model as YAML/JSON or human-readable.
    """
    parser = argparse.ArgumentParser(
        description="Validate .onextree files against actual directory contents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python onextree_validator.py --onextree-path src/omnibase/.onextree --root-dir src/omnibase
  python onextree_validator.py --output-format yaml
        """,
    )
    parser.add_argument(
        "--onextree-path",
        type=str,
        required=True,
        help="Path to the .onextree manifest file (YAML or JSON)",
    )
    parser.add_argument(
        "--root-dir",
        type=str,
        required=True,
        help="Root directory to validate against",
    )
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["yaml", "json", "human"],
        default="human",
        help="Output format: yaml, json, or human-readable (default: human)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    args = parser.parse_args()

    validator = OnextreeValidator(verbose=args.verbose)
    result = validator.validate_onextree_file(
        onextree_path=Path(args.onextree_path),
        root_directory=Path(args.root_dir),
    )
    if args.output_format == "json":
        emit_log_event(
            LogLevelEnum.INFO,
            result.model_dump_json(indent=2),
            node_id=_COMPONENT_NAME,
        )
    elif args.output_format == "yaml":
        emit_log_event(
            LogLevelEnum.INFO,
            yaml.safe_dump(result.model_dump(), sort_keys=False),
            node_id=_COMPONENT_NAME,
        )
    else:
        validator.print_results(result)
    sys.exit(validator.get_exit_code(result))


if __name__ == "__main__":
    main()
