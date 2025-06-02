from pathlib import Path
from typing import Any, Callable, Optional
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.enums import OnexStatus
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.nodes.node_constants import (
    TEST_HANDLER_NAME, TEST_EXTENSION, SOURCE_TEST
)

# Canonical test case base class
class HandlerRegistryTestCase:
    def __init__(self, id: str, description: str, test_logic: Callable, success_criteria: Callable):
        self.id = id
        self.description = description
        self.test_logic = test_logic
        self.success_criteria = success_criteria
    def run(self, handler_registry):
        result = self.test_logic(handler_registry)
        self.success_criteria(result)

# Example test logic and success criteria for registration

def test_enhanced_handler_registration_logic(handler_registry):
    class MockCustomHandler(ProtocolFileTypeHandler):
        def __init__(self, name: str = TEST_HANDLER_NAME): self.name = name
        @property
        def handler_name(self): return self.name
        @property
        def handler_version(self): return "1.0.0"
        @property
        def handler_author(self): return "Test Suite"
        @property
        def handler_description(self): return f"Mock handler: {self.name}"
        @property
        def supported_extensions(self): return [TEST_EXTENSION]
        @property
        def supported_filenames(self): return []
        @property
        def handler_priority(self): return 0
        @property
        def requires_content_analysis(self): return True
        def can_handle(self, path, content): return True
        def extract_block(self, path, content): return None, content
        def serialize_block(self, meta): return ""
        def stamp(self, path, content, **kwargs):
            return OnexResultModel(status=OnexStatus.SUCCESS, target=str(path), messages=[], metadata={"handler": self.name})
        def validate(self, path, content, **kwargs):
            return OnexResultModel(status=OnexStatus.SUCCESS, target=str(path), messages=[], metadata={"validated": True})
        def pre_validate(self, path, content, **kwargs): return None
        def post_validate(self, path, content, **kwargs): return None
    handler = MockCustomHandler(TEST_HANDLER_NAME)
    handler_registry.register_handler(TEST_EXTENSION, handler, source=SOURCE_TEST, priority=20)
    retrieved = handler_registry.get_handler(Path(f"test{TEST_EXTENSION}"))
    return retrieved

def enhanced_handler_registration_success_criteria(result):
    assert result is not None
    assert hasattr(result, "handler_name")
    assert result.handler_name == TEST_HANDLER_NAME

# Add additional test cases following this pattern

NODE_REGISTRY_TEST_CASES = [
    HandlerRegistryTestCase(
        id="enhanced_handler_registration",
        description="Test enhanced handler registration and retrieval by extension.",
        test_logic=test_enhanced_handler_registration_logic,
        success_criteria=enhanced_handler_registration_success_criteria,
    ),
    # ... Add more cases for named handler, priority, override, etc. ...
] 