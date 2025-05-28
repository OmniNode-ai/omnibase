#!/usr/bin/env python3
"""
Test to reproduce the UUID and created_at idempotency bug.

This test demonstrates that UUID and created_at fields are changing
when they should be preserved for idempotency.
"""

import tempfile
from pathlib import Path
from typing import Dict, Any
import re

from omnibase.nodes.stamper_node.v1_0_0.helpers.stamper_engine import StamperEngine
from omnibase.nodes.stamper_node.v1_0_0.models.state import StamperInputState
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_python import PythonHandler
from omnibase.utils.real_file_io import RealFileIO
from omnibase.fixtures.mocks.dummy_schema_loader import DummySchemaLoader
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import OnexVersionLoader


def extract_metadata_fields(content: str) -> Dict[str, str]:
    """Extract metadata fields from stamped content."""
    fields = {}
    
    # Extract UUID
    uuid_match = re.search(r'# uuid: ([a-f0-9-]+)', content)
    if uuid_match:
        fields['uuid'] = uuid_match.group(1)
    
    # Extract created_at
    created_match = re.search(r'# created_at: ([0-9T:.+-]+)', content)
    if created_match:
        fields['created_at'] = created_match.group(1)
    
    # Extract last_modified_at
    modified_match = re.search(r'# last_modified_at: ([0-9T:.+-]+)', content)
    if modified_match:
        fields['last_modified_at'] = modified_match.group(1)
    
    # Extract hash
    hash_match = re.search(r'# hash: ([a-f0-9]+)', content)
    if hash_match:
        fields['hash'] = hash_match.group(1)
    
    return fields


