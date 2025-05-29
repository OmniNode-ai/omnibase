# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:01:58.029715'
# description: Stamped by PythonHandler
# entrypoint: python://revert_incorrect_stamps.py
# hash: 5d32b4440a19308a6aa4d427a08cb17acd6f9e6a388da61d520073fdeb4a7606
# last_modified_at: '2025-05-29T13:43:05.957437+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: revert_incorrect_stamps.py
# namespace:
#   value: py://omnibase.revert_incorrect_stamps_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 8da96c31-44a8-4543-9d7f-cd3247a3868d
# version: 1.0.0
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Script to identify and revert files that only have incorrect stamper changes.

This script identifies files where the only changes are:
1. protocol_version changed from 0.1.0 to 1.1.0 (incorrect)
2. schema_version changed from 0.1.0 to 1.1.0 (incorrect)
3. uuid changed (should be preserved - idempotency bug)
4. created_at changed (should be preserved - idempotency bug)
5. last_modified_at changed (expected)
6. hash changed (expected due to other changes)

If a file only has these metadata header changes and no actual content changes,
it will be reverted.
"""

import subprocess
import sys
from pathlib import Path


def get_modified_files():
    """Get list of modified files from git."""
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True,
        check=True
    )
    return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]


def get_file_diff(filepath):
    """Get the diff for a specific file."""
    result = subprocess.run(
        ["git", "diff", filepath],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout


def is_only_incorrect_header_changes(diff_content):
    """
    Check if the diff only contains incorrect header changes.
    
    Returns True if the file should be reverted (only has incorrect stamper changes).
    """
    lines = diff_content.split('\n')
    
    # Track what we've seen
    has_protocol_version_change = False
    has_schema_version_change = False
    has_uuid_change = False
    has_created_at_change = False
    has_content_changes = False
    
    # Look for specific patterns
    for line in lines:
        if line.startswith('@@'):
            continue
        elif line.startswith('diff --git') or line.startswith('index '):
            continue
        elif line.startswith('---') or line.startswith('+++'):
            continue
        elif '# protocol_version:' in line:
            if '-# protocol_version: 0.1.0' in line or '+# protocol_version: 1.1.0' in line:
                has_protocol_version_change = True
            else:
                # Unexpected protocol_version change
                return False
        elif '# schema_version:' in line:
            if '-# schema_version: 0.1.0' in line or '+# schema_version: 1.1.0' in line:
                has_schema_version_change = True
            else:
                # Unexpected schema_version change
                return False
        elif '# uuid:' in line:
            has_uuid_change = True
        elif '# created_at:' in line:
            has_created_at_change = True
        elif '# last_modified_at:' in line:
            # Expected to change
            continue
        elif '# hash:' in line:
            # Expected to change
            continue
        elif '# namespace:' in line:
            # May change, but not a content change
            continue
        elif line.startswith('-') or line.startswith('+'):
            # Check if this is a metadata line or actual content
            stripped = line[1:].strip()
            if not (stripped.startswith('#') or stripped == '' or 
                   'metadata_version:' in stripped or 'protocol_version:' in stripped or
                   'owner:' in stripped or 'copyright:' in stripped or 
                   'schema_version:' in stripped or 'name:' in stripped or
                   'version:' in stripped or 'uuid:' in stripped or
                   'author:' in stripped or 'created_at:' in stripped or
                   'last_modified_at:' in stripped or 'description:' in stripped or
                   'state_contract:' in stripped or 'lifecycle:' in stripped or
                   'hash:' in stripped or 'entrypoint:' in stripped or
                   'runtime_language_hint:' in stripped or 'namespace:' in stripped or
                   'meta_type:' in stripped or '===' in stripped):
                has_content_changes = True
                break
    
    # File should be reverted if:
    # 1. It has the incorrect protocol_version change (0.1.0 -> 1.1.0)
    # 2. It has the incorrect schema_version change (0.1.0 -> 1.1.0) 
    # 3. It has uuid/created_at changes (idempotency bug)
    # 4. It has NO actual content changes
    return (has_protocol_version_change and 
            has_schema_version_change and 
            (has_uuid_change or has_created_at_change) and 
            not has_content_changes)


def revert_file(filepath):
    """Revert a specific file."""
    print(f"Reverting {filepath}...")
    subprocess.run(["git", "checkout", "HEAD", "--", filepath], check=True)


def main():
    """Main function."""
    print("Identifying files with only incorrect stamper changes...")
    
    modified_files = get_modified_files()
    files_to_revert = []
    
    for filepath in modified_files:
        if not Path(filepath).exists():
            continue
            
        # Skip certain files that we know should not be reverted
        if filepath in ['.onextree', 'src/omnibase/model/model_node_metadata.py', 
                       'src/omnibase/runtimes/onex_runtime/v1_0_0/handlers/handler_python.py',
                       'src/omnibase/nodes/node_manager_node/v1_0_0/helpers/helpers_cli_commands.py',
                       'src/omnibase/nodes/node_manager_node/v1_0_0/helpers/helpers_maintenance.py']:
            print(f"Skipping {filepath} (intentional changes)")
            continue
            
        try:
            diff_content = get_file_diff(filepath)
            if is_only_incorrect_header_changes(diff_content):
                files_to_revert.append(filepath)
                print(f"✓ {filepath} - only incorrect header changes")
            else:
                print(f"✗ {filepath} - has content changes, keeping")
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    if files_to_revert:
        print(f"\nFound {len(files_to_revert)} files to revert:")
        for filepath in files_to_revert:
            print(f"  - {filepath}")
        
        response = input(f"\nRevert these {len(files_to_revert)} files? (y/N): ")
        if response.lower() == 'y':
            for filepath in files_to_revert:
                revert_file(filepath)
            print(f"\nReverted {len(files_to_revert)} files.")
        else:
            print("Aborted.")
    else:
        print("\nNo files found that need reverting.")


if __name__ == "__main__":
    main()
