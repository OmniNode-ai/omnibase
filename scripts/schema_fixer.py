# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: schema_fixer.py
# version: 1.0.0
# uuid: f6382d42-3f94-4f3f-8b52-901b8ed58ee7
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.300848
# last_modified_at: 2025-05-28T17:20:05.343215
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 97bf7f1e8e4aaddd36a367c31c8724d813fdb148f9de22a519f5f1077d0bacc2
# entrypoint: python@schema_fixer.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.schema_fixer
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Schema-specific YAML fixer

This script handles complex schema files that need proper indentation
and line length fixes while preserving their semantic structure.
"""

import re
from pathlib import Path


def fix_schema_indentation(content: str) -> str:
    """Fix indentation issues in schema files."""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            fixed_lines.append(line)
            continue

        # Calculate proper indentation based on YAML structure
        if stripped.startswith("$") or stripped in [
            "type:",
            "required:",
            "properties:",
            "description:",
            "enum:",
            "items:",
            "oneOf:",
        ]:
            # Top-level or major section keys
            if stripped.startswith("$"):
                fixed_lines.append(stripped)  # No indentation for schema directives
            else:
                fixed_lines.append(stripped)  # Top-level properties
        elif stripped.startswith("- "):
            # List items - determine proper indentation based on context
            # Look at previous non-empty line to determine context
            prev_line = None
            for i in range(len(fixed_lines) - 1, -1, -1):
                if fixed_lines[i].strip():
                    prev_line = fixed_lines[i]
                    break

            if prev_line and (
                "required:" in prev_line
                or "enum:" in prev_line
                or "items:" in prev_line
            ):
                fixed_lines.append("  " + stripped)  # 2-space indent for list items
            else:
                fixed_lines.append("    " + stripped)  # 4-space indent for nested lists
        elif ":" in stripped:
            # Key-value pairs - determine indentation level
            if any(
                keyword in stripped
                for keyword in [
                    "type:",
                    "format:",
                    "pattern:",
                    "default:",
                    "description:",
                ]
            ):
                # Property attributes
                fixed_lines.append("    " + stripped)
            elif stripped.endswith(":") and not stripped.startswith(" "):
                # Property names
                fixed_lines.append("  " + stripped)
            else:
                # Nested properties
                fixed_lines.append("      " + stripped)
        else:
            # Preserve existing indentation for complex cases
            fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_line_length(content: str, max_length: int = 120) -> str:
    """Fix line length issues by using YAML folded strings."""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        if len(line) <= max_length:
            fixed_lines.append(line)
            continue

        stripped = line.strip()
        indent = line[: len(line) - len(stripped)]

        # Handle long description lines
        if "description:" in stripped:
            # Split long descriptions using YAML folded string
            desc_match = re.match(r"(\s*description:\s*)(.*)", line)
            if desc_match:
                prefix = desc_match.group(1)
                desc_text = desc_match.group(2).strip("'\"")

                # Use folded string format for long descriptions
                fixed_lines.append(f"{prefix}>")

                # Split the description into multiple lines
                words = desc_text.split()
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= max_length - len(indent) - 2:
                        current_line += (" " if current_line else "") + word
                    else:
                        if current_line:
                            fixed_lines.append(f"{indent}  {current_line}")
                        current_line = word

                if current_line:
                    fixed_lines.append(f"{indent}  {current_line}")
            else:
                fixed_lines.append(line)
        else:
            # For other long lines, try to preserve them or split carefully
            fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_schema_file(file_path: Path) -> bool:
    """Fix a schema file with proper indentation and line length."""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Apply fixes
        fixed_content = fix_schema_indentation(content)
        fixed_content = fix_line_length(fixed_content)

        # Only write if content changed
        if fixed_content != content:
            with open(file_path, "w") as f:
                f.write(fixed_content)
            return True

        return False

    except Exception as e:
        print(f"Error fixing schema file {file_path}: {e}")
        return False


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix schema YAML files")
    parser.add_argument("file", help="Schema file to fix")

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return 1

    success = fix_schema_file(file_path)
    if success:
        print(f"✅ Fixed {file_path}")
    else:
        print(f"⚠️  No changes needed for {file_path}")

    return 0


if __name__ == "__main__":
    exit(main())
