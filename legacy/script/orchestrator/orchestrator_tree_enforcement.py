# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# name: "orchestrator_tree_enforcement"
# namespace: "foundation.script.orchestrator"
# meta_type: "tool"
# version: "0.1.0"
# owner: "foundation-team"
# entrypoint: "orchestrator_tree_enforcement.py"
# === /OmniNode:Tool_Metadata ===

"""
Orchestrator for directory tree enforcement and automation (DI-compliant).

Usage:
  python orchestrator_tree_enforcement.py validate --tree-file <path> --project-root <src_root>
  python orchestrator_tree_enforcement.py generate --tree-file <path> --project-root <src_root>

Both --tree-file and --project-root are required and must be injected by the caller (pre-commit, post-commit, CI, etc).
This script never hardcodes or resolves the .tree file or project root path directly.
"""

import argparse
import subprocess
import sys
from pathlib import Path

def run_validate(tree_file: Path, project_root: Path):
    validator_path = project_root / "foundation/script/validate/validate_directory_tree.py"
    cmd = [
        sys.executable,
        str(validator_path),
        "--root", str(project_root),
        "--base-template", str(tree_file),
        "--output-format", "text",
    ]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def run_generate(tree_file: Path, project_root: Path):
    tree_tool_path = project_root / "foundation/script/tool/tool_directory_tree.py"
    cmd = [
        sys.executable,
        str(tree_tool_path),
        "scan", str(project_root),
        "--output", str(tree_file),
    ]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Orchestrate directory tree enforcement (DI-compliant).")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate", help="Validate current structure against injected .tree file")
    validate_parser.add_argument("--tree-file", required=True, type=Path, help="Path to the canonical .tree file (injected)")
    validate_parser.add_argument("--project-root", required=True, type=Path, help="Path to the canonical source root (injected)")
    generate_parser = subparsers.add_parser("generate", help="Regenerate .tree file at injected path from current structure")
    generate_parser.add_argument("--tree-file", required=True, type=Path, help="Path to the canonical .tree file (injected)")
    generate_parser.add_argument("--project-root", required=True, type=Path, help="Path to the canonical source root (injected)")
    args = parser.parse_args()
    if args.command == "validate":
        run_validate(args.tree_file, args.project_root)
    elif args.command == "generate":
        run_generate(args.tree_file, args.project_root)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 