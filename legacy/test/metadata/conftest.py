import pytest
from foundation.fixture.fixture_registry import FIXTURE_REGISTRY

@pytest.fixture(scope="session")
def fixture_registry():
    return FIXTURE_REGISTRY 