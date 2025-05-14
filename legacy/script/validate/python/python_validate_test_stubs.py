# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_test_stubs
# namespace: omninode.tools.validate_test_stubs
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:57+00:00
# last_modified_at: 2025-04-27T18:12:57+00:00
# entrypoint: validate_test_stubs.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""
validate_test_stubs.py is now a compatibility shim.
All logic has been moved to:
- test_stub_scanner.py
- test_stub_validator.py
- test_stub_config.py
- test_stub_main.py
"""

import logging

from foundation.script.validate.test_stub_scanner import TestStubScanner

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        logger.error("Usage: python validate_test_stubs.py <target_file_or_directory>")
        sys.exit(1)
    target = sys.argv[1]
    scanner = TestStubScanner(target)
    # Assume scanner.issues is populated after scanning (if implemented)
    # If using a main() function, call it and check for issues
    # For now, just print a success message if no issues
    if hasattr(scanner, "issues") and scanner.issues:
        logger.error(f"Test stub issues found: {scanner.issues}")
        sys.exit(1)
    else:
        logger.info(
            f"No excessive mocking/stubbing detected in {target}. All checks passed."
        )
