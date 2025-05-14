#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_stub_cli"
# namespace: "omninode.tools.test_stub_cli"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:27+00:00"
# last_modified_at: "2025-05-05T13:00:27+00:00"
# entrypoint: "test_stub_cli.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""cli.py
containers.foundation.src.foundation.script.validation.test_stub.cli.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Scan for excessive stubbing in test files."
    )
    parser.add_argument("path", help="Path to scan (file or directory)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    scanner = TestStubScanner(args.path, verbose=args.verbose)
    issues = scanner.scan()
    if issues:
        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(issue)
    else:
        print("No excessive stubbing issues found.")


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    main()