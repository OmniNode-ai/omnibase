#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: yaml_schema_linter
# namespace: omninode.tools.yaml_schema_linter
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:01+00:00
# last_modified_at: 2025-04-27T18:13:01+00:00
# entrypoint: yaml_schema_linter.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""yaml_schema_linter.py
containers.foundation.src.foundation.script.validate.yaml_schema_linter.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

REQUIRED_FIELDS = [
    "metadata_version",
    "name",
    "namespace",
    "version",
    "entrypoint",
    "protocols_supported",
    "owner",
]
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def lint_yaml_schema(yaml_path: Path):
    errors = []
    try:
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        errors.append(f"YAML load error: {e}")
        return errors
    if not isinstance(data, dict):
        errors.append("YAML root is not a dictionary.")
        return errors
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    version = data.get("version")
    if version and not SEMVER_PATTERN.match(str(version)):
        errors.append(f"Invalid version format: {version}")
    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Lint YAML schemas and metadata blocks."
    )
    parser.add_argument("path", help="Path to YAML file or directory to lint")
    parser.add_argument(
        "--check-only", action="store_true", help="Only report issues, do not fix"
    )
    args = parser.parse_args()
    target = Path(args.path)
    files = []
    if target.is_dir():
        files = list(target.glob("*.yml")) + list(target.glob("*.yaml"))
    elif target.is_file():
        files = [target]
    else:
        print(f"Path not found: {target}")
        sys.exit(1)
    failed = False
    for f in files:
        errors = lint_yaml_schema(f)
        if errors:
            print(f"[FAIL] {f}:")
            for e in errors:
                print(f"  - {e}")
            failed = True
        else:
            print(f"[PASS] {f}")
    if failed:
        sys.exit(1)
    else:
        print("All YAML schemas passed linting.")


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()
