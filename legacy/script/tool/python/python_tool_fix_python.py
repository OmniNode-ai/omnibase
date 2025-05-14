#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: tool_fix_python
# namespace: omninode.tools.tool_fix_python
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:53+00:00
# last_modified_at: 2025-04-27T18:12:53+00:00
# entrypoint: tool_fix_python.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

import subprocess
import sys
from pathlib import Path

from foundation.script.metadata import metadata_stamper


def get_staged_python_files(subprocess_run=subprocess.run):
    result = subprocess_run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        stdout=subprocess.PIPE,
        text=True,
    )
    return [f for f in result.stdout.splitlines() if f.endswith(".py")]


def run_isort(files, subprocess_run=subprocess.run):
    if files:
        print("Sorting imports with isort..")
        subprocess_run(["isort", "--filter-files"] + files, check=True)


def run_black(files, subprocess_run=subprocess.run):
    if files:
        print("Formatting code with black..")
        subprocess_run(["black", "--check"] + files, check=True)


def run_metadata_stamp(files):
    stamped = []
    skipped = []
    for file in files:
        path = Path(file)
        # Only stamp .py files
        if path.suffix != ".py":
            continue
        # Use the canonical metadata stamper
        changed = metadata_stamper.stamp_file(path, overwrite=True)
        if changed:
            stamped.append(file)
        else:
            skipped.append(file)
    print(f"Metadata stamped: {len(stamped)} file(s)")
    if stamped:
        for f in stamped:
            print(f"  [+] {f}")
    print(f"Already compliant: {len(skipped)} file(s)")
    if skipped:
        for f in skipped:
            print(f"  [✓] {f}")


def main(
    get_staged_files_fn=get_staged_python_files,
    run_isort_fn=run_isort,
    run_black_fn=run_black,
    run_metadata_stamp_fn=run_metadata_stamp,
    subprocess_run=subprocess.run,
):
    files = get_staged_files_fn(subprocess_run)
    if not files:
        print("No Python files staged for formatting.")
        return 0
    try:
        run_isort_fn(files, subprocess_run)
        run_black_fn(files, subprocess_run)
        run_metadata_stamp_fn(files)
    except subprocess.CalledProcessError as e:
        print(f"Formatting or stamping failed: {e}")
        return 1
    print("Formatting and metadata stamping complete.")
    return 0


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    sys.exit(main())  # test pre-commit hook
# test docstring enforcement
