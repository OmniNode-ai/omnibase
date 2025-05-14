# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# name: "tool_directory_tree"
# namespace: "foundation.script.tool"
# meta_type: "tool"
# version: "0.1.0"
# owner: "foundation-team"
# entrypoint: "tool_directory_tree.py"
# === /OmniNode:Tool_Metadata ===

"""
CLI tool for directory-to-tree and tree-to-directory conversion.
- 'scan': Scan a directory and output a tree_sync.TreeNode YAML.
- 'apply': Read a tree_sync.TreeNode YAML and create the directory structure.
"""

import argparse
import sys
import yaml
from pathlib import Path
from foundation.util.util_tree_sync import directory_to_tree_template, tree_template_to_directory
from foundation.model.model_struct_index import TreeNode
from foundation.protocol.protocol_logger import ProtocolLogger


def main(logger: ProtocolLogger) -> None:
    parser = argparse.ArgumentParser(description="Directory <-> Tree Template Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan a directory and output a tree template YAML")
    scan_parser.add_argument("directory", type=str, help="Directory to scan")
    scan_parser.add_argument("--output", type=str, help="Output YAML file (default: stdout)")

    apply_parser = subparsers.add_parser("apply", help="Apply a tree template YAML to create a directory structure")
    apply_parser.add_argument("template", type=str, help="YAML file with tree_sync.TreeNode")
    apply_parser.add_argument("directory", type=str, help="Target directory to create structure in")

    args = parser.parse_args()

    if args.command == "scan":
        template = directory_to_tree_template(args.directory)
        yaml_str = yaml.dump(template.model_dump(), sort_keys=False)
        if args.output:
            Path(args.output).write_text(yaml_str)
            logger.info(f"Tree template YAML written to {args.output}")
        else:
            print(yaml_str)
    elif args.command == "apply":
        with open(args.template, "r") as f:
            data = yaml.safe_load(f)
        template = tree_sync.TreeNode.model_validate(data)
        tree_template_to_directory(template, args.directory)
        logger.info(f"Directory structure created at {args.directory}")
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    import structlog
    from foundation.protocol.protocol_logger import ProtocolLogger
    logger: ProtocolLogger = structlog.get_logger("tool_directory_tree")  # type: ignore
    main(logger) 