import pytest
from foundation.script.validate.validate_registry import ValidatorRegistry

class TestValidator:
    def validate(self, *args, **kwargs):
        pass

def test_validator_version_tracking():
    registry = ValidatorRegistry()
    
    # Register multiple versions of a validator
    meta_v1 = ValidatorMetadata(
        name="test_validator",
        version="1.0.0",
        protocol_version="0.1.0"
    )
    meta_v2 = ValidatorMetadata(
        name="test_validator",
        version="2.0.0",
        protocol_version="0.1.0"
    )
    
    registry.register("test_validator", TestValidator, meta_v1)
    registry.register("test_validator", TestValidator, meta_v2)
    
    # Test getting all versions
    versions = registry.get_validator_versions("test_validator")
    assert len(versions) == 2
    assert "1.0.0" in versions
    assert "2.0.0" in versions
    
    # Test getting latest version
    latest = registry.get_latest_version("test_validator")
    assert latest == "2.0.0"
    
    # Test getting specific version
    validator = registry.get_validator("test_validator", "1.0.0")
    assert validator is not None
    
    # Test version compatibility
    assert registry.check_version_compatibility("test_validator", "1.0.0")
    assert registry.check_version_compatibility("test_validator", "2.0.0")

def test_incompatible_protocol_version():
    registry = ValidatorRegistry()
    
    # Register validator with incompatible protocol version
    meta = ValidatorMetadata(
        name="test_validator",
        version="1.0.0",
        protocol_version="1.0.0"  # Different major version
    )
    
    registry.register("test_validator", TestValidator, meta)
    
    # Should not be compatible with current protocol version (0.1.0)
    assert not registry.check_version_compatibility("test_validator", "1.0.0")

def test_version_parsing():
    registry = ValidatorRegistry()
    
    # Test version parsing with 'v' prefix
    meta = ValidatorMetadata(
        name="test_validator",
        version="v1.0.0",
        protocol_version="v0.1.0"
    )
    
    registry.register("test_validator", TestValidator, meta)
    assert registry.check_version_compatibility("test_validator", "v1.0.0") 