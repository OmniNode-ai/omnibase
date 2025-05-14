# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_di_interfaces"
# namespace: "omninode.tools.test_di_interfaces"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:23+00:00"
# last_modified_at: "2025-05-05T13:00:23+00:00"
# entrypoint: "test_di_interfaces.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ABC', 'IDataAccess', 'ILogger']
# base_class: ['ABC', 'IDataAccess', 'ILogger']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Tests for interface-based registration in the dependency injection container.

This module tests the ability to register implementations against interface types,
which are defined using abstract base classes.
"""

from abc import ABC, abstractmethod

from foundation.di.di_container import DIContainer, ServiceLifetime


# Define interfaces (abstract base classes)
class ILogger(ABC):
    """Interface for logging implementations."""

    @abstractmethod
    def log(self, message: str) -> None:
        """Log a message.

        Args:
            message: The message to log.
        """
        pass


class IDataAccess(ABC):
    """Interface for data access implementations."""

    @abstractmethod
    def get_data(self) -> dict:
        """Get data from the data store.

        Returns:
            The retrieved data.
        """
        pass

    @abstractmethod
    def save_data(self, data: dict) -> None:
        """Save data to the data store.

        Args:
            data: The data to save.
        """
        pass


# Implementations
class ConsoleLogger(ILogger):
    """Logger implementation that writes to the console."""

    def log(self, message: str) -> None:
        """Log a message to the console.

        Args:
            message: The message to log.
        """
        print(f"Console: {message}")


class FileLogger(ILogger):
    """Logger implementation that writes to a file."""

    def log(self, message: str) -> None:
        """Log a message to a file.

        Args:
            message: The message to log.
        """
        print(f"File: {message}")


class PostgresDataAccess(IDataAccess):
    """Data access implementation using PostgreSQL."""

    def get_data(self) -> dict:
        """Get data from PostgreSQL.

        Returns:
            The retrieved data.
        """
        return {"source": "postgres"}

    def save_data(self, data: dict) -> None:
        """Save data to PostgreSQL.

        Args:
            data: The data to save.
        """
        print(f"Saving to Postgres: {data}")


class MongoDataAccess(IDataAccess):
    """Data access implementation using MongoDB."""

    def get_data(self) -> dict:
        """Get data from MongoDB.

        Returns:
            The retrieved data.
        """
        return {"source": "mongo"}

    def save_data(self, data: dict) -> None:
        """Save data to MongoDB.

        Args:
            data: The data to save.
        """
        print(f"Saving to MongoDB: {data}")


# Service that depends on interfaces
class UserService:
    """Service for user management that depends on interfaces."""

    def __init__(self, logger: ILogger, data_access: IDataAccess):
        """Initialize the service with dependencies.

        Args:
            logger: The logger to use.
            data_access: The data access implementation to use.
        """
        self.logger = logger
        self.data_access = data_access

    def create_user(self, name: str) -> None:
        """Create a new user.

        Args:
            name: The name of the user to create.
        """
        self.logger.log(f"Creating user: {name}")
        self.data_access.save_data({"name": name})


class TestInterfaceRegistration:
    """Tests for interface-based registration."""

    def test_register_implementation_for_interface(self):
        """Test registering and resolving implementations for interfaces."""
        container = DIContainer()

        # Register implementations for interfaces
        container.register(ILogger, ConsoleLogger)
        container.register(IDataAccess, PostgresDataAccess)

        # Resolve by interface
        logger = container.resolve(ILogger)
        data_access = container.resolve(IDataAccess)

        # Verify they're the correct implementations
        assert isinstance(logger, ConsoleLogger)
        assert isinstance(data_access, PostgresDataAccess)

    def test_service_with_interface_dependencies(self):
        """Test registering a service with interface dependencies."""
        container = DIContainer()

        # Register implementations for interfaces
        container.register(ILogger, ConsoleLogger)
        container.register(IDataAccess, PostgresDataAccess)

        # Register the service
        container.register(UserService)

        # Resolve the service
        user_service = container.resolve(UserService)

        # Verify service has correct implementations
        assert isinstance(user_service.logger, ConsoleLogger)
        assert isinstance(user_service.data_access, PostgresDataAccess)

    def test_register_multiple_implementations_with_names(self):
        """Test registering multiple implementations for an interface using names."""
        container = DIContainer()

        # Register multiple implementations for interfaces with names
        container.register(ILogger, ConsoleLogger, name="console")
        container.register(ILogger, FileLogger, name="file")
        container.register(IDataAccess, PostgresDataAccess, name="postgres")
        container.register(IDataAccess, MongoDataAccess, name="mongo")

        # Resolve by name
        console_logger = container.resolve(ILogger, name="console")
        file_logger = container.resolve(ILogger, name="file")
        postgres_data = container.resolve(IDataAccess, name="postgres")
        mongo_data = container.resolve(IDataAccess, name="mongo")

        # Verify they're the correct implementations
        assert isinstance(console_logger, ConsoleLogger)
        assert isinstance(file_logger, FileLogger)
        assert isinstance(postgres_data, PostgresDataAccess)
        assert isinstance(mongo_data, MongoDataAccess)

    def test_lifetime_management_with_interfaces(self):
        """Test lifetime management with interface-based registration."""
        container = DIContainer()

        # Register with different lifetimes
        container.register(ILogger, ConsoleLogger, lifetime=ServiceLifetime.SINGLETON)
        container.register(
            IDataAccess, PostgresDataAccess, lifetime=ServiceLifetime.TRANSIENT
        )

        # Test singleton - should be the same instance
        singleton1 = container.resolve(ILogger)
        singleton2 = container.resolve(ILogger)
        assert singleton1 is singleton2

        # Test transient - should be different instances
        transient1 = container.resolve(IDataAccess)
        transient2 = container.resolve(IDataAccess)
        assert transient1 is not transient2