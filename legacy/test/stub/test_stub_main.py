#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_stub_main"
# namespace: "omninode.tools.test_stub_main"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:27+00:00"
# last_modified_at: "2025-05-05T13:00:27+00:00"
# entrypoint: "test_stub_main.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""test_stub_main.py containers.foundation.src.foundation.script.validation.te
st_stubs.test_stub_main.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[6] / "src"))
from .test_stub_constants import DEFAULT_MOCK_RATIO_THRESHOLD
from .test_stub_scanner import TestStubScanner


def main():
    parser = argparse.ArgumentParser(description="Test Stub Scanner CLI")
    parser.add_argument("--path", default=".", help="Path to scan for test files")
    parser.add_argument("--threshold", type=float, help="Mock ratio threshold")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--staged-only", action="store_true", help="Only scan staged files"
    )
    parser.add_argument(
        "--mode",
        choices=["warn", "strict"],
        default=None,
        help="Enforcement mode: warn (never block), strict (block on violations)",
    )
    args = parser.parse_args()

    # Determine enforcement mode
    mode = args.mode or os.environ.get("STUBSCANNER_MODE")
    if not mode:
        # Auto-detect: warn-only for foundation, strict otherwise
        cwd = os.getcwd()
        path = str(args.path)
        if "foundation" in cwd or "foundation" in path:
            mode = "warn"
        else:
            mode = "strict"

    scanner = TestStubScanner(
        path=args.path,
        mock_ratio_threshold=args.threshold or DEFAULT_MOCK_RATIO_THRESHOLD,
        verbose=args.verbose,
        staged_only=args.staged_only,
    )

    issues = scanner.scan()
    scanner.print_report()

    if issues:
        if mode == "warn":
            print(
                "\n[STUB SCANNER] WARN-ONLY MODE: Issues found, but not blocking commit/CI."
            )
            sys.exit(0)
        else:
            print("\n[STUB SCANNER] STRICT MODE: Issues found, blocking commit/CI.")
            sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()