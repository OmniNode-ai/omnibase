#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: util_header_templates
# namespace: omninode.tools.util_header_templates
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:52+00:00
# last_modified_at: 2025-04-27T18:12:52+00:00
# entrypoint: util_header_templates.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""
util_header_templates.py
containers.foundation.src.foundation.script.utils.util_header_templates

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import os
import sys
from typing import List

# Constants
SHEBANG = "#!/usr/bin/env python3"
AUTHOR = "Jonah Gray <jonah@omninode.ai>"
DEFAULT_COPYRIGHT = "Copyright (c) 2025 OmniNode.ai"

# Path constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "./."))
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")
HEADER_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "python_header_template.txt")
MODULE_DOCSTRING_TEMPLATE_PATH = os.path.join(
    TEMPLATES_DIR, "python_module_docstring_template.txt"
)


def get_header_template() -> str:
    """
    Get the header template from the template file.

    Returns:
        The header template as a string
    """
    try:
        with open(HEADER_TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading header template: {e}", file=sys.stderr)
        # Fallback template
        return "\n".join(
            [
                "# Copyright (c) 2025 OmniNode.ai",
                "# Filename: {File Name}",
                "# Author: Jonah Gray <jonah@omninode.ai>",
            ]
        )


def get_module_docstring_template() -> str:
    """
    Get the module docstring template from the template file.

    Returns:
        The module docstring template as a string
    """
    try:
        with open(MODULE_DOCSTRING_TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading module docstring template: {e}", file=sys.stderr)
        return "{File Name}\n{Namespace}\n\nModule that handles functionality for the OmniNode platform.\n\nProvides core interfaces and validation logic."


def get_formatted_header(filename: str, include_shebang: bool = True) -> List[str]:
    """
    Get the formatted header for a Python file.

    Args:
        filename: The name of the file
        include_shebang: Whether to include the shebang line

    Returns:
        List of formatted header lines
    """
    # Get the template
    template = get_header_template()

    # Replace placeholders
    header = template.replace("{File Name}", filename)

    # Split into lines
    lines = header.splitlines()

    # Add shebang if requested
    if include_shebang:
        lines.insert(0, SHEBANG)

    return lines


def get_formatted_docstring(filename: str = None, namespace: str = None) -> List[str]:
    """
    Get the formatted module docstring for a Python file.
    Args:
        filename: The name of the file
        namespace: The Python import path for the file
    Returns:
        List of formatted docstring lines
    """
    # Get the template
    template = get_module_docstring_template()
    if filename is None:
        filename = "<unknown>"
    if namespace is None:
        namespace = "<unknown>"
    # Replace placeholders
    docstring = template.replace("{File Name}", filename).replace(
        "{Namespace}", namespace
    )
    # Split into lines (preserving triple quotes)
    lines = docstring.splitlines()
    return lines


def main():
    """Main function to test the template utilities"""
    if len(sys.argv) < 3:
        print("Usage: python util_header_templates.py <filename> <namespace>")
        return 1
    filename = sys.argv[1]
    namespace = sys.argv[2]
    print("Header template:")
    print("-" * 40)
    for line in get_formatted_header(filename):
        print(line)
    print("-" * 40)
    print("\nDocstring template:")
    print("-" * 40)
    for line in get_formatted_docstring(filename, namespace):
        print(line)
    print("-" * 40)
    return 0


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    sys.exit(main())
