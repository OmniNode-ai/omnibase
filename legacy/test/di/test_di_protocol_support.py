# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_di_protocol_support"
# namespace: "omninode.tools.test_di_protocol_support"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:23+00:00"
# last_modified_at: "2025-05-05T13:00:23+00:00"
# entrypoint: "test_di_protocol_support.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Protocol']
# base_class: ['Protocol']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Tests for Protocol support in the dependency injection container.

This module tests the ability to register implementations against Protocol types,
which define structural interfaces in Python.
"""

from typing import Protocol, runtime_checkable

from foundation.di.di_container import DIContainer


# Define protocols
@runtime_checkable
class Serializable(Protocol):
    """Protocol for objects that can be serialized to and from dictionaries."""

    def to_dict(self) -> dict:
        """Convert the object to a dictionary.

        Returns:
            Dictionary representation of the object.
        """
        ...

    def from_dict(self, data: dict) -> None:
        """Initialize the object from a dictionary.

        Args:
            data: Dictionary containing object data.
        """
        ...


@runtime_checkable
class Identifiable(Protocol):
    """Protocol for objects that have an ID."""

    @property
    def id(self) -> str:
        """Get the object ID.

        Returns:
            The object ID as a string.
        """
        ...


# Implementations
class User:
    """User implementation that satisfies both Serializable and Identifiable protocols."""

    def __init__(self, name: str = "Default", user_id: str = "default"):
        """Initialize a new user.

        Args:
            name: The user's name.
            user_id: The user's ID.
        """
        self.name = name
        self._id = user_id

    def to_dict(self) -> dict:
        """Convert the user to a dictionary.

        Returns:
            Dictionary representation of the user.
        """
        return {"name": self.name, "id": self._id}

    def from_dict(self, data: dict) -> None:
        """Initialize the user from a dictionary.

        Args:
            data: Dictionary containing user data.
        """
        self.name = data.get("name", "")
        self._id = data.get("id", "")

    @property
    def id(self) -> str:
        """Get the user ID.

        Returns:
            The user ID.
        """
        return self._id


class Product:
    """Product implementation that satisfies both Serializable and Identifiable protocols."""

    def __init__(self, title: str = "Default", product_id: str = "default"):
        """Initialize a new product.

        Args:
            title: The product's title.
            product_id: The product's ID.
        """
        self.title = title
        self._id = product_id

    def to_dict(self) -> dict:
        """Convert the product to a dictionary.

        Returns:
            Dictionary representation of the product.
        """
        return {"title": self.title, "id": self._id}

    def from_dict(self, data: dict) -> None:
        """Initialize the product from a dictionary.

        Args:
            data: Dictionary containing product data.
        """
        self.title = data.get("title", "")
        self._id = data.get("id", "")

    @property
    def id(self) -> str:
        """Get the product ID.

        Returns:
            The product ID.
        """
        return self._id


# Service using protocols
class DataStore:
    """Service that stores Serializable objects."""

    def __init__(self, serializable_items: list[Serializable]):
        """Initialize the data store with a list of serializable items.

        Args:
            serializable_items: List of items that can be serialized.
        """
        self.items = serializable_items

    def add_item(self, item: Serializable) -> None:
        """Add a serializable item to the store.

        Args:
            item: Item that can be serialized.
        """
        self.items.append(item)

    def get_all_dicts(self) -> list[dict]:
        """Get all items as dictionaries.

        Returns:
            List of dictionaries representing the items.
        """
        return [item.to_dict() for item in self.items]


class Registry:
    """Service that registers objects by ID."""

    def __init__(self):
        """Initialize an empty registry."""
        self.registry = {}

    def register_item(self, item: Identifiable) -> None:
        """Register an item in the registry.

        Args:
            item: Item with an ID.
        """
        self.registry[item.id] = item

    def get_item(self, item_id: str) -> Identifiable:
        """Get an item from the registry by ID.

        Args:
            item_id: The ID of the item to get.

        Returns:
            The item with the specified ID.
        """
        return self.registry.get(item_id)


class TestProtocolSupport:
    """Tests for Protocol support."""

    def test_register_protocol_implementation(self):
        """Test registering and resolving implementations for protocols."""
        container = DIContainer()

        # Register primitive types
        container.register_instance(str, "default-name")

        # Register an implementation for a protocol
        container.register(Serializable, User)

        # Resolve by protocol
        serializable = container.resolve(Serializable)

        # Verify it's the correct implementation
        assert isinstance(serializable, User)
        # Verify it satisfies the protocol
        assert isinstance(serializable, Serializable)

    def test_register_multiple_protocol_implementations(self):
        """Test registering multiple implementations for a protocol using names."""
        container = DIContainer()

        # Register primitive types with names
        container.register_instance(str, "John", name="user_name")
        container.register_instance(str, "user123", name="user_id")
        container.register_instance(str, "Laptop", name="product_title")
        container.register_instance(str, "prod456", name="product_id")

        # Register User as a named singleton to make sure the same instance is used
        user = User("John", "user123")
        container.register_instance(User, user, name="user")

        # Register Product as a named singleton to make sure the same instance is used
        product = Product("Laptop", "prod456")
        container.register_instance(Product, product, name="product")

        # Register multiple implementations for protocols with names
        container.register(Serializable, User, name="user")
        container.register(Serializable, Product, name="product")
        container.register(Identifiable, User, name="user")
        container.register(Identifiable, Product, name="product")

        # Resolve by name
        user_serializable = container.resolve(Serializable, name="user")
        product_serializable = container.resolve(Serializable, name="product")
        user_identifiable = container.resolve(Identifiable, name="user")
        product_identifiable = container.resolve(Identifiable, name="product")

        # Verify they're the correct implementations
        assert isinstance(user_serializable, User)
        assert isinstance(product_serializable, Product)
        assert isinstance(user_identifiable, User)
        assert isinstance(product_identifiable, Product)

        # Verify they have the expected values
        assert user_serializable.name == "John"
        assert user_serializable.id == "user123"
        assert product_serializable.title == "Laptop"
        assert product_serializable.id == "prod456"

    def test_service_with_protocol_dependencies(self):
        """Test services with protocol dependencies."""
        container = DIContainer()

        # Create some instances
        user = User("John", "user123")
        product = Product("Laptop", "prod456")

        # Register a factory that creates DataStore with the list of items
        container.register_factory(DataStore, lambda: DataStore([user, product]))

        # Resolve the DataStore
        data_store = container.resolve(DataStore)

        # Verify it has the correct items
        assert len(data_store.items) == 2
        assert user in data_store.items
        assert product in data_store.items

        # Test dictionaries
        dicts = data_store.get_all_dicts()
        assert len(dicts) == 2
        assert {"name": "John", "id": "user123"} in dicts
        assert {"title": "Laptop", "id": "prod456"} in dicts

    def test_registry_with_protocol_dependencies(self):
        """Test registry with Identifiable protocol dependencies."""
        container = DIContainer()

        # Register Registry
        container.register(Registry)

        # Resolve Registry
        registry = container.resolve(Registry)

        # Create and register items
        user = User("John", "user123")
        product = Product("Laptop", "prod456")

        registry.register_item(user)
        registry.register_item(product)

        # Test retrieval
        retrieved_user = registry.get_item("user123")
        retrieved_product = registry.get_item("prod456")

        assert retrieved_user is user
        assert retrieved_product is product
        assert isinstance(retrieved_user, Identifiable)
        assert isinstance(retrieved_product, Identifiable)