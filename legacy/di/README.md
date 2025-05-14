# Dependency Injection Framework

## Overview

The Foundation DI framework provides a comprehensive dependency injection system built on top of the [Punq](https://github.com/bobthemighty/punq) library, with significant enhancements for enterprise-level applications. It manages object creation, lifetime, and dependency resolution in a clean, testable, and maintainable way.

Key features:
- Service lifetime management (transient, scoped, singleton)
- Interface and Protocol support
- Named and conditional service registration
- Dependency validation and circular dependency detection
- Container scoping and inheritance
- Factory method registration
- Async context management
- Middleware pattern for container extensions

## Centralized Protocol Registration

All core Protocols and their default/mock/real implementations are registered in a single file:

- `foundation/di/di_protocol_registration.py`

This file is the single source of truth for Protocol registration. Update it whenever you add, remove, or change a Protocol or its implementation. This ensures:
- Auditability and clarity for onboarding and code review
- Easy environment/test overrides
- Explicit, maintainable DI wiring

**How to use:**
- Import and call `register_protocols(container)` during DI container initialization (e.g., in your app or in `DIContainerFactory`).
- Add new Protocols and their implementations to this file as the project evolves.
- For plugin/extension Protocols, see the plugin registration pattern below.

## Plugin/Extension Protocol Registration

For plugins or non-core extensions, use a distributed or auto-discovery pattern. Document the registration function in your plugin and call it after core registration if needed.

## Installation

The DI framework is part of the foundation package and is available after installing the foundation container:

```python
from foundation.di import DIContainer, ServiceLifetime
```

## Architecture

The framework is organized into several modules:

- **container.py**: Core container implementation with registration and resolution
- **interfaces.py**: Interface and Protocol support
- **advanced.py**: Advanced features like validation and conditional resolution
- **management.py**: Container management features like scoping and middleware

## Basic Usage

### Creating a Container

```python
from foundation.di import DIContainer

# Create a new container
container = DIContainer()
```

### Registering Services

```python
# Basic registration
container.register(IService, ServiceImpl)

# With lifetime
container.register(IService, ServiceImpl, lifetime=ServiceLifetime.SINGLETON)

# Named registration
container.register(IService, ServiceImpl1, name="implementation1")
container.register(IService, ServiceImpl2, name="implementation2")

# Instance registration
service = ServiceImpl()
container.register_instance(IService, service)

# Factory registration
container.register_factory(IService, lambda: ServiceImpl())

# Factory with container access
container.register_factory(
    IService,
    lambda container: ServiceImpl(container.resolve(IDependency))
)
```

### Resolving Services

```python
# Basic resolution
service = container.resolve(IService)

# Named resolution
service1 = container.resolve(IService, name="implementation1")
service2 = container.resolve(IService, name="implementation2")

# Automatic dependency resolution
class ServiceWithDependencies:
    def __init__(self, dependency: IDependency):
        self.dependency = dependency

container.register(ServiceWithDependencies)
service = container.resolve(ServiceWithDependencies)  # Dependency automatically injected
```

## Advanced Features

### Interface and Protocol Support

```python
# Abstract Base Class (Interface)
class ILogger(abc.ABC):
    @abc.abstractmethod
    def log(self, message: str) -> None:
        pass

# Protocol
class IDataAccess(Protocol):
    def get_data(self, id: str) -> dict:
        ...

# Register implementations
container.register(ILogger, ConsoleLogger)
container.register(IDataAccess, PostgresDataAccess)
```

### Service Lifetimes

```python
# Transient: New instance every time (default)
container.register(IService, ServiceImpl, lifetime=ServiceLifetime.TRANSIENT)

# Singleton: Same instance every time
container.register(IService, ServiceImpl, lifetime=ServiceLifetime.SINGLETON)

# Scoped: Same instance within a scope
container.register(IService, ServiceImpl, lifetime=ServiceLifetime.SCOPED)
```

### Scoped Resolution

```python
# Create a scoped container
scoped = container.create_scope()

# Resolve scoped service
service1 = scoped.resolve(IScopedService)  # New instance
service2 = scoped.resolve(IScopedService)  # Same instance as service1

# Create another scope
scoped2 = container.create_scope()
service3 = scoped2.resolve(IScopedService)  # Different instance than service1/service2
```

### Async Context Management

```python
# Using async context manager for scopes
async with container.create_async_scope() as async_scope:
    service = async_scope.resolve(IService)
    await service.async_operation()
    # Service will be disposed when context exits if it has a dispose method
```

### Conditional Resolution

```python
# Register with condition
container.register(
    IConfig,
    DevConfig,
    condition=lambda ctx: ctx.get("environment") == "development"
)
container.register(
    IConfig,
    ProdConfig,
    condition=lambda ctx: ctx.get("environment") == "production"
)

# Set context and resolve
container._context["environment"] = "development"
config = container.resolve(IConfig)  # Returns DevConfig instance
```

### Container Factory

```python
# Create a factory with default registrations
factory = DIContainerFactory()
factory.add_default_registration(ILogger, ConsoleLogger)
factory.add_default_registration(IConfig, AppConfig)

# Create containers from factory
container1 = factory.create_container()
container2 = factory.create_container()
```

### Middleware Pattern

```python
# Create a middleware
class LoggingMiddleware(ContainerMiddleware):
    def process(self, service, service_type, next_middleware):
        print(f"Resolving {service_type.__name__}")
        result = next_middleware(service, service_type)
        print(f"Resolved {service_type.__name__}")
        return result

# Add middleware to container
container.use_middleware(LoggingMiddleware())
```

### Dependency Validation

```python
# Check for missing dependencies
validator = DependencyValidator()
validator.validate_dependencies(container)

# Detect circular dependencies
validator.detect_circular_dependencies(ServiceA, get_dependencies_func)
```

## Best Practices

1. **Use Interfaces**: Register services by their interfaces rather than concrete types
2. **Define Clear Lifetimes**: Choose appropriate lifetimes for services
3. **Use Factory Methods** for complex instantiation logic
4. **Container Scope Management**: Create and dispose scopes properly
5. **Validate Dependencies** early to detect issues
6. **Use Middleware** for cross-cutting concerns

## Testing with DI

```python
# Create a container for testing
container = DIContainer()

# Register mocks
mock_service = MagicMock(spec=IService)
container.register_instance(IService, mock_service)

# Use container snapshot for isolation
snapshot = container.create_snapshot()

# Reset container state after test
container.restore_snapshot(snapshot)
```

## Error Handling

The framework provides specific exceptions:

- **MissingDependencyError**: When a required dependency cannot be resolved
- **CircularDependencyError**: When circular dependencies are detected
- **DependencyValidationError**: When dependency validation fails

## Performance Considerations

- Singleton and scoped services provide better performance for expensive objects
- Use container snapshots for test isolation without recreation cost
- Consider factory methods for lazy initialization of resource-intensive services

## Integration with FastAPI (Coming Soon)

The next phase will include seamless integration with FastAPI:

```python
# Register the container with FastAPI
app = FastAPI()
container = DIContainer()
app.container = container

# Use DI in endpoints
@app.get("/items/{item_id}")
def read_item(item_id: str, service: ItemService = Depends(Inject(ItemService))):
    return service.get_item(item_id)
```
