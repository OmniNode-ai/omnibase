#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: util_format_docstrings
# namespace: omninode.tools.util_format_docstrings
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:54+00:00
# last_modified_at: 2025-04-27T18:12:54+00:00
# entrypoint: util_format_docstrings.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""
Format all Python docstrings in the project using docformatter.

This script auto-formats docstrings to PEP 257 compliance.
Supports a --dry-run option for CI/testing.
"""
import argparse
import subprocess
import sys


def run_docformatter(path, dry_run, subprocess_runner=subprocess.run):
    cmd = ["docformatter", "-r", path]
    if dry_run:
        cmd.append("--check")
    else:
        cmd.append("-i")
    result = subprocess_runner(cmd, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    if dry_run:
        print("[DRY RUN] docformatter exit code:", result.returncode)
        return 0
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Format Python docstrings using docformatter."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry mode (just print what would change, do not modify files)",
    )
    parser.add_argument(
        "--path",
        default="containers/foundation/src/foundation/scripts/validation/",
        help="Path to format (default: validation scripts)",
    )
    args = parser.parse_args()
    exit_code = run_docformatter(
        args.path, args.dry_run, subprocess_runner=subprocess.run
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()