def test_idempotency_bug_reproduction():
    """Test that reproduces the UUID and created_at idempotency bug."""
    
    # Create a simple Python file
    test_content = '''# Test file for idempotency
def hello():
    return "world"
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        test_file_path = Path(f.name)
    
    try:
        # Initialize stamper components
        file_io = RealFileIO()
        schema_loader = DummySchemaLoader()
        handler = PythonHandler()
        stamper_engine = StamperEngine(file_io=file_io, schema_loader=schema_loader)
        
        # Get the current schema version
        version_loader = OnexVersionLoader()
        schema_version = version_loader.get_onex_versions().schema_version
        
        # First stamping
        print("=== FIRST STAMPING ===")
        input_state = StamperInputState(
            version=schema_version,
            file_path=str(test_file_path),
            author="Test Author",
            discover_functions=False
        )
        
        result1 = stamper_engine.stamp_file(input_state)
        content1 = test_file_path.read_text()
        fields1 = extract_metadata_fields(content1)
        
        print(f"UUID: {fields1.get('uuid')}")
        print(f"created_at: {fields1.get('created_at')}")
        print(f"last_modified_at: {fields1.get('last_modified_at')}")
        print(f"hash: {fields1.get('hash')}")
        
        # Second stamping (should be idempotent)
        print("\n=== SECOND STAMPING (should be idempotent) ===")
        result2 = stamper_engine.stamp_file(input_state)
        content2 = test_file_path.read_text()
        fields2 = extract_metadata_fields(content2)
        
        print(f"UUID: {fields2.get('uuid')}")
        print(f"created_at: {fields2.get('created_at')}")
        print(f"last_modified_at: {fields2.get('last_modified_at')}")
        print(f"hash: {fields2.get('hash')}")
        
        # Check for idempotency violations
        print("\n=== IDEMPOTENCY CHECK ===")
        
        uuid_changed = fields1.get('uuid') != fields2.get('uuid')
        created_changed = fields1.get('created_at') != fields2.get('created_at')
        
        if uuid_changed:
            print(f"❌ UUID CHANGED: {fields1.get('uuid')} -> {fields2.get('uuid')}")
        else:
            print(f"✅ UUID preserved: {fields1.get('uuid')}")
            
        if created_changed:
            print(f"❌ created_at CHANGED: {fields1.get('created_at')} -> {fields2.get('created_at')}")
        else:
            print(f"✅ created_at preserved: {fields1.get('created_at')}")
        
        # last_modified_at should be the same for idempotent operations
        modified_changed = fields1.get('last_modified_at') != fields2.get('last_modified_at')
        if modified_changed:
            print(f"❌ last_modified_at CHANGED: {fields1.get('last_modified_at')} -> {fields2.get('last_modified_at')}")
        else:
            print(f"✅ last_modified_at preserved: {fields1.get('last_modified_at')}")
        
        # Hash should be the same for identical content
        hash_changed = fields1.get('hash') != fields2.get('hash')
        if hash_changed:
            print(f"❌ hash CHANGED: {fields1.get('hash')} -> {fields2.get('hash')}")
        else:
            print(f"✅ hash preserved: {fields1.get('hash')}")
        
        # Test with content change
        print("\n=== THIRD STAMPING (with content change) ===")
        modified_content = test_content + '\n# Added comment\n'
        test_file_path.write_text(modified_content)
        
        result3 = stamper_engine.stamp_file(input_state)
        content3 = test_file_path.read_text()
        fields3 = extract_metadata_fields(content3)
        
        print(f"UUID: {fields3.get('uuid')}")
        print(f"created_at: {fields3.get('created_at')}")
        print(f"last_modified_at: {fields3.get('last_modified_at')}")
        print(f"hash: {fields3.get('hash')}")
        
        # After content change
        print("\n=== CONTENT CHANGE CHECK ===")
        
        uuid_changed_after_content = fields2.get('uuid') != fields3.get('uuid')
        created_changed_after_content = fields2.get('created_at') != fields3.get('created_at')
        modified_changed_after_content = fields2.get('last_modified_at') != fields3.get('last_modified_at')
        hash_changed_after_content = fields2.get('hash') != fields3.get('hash')
        
        if uuid_changed_after_content:
            print(f"❌ UUID CHANGED after content change: {fields2.get('uuid')} -> {fields3.get('uuid')}")
        else:
            print(f"✅ UUID preserved after content change: {fields2.get('uuid')}")
            
        if created_changed_after_content:
            print(f"❌ created_at CHANGED after content change: {fields2.get('created_at')} -> {fields3.get('created_at')}")
        else:
            print(f"✅ created_at preserved after content change: {fields2.get('created_at')}")
        
        if modified_changed_after_content:
            print(f"✅ last_modified_at updated after content change: {fields2.get('last_modified_at')} -> {fields3.get('last_modified_at')}")
        else:
            print(f"❌ last_modified_at should have updated: {fields2.get('last_modified_at')}")
        
        if hash_changed_after_content:
            print(f"✅ hash updated after content change: {fields2.get('hash')} -> {fields3.get('hash')}")
        else:
            print(f"❌ hash should have updated: {fields2.get('hash')}")
        
        # Summary
        print("\n=== SUMMARY ===")
        idempotency_violations = []
        
        if uuid_changed:
            idempotency_violations.append("UUID changed during idempotent operation")
        if created_changed:
            idempotency_violations.append("created_at changed during idempotent operation")
        if modified_changed:
            idempotency_violations.append("last_modified_at changed during idempotent operation")
        if hash_changed:
            idempotency_violations.append("hash changed during idempotent operation")
            
        if uuid_changed_after_content:
            idempotency_violations.append("UUID changed after content modification")
        if created_changed_after_content:
            idempotency_violations.append("created_at changed after content modification")
        
        if idempotency_violations:
            print("❌ IDEMPOTENCY VIOLATIONS DETECTED:")
            for violation in idempotency_violations:
                print(f"   - {violation}")
            return False
        else:
            print("✅ All idempotency checks passed!")
            return True
            
    finally:
        # Cleanup
        if test_file_path.exists():
            test_file_path.unlink()


if __name__ == "__main__":
    test_idempotency_bug_reproduction() 