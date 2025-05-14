import pytest
from omnibase.core.core_registry import CoreRegistry

@pytest.fixture
def registry():
    # Return a minimal registry instance for tests
    return CoreRegistry() 