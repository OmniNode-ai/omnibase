# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_di_container"
# namespace: "omninode.tools.test_di_container"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:23+00:00"
# last_modified_at: "2025-05-05T13:00:23+00:00"
# entrypoint: "test_di_container.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""Tests for the dependency injection container (pytest style, flexible setup)."""

from typing import Any

import pytest
from foundation.di.di_container import DIContainer, ServiceLifetime
from foundation.protocol.logger import ILogger
from foundation.protocol.repository import IRepository
from punq import MissingDependencyError


class Logger:
    def log(self, message: str) -> None:
        return None


class Database:
    def query(self, sql: str) -> list[Any]:
        return []


class Repository:
    def __init__(self, db: IDatabase):
        self.db = db

    def get_all(self) -> list[Any]:
        return self.db.query("SELECT * FROM items")


class Service:
    def __init__(self, logger: ILogger, repo: IRepository):
        self.logger = logger
        self.repo = repo
        self.counter = 0

    def increment(self) -> int:
        self.counter += 1
        return self.counter


@pytest.fixture
def container():
    """Fixture for a fresh DIContainer instance."""
    return DIContainer()


def test_register_concrete_type(container):
    """Test registering a concrete type."""
    container.register(Logger)
    logger = container.resolve(Logger)
    assert isinstance(logger, Logger)


def test_register_interface(container):
    """Test registering an interface with a concrete type."""
    container.register(ILogger, Logger)
    logger = container.resolve(ILogger)
    assert isinstance(logger, Logger)


def test_register_singleton(container):
    """Test registering a singleton service."""
    container.register(Logger, lifetime=ServiceLifetime.SINGLETON)
    logger1 = container.resolve(Logger)
    logger2 = container.resolve(Logger)
    assert logger1 is logger2  # Same instance


def test_register_transient(container):
    """Test registering a transient service."""
    container.register(Logger, lifetime=ServiceLifetime.TRANSIENT)
    logger1 = container.resolve(Logger)
    logger2 = container.resolve(Logger)
    assert logger1 is not logger2  # Different instances


def test_register_scoped(container):
    """Test registering a scoped service."""
    container.register(Logger, lifetime=ServiceLifetime.SCOPED)
    with container.create_scope() as scope:
        logger1 = scope.resolve(Logger)
        logger2 = scope.resolve(Logger)
        assert logger1 is logger2
    with container.create_scope() as scope:
        logger3 = scope.resolve(Logger)
        assert logger1 is not logger3


def test_automatic_dependency_resolution(container):
    """Test automatic resolution of dependencies."""
    container.register(ILogger, Logger)
    container.register(IDatabase, Database)
    container.register(IRepository, Repository)
    container.register(Service)
    service = container.resolve(Service)
    assert isinstance(service, Service)
    assert isinstance(service.logger, Logger)
    assert isinstance(service.repo, Repository)
    assert isinstance(service.repo.db, Database)


def test_factory_registration(container):
    """Test registering a factory function."""

    def create_logger() -> ILogger:
        logger = Logger()
        return logger

    container.register_factory(ILogger, create_logger)
    logger = container.resolve(ILogger)
    assert isinstance(logger, Logger)


def test_instance_registration(container):
    """Test registering a specific instance."""
    logger_instance = Logger()
    container.register_instance(ILogger, logger_instance)
    resolved_logger = container.resolve(ILogger)
    assert resolved_logger is logger_instance


def test_cannot_resolve_unregistered_service(container):
    """Test that resolving an unregistered service raises an exception."""
    with pytest.raises(MissingDependencyError):
        container.resolve(Logger)