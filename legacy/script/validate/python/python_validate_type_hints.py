#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_type_hints
# namespace: omninode.tools.validate_type_hints
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:03+00:00
# last_modified_at: 2025-04-27T18:13:03+00:00
# entrypoint: validate_type_hints.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""
# ---
# schema_version: "1.0"
# metadata_version: "0.1"
# name: "Type Hint Validator"
# namespace: "foundation.script.validate.validate_type_hints"
# version: "1.0.0"
# meta_type: "validator"
# entrypoint: "main"
# protocols_supported:
#   - "omninode_v1"
# owner: "foundation-team"
# last_modified_by: "ai-dev-assistant"
# last_modified_at: "2025-04-26T12:34:00Z"
# ---

validate_type_hints.py

Checks for missing type hints in all public functions and methods in the codebase.
- Recursively scans Python files (skipping __pycache__)
- Reports any public function/method missing parameter or return type hints
- Outputs plain text: file, line, function name
- --strict: exit nonzero if violations are found (for CI/pre-commit)
- --json: output machine-readable JSON for CI integration
- describe(): print TOOL_METADATA for registry/discovery

Feedback/Retrospective: Update this validator as standards evolve or new enforcement requirements are added.
"""
import argparse
import ast
import json
import os
import sys

TOOL_METADATA = {
    "schema_version": "1.0",
    "metadata_version": "0.1",
    "name": "Type Hint Validator",
    "namespace": "foundation.script.validate.validate_type_hints",
    "version": "1.0.0",
    "type": "validator",
    "entrypoint": "main",
    "protocols_supported": ["omninode_v1"],
    "owner": "foundation-team",
    "last_modified_by": "ai-dev-assistant",
    "last_modified_at": "2025-04-26T12:34:00Z",
}

SKIP_DIRS = {"__pycache__"}


def has_type_hints(func: ast.FunctionDef) -> bool:
    # Check all arguments (skip self/cls for methods)
    args = func.args.args
    if args and args[0].arg in {"self", "cls"}:
        args = args[1:]
    for arg in args:
        if arg.annotation is None:
            return False
    # Check return type
    if func.returns is None:
        return False
    return True


def is_public(func: ast.FunctionDef) -> bool:
    return not func.name.startswith("_")


def scan_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except Exception as e:
            print(f"[ERROR] Could not parse {filepath}: {e}")
            return []
    missing = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if is_public(node) and not has_type_hints(node):
                missing.append(
                    {"file": filepath, "line": node.lineno, "function": node.name}
                )
    return missing


def scan_dir(root):
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname.endswith(".py"):
                results.extend(scan_file(os.path.join(dirpath, fname)))
    return results


def describe():
    print(json.dumps(TOOL_METADATA, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Check for missing type hints in public functions/methods."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero if violations are found (for CI/pre-commit)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON for CI integration",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--describe", action="store_true", help="Print TOOL_METADATA and exit"
    )
    args = parser.parse_args()
    if args.describe:
        describe()
        sys.exit(0)
    results = scan_dir(args.root)
    if args.json:
        print(json.dumps({"missing_type_hints": results}, indent=2))
    else:
        if results:
            print("Missing type hints in public functions/methods:")
            for r in results:
                print(f"{r['file']}:{r['line']}: {r['function']}")
        else:
            print("All public functions/methods have type hints.")
    if args.strict and results:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
