# === OmniNode:BaseTest_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "base_metadata_block_test"
# namespace: "foundation.base"
# meta_type: "base_test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "foundation-team"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-11T00:00:00+00:00"
# last_modified_at: "2025-05-11T00:00:00+00:00"
# entrypoint: "base_metadata_block_test.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:BaseTest_Metadata ===

from pathlib import Path
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedMessageModel, UnifiedStatus
from foundation.script.validate.validate_metadata_block_registry import MetadataValidateBlockRegistry

metadata_validate_block_registry = MetadataValidateBlockRegistry()

class BaseMetadataBlockTest:
    """Base class for shared metadata block test logic (not a Protocol)."""
    def _get_validator_for_file(self, fname: str, utility_registry):
        ext = Path(fname).suffix.lower()
        validator_cls = metadata_validate_block_registry.get_validator(ext)
        assert validator_cls is not None, f"No validator registered for {ext}"
        return validator_cls(logger=None, utility_registry=utility_registry)

    def get_canonical_validator(self, utility_registry):
        """Return a canonical validator instance for type safety tests (default: .py)."""
        ext = '.py'
        validator_cls = metadata_validate_block_registry.get_validator(ext)
        assert validator_cls is not None, f"No validator registered for {ext}"
        return validator_cls(logger=None, utility_registry=utility_registry)

    def test_type_safety(self):
        """Type safety test for canonical metadata block validator."""
        class TestLogger:
            def info(self, msg, *a, **k): pass
            def warning(self, msg, *a, **k): pass
            def error(self, msg, *a, **k): pass
            def debug(self, msg, *a, **k): pass
        ext = '.py'
        validator_cls = metadata_validate_block_registry.get_validator(ext)
        assert validator_cls is not None, f"No validator registered for {ext}"
        validator = validator_cls(logger=TestLogger())
        assert hasattr(validator, "validate"), "Validator must have a validate method"
        assert callable(getattr(validator, "validate")), "validate must be callable"
        if hasattr(validator, "get_name"):
            assert callable(getattr(validator, "get_name")), "get_name must be callable if present"
        if hasattr(validator, "validate_main"):
            assert callable(getattr(validator, "validate_main")), "validate_main must be callable if present" 