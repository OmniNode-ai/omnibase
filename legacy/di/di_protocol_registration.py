# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "di_protocol_registration"
# namespace: "omninode.tools.di_protocol_registration"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:12+00:00"
# last_modified_at: "2025-05-05T13:00:12+00:00"
# entrypoint: "di_protocol_registration.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Centralized Protocol Registration for Foundation DI

This module registers all core Protocols and their default/mock/real implementations
with the DI container. Update this file as new Protocols or implementations are added.

For plugin/extension Protocols, see the plugin registration pattern in the DI README.
"""

from foundation.di.di_container import DIContainer, ServiceLifetime
from foundation.protocol.protocol_validate_async import ProtocolValidateAsync
from foundation.protocol.protocol_database import ProtocolDatabase
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.protocol.protocol_logger import ProtocolLogger
from foundation.protocol.protocol_repository import ProtocolRepository

# Add additional Protocol imports as needed


# --- Placeholder/mock implementations (replace with real ones as available) ---
class NoOpLogger:
    def info(self, msg, *args, **kwargs):
        pass

    def warning(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        pass

    def debug(self, msg, *args, **kwargs):
        pass


class InMemoryDatabase:
    def query(self, sql):
        return []


class InMemoryRepository:
    def get_all(self):
        return []


class DummyProtocolValidateFixture:
    def get_fixture(self, config=None):
        return None


class DummyProtocolValidateAsync:
    async def validate(self, target, config=None):
        return {}


# --- Registration function ---
def register_protocols(container: DIContainer):
    """
    Register all core Protocols and their default/mock/real implementations
    with the provided DI container.
    """
    container.register(ProtocolLogger, NoOpLogger, lifetime=ServiceLifetime.SINGLETON)
    container.register(ProtocolDatabase, InMemoryDatabase, lifetime=ServiceLifetime.SINGLETON)
    container.register(
        ProtocolRepository, InMemoryRepository, lifetime=ServiceLifetime.SINGLETON
    )
    container.register(
        ProtocolValidateFixture, DummyProtocolValidateFixture, lifetime=ServiceLifetime.TRANSIENT
    )
    container.register(
        ProtocolValidateAsync, DummyProtocolValidateAsync, lifetime=ServiceLifetime.TRANSIENT
    )
    # Add additional Protocol registrations as needed