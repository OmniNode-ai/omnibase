# Minimal conftest.py for node-local tests
# Ensures pytest discovers shared fixtures from src/omnibase/conftest.py
# See ONEX testing standards for rationale
from omnibase.conftest import *
from omnibase.schemas.loader import SchemaLoader  # Canonical implementation for tests
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader

@pytest.fixture
def metadata_loader() -> ProtocolSchemaLoader:
    """Fixture for protocol-typed metadata loader (SchemaLoader)."""
    return SchemaLoader()

# When instantiating NodeRegistryNode in tests, inject metadata_loader=metadata_loader
